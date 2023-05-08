import torch
import torch.nn.functional as F
from transformers import AutoTokenizer, AutoModel

# Load the model stored in models/embedding-model
tokenizer = AutoTokenizer.from_pretrained('models/embedding-model', local_files_only=True)
model = AutoModel.from_pretrained('models/embedding-model', local_files_only=True)

# Mean Pooling - Take attention mask into account for correct averaging
def mean_pooling(model_output, attention_mask):
    token_embeddings = model_output[0] #First element of model_output contains all token embeddings
    input_mask_expanded = attention_mask.unsqueeze(-1).expand(token_embeddings.size()).float()
    return torch.sum(token_embeddings * input_mask_expanded, 1) / torch.clamp(input_mask_expanded.sum(1), min=1e-9)

# Create embeddings using chosen embedding-model
def get_embeddings(sentence):
    # Sentences we want sentence embeddings for
    sentences = [sentence]
    
    # Tokenize sentences
    # Default model will truncate the document and only gets embeddings of the first 256 tokens.
    # Semantic search will only be effective on these first 256 tokens.
    # Context loading in 4_app context will still include the ENTIRE document file
    encoded_input = tokenizer(sentences, padding='max_length', truncation=True, return_tensors='pt')

    # Compute token embeddings
    with torch.no_grad():
        model_output = model(**encoded_input)

    # Perform pooling
    sentence_embeddings = mean_pooling(model_output, encoded_input['attention_mask'])

    # Normalize embeddings
    sentence_embeddings = F.normalize(sentence_embeddings, p=2, dim=1)

    return (sentence_embeddings.tolist()[0])
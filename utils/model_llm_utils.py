from transformers import pipeline, AutoModelForCausalLM, AutoTokenizer, StoppingCriteria, StoppingCriteriaList
import torch

class KeywordsStoppingCriteria(StoppingCriteria):
    def __init__(self, keywords_ids:list):
        self.keywords = keywords_ids

    def __call__(self, input_ids: torch.LongTensor, scores: torch.FloatTensor, **kwargs) -> bool:
        if input_ids[0][-1] in self.keywords:
            return True
        return False

# Load the model stored in models/llm-model
print(f"Starting to load the LLM model")
model = AutoModelForCausalLM.from_pretrained('models/llm-model', local_files_only=True, torch_dtype=torch.bfloat16, device_map="auto")

print(f"Starting to load the LLM tokenizer")
tokenizer = AutoTokenizer.from_pretrained('models/llm-model', local_files_only=True, padding_side="left")

print(f"Finished loading the model and tokenizer")

# Now create a generator and a prompting function to ask a question to the LLM where the prompt sets context and attempts to massage some instructions to answer the question
generator = pipeline('text-generation', model=model, tokenizer=tokenizer)

# Generate text using loaded LLM model
# Total prompt size is limited to 2048 tokens with the included model
# the prompt includes (prompt template, user input, retrieved context)
def get_llm_generation(prompt, stop_words, temperature=0.7, max_new_tokens=256, top_p=0.85, top_k=70, repetition_penalty=1.07, do_sample=False):
    stop_ids = [tokenizer.encode(w)[0] for w in stop_words]
    stop_criteria = KeywordsStoppingCriteria(stop_ids)

    generated_text = generator(prompt, max_new_tokens=max_new_tokens, do_sample=do_sample, temperature=temperature, top_p=top_p, top_k=top_k, repetition_penalty=repetition_penalty, pad_token_id=tokenizer.eos_token_id, stopping_criteria=StoppingCriteriaList([stop_criteria]),)[0]

    #return a response that cuts out the prompt
    return generated_text['generated_text'][len(prompt):]

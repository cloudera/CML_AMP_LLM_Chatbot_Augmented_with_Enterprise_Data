import os
import gradio

from milvus import default_server
from pymilvus import connections, Collection
import utils.model_llm_utils as model_llm
import utils.vector_db_utils as vector_db
import utils.model_embedding_utils as model_embedding


def main():
    # Configure gradio QA app 
    print("Configuring gradio app")
    demo = gradio.Interface(fn=get_responses, 
                            inputs=gradio.Textbox(label="Question", placeholder=""),
                            outputs=[gradio.Textbox(label="Asking LLM with No Context"),
                                     gradio.Textbox(label="Asking LLM with Context (RAG)")],
                            examples=["What are ML Runtimes?",
                                      "What kinds of users use CML?",
                                      "How do data scientists use CML?"],
                            allow_flagging="never")


    # Launch gradio app
    print("Launching gradio app")
    demo.launch(share=True,
                enable_queue=True,
                show_error=True,
                server_name='127.0.0.1',
                server_port=int(os.getenv('CDSW_APP_PORT')))
    print("Gradio app ready")
# Helper function for generating responses for the QA app
def get_responses(question):
    
    # Load Milvus Vector DB collection
    vector_db_collection = Collection('cloudera_ml_docs')
    vector_db_collection.load()
    
    # Phase 1: Get nearest knowledge base chunk for a user question from a vector db
    context_chunk = get_nearest_chunk_from_vectordb(vector_db_collection, question)
    vector_db_collection.release()
    
    # Phase 2: Create enhanced instruction prompts for use with the LLM
    prompt_with_context = create_enhanced_prompt(context_chunk, question)
    prompt_without_context = create_enhanced_prompt("none", question)
    
    # Phase 3a: Perform text generation with LLM model using found kb context chunk
    contextResponse = get_llm_response(prompt_with_context)
    rag_response = contextResponse
    
    # Phase 3b: For comparison, also perform text generation with LLM model without providing context
    plainResponse = get_llm_response(prompt_without_context)
    plain_response = plainResponse

    return plain_response, rag_response

# Get embeddings for a user question and query Milvus vector DB for nearest knowledge base chunk
def get_nearest_chunk_from_vectordb(vector_db_collection, question):
    # Generate embedding for user question
    question_embedding =  model_embedding.get_embeddings(question)
    
    # Define search attributes for Milvus vector DB
    vector_db_search_params = {"metric_type": "IP", "params": {"nprobe": 10}}
    
    # Execute search and get nearest vector, outputting the relativefilepath
    nearest_vectors = vector_db_collection.search(
        data=[question_embedding], # The data you are querying on
        anns_field="embedding", # Column in collection to search on
        param=vector_db_search_params,
        limit=1, # limit results to 1
        expr=None, 
        output_fields=['relativefilepath'], # The fields you want to retrieve from the search result.
        consistency_level="Strong"
    )
    
    # Print the file path of the kb chunk
    print(nearest_vectors[0].ids[0])
    
    # Return text of the nearest knowledgebase chunk
    return load_context_chunk_from_data(nearest_vectors[0].ids[0])
  
# Return the Knowledge Base doc based on Knowledge Base ID (relative file path)
def load_context_chunk_from_data(id_path):
    with open(id_path, "r") as f: # Open file in read mode
        return f.read()
      
def create_enhanced_prompt(context, question):
    prompt_template = """<human>:%s. Answer this question based on given context %s
<bot>:"""
    prompt = prompt_template % (context, question)
    return prompt
  
# Pass through user input to LLM model with enhanced prompt and stop tokens
def get_llm_response(prompt):
    stop_words = ['<human>:', '\n<bot>:']

    generated_text = model_llm.get_llm_generation(prompt,
                                                  stop_words,
                                                  max_new_tokens=256,
                                                  do_sample=False,
                                                  temperature=0.7,
                                                  top_p=0.85,
                                                  top_k=70,
                                                  repetition_penalty=1.07)
    return generated_text  

if __name__ == "__main__":
    main()

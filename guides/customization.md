## Customization
### Knowledge base
The sample knowledge base included in this AMP can be modified or augmented to provide different contexts in the Chatbot app.

0. Prepare your additional documents
   - Custom knowledgebase documents should conform to the following requirements:
        * Less than 500 words (see [Limitations](troubleshooting.md#limitations))
        * Ensure ASCII character encoding (i.e. avoid Smart Quotes)
1. Add document files to the `/data` directory
2. Rerun the job `Populate Vector DB with documents embeddings`
3. Restart the application `CML LLM Chatbot`

> Note: Keep in mind the semantic representation of each document is only calculated on the first 256 tokens. However the **entire** contents of the document file is included in the LLM enhanced prompt.


### Models
The models used in the AMP can be swapped with other pre-trained models of similar type and compatibility with transformers interfaces.
#### Embeddings Model
This model is used to generate the embeddings (mathematical semantic representation) of each knowledgebase document.
> Your chosen model should be compatible with hugging face transformers.AutoModel
1. Modify `2_job-download-models/download_models.sh`
    - EMBEDDING_MODEL_REPO
    - EMBEDDING_MODEL_COMMIT
2. Then rerun the job `Download Models` 
3. Rerun the job `Populate Vector DB with documents embeddings`
4. Restart the application `CML LLM Chatbot`

#### Large Language Model
This model is used to perform text generation with intruction prompts.
> Your chose model should be compatible with hugging face transformers.AutoModelForCausalLM
1. Modify `2_job-download-models/download_models.sh`
    - LLM_MODEL_REPO
    - LLM_MODEL_COMMIT
2. Then rerun the job `Download Models` 
3. (Optional) Consider modifying the ehanced prompt used in the function `create_enhanced_prompt()` defined in`4_app/llm_rag_app.py`
    -  The prompt template should be similar to the patterns used when your chosen model was trained.
4. Restart the application `CML LLM Chatbot`

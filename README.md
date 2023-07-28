# LLM Chatbot Augmented with Enterprise Data 

This repository demonstrates how to use an open source pre-trained instruction-following LLM (Large Language Model) to build a ChatBot-like web application. The responses of the LLM are enhanced by giving it context from an internal knowledge base. This context is retrieved by using an open source Vector Database to do semantic search. 

Watch the Chatbot in action [here](https://www.youtube.com/watch?v=WBH9hYDyHKU).

![image](./images/app-screenshot.png)
All the components of the application (knowledge base, context retrieval, prompt enhancement LLM) are running within CML. This application does not call any external model APIs nor require any additional training of an LLM. The knowledge base provided in this repository is a slice of the Cloudera Machine Learning documentation.

> **IMPORTANT**: Please read the following before proceeding.  By configuring and launching this AMP, you will cause h2oai/h2ogpt-oig-oasst1-512-6.9b, which is a third party large language model (LLM), to be downloaded and installed into your environment from the third party’s website.  Please see https://huggingface.co/h2oai/h2ogpt-oig-oasst1-512-6.9b for more information about the LLM, including the applicable license terms.  If you do not wish to download and install h2oai/h2ogpt-oig-oasst1-512-6.9b, do not deploy this repository.  By deploying this repository, you acknowledge the foregoing statement and agree that Cloudera is not responsible or liable in any way for h2oai/h2ogpt-oig-oasst1-512-6.9b. Author: Cloudera Inc.

## Table of Contents 
#### README
* [Enhancing Chatbot with Enterprise Context to reduce hallucination](#enhancing-chatbot-with-enterprise-context-to-reduce-hallucination)
  * [Retrieval Augmented Generation (RAG) Architecture](#retrieval-augmented-generation--rag--architecture)
* [Requirements](#requirements)
* [Project Structure](#project-structure)
  * [Implementation](#implementation)
* [Technologies Used](#technologies-used)

#### Guides
* [Customization](guides/customization.md)
    * [Knowledgebase](guides/customization.md#knowledgebase)
    * [Models](guides/customization.md#Model)
* [Troubleshooting](guides/troubleshooting.md)
    * [AMP Failures](guides/troubleshooting.md#amp-failures)
    * [Limitations](guides/troubleshooting.md#limitations)

## Enhancing Chatbot with Enterprise Context to reduce hallucination
![image](./images/rag-architecture.png)
When a user question is directly sent to the open-source LLM, there is increased potential for halliucinated responses based on the generic dataset the LLM was trained on. By enhancing the user input with context retrieved from a knowledge base, the LLM can more readily generate a response with factual content. This is a form of Retrieval Augmented Generation.

For more detailed description of architectures like this and how it can enhance NLP tasks see this paper: [Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks
](https://arxiv.org/abs/2005.11401)

### Retrieval Augmented Generation (RAG) Architecture
- Knowledge base Ingest into Vector Database
  - Given a local directory of proprietary data files (in this example 11 documentation files about CML)
  - Generate embeddings with an open sourced pretrained model for each of those files
  - Store those embeddings along with document IDs in a Vector Database to enable semantic search
- Augmenting User Question with Additional Context from Knowledge Base
  - Given user question, search the Vector Database for documents that are semantically closest based on embeddings
  - Retrieve context based on document IDs and embeddings returned in the search response
- Submit Enhanced prompt to LLM to generate a factual response
  - Create a prompt including the retrieved context and the user question
  - Return the LLM response in a web application

## Requirements
#### CML Instance Types
- A GPU instance is required to perform inference on the LLM
  - [CML Documentation: GPUs](https://docs.cloudera.com/machine-learning/cloud/gpu/topics/ml-gpu.html)
- A CUDA 5.0+ capable GPU instance type is recommended
  - The torch libraries in this AMP require a GPU with CUDA compute capability 5.0 or higher. (i.e. nVidia V100, A100, T4 GPUs)

#### Resource Requirements
This AMP creates the following workloads with resource requirements:
- CML Session: `1 CPU, 4GB MEM`
- CML Jobs: `1 CPU, 4GB MEM`
- CML Application: `2 CPU, 1 GPU, 16GB MEM`

#### External Resources
This AMP requires pip packages and models from huggingface. Depending on your CML networking setup, you may need to whitelist some domains:
- pypi.python.org
- pypi.org
- pythonhosted.org
- huggingface.co

## Project Structure
### Folder Structure

The project is organized with the following folder structure:
```
.
├── 0_session-resource-validation/  # Script for checking CML workspace requirements
├── 1_session-install-deps/   # Setup script for installing python dependencies
├── 2_job-download-models/    # Setup scripts for downloading pre-trained models
├── 3_job-populate-vectordb/  # Setup scripts for initializing and populating a vector database with context documents
├── 4_app/                    # Backend scripts for launching chat webapp and making requests to locally running pre-trained models
├── data/                     # Sample documents to use to context retrieval
├── utils/                    # Python module for functions used for interacting with pre-trained models
├── images/
├── README.md
└── LICENSE.txt
```
## Implementation
### `data/`
This directory stores all the individual sample documents that are used for context retrieval in the chatbot application
- Sourced from:
  - [CML](https://docs.cloudera.com/machine-learning/cloud/index.html)
  - [Iceberg](https://iceberg.apache.org/docs/1.2.0/)
  - [Ozone](https://docs.cloudera.com/cdp-private-cloud-base/7.1.8/ozone-overview/topics/ozone-introduction.html)

### `1_session-install-deps`
- Install python dependencies specified in 1_session-install-deps/requirements.txt

### `2_job-download-models`
Definition of the job **Download Models** 
- Directly download specified models from huggingface repositories
- These are pulled to new directories models/llm-model and models/embedding-model

### `3_job-populate-vectordb`
Definition of the job **Populate Vector DB with documents embeddings**
- Start the milvus vector database and set database to be persisted in new directory milvus-data/
- Generate embeddings for each document in data/
- The embeddings vector for each document is inserted into the vector database
- Stop the vector database

### `4_app`
Definition of the application `CML LLM Chatbot`
- Start the milvus vector database using persisted database data in milvus-data/
- Load locally persisted pre-trained models from models/llm-model and models/embedding-model 
- Start gradio interface 
- The chat interface performs both retrieval-augmented LLM generation and regular LLM generation for bot responses.

## Technologies Used
#### Open-Source Models and Utilities
- [all-MiniLM-L12-v2](https://huggingface.co/sentence-transformers/all-MiniLM-L12-v2/tree/9e16800aed25dbd1a96dfa6949c68c4d81d5dded)
     - Vector Embeddings Generation Model
- [h2ogpt-oig-oasst1-512-6.9b](https://huggingface.co/h2oai/h2ogpt-oig-oasst1-512-6.9b/tree/4e336d947ee37d99f2af735d11c4a863c74f8541)
   - Instruction-following Large Language Model
- [Hugging Face transformers library](https://pypi.org/project/transformers/)
#### Vector Database
- [Milvus](https://github.com/milvus-io/milvus)
#### Chat Frontend
- [Gradio](https://github.com/gradio-app/gradio)

## Deploying on CML
There are two ways to launch this prototype on CML:

1. **From Prototype Catalog** - Navigate to the Prototype Catalog on a CML workspace, select the "LLM Chatbot Augmented with Enterprise Data" tile, click "Launch as Project", click "Configure Project"
2. **As ML Prototype** - In a CML workspace, click "New Project", add a Project Name, select "ML Prototype" as the Initial Setup option, copy in the [repo URL](https://github.com/cloudera/CML_AMP_LLM_Chatbot_Augmented_with_Enterprise_Data), click "Create Project", click "Configure Project"

from milvus import default_server
from pymilvus import connections, FieldSchema, CollectionSchema, DataType, Collection, utility
import subprocess

import utils.model_embedding_utils as model_embedding

import os
from pathlib import Path

def create_milvus_collection(collection_name, dim):
      if utility.has_collection(collection_name):
          utility.drop_collection(collection_name)

      fields = [
      FieldSchema(name='relativefilepath', dtype=DataType.VARCHAR, description='file path relative to root directory ', max_length=1000, is_primary=True, auto_id=False),
      FieldSchema(name='embedding', dtype=DataType.FLOAT_VECTOR, description='embedding vectors', dim=dim)
      ]
      schema = CollectionSchema(fields=fields, description='reverse image search')
      collection = Collection(name=collection_name, schema=schema)

      # create IVF_FLAT index for collection.
      index_params = {
          'metric_type':'IP',
          'index_type':"IVF_FLAT",
          'params':{"nlist":2048}
      }
      collection.create_index(field_name="embedding", index_params=index_params)
      return collection
    
# Create an embedding for given text/doc and insert it into Milvus Vector DB
def insert_embedding(collection, id_path, text):
    embedding =  model_embedding.get_embeddings(text)
    data = [[id_path], [embedding]]
    collection.insert(data)
    
def main():
  # Reset the vector database files
  print(subprocess.run(["rm -rf milvus-data"], shell=True))

  default_server.set_base_dir('milvus-data')
  default_server.start()

  try:
    connections.connect(alias='default', host='localhost', port=default_server.listen_port)   
    print(utility.get_server_version())

    # Create/Recreate the Milvus collection
    collection_name = 'cloudera_ml_docs'
    collection = create_milvus_collection(collection_name, 384)

    print("Milvus database is up and collection is created")

    # Read KB documents in ./data directory and insert embeddings into Vector DB for each doc
    # The default embeddings generation model specified in this AMP only generates embeddings for the first 256 tokens of text.
    doc_dir = './data'
    for file in Path(doc_dir).glob(f'**/*.txt'):
        with open(file, "r") as f: # Open file in read mode
            print("Generating embeddings for: %s" % file.name)
            text = f.read()
            insert_embedding(collection, os.path.abspath(file), text)

    collection.flush()
    print('Total number of inserted embeddings is {}.'.format(collection.num_entities))
    print('Finished loading Knowledge Base embeddings into Milvus')

  except Exception as e:
    default_server.stop()
    raise (e)
    
  
  default_server.stop()


if __name__ == "__main__":
    main()

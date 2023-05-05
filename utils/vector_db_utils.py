from milvus import default_server
from pymilvus import connections, Collection, utility

# Start Milvus Vector DB
default_server.stop()
default_server.set_base_dir('milvus-data')
default_server.start()


try:
    connections.connect(alias='default', host='localhost', port=default_server.listen_port)   
except Exception as e:
    default_server.stop()
    raise e
    
print(utility.get_server_version())
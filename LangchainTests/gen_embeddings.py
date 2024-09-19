from langchain_openai import AzureOpenAIEmbeddings
from langchain_community.vectorstores.azuresearch import AzureSearch
import argparse
import configparser
import os
import json

parser = argparse.ArgumentParser(description='Pass in a config file with an API key and model endpoint to generate embeddings.')
parser.add_argument('--config', type=str, help='Path to the config file (relative or full)', default='..\localconfig.ini')
args = parser.parse_args()

if not os.path.isabs(args.config):
    args.config = os.path.abspath(f'{os.path.dirname(os.path.realpath(__file__))}\{args.config}')

config = configparser.ConfigParser()
config.read(args.config)

EMBEDDING_API_KEY = config['EMBEDDING']['apiKey']
EMBEDDING_ENDPOINT = config['EMBEDDING']['modelEndpoint']
EMBEDDING_MODEL = config['EMBEDDING']['model']
EMBEDDING_VERSION = config['EMBEDDING']['version']

AZS_API_KEY = config['AZURE_SEARCH']['apiKey']
AZS_ENDPOINT = config['AZURE_SEARCH']['modelEndpoint']
AZS_INDEX_NAME = config['AZURE_SEARCH']['indexName']

document = None
document_vectors = list()

# Assuming the chunked json file that's in the loop
with open(f'{os.path.dirname(os.path.realpath(__file__))}\document.json', 'r') as in_doc:
    document = json.load(in_doc)

embeddings = AzureOpenAIEmbeddings(
    api_key=EMBEDDING_API_KEY, 
    azure_endpoint=EMBEDDING_ENDPOINT, 
    openai_api_version=EMBEDDING_VERSION, 
    model=EMBEDDING_MODEL
)

vector_store = AzureSearch(
    azure_search_key=AZS_API_KEY, 
    azure_search_endpoint=AZS_ENDPOINT,
    embedding_function=embeddings.embed_query,
    index_name=AZS_INDEX_NAME
)

# Not sure if this is the right way to add the document vectors. The add_embeddings() method expects Iterable[Tuple[str, List[float]]]
document_vectors.append((document['Summary'], embeddings.embed_query(document['cleanedChunk'])))

for property in document["properties"]:
    document_vectors.append((property["description"], embeddings.embed_query(property["description"])))

vector_store.add_embeddings(document_vectors)

from langchain_openai import AzureOpenAIEmbeddings
import configparser
import os
import json

config = configparser.ConfigParser()
config.read(f'{os.path.dirname(os.path.realpath(__file__))}\..\DataProductAssistant\localconfig.ini')

API_KEY = config['DEFAULT']['apiKey']

ENDPOINT = config['DEFAULT']['modelEndpoint']

document = None

with open(f'{os.path.dirname(os.path.realpath(__file__))}\document.json', 'r') as in_doc:
    document = json.load(in_doc)

embeddings = AzureOpenAIEmbeddings(
    api_key=API_KEY, 
    azure_endpoint=ENDPOINT, 
    openai_api_version="2023-05-15", 
    model="text-embedding-3-large"
)

vector = embeddings.embed_query(document['cleanedChunk'])
print(vector)
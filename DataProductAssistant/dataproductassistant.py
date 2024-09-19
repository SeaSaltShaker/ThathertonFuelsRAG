import os
import requests
import configparser
import argparse
from string import Template
from langchain_community.vectorstores.azuresearch import AzureSearch
from langchain_openai import AzureOpenAIEmbeddings

parser = argparse.ArgumentParser(description='Pass in a config file with an API key and model endpoint, and a query to ask the model against data in an Azure Search service')
parser.add_argument('--config', type=str, help='Path to the config file (relative or full)', default='..\localconfig.ini')
parser.add_argument('--question', type=str, help='Question to ask the model', default='What message formats does Microsoft Graph support?')
args = parser.parse_args()

if not os.path.isabs(args.config):
    args.config = os.path.abspath(f'{os.path.dirname(os.path.realpath(__file__))}\{args.config}')

config = configparser.ConfigParser()
config.read(args.config)

# Three endpoints are needed: GPT-4 for the final query, an embedding model to do the vector search, and Azure Search, which holds the vector mappings
API_KEY = config['OPENAI']['apiKey']
ENDPOINT = config['OPENAI']['modelEndpoint']

EMBEDDING_ENDPOINT = config['EMBEDDING']['modelEndpoint']
EMBEDDING_API_KEY = config['EMBEDDING']['apiKey']
EMBEDDING_MODEL = config['EMBEDDING']['model']
EMBEDDING_VERSION = config['EMBEDDING']['version']

AZS_API_KEY = config['AZURE_SEARCH']['apiKey']
AZS_ENDPOINT = config['AZURE_SEARCH']['modelEndpoint']
AZS_INDEX_NAME = config['AZURE_SEARCH']['indexName']

RAG_Context_Query = """\
Use the following context to answer the user's query. If you cannot answer the question using only the context, please respond with 'I don't know.'

Question:
$question

Context:
$context
"""
rag_prompt = Template(RAG_Context_Query)

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

# Get the closest matches to the question
contextes = vector_store.similarity_search(
    query=args.question,
    k=3,
    search_type="similarity",
)

headers = {
    "Content-Type": "application/json",
    "api-key": API_KEY,
}

# Payload for the request
payload = {
  "messages": [
    {
      "role": "system",
      "content": [
        {
          "type": "text",
          "text": "You are an AI assistant that helps people find information."
        }
      ]
    },
        {
      "role": "user",
      "content": [
        {
          "type": "text",
          # I concatenate all the closest matches to provide the greatest context
          "text": rag_prompt.substitute(question=args.question, context=" ".join([context.page_content for context in contextes]))
        }
      ]
    }
  ],
  "temperature": 0.7,
  "top_p": 0.95,
  "max_tokens": 800
}

# Send request
try:
    print(f"Query: {rag_prompt.substitute(question=args.question, context=' '.join([context.page_content for context in contextes]))}")
    response = requests.post(ENDPOINT, headers=headers, json=payload)
    response.raise_for_status()  # Will raise an HTTPError if the HTTP request returned an unsuccessful status code
except requests.RequestException as e:
    raise SystemExit(f"Failed to make the request. Error: {e}")

# Handle the response as needed (e.g., print or process)
output = response.json().get("choices")[0].get("message").get("content")

print(output)


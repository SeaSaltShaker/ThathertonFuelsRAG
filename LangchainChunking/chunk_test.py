from langchain_openai import AzureOpenAIEmbeddings
from langchain_community.vectorstores.azuresearch import AzureSearch
import configparser
import os
import json

config = configparser.ConfigParser()
config.read(f'{os.path.dirname(os.path.realpath(__file__))}\..\DataProductAssistant\localconfig.ini')

OPENAI_API_KEY = config['OPENAI']['apiKey']
OPENAI_ENDPOINT = config['OPENAI']['modelEndpoint']

AZS_API_KEY = config['AZURE_SEARCH']['apiKey']
AZS_ENDPOINT = config['AZURE_SEARCH']['modelEndpoint']

document = None
document_vectors = list()

# Assuming the chunked json file that's in the loop
with open(f'{os.path.dirname(os.path.realpath(__file__))}\document.json', 'r') as in_doc:
    document = json.load(in_doc)

embeddings = AzureOpenAIEmbeddings(
    api_key=OPENAI_API_KEY, 
    azure_endpoint=OPENAI_ENDPOINT, 
    openai_api_version="2023-05-15", 
    model="text-embedding-3-large"
)

vector_store = AzureSearch(
    azure_search_key=AZS_API_KEY, 
    azure_search_endpoint=AZS_ENDPOINT,
    embedding_function=embeddings.embed_query,
    index_name="hacka-vectors"
)

# Not sure if this is the right way to add the document vectors. The add_embeddings() method expects Iterable[Tuple[str, List[float]]]
document_vectors.append(("test_doc", embeddings.embed_query(document['cleanedChunk'])))

document_vectors.append(("test_query",embeddings.embed_query('this is a test')))
vector_store.add_embeddings(document_vectors)

# Use the first question as the query
docs = vector_store.similarity_search(
    query=document["Questions"][0]["question"],
    k=3,
    search_type="similarity",
)

# Errors out here..
if docs:
    print(docs[0].page_content)
else:
    print("No documents found")

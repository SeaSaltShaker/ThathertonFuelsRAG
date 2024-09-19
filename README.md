# ThathertonFuelsRAG

Is an investigation/forray into RAG utilizing resources available in a Microsoft Azure Subscription.

`LangChainTests\gen_embeddings.py` will generate embeddings based on `document.json`, which is assumed to be already chunked in some way. These embeddings are stored in an Azure Serach Service object provided based on the provided `config.ini` file.

It expects the following template:

```ini
[EMBEDDING]
modelEndpoint = 
apiKey = 
model = 
version = 
[AZURE_SEARCH]
modelEndpoint = 
apiKey = 
indexName = 
```

---

`DataProductAssistant/dataproductassistant.py` will transform a query using a provided embedding model and will match those embeddings against the provided Azure Serach Service index. It will supplement the context and ask the GPT model the following prompt:

```text
Use the following context to answer the user's query. If you cannot answer the question using only the context, please respond with 'I don't know.'

Question:
$question

Context:
$context
```

This script expects a config file as input in the following format.

```ini
[EMBEDDING]
modelEndpoint = 
apiKey = 
model = 
version = 
[AZURE_SEARCH]
modelEndpoint = 
apiKey = 
indexName = 
[OPENAI]
modelEndpoint = 
apiKey = 
```

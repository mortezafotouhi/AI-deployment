import os
from langchain_openai import AzureOpenAIEmbeddings
from secret_key import key_us, endpoint_us
import numpy as np

os.environ["AZURE_OPENAI_API_KEY"] = key_us
os.environ["AZURE_OPENAI_ENDPOINT"] = endpoint_us

embedding_function = AzureOpenAIEmbeddings(
    azure_deployment="embedding",
    openai_api_version="2023-05-15"
)


class Embeddings:
    def create_vectordb(self, texts: list[str], path=None):
        embeddings = np.array(embedding_function.embed_documents(texts))
        if path:
            np.save(path, embeddings)
        return embeddings

    def embed_query(self, query: str):
        return np.array(embedding_function.embed_query(query))

    def retrieve_vectordb(self, name):
        if name == "module_description":
            return np.load("data/embedding-module-description.npy")
        elif name == "articles":
            return np.load("data/embedding-articles.npy")

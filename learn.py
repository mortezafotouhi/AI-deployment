import json
import numpy as np

from embedding import Embeddings


class Learn:
    with open('data/articles.json', 'r') as file:
        ARTICLES = json.load(file)

    def article_similarity(self, query, k):
        Embed = Embeddings()

        embeddings = Embed.retrieve_vectordb("articles")
        embedded_query = Embed.embed_query(query)
        similarities = [np.dot(embedded_query, vec) / (np.linalg.norm(embedded_query) * np.linalg.norm(vec)) for vec in
                        embeddings]

        return [self.ARTICLES[index] for index in np.argsort(similarities)[-k:][::-1]]


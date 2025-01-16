import faiss
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer

class VectorStore:
    def __init__(self, dimension: int = 128, data=None):

        self.dimension = dimension
        self.index = faiss.IndexFlatL2(dimension)
        self.id_to_name = []
        self.vectorizer = TfidfVectorizer(tokenizer=lambda x: x, preprocessor=lambda x: x, token_pattern=None)
        self.data = data

    def build_index(self):

        sentences = [" ".join(ingredients) for ingredients in self.data["ingredients"]]
        embeddings = self.vectorizer.fit_transform(sentences).toarray().astype("float32")

        if embeddings.shape[1] < self.dimension:
            embeddings = np.pad(embeddings, ((0, 0), (0, self.dimension - embeddings.shape[1])))
        elif embeddings.shape[1] > self.dimension:
            embeddings = embeddings[:, :self.dimension]

        self.index.add(embeddings)
        self.id_to_name = self.data["name"].tolist()

    def search_similar(self, query_ingredients, top_k=5, min_matches=1):

        query_list = [ingredient.strip().lower() for ingredient in query_ingredients.split(",")]
        query_vector = self.vectorizer.fit_transform([" ".join(query_list)]).toarray().astype("float32")

        if query_vector.shape[1] < self.dimension:
            query_vector = np.pad(query_vector, ((0, 0), (0, self.dimension - query_vector.shape[1])))
        elif query_vector.shape[1] > self.dimension:
            query_vector = query_vector[:, :self.dimension]

        distances, indices = self.index.search(query_vector, top_k)
        results = []
        for i in indices[0]:
            cocktail_ingredients = [ingredient.lower() for ingredient in self.data.iloc[i]["ingredients"]]

            matches = sum(
                1 for q in query_list
                if any(q in ingredient for ingredient in cocktail_ingredients)
            )
            print(f"compare: {query_list} з {cocktail_ingredients} - matches: {matches}")
            if matches >= min_matches:
                results.append(self.id_to_name[i])
        return results

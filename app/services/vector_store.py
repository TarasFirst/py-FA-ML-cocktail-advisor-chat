import faiss
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer


class VectorStore:
    def __init__(self, dimension: int = 128, data=None):
        """
        Ініціалізує FAISS векторну базу.
        :param dimension: Розмірність векторів.
        :param data: DataFrame з інформацією про коктейлі.
        """
        self.dimension = dimension
        self.index = faiss.IndexFlatL2(dimension)
        self.id_to_name = []
        self.vectorizer = TfidfVectorizer(tokenizer=lambda x: x, preprocessor=lambda x: x, token_pattern=None)
        self.data = data  # Зберігаємо DataFrame як атрибут класу

    def build_index(self):
        """
        Створює вектори для коктейлів і додає їх до FAISS.
        """
        sentences = [" ".join(ingredients) for ingredients in self.data["ingredients"]]
        embeddings = self.vectorizer.fit_transform(sentences).toarray().astype("float32")

        if embeddings.shape[1] < self.dimension:
            embeddings = np.pad(embeddings, ((0, 0), (0, self.dimension - embeddings.shape[1])))
        elif embeddings.shape[1] > self.dimension:
            embeddings = embeddings[:, :self.dimension]

        self.index.add(embeddings)
        self.id_to_name = self.data["name"].tolist()

    def search_similar(self, query_ingredients, top_k=5, min_matches=2):
        """
        Шукає схожі коктейлі на основі інгредієнтів.
        :param query_ingredients: Рядок із запитом інгредієнтів (розділені комами).
        :param top_k: Кількість результатів.
        :param min_matches: Мінімальна кількість збігів між запитом і коктейлем.
        :return: Список назв коктейлів.
        """
        query_vector = self.vectorizer.fit_transform([query_ingredients]).toarray().astype("float32")

        if query_vector.shape[1] < self.dimension:
            query_vector = np.pad(query_vector, ((0, 0), (0, self.dimension - query_vector.shape[1])))
        elif query_vector.shape[1] > self.dimension:
            query_vector = query_vector[:, :self.dimension]

        distances, indices = self.index.search(query_vector, top_k)
        results = []
        for i in indices[0]:
            cocktail_ingredients = self.data.iloc[i]["ingredients"]
            matches = len(set(query_ingredients.split(", ")) & set(cocktail_ingredients))
            if matches >= min_matches:
                results.append(self.id_to_name[i])
        return results

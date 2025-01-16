from fastapi import FastAPI
from app.api import chat, recommend


# Ініціалізація FastAPI додатку
app = FastAPI(
    title="Cocktail Advisor Chat",
    description="A chat-based application with cocktail recommendations powered by RAG and LLM.",
    version="1.0.0",
)

# Підключення роутерів
app.include_router(chat.router, prefix="/chat", tags=["Chat"])
app.include_router(recommend.router, prefix="/recommend", tags=["Recommendations"])

# Кореневий ендпойнт
@app.get("/")
def read_root():
    return {"message": "Welcome to the Cocktail Advisor Chat!"}


from app.services.vector_store import VectorStore
from app.utils.data_loader import load_cocktail_data

# Завантаження даних
data = load_cocktail_data("data/cocktails.csv")

# Ініціалізація FAISS
vector_store = VectorStore(dimension=128, data=data)
vector_store.build_index()

# Тест пошуку
query = "lime, tequila, salt"
similar_cocktails = vector_store.search_similar(query)
print(f"Схожі коктейлі для запиту '{query}': {similar_cocktails}")
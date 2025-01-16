from openai import OpenAIError, OpenAI
from fastapi import FastAPI
from app.utils.data_loader import load_cocktail_data
from app.services.vector_store import VectorStore
from pydantic import BaseModel
from fastapi.responses import JSONResponse
import traceback

app = FastAPI(
    title="Cocktail Advisor",
    description="Tips for cocktails",
    version="1.0.0"
)

@app.exception_handler(Exception)
async def exception_handler(request, exc):
    traceback.print_exc()
    return JSONResponse(
        status_code=500,
        content={"detail": str(exc)},
    )


class LLMRequest(BaseModel):
    question: str


client = OpenAI(api_key="KEY")


async def query_llm(prompt: str):

    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a cocktail expert."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=150,
            temperature=0.7
        )
        return response.choices[0].message.content.strip()
    except OpenAIError as e:
        return (f"E"
                f"Error query to the LLM: {e}")

user_favorites = set()

data = None

try:
    data = load_cocktail_data("data/cocktails.csv")
    print(f"Success download, amount is : {len(data)}")
    print(data.head())
except Exception as e:
    print(f"Error download: {e}")

vector_store = None

if data is not None:
    vector_store = VectorStore(dimension=128, data=data)
    vector_store.build_index()
    print(f"Amount vectors in FAISS: {vector_store.index.ntotal}")

@app.get("/")
def read_root():  #WORK
    return {"message": "Welcome to the Cocktail Advisor API!"}

@app.get("/cocktails_by_ingredient")
def get_cocktails_by_ingredient(ingredient: str, limit: int = 5):  #WORK

    if data is None:
        return {"message": "Dataset not loaded."}

    ingredient = ingredient.lower()
    matching_cocktails = data[data["ingredients"].apply(
        lambda ingredients: any(ingredient in i for i in ingredients)
    )]
    result = matching_cocktails.head(limit)
    return {"ingredient": ingredient, "cocktails": result["name"].tolist()}

@app.get("/non_alcoholic_cocktails")
def get_non_alcoholic_cocktails(ingredient: str = "sugar", limit: int = 5):  #WORK

    if data is None:
        return {"message": "Dataset not loaded."}

    ingredient = ingredient.lower()
    matching_cocktails = data[
        (data["alcoholic"] == "Non alcoholic") &
        (data["ingredients"].apply(lambda ingredients: any(ingredient in i for i in ingredients)))
    ]
    result = matching_cocktails.head(limit)
    return {"ingredient": ingredient, "cocktails": result["name"].tolist()}

@app.post("/add_favorite_ingredient")
def add_favorite_ingredient(ingredient: str):  #WORK

    ingredient = ingredient.lower()
    user_favorites.add(ingredient)
    return {"message": f"Ingredient '{ingredient}' added to favorites.", "favorites": list(user_favorites)}

@app.get("/get_favorite_ingredients")
def get_favorite_ingredients():  #WORK

    return {"favorites": list(user_favorites)}

@app.get("/recommend_by_favorites")
def recommend_by_favorites(limit: int = 5):  #WORK

    if not user_favorites:
        return {"message": "No favorite ingredients found.", "recommendations": []}

    if data is None:
        return {"message": "Dataset not loaded."}

    matching_cocktails = data[data["ingredients"].apply(
        lambda ingredients: any(fav in ingredients for fav in user_favorites)
    )]
    result = matching_cocktails.head(limit)
    return {"favorites": list(user_favorites), "recommendations": result["name"].tolist()}

@app.get("/recommend_similar")
def recommend_similar(cocktail_name: str, limit: int = 5):  #WORK

    if data is None:
        return {"message": "Dataset not loaded."}

    cocktail = data[data["name"].str.lower() == cocktail_name.lower()]
    if cocktail.empty:
        return {"message": f"Cocktail '{cocktail_name}' not found.", "recommendations": []}

    ingredients = cocktail.iloc[0]["ingredients"]
    query = ", ".join(ingredients)

    if not vector_store:
        return {"message": "Vector store not initialized."}

    similar_cocktails = vector_store.search_similar(query, top_k=limit)
    return {"cocktail": cocktail_name, "recommendations": similar_cocktails}


@app.post("/ask_llm")
async def ask_llm(request: LLMRequest):  #TODO

    prompt = f"""
    You are a cocktail expert. Answer the user's question using the following knowledge base:
    - You know the ingredients and details of cocktails in the provided dataset.
    - You can suggest cocktails based on ingredients, categories, or similarity.

    User's question: {request.question}
    """
    answer = await query_llm(prompt)
    return {"question": request.question, "answer": answer}

@app.get("/recommendations")
def get_recommendations(query: str):  # TODO

    if not vector_store:
        return {"message": "Vector store not initialized."}

    similar_cocktails = vector_store.search_similar(query)
    return {"query": query, "recommendations": similar_cocktails}


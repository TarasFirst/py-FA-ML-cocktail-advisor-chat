from fastapi import APIRouter

router = APIRouter()

@router.get("/")
def recommend_cocktails():

    return {"recommendations": ["Margarita", "Mojito", "Cosmopolitan"]}

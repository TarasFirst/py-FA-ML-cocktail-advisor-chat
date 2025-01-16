from fastapi import APIRouter

router = APIRouter()

@router.get("/")
def recommend_cocktails():
    """
    Повертає рекомендації коктейлів (поки що заглушка).
    """
    # Тимчасова відповідь для тестування
    return {"recommendations": ["Margarita", "Mojito", "Cosmopolitan"]}

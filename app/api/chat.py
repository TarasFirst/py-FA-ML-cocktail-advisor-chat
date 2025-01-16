from fastapi import APIRouter

router = APIRouter()

@router.post("/")
def chat_with_user(user_input: str):
    """
    Обробляє повідомлення користувача і повертає відповідь.
    """
    # Тимчасова відповідь для тестування
    return {"response": f"Received: {user_input}"}

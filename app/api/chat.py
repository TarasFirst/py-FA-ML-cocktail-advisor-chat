from fastapi import APIRouter

router = APIRouter()

@router.post("/")
def chat_with_user(user_input: str):

    return {"response": f"Received: {user_input}"}

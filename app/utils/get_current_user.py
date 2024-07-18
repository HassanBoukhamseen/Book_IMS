from fastapi import HTTPException
from app.services.token_services import verify_token

def get_current_user(token: str):
    if not token:
        raise HTTPException(status_code=403, detail="Not authenticated")
    user = verify_token(token)
    if not user:
        raise HTTPException(status_code=403, detail="Invalid token")
    return user

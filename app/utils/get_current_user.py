from fastapi import HTTPException, Header
from typing import Annotated
from app.services.token_services import verify_token

def get_current_user(authorization: Annotated[str, Header()]):
    if not authorization:
        raise HTTPException(status_code=403, detail="Not authenticated")
    token = authorization.split(" ")[1] if " " in authorization else authorization
    user = verify_token(token)
    if not user:
        raise HTTPException(status_code=403, detail="Invalid token")
    return user

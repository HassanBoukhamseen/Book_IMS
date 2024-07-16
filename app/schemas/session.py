from pydantic import BaseModel

class SessionData(BaseModel):
    fname: str
    lname: str
    email: str
    role: int
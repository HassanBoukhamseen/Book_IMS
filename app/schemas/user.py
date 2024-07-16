from pydantic import BaseModel , EmailStr

class User(BaseModel):
    fname: str
    lname: str
    email: EmailStr
    password: str
    role: int
from pydantic import BaseModel, EmailStr, ConfigDict


class UserCreate(BaseModel):
    username: str
    password: str
    email: EmailStr

class UserIn(BaseModel):
    username: str
    password: str

class UserRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    username: str
    email: EmailStr
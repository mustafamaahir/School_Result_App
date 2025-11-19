# backend/schemas.py
from pydantic import BaseModel
from typing import Optional

class UserCreate(BaseModel):
    username: str
    password: str
    role: str = "student"  # default role
    full_name: Optional[str] = None

class UserLogin(BaseModel):
    username: str
    password: str

class UserOut(BaseModel):
    id: int
    username: str
    role: str
    full_name: Optional[str] = None

    class Config:
        orm_mode = True

class ResultBase(BaseModel):
    name: str
    student_class: str
    subject: str
    percentage: float

    class Config:
        orm_mode = True

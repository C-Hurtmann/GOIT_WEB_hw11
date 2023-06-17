from datetime import date
from typing import Optional
from pydantic import BaseModel, Field, EmailStr


class ContactModel(BaseModel):
    first_name: str = Field(max_length=100)
    last_name: str = Field(max_length=100)
    email: EmailStr
    phone: Optional[str]
    birthday: date


class ContactResponce(ContactModel):
    id: int
    
    class Config:
        orm_mode = True
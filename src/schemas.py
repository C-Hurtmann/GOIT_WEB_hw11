from datetime import date
from pydantic import BaseModel, Field, EmailStr, constr, validator


class ContactModel(BaseModel):
    first_name: str = Field(max_length=100)
    last_name: str = Field(max_length=100)
    email: EmailStr
    phone: constr(
        regex="^\+380\d{9}$",
        strict=True,
        strip_whitespace=True)
    birthday: date
    
    @validator('birthday')
    def validate_birthday(cls, value):
        today = date.today()
        if value > today:
            raise ValueError('Birthday must be in past')
        return value


class ContactResponce(ContactModel):
    id: int
    
    class Config:
        orm_mode = True


class UserModel(BaseModel):
    email: EmailStr
    password: str


class UserDB(BaseModel):
    id: id
    email: EmailStr
    password: str
    
    class Config:
        orm_mode = True


class UserResponse(BaseModel):
    user: UserDB
    detail: str = 'User created'


class TokenModel(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = 'bearer'

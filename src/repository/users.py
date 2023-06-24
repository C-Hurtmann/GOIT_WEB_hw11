from sqlalchemy.orm import Session
from pydantic import EmailStr

from src.database.models import User
from src.schemas import UserModel


async def get_user_by_email(email: EmailStr, db: Session) -> User:
    return db.query(User).filter(User.email == email).first()

async def create_user(body: UserModel, db: Session) -> User:
    new_user = User(**body.dict())
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

async def update_token(user: User, token: str | None, db: Session) -> None:
    user.refresh_token = token
    db.commit()
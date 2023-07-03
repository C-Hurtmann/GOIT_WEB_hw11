from libgravatar import Gravatar
from sqlalchemy.orm import Session

from src.database.models import User
from src.schemas import UserModel


async def get_user_by_email(email: str, db: Session) -> User:
    return db.query(User).filter(User.email == email).first()

async def create_user(body: UserModel, db: Session) -> User:
    try:
        gravatar = Gravatar(body.email)
        avatar = gravatar.get_image()
    except Exception:
        avatar = None

    new_user = User(**body.dict(), avatar=avatar)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

async def update_token(user: User, token: str | None, db: Session) -> None:
    user.refresh_token = token
    db.commit()

async def confirm_email(email: str, db: Session) -> None:
    user = await get_user_by_email(email, db)
    user.confirmed = True
    db.commit()
    db.refresh(user)

async def reset_password(user: User, password: str, db: Session) -> None:
    user.password = password
    db.commit()
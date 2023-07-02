from sqlalchemy.orm import Session

from src.database.models import User
from src.repository.auth import get_user_by_email


async def update_avatar(email, url: str, db: Session) -> User:
    user = await get_user_by_email(email, db)
    user.avatar = url
    db.commit()
    db.refresh(user)
    return user
from sqlalchemy.orm import Session

from src.database.models import User
from src.repository.auth import get_user_by_email


async def update_avatar(email: str, url: str, db: Session) -> User:
    """
    Update avatar url.
    
    :param email: User email to get user object.
    :type email: str
    :param url: Url for new avatar.
    :type url: str
    :param db: Database session.
    :type db: Session
    :return: User object.
    :rtype: User
    """
    user = await get_user_by_email(email, db)
    user.avatar = url
    db.commit()
    db.refresh(user)
    return user
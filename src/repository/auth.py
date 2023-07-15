from libgravatar import Gravatar
from sqlalchemy.orm import Session

from src.database.models import User
from src.schemas import UserModel


async def get_user_by_email(email: str, db: Session) -> User:
    """
    Get first User object by email.
    
    :param email: User email.
    :type email: str
    :param db: Database session.
    :type db: Session
    :return: User object.
    :rtype: User
    """
    return db.query(User).filter(User.email == email).first()

async def create_user(body: UserModel, db: Session) -> User:
    """
    Create new user in database.
    
    Generate default avatar.
    
    :param body: User info.
    :type body: UserModel
    :param db: Database session.
    :type db: Session
    :return: New user object.
    :rtype: User
    """
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
    """
    Update refresh token in User object.
    
    If not token, delete refresh token from User object.
    
    :param user: User object.
    :type user: User
    :param token: Refresh token.
    :type token: str | None
    :param db: Database session.
    :type db: Session
    :rtype: None
    """
    user.refresh_token = token
    db.commit()

async def confirm_email(email: str, db: Session) -> None:
    """
    Changed User object to confirmed.
    
    :param email: User email.
    :type email: str
    :param db: Database session.
    :type db: Session
    :rtype: None
    """
    user = await get_user_by_email(email, db)
    user.confirmed = True
    db.commit()
    db.refresh(user)

async def reset_password(user: User, password: str, db: Session) -> None:
    """
    Update password hash in User object.
    
    :param user: User object.
    :type user: User
    :param password: New password hash.
    :type password: str
    :param db: Database session.
    :type db: Session
    :rtype: None
    """
    user.password = password
    db.commit()
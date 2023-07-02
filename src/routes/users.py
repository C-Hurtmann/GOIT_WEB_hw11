import cloudinary
import cloudinary.uploader
from fastapi import APIRouter, Depends, UploadFile, File
from sqlalchemy.orm import Session

from src.conf.config import settings
from src.database.db import get_db
from src.database.models import User
from src.repository import users as repo_users
from src.services.auth import auth_service
from src.schemas import UserDB

router = APIRouter(prefix='/users', tags=['users'])

@router.get('/me', response_model=UserDB)
async def read_users_me(current_user: User = Depends(auth_service.get_current_user)):
    return current_user


async def update_user_avatar(file: UploadFile = File(),
                             current_user: User = Depends(auth_service.get_current_user),
                             db: Session = Depends(get_db)):
    cloudinary.config(
        cloud_name=settings.cloud_name,
        api_key=settings.cloud_api_key,
        api_secret=settings.cloud_api_secret,
        secure=True
    )
    public_id = f'ContactApp/{current_user.id}'
    r = cloudinary.uploader.upload(file.file, public_id=public_id, overwrite=True)
    src_url = cloudinary.CloudinaryImage(public_id).build_url(width=250,
                                                              height=250,
                                                              crop='fill',
                                                              version=r.get('version'))
    
    user = await repo_users.update_avatar(current_user.email, src_url, db)
    return user
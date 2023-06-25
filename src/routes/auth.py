from fastapi import APIRouter, Depends, HTTPException, status, Security
from fastapi.security import OAuth2PasswordRequestForm, HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from src.database.db import get_db
from src.schemas import UserModel, UserResponse, TokenModel
from src.repository import auth as repo_auth
from src.services.auth import auth_service

router = APIRouter(prefix='/auth', tags=['auth'])
security = HTTPBearer()


@router.post('/signup', response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def signup(body: UserModel, db: Session = Depends(get_db)):
    exist_user = await repo_auth.get_user_by_email(body.email, db)
    if exist_user:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail='Account with this email already exist')
    body.password = auth_service.get_password_hash(body.password)
    new_user = await repo_auth.create_user(body, db)
    return new_user

@router.post('/login', response_model=TokenModel)
async def login(body: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = await repo_auth.get_user_by_email(body.email, db)
    if not user: # if user attempt to login with email hadn't signed up
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Invalid email') 
    if not auth_service.verify_password(body.password, user.password): # if user put wrong password
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Invalid password') 
    access_token = await auth_service.create_access_token(data={'sub': user.email})
    refresh_token = await auth_service.create_refresh_token(data={'sub': user.email})
    await repo_auth.update_token(user, refresh_token, db)
    return {'access_token': access_token, 'refresh_token': refresh_token, 'token_type': 'bearer'}

@router.get('/refresh_token', response_model=TokenModel)
async def refresh_token(credentials: HTTPAuthorizationCredentials = Security(security), db: Session = Depends(get_db)):
    token = credentials.credentials
    email = await auth_service.decode_refresh_token(token)
    user  = await repo_auth.get_user_by_email(email, db)
    if user.refresh_token != token:
        await repo_auth.update_token(user, None, db)
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Invalid refresh token')
    access_token = await auth_service.create_access_token({'sub': email})
    refresh_token = await auth_service.create_refresh_token({'sub': email})
    await repo_auth.update_token(user, refresh_token, db)
    return {'access_token': access_token, 'Refresh_token': refresh_token, 'token_type': 'bearer'}
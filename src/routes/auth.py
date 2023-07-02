from fastapi import APIRouter, Depends, HTTPException, status, Security, BackgroundTasks, Request
from fastapi.security import OAuth2PasswordRequestForm, HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from src.database.db import get_db, redis_session
from src.schemas import UserModel, UserResponse, TokenModel, RequestEmail
from src.repository import auth as repo_auth
from src.services.auth import auth_service
from src.services.email import send_email


router = APIRouter(prefix='/auth', tags=['auth'])
security = HTTPBearer()


@router.post('/signup', response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def signup(body: UserModel,
                 background_tasks: BackgroundTasks,
                 request: Request, db: Session = Depends(get_db)):
    exist_user = await repo_auth.get_user_by_email(body.email, db)
    if exist_user:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail='Account with this email already exist')
    body.password = auth_service.get_password_hash(body.password)
    new_user = await repo_auth.create_user(body, db)
    background_tasks.add_task(send_email, new_user.email, request.base_url) # starts verification way
    return {"user": new_user, "detail": "User successfully created. Check your email for confirmation"}


@router.post('/login', response_model=TokenModel)
async def login(body: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = await repo_auth.get_user_by_email(body.username, db)
    
    if not user: # if user attempt to login with email hadn't signed up
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Invalid email')
    if not user.confirmed:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Email hasn't confirmed yet")
    if not auth_service.verify_password(body.password, user.password): # if user put wrong password
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Invalid password')
 
    access_token = await auth_service.create_access_token(data={'sub': user.email})
    refresh_token = await auth_service.create_refresh_token(data={'sub': user.email})

    await repo_auth.update_token(user, refresh_token, db)
    return {'access_token': access_token, 'refresh_token': refresh_token, 'token_type': 'bearer'}


@router.get('/refresh_token', response_model=TokenModel) # TODO find out when this route use
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


@router.get('/confirmed_email/{token}') #  link for confirmation email
async def connfirm_email(token: str, db: Session = Depends(get_db)):
    email = await auth_service.get_email_from_token(token)
    user = await repo_auth.get_user_by_email(email, db)
    if not user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Verification error')
    if user.confirmed:
        return {'message': 'Your email has already been confirmed'}
    await repo_auth.confirm_email(email, db)
    return {'message': 'Email confirmed'}


@router.post('/request_email')
async def request_email(body: RequestEmail,
                        background_tasks: BackgroundTasks,
                        request: Request, db: Session = Depends(get_db)): 
    user = await repo_auth.get_user_by_email(body.email, db)
    
    if user.confirmed:
        return {'message': 'Email has already been confirmed'}
    if user:
        background_tasks.add_task(send_email, user.email, request.base_url)
    return {'message': 'Check your email for confirmation'}
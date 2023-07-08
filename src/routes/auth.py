from fastapi import APIRouter, Depends, HTTPException, status, Security, BackgroundTasks, Request
from fastapi.security import OAuth2PasswordRequestForm, HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from src.database.db import get_db
from src.schemas import UserModel, UserResponse, TokenModel, RequestEmail
from src.repository import auth as repo_auth
from src.services.auth import auth_service
from src.services.email import send_email, send_reset_password_email


router = APIRouter(prefix='/auth', tags=['auth'])
security = HTTPBearer()


@router.post('/signup', response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def signup(body: UserModel,
                 background_tasks: BackgroundTasks,
                 request: Request, db: Session = Depends(get_db)):
    """
    Create nwe user. If user with this email exists, raise 409 error
    
    After send request, app send message with verification token to confirm email.

    :param body: Email and password.
    :type body: UserModel
    :param background_tasks: Object to send email messages.
    :type background_tasks: BackgroundTasks
    :param request: Request object to get base url.
    :type request: Request
    :param db: Database session.
    :type db: Session
    :return: Message with new user info. Response with 201 status code.
    :rtype: UserResponse
    """
    exist_user = await repo_auth.get_user_by_email(body.email, db)
    if exist_user:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail='Account with this email already exist')
    body.password = auth_service.get_password_hash(body.password)
    new_user = await repo_auth.create_user(body, db)
    background_tasks.add_task(send_email, new_user.email, request.base_url) # starts verification way
    return {"user": new_user, "detail": "User successfully created. Check your email for confirmation"}


@router.post('/login', response_model=TokenModel)
async def login(body: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """
    Authenticate user. Return jwt access and refresh token. 
    
    If email which user attempt to login isn't signed up, or email is not confirmed, or password is wrong.
    
    :param body: Email and password.
    :type body: OAuth2PasswordRequestForm
    :param db: Database session.
    :type db: Session
    :return: Access and refresh tokens.
    :rtype: TokenModel
    """
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


@router.get('/refresh_token', response_model=TokenModel)
async def refresh_token(credentials: HTTPAuthorizationCredentials = Security(security), db: Session = Depends(get_db)):
    """
    Take refresh token. If token is valid, update access and refresh tokens.
    
    IF refresh token is not valid, delete refresh token and raise 401 error.
    
    :param credenticals: JWT refresh token.
    :type credentials: HTTPAuthorizationCredentials
    :param db: Database session
    :type db: Session
    :return: Access and refresh tokens.
    :rtype: TokenModel
    """
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
    """
    Route for confirmation email. Take token from url. Get email from token.
    
    If user with this email doesn't exist raise 400 error.
    IF user is already confirmed, return messsage 'Your email has already been confirmed'
    
    :param token: 
    :type token: str
    :param db: Database session.
    :type db: Session
    :return: Message "email confirmed'.
    :rtype: dict
    """
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
    """
    Separate function for confirming email.
    
    Take email. If user is already confirmed, return message 'Email has already been confirmed'
    
    After send request, app send message with verification token to confirm email.

    :param body: Email
    :type body: RequestEmail
    :param background_tasks: Request object to get base url.
    :type background_tasks: BackgroundTasks
    :param request: Request object to get base url.
    :type request: Request
    :param db: Database session.
    :type db: Session
    :return: Message 'Check your email for confirmation'.
    :rtype: dict
    """
    user = await repo_auth.get_user_by_email(body.email, db)
    
    if user.confirmed:
        return {'message': 'Email has already been confirmed'}
    if user:
        background_tasks.add_task(send_email, user.email, request.base_url)
    return {'message': 'Check your email for confirmation'}


@router.post('/reset_password')
async def reset_password(body: UserModel,
                         background_task: BackgroundTasks,
                         request: Request, db: Session = Depends(get_db)):
    """
    Route ror reset password request. Get user by email and new password. Send reset password token with them on email.
    
    If user email is not confirmed raise 401 error.
    
    If user with this email was not found raise 409 error.
    
    :param body: Email and new password
    :type body: UserModel
    :param background_task: Object to send email messages.
    :type background_task: BackgroundTasks
    :param request: Request object to get base url.
    :type request: Request
    :param db: Database session.
    :type db: Session
    :return: Message 'Check your email'.
    :rtype: dict
    """
    user = await repo_auth.get_user_by_email(body.email, db)
    
    if not user.confirmed:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Email hasn't confirmed yet")
    if not user:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail='Account with this email already exist')
    else:
        background_task.add_task(send_reset_password_email, user.email, body.password, request.base_url)
        return {'message': 'Check your email'}

@router.get('/reset_password/done/{token}')
async def reset_password_done(token: str, db: Session = Depends(get_db)):
    """
    Route for confirmation reset password request.
    
    If token is valid replace password in database.
    
    :param token: Reset password token.
    :type token: str
    :param db: Database session.
    :type db: Session
    :return: Message 'Password has been reset'.
    :rtype: dict
    """
    email = await auth_service.get_email_from_token(token)
    password = await auth_service.get_password_from_token(token)
    user = await repo_auth.get_user_by_email(email, db)
    if not user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Verification error')
    await repo_auth.reset_password(user, password, db)
    return {'message': 'Password has been reset'}

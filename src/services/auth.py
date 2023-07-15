from datetime import datetime, timedelta
from typing import Optional
import pickle

from jose import jwt, JWTError
from fastapi import Depends, status, HTTPException
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from src.database.db import get_db, redis_session
from src.repository import auth as repo_users
from src.conf.config import settings

class Auth:
    """
    Class with authentication methods.
    
    Create and decode JWT tokens. Hash and verify passwords.
    
    Have method for get current user for dependency injection.
    """
    pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')
    SECRET_KEY = settings.secret_key
    ALGORITHM = settings.algorithm
    oauth2_scheme = OAuth2PasswordBearer(tokenUrl='api/auth/login')
    r = redis_session
    
    def verify_password(self, plain_password: str, hashed_password: str):
        """
        For authentication. Compare hashed password from database and plain password from auth form.
        
        :param plain_password: Password from auth form.
        :type plain_password: str
        :param hashed_password: Password hash from database.
        :type hashed_password: str
        """
        result = self.pwd_context.verify(plain_password, hashed_password)
        return result
    
    def get_password_hash(self, password: str):
        """
        Hash password.
        
        :param password: Password itself.
        :type password: str
        :return: Hashed password.
        :rtype: str
        """
        result = self.pwd_context.hash(password)
        return result
    
    async def get_email_from_token(self, token: str):
        """
        Decode access token and return token from it.
        
        :param token: Access token.
        :type token: str
        :return: Email from token.
        :rtype: EmailStr
        """
        try:
            payload = jwt.decode(token, self.SECRET_KEY, self.ALGORITHM)
            email = payload['sub']
            return email
        except JWTError as err:
            print(err)
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail='Invalid verification token')
    
    async def get_password_from_token(self, token: str):
        """
        Decode reset password token and return new password hash.
        
        :param token: Reset password token.
        :type token: str
        :return: Password hash.
        :rtype: str
        """
        try:
            payload = jwt.decode(token, self.SECRET_KEY, self.ALGORITHM)
            password = payload['pas']
            return password
        except JWTError as err:
            print(err)
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail='Invalid verification token')

    async def create_access_token(self, data: dict, expires: Optional[float] = None):
        """
        Create access token.
        
        :param data: User email.
        :type data: dict
        :param expires: Optional argument. Time that jwt token should be expired. If None, default time is 15 minutes.
        :type expires: Optional[float]
        :return: Access jwt token.
        :rtype: str
        """
        payload = data.copy()
        if expires:
            expires_time = datetime.utcnow() + timedelta(seconds=expires)
        else:
            expires_time = datetime.utcnow() + timedelta(minutes=15)
        payload.update({'iat': datetime.utcnow(), 'exp': expires_time, 'scope': 'access_token'})
        access_token = jwt.encode(payload, self.SECRET_KEY, algorithm=self.ALGORITHM)
        return access_token
    
    async def create_refresh_token(self, data: dict, expires: Optional[float] = None):
        """
        Create refresh token.
        
        :param data: User email.
        :type data: dict
        :param expires: Optional argument. Time that jwt token should be expired. If None, default time is 15 minutes.
        :type expires: Optional[float]
        :return: Refresh jwt token.
        :rtype: str
        """
        payload = data.copy()
        if expires:
            expires_time = datetime.utcnow() + timedelta(seconds=expires)
        else:
            expires_time = datetime.utcnow() + timedelta(minutes=15)
        payload.update({'iat': datetime.utcnow(), 'exp': expires_time, 'scope': 'refresh_token'})
        access_token = jwt.encode(payload, self.SECRET_KEY, algorithm=self.ALGORITHM)
        return access_token
    
    async def create_verification_token(self, data: dict):
        """
        Create verification token. Expires in 7 days.
        
        :param data: User email.
        :type data: dict
        :return: Verification jwt token.
        :rtype: str
        """
        payload = data.copy()
        expires_time = datetime.utcnow() + timedelta(days=7)
        payload.update({'iat': datetime.utcnow(), 'exp': expires_time})
        token = jwt.encode(payload, self.SECRET_KEY, algorithm=self.ALGORITHM)
        return token
    
    async def create_reset_password_token(self, data: dict):
        """
        Create reset password token. Expires in 1 hour.
        
        :param data: User email and new password hash.
        :type data: dict
        :return: Reset password jwt token.
        :rtype: str
        """
        payload = data.copy()
        expires_time = datetime.utcnow() + timedelta(hours=1)
        payload.update({'iat': datetime.utcnow(), 'exp': expires_time})
        token = jwt.encode(payload, self.SECRET_KEY, self.ALGORITHM)
        return token
    
    async def decode_refresh_token(self, refresh_token: str):
        """
        Decode refresh token. Return email from it.
        
        If not refresh token given, raise 401 error.
        
        :param refresh_token:
        :type refresh_token: str
        :return: User email.
        :rtype: EmailStr
        
        """
        try:
            payload = jwt.decode(refresh_token, self.SECRET_KEY, algorithms=[self.ALGORITHM])
            if payload['scope'] == 'refresh_token':
                email = payload['sub']
                return email
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Invalid scope for token')
        except JWTError:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Couldn't validate credentials")
    
    async def get_current_user(self, token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)): # aka decode_access_token
        """
        Decode access token and get email form it.
        
        If not access token given, raise 401 error.
        
        After that get from hash User object
        
        If User object not in hash, get User object from database and then hash it on 9000 seconds.
        
        :param token: Access token.
        :type token: str
        :param db: Database session.
        :type db: Session
        :return: User object.
        :rtype: User
        
        """

        credentials_exception = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                              detail="Couldn't validate credentials",
                                              headers={'WWW-Authenticate': 'Bearer'})

        try: # trying to decode jwt token to get user
            payload = jwt.decode(token, self.SECRET_KEY, algorithms=[self.ALGORITHM])
            if payload['scope'] == 'access_token':
                email = payload['sub']
                if not email:
                    raise credentials_exception
            else:
                raise credentials_exception
        except JWTError:
            raise credentials_exception
        
        user = await self.r.get(email) # get user from cache
        if not user:
            user = await repo_users.get_user_by_email(email, db)
            if not user:
                raise credentials_exception
            await self.r.set(email, pickle.dumps(user)) # set user to cache on 9000 seconds
            await self.r.expire(email, 9000)
        else:
            user = pickle.loads(user)
        return user


auth_service = Auth()
from pydantic import BaseConfig


class Settings(BaseConfig):
    SQLALCHEMY_DATABASE_URL: str
    SECRET_KEY: str
    ALGORITHM: str
    MAIL_USERNAME: str
    MAIL_PASSWORD: str
    MAIL_FROM: str
    MAIL_PORT: int
    MAIL_SERVER: str
    REDIS_HOST: str = 'localhost'
    REDIS_PORT: int = 6379
    
    class Config:
        env_file = '.env'
        env_file_encoding = 'utf-8'


settings = Settings()
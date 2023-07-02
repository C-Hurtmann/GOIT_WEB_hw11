from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from redis.asyncio import Redis
from src.conf.config import settings

SQLALCHEMY_DATABASE_URL = settings.sqlalchemy_database_url

engine = create_engine(SQLALCHEMY_DATABASE_URL)
Sessionlocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)


def get_db():
    db = Sessionlocal()
    try:
        yield db
    finally:
        db.close()


redis_session = Redis(host=settings.redis_host, port=settings.redis_port, db=0, encoding='utf-8', decode_responses=True)
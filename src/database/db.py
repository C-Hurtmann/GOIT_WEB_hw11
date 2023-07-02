from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

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


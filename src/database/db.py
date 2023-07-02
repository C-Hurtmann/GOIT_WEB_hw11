from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.conf.config import settings


engine = create_engine(settings.sqlalchemy_database_url)
Sessionlocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)


def get_db():
    db = Sessionlocal()
    try:
        yield db
    finally:
        db.close()


from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


SQLALCHEMY_DATABASE_URL = "postgresql+psycopg2://czagorodnyi:B34f56j47h55@localhost:5432/postgres"

engine = create_engine(SQLALCHEMY_DATABASE_URL)
Sessionlocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)


def get_db():
    db = Sessionlocal()
    try:
        yield db
    finally:
        db.close()


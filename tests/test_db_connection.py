from pathlib import Path
import sys


from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

root_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(root_dir))

from src.database.models import Base

SQLALCHEMY_DATABASE_URL = 'postgresql+psycopg2://admin:admin@localhost:5434/postgres'

engine = create_engine(SQLALCHEMY_DATABASE_URL)
TestSession = sessionmaker(bind=engine, autocommit=False, autoflush=False)

Base.metadata.bind = engine

Base.metadata.create_all(engine)

print(sys.path)
import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

root_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(root_dir))

from main import app
from src.database.models import Base
from src.database.db import get_db


SQLALCHEMY_DATABASE_URL = 'postgresql+psycopg2://admin:admin@localhost:5434/postgres'

engine = create_engine(SQLALCHEMY_DATABASE_URL)

TestSession = sessionmaker(bind=engine, autoflush=False, autocommit=False)


@pytest.fixture(scope='module')
def session():
    
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    
    db = TestSession()
    
    try:
        yield db
    finally:
        db.close()

@pytest.fixture(scope='module')
def client(session):
    
    def override_get_db():
        try:
            yield session
        finally:
            session.close()
    
    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)

@pytest.fixture(scope='module')
def user():
    return {'email': 'test@gmail.com', 'password': '123456789'}
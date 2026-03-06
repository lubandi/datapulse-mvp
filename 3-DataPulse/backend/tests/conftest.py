"""Test fixtures for pytest."""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.database import Base, get_db

SQLALCHEMY_TEST_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_TEST_URL, connect_args={"check_same_thread": False})
TestSession = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    db = TestSession()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(scope="session", autouse=True)
def setup_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def test_db():
    db = TestSession()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture
def sample_user(client):
    resp = client.post("/api/auth/register",
        json={"email": "test@example.com", "password": "test123", "full_name": "Test User"})
    return resp.json()


@pytest.fixture
def auth_token(sample_user):
    return sample_user["access_token"]

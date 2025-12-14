import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from db.base import Base, get_db
from main import app

SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture
def db_session():
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def client(db_session):
    def override_get_db():
        try:
            yield db_session
        finally:
            db_session.close()
    
    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)
    app.dependency_overrides.clear()


def test_register_user(client):
    response = client.post(
        "/api/v1/auth/register",
        json={"email": "test@example.com", "password": "testpass123"}
    )
    assert response.status_code == 201
    assert response.json()["email"] == "test@example.com"


def test_register_duplicate_email(client):
    # Register first time
    client.post(
        "/api/v1/auth/register",
        json={"email": "test@example.com", "password": "testpass123"}
    )
    # Try to register again
    response = client.post(
        "/api/v1/auth/register",
        json={"email": "test@example.com", "password": "testpass123"}
    )
    assert response.status_code == 400


def test_login_success(client):
    # Register user
    client.post(
        "/api/v1/auth/register",
        json={"email": "test@example.com", "password": "testpass123"}
    )
    # Login
    response = client.post(
        "/api/v1/auth/login",
        data={"email": "test@example.com", "password": "testpass123"}
    )
    assert response.status_code == 200
    assert "access_token" in response.json()


def test_login_invalid_credentials(client):
    response = client.post(
        "/api/v1/auth/login",
        data={"email": "nonexistent@example.com", "password": "wrongpass"}
    )
    assert response.status_code == 401






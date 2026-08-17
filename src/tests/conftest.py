import pytest
from unittest.mock import AsyncMock
from fastapi.testclient import TestClient
from datetime import datetime, timezone
from uuid import uuid4, UUID
from src import app
from src.db.main import get_session
from src.db.model import User
from src.books.service import get_book_service
from src.books.book_routes import access_token_bearer
from src.auth.dependencies import get_curr_user

mock_session = AsyncMock()
mock_book_service = AsyncMock()
fake_uid = uuid4()

def get_mock_session():
    yield mock_session

def get_mock_book_service():
    return mock_book_service

def get_fake_curr_user():
    return User(
        username="tes_tuser",
        email="test@test.com",
        f_name="Test",
        l_name="User",
        pswd="fake_password",
        is_verified=True,
        role="user",
    )

def get_fake_payload():
    return {
        "user": {
            'email': "test@mail.com",
            'user_uid': str(fake_uid),
            'role': "user",
        },
        "exp": datetime.now(timezone.utc),
        "jti": str(uuid4()),
        "refresh": False,
    }

app.dependency_overrides[get_session] = get_mock_session
app.dependency_overrides[get_book_service] = get_mock_book_service
app.dependency_overrides[get_curr_user] = get_fake_curr_user
app.dependency_overrides[access_token_bearer] = get_fake_payload

@pytest.fixture
def fake_session():
    return mock_session

@pytest.fixture
def fake_book_service():
    return mock_book_service

@pytest.fixture
def test_client():
    return TestClient(app)

@pytest.fixture()
def fake_uid_fixture():
    return fake_uid

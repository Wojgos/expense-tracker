import pytest
from datetime import timedelta
from unittest.mock import patch
from jose import jwt

from app.core.security import (
    hash_password,
    verify_password,
    create_access_token,
    decode_access_token,
)

@pytest.fixture
def mock_settings():
    with patch("app.core.security.settings") as mocked:
        mocked.secret_key = "test_secret_key"
        mocked.algorithm = "HS256"
        mocked.access_token_expire_minutes = 30
        yield mocked

class TestHashPassword:
    def test_hash_password_returns_string(self):
        hashed = hash_password("password123")
        assert isinstance(hashed, str)
        assert hashed != "password123"

    def test_hash_password_different_salts(self):
        plain = "password123"
        assert hash_password(plain) != hash_password(plain)

    def test_hash_password_not_empty(self):
        assert len(hash_password("pass")) > 0

class TestVerifyPassword:
    @pytest.mark.parametrize("password", [
        "short",
        "VeryLongPassword123!@#",
        " ",
        "zażółć gęślą jaźń",
        "12345678"
    ])
    def test_verify_password_various_formats(self, password):
        hashed = hash_password(password)
        assert verify_password(password, hashed) is True

    def test_verify_password_fail(self):
        hashed = hash_password("correct_pass")
        assert verify_password("wrong_pass", hashed) is False

class TestCreateAccessToken:
    def test_create_access_token_default_expiry(self, mock_settings):
        token = create_access_token("user123")
        assert isinstance(token, str)
        assert len(token) > 0

    def test_create_access_token_custom_expiry(self, mock_settings):
        token = create_access_token("user123", timedelta(hours=1))
        assert isinstance(token, str)

    def test_create_access_token_subject_in_payload(self, mock_settings):
        subject = "user123"
        token = create_access_token(subject)
        payload = jwt.decode(token, mock_settings.secret_key, algorithms=[mock_settings.algorithm])
        assert payload["sub"] == subject

class TestDecodeAccessToken:
    def test_decode_access_token_valid(self, mock_settings):
        subject = "user123"
        token = create_access_token(subject)
        assert decode_access_token(token) == subject

    def test_decode_access_token_expired(self, mock_settings):
        token = create_access_token("user123", timedelta(seconds=-1))
        assert decode_access_token(token) is None

    @pytest.mark.parametrize("invalid_token", [
        "invalid.jwt.token",                  # Niepoprawny format
        "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.YmFkX2RhdGE.signature", # Malformed JSON
        "",                                   # Pusty string
        None,                                 # Brak tokena
        "totally-not-a-token"                 # Losowe znaki
    ])
    def test_decode_access_token_invalid_cases(self, mock_settings, invalid_token):
        assert decode_access_token(invalid_token) is None
        #if not token: return None trzeba dodać w funkcji decode_access_token, bo biblioteka jose robi rsplit na pustej wartości. brak walidacji
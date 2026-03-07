import pytest
from datetime import timedelta
from unittest.mock import patch

from app.core.security import (
    hash_password,
    verify_password,
    create_access_token,
    decode_access_token,
)


class TestHashPassword:
    def test_hash_password_returns_string(self):
        plain = "password123"
        hashed = hash_password(plain)
        assert isinstance(hashed, str)
        assert hashed != plain

    def test_hash_password_different_salts(self):
        plain = "password123"
        hashed1 = hash_password(plain)
        hashed2 = hash_password(plain)
        assert hashed1 != hashed2

    def test_hash_password_not_empty(self):
        plain = "pass"
        hashed = hash_password(plain)
        assert len(hashed) > 0


class TestVerifyPassword:
    def test_verify_password_correct(self):
        plain = "password123"
        hashed = hash_password(plain)
        assert verify_password(plain, hashed) is True

    def test_verify_password_incorrect(self):
        plain = "password123"
        wrong = "wrongpass"
        hashed = hash_password(plain)
        assert verify_password(wrong, hashed) is False

    def test_verify_password_empty_plain(self):
        plain = ""
        hashed = hash_password(plain)
        assert verify_password(plain, hashed) is True
        assert verify_password("notempty", hashed) is False

    def test_verify_password_case_sensitive(self):
        plain = "Password123"
        hashed = hash_password(plain)
        assert verify_password("password123", hashed) is False


class TestCreateAccessToken:
    @patch('app.core.security.settings')
    def test_create_access_token_default_expiry(self, mock_settings):
        mock_settings.access_token_expire_minutes = 30
        mock_settings.secret_key = "secret"
        mock_settings.algorithm = "HS256"
        subject = "user123"
        token = create_access_token(subject)
        assert isinstance(token, str)
        assert len(token) > 0

    @patch('app.core.security.settings')
    def test_create_access_token_custom_expiry(self, mock_settings):
        mock_settings.secret_key = "secret"
        mock_settings.algorithm = "HS256"
        subject = "user123"
        expiry = timedelta(hours=1)
        token = create_access_token(subject, expiry)
        assert isinstance(token, str)

    @patch('app.core.security.settings')
    def test_create_access_token_subject_in_payload(self, mock_settings):
        mock_settings.secret_key = "secret"
        mock_settings.algorithm = "HS256"
        subject = "user123"
        token = create_access_token(subject)
        decoded = decode_access_token(token)
        assert decoded == subject


class TestDecodeAccessToken:
    @patch('app.core.security.settings')
    def test_decode_access_token_valid(self, mock_settings):
        mock_settings.secret_key = "secret"
        mock_settings.algorithm = "HS256"
        subject = "user123"
        token = create_access_token(subject)
        decoded = decode_access_token(token)
        assert decoded == subject

    @patch('app.core.security.settings')
    def test_decode_access_token_invalid(self, mock_settings):
        mock_settings.secret_key = "secret"
        mock_settings.algorithm = "HS256"
        invalid_token = "invalid.jwt.token"
        decoded = decode_access_token(invalid_token)
        assert decoded is None

    @patch('app.core.security.settings')
    def test_decode_access_token_wrong_secret(self, mock_settings):
        mock_settings.secret_key = "secret"
        mock_settings.algorithm = "HS256"
        subject = "user123"
        token = create_access_token(subject)
        # Change secret
        mock_settings.secret_key = "wrongsecret"
        decoded = decode_access_token(token)
        assert decoded is None

    @patch('app.core.security.settings')
    def test_decode_access_token_expired(self, mock_settings):
        mock_settings.secret_key = "secret"
        mock_settings.algorithm = "HS256"
        subject = "user123"
        # Expired token
        expired_delta = timedelta(seconds=-1)
        token = create_access_token(subject, expired_delta)
        decoded = decode_access_token(token)
        assert decoded is None
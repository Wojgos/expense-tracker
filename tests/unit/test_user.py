import pytest
import uuid
from unittest.mock import AsyncMock, MagicMock
from sqlalchemy.ext.asyncio import AsyncSession
from app.crud.user import get_user_by_email, get_user_by_id, create_user
from app.db.models.user import User


@pytest.fixture
def mock_db():
    """Tworzy wirtualną sesję bazy danych."""
    return AsyncMock(spec=AsyncSession)


@pytest.mark.asyncio
class TestUserCRUD:

    async def test_get_user_by_email_found(self, mock_db):
        email = "test@example.com"
        mock_user = User(email=email, display_name="Tester")

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_user
        mock_db.execute.return_value = mock_result

        result = await get_user_by_email(mock_db, email)

        assert result is not None
        assert result.email == email
        mock_db.execute.assert_called_once()

    async def test_get_user_by_email_not_found(self, mock_db):
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_db.execute.return_value = mock_result

        result = await get_user_by_email(mock_db, "nonexistent@example.com")

        assert result is None

    async def test_get_user_by_id(self, mock_db):
        user_id = uuid.uuid4()
        mock_user = User(id=user_id, email="test@test.pl")
        mock_db.get.return_value = mock_user

        result = await get_user_by_id(mock_db, user_id)

        assert result == mock_user
        mock_db.get.assert_called_once_with(User, user_id)

    async def test_create_user(self, mock_db):
        email = "new@user.com"
        password = "hashed_password_123"
        name = "New User"

        user = await create_user(mock_db, email, password, name)

        assert user.email == email
        assert user.hashed_password == password
        assert user.display_name == name

        mock_db.add.assert_called_once()
        mock_db.flush.assert_called_once()
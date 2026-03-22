import pytest
import uuid

BASE_URL = "http://localhost:3000"
API_URL = "http://localhost:3000/api"


def _unique_suffix():
    return uuid.uuid4().hex[:8]


@pytest.fixture(scope="session")
def base_url():
    return BASE_URL


@pytest.fixture(scope="session")
def test_user_credentials():
    """Unique credentials used across all tests in the session."""
    suffix = _unique_suffix()
    return {
        "email": f"e2e_{suffix}@test.com",
        "password": "TestPass123!",
        "display_name": f"E2E User {suffix}",
    }


@pytest.fixture(scope="session")
def _register_test_user(test_user_credentials):
    """Register the test user via API once per session."""
    import httpx
    resp = httpx.post(f"{API_URL}/auth/register", json={
        "email": test_user_credentials["email"],
        "password": test_user_credentials["password"],
        "display_name": test_user_credentials["display_name"],
    })
    assert resp.status_code == 201, f"Registration failed: {resp.text}"
    return resp.json()
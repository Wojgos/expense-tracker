import pytest
from playwright.sync_api import Playwright, Browser, Page
import uuid
import httpx

API_URL = "http://localhost:3000/api"


@pytest.fixture(scope="session")
def browser_context_args(browser_context_args):
    return {
        **browser_context_args,
        "viewport": {"width": 1280, "height": 720},
    }


@pytest.fixture(scope="function")
def page(browser: Browser) -> Page:
    context = browser.new_context()
    context.set_default_timeout(5000)
    page = context.new_page()
    yield page
    context.close()


@pytest.fixture(scope="session")
def test_users_credentials():
    suffix = uuid.uuid4().hex[:8]
    return {
        "user1": {
            "email": f"user1_{suffix}@example.com",
            "password": "password",
            "display_name": f"User1 {suffix}",
        },
        "user2": {
            "email": f"user2_{suffix}@example.com",
            "password": "password",
            "display_name": f"User2 {suffix}",
        },
        "user3": {
            "email": f"user3_{suffix}@example.com",
            "password": "password",
            "display_name": f"User3 {suffix}",
        },
    }


@pytest.fixture(scope="session")
def _register_test_users(test_users_credentials):
    """Register the test users via API once per session."""
    registered_users = {}

    for user_key, creds in test_users_credentials.items():
        resp = httpx.post(f"{API_URL}/auth/register", json={
            "email": creds["email"],
            "password": creds["password"],
            "display_name": creds["display_name"],
        })
        assert resp.status_code == 201, f"Registration failed for {user_key}: {resp.text}"
        registered_users[user_key] = resp.json()

    return registered_users

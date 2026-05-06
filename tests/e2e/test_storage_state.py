import json
import os
import uuid
import tempfile

import httpx
import pytest
from playwright.sync_api import Browser, BrowserContext, Page, expect

BASE_URL = "http://localhost:3000"
API_URL = "http://localhost:3000/api"

STORAGE_STATE_PATH = os.path.join(
    tempfile.gettempdir(), "expense_tracker_auth_state.json"
)


@pytest.fixture(scope="module")
def auth_credentials() -> dict:
    suffix = uuid.uuid4().hex[:8]
    return {
        "email": f"storage_state_{suffix}@example.com",
        "password": "StoragePass123!",
        "display_name": f"StorageState User {suffix}",
    }


@pytest.fixture(scope="module")
def _register_user(auth_credentials: dict):
    resp = httpx.post(f"{API_URL}/auth/register", json={
        "email": auth_credentials["email"],
        "password": auth_credentials["password"],
        "display_name": auth_credentials["display_name"],
    })
    assert resp.status_code == 201, f"Registration failed: {resp.text}"
    return resp.json()


@pytest.fixture(scope="module")
def authenticated_state(browser: Browser, auth_credentials: dict, _register_user) -> str:
    context = browser.new_context()
    context.set_default_timeout(10_000)
    page = context.new_page()

    page.goto(f"{BASE_URL}/login")
    page.fill("#email", auth_credentials["email"])
    page.fill("#password", auth_credentials["password"])
    page.click("button:has-text('Sign in')")

    page.wait_for_timeout(1500)
    page.goto(BASE_URL)
    expect(page.locator("h1", has_text="My Groups")).to_be_visible(timeout=10_000)

    context.storage_state(path=STORAGE_STATE_PATH)
    context.close()

    return STORAGE_STATE_PATH


@pytest.fixture()
def auth_page(browser: Browser, authenticated_state: str) -> Page:
    context = browser.new_context(storage_state=authenticated_state)
    context.set_default_timeout(10_000)
    page = context.new_page()
    yield page
    context.close()


def test_storage_state_dashboard_access_without_login(auth_page: Page, auth_credentials: dict):
    """Autor: Wojciech Domański."""
    auth_page.goto(BASE_URL)

    expect(auth_page.locator("h1", has_text="My Groups")).to_be_visible(timeout=10_000)
    expect(auth_page.locator(f"text={auth_credentials['display_name']}")).to_be_visible()
    expect(auth_page.locator("button", has_text="+ New Group")).to_be_visible()

    expect(auth_page.locator("text=Sign in to your account")).not_to_be_visible()


def test_storage_state_create_group_without_login(auth_page: Page, auth_credentials: dict):
    """Autor: Arkadiusz Gnidziejko."""
    auth_page.goto(BASE_URL)
    expect(auth_page.locator("h1", has_text="My Groups")).to_be_visible(timeout=10_000)

    group_name = f"StorageState Group {uuid.uuid4().hex[:6]}"

    auth_page.click("button:has-text('+ New Group')")
    expect(auth_page.locator("h2", has_text="New Group")).to_be_visible()
    auth_page.fill("input[placeholder='e.g. Vacation 2026']", group_name)
    auth_page.fill("input[placeholder='Shared expenses for the trip']", "Test storageState")
    auth_page.click("button:has-text('Create')")

    auth_page.wait_for_timeout(2000)
    auth_page.goto(BASE_URL)
    expect(auth_page.locator(f"text={group_name}")).to_be_visible(timeout=10_000)


def test_storage_state_navigate_balances_without_login(auth_page: Page, auth_credentials: dict):
    """Autor: Jakub Gerwel."""
    auth_page.goto(f"{BASE_URL}/balances")

    expect(auth_page.locator("text=Total Balance")).to_be_visible(timeout=10_000)
    expect(auth_page.locator("text=Your Accounts")).to_be_visible()

    expect(auth_page.locator("text=Sign in to your account")).not_to_be_visible()
    expect(auth_page.locator("button:has-text('Add Account'), button:has-text('Add First Account')").first).to_be_visible()

import httpx
import pytest
import uuid
from playwright.sync_api import Browser, Page, expect

BASE_URL = "http://localhost:3000"
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


def _unique_balances_user() -> dict[str, str]:
    suffix = uuid.uuid4().hex[:8]
    return {
        "email": f"balances_{suffix}@example.com",
        "password": "TestPass123!",
        "display_name": f"Balances User {suffix}",
    }


def _balances_register_and_login(page: Page) -> dict[str, str]:
    creds = _unique_balances_user()

    register_response = page.request.post(
        f"{API_URL}/auth/register",
        data={
            "email": creds["email"],
            "password": creds["password"],
            "display_name": creds["display_name"],
        },
    )
    assert register_response.status == 201, register_response.text()

    login_response = page.request.post(
        f"{API_URL}/auth/login",
        data={
            "email": creds["email"],
            "password": creds["password"],
        },
    )
    assert login_response.status == 200, login_response.text()
    token = login_response.json()["access_token"]

    page.goto(BASE_URL)
    page.evaluate("(token) => localStorage.setItem('token', token)", token)
    page.goto(f"{BASE_URL}/balances")
    expect(page.locator("text=Your Accounts")).to_be_visible(timeout=10000)

    return creds


def _auth_headers(page: Page) -> dict[str, str]:
    token = page.evaluate("localStorage.getItem('token')")
    assert token, "Auth token not found in localStorage"
    return {"Authorization": f"Bearer {token}"}


def _account_card(page: Page, account_name: str):
    return page.locator(
        "div.rounded-xl.border.border-gray-200.bg-white",
        has_text=account_name,
    ).first


def _create_account_via_ui(
    page: Page,
    account_name: str,
    balance: str,
    currency: str = "PLN",
    account_type: str = "Cash",
    trigger_text: str = "Add Account",
) -> None:
    page.click(f'button:has-text("{trigger_text}")')
    modal = page.locator("div.fixed.inset-0").last
    expect(modal.locator('h2:has-text("Add Account")')).to_be_visible()

    modal.locator('input[placeholder="e.g. Wallet, Main Bank"]').fill(account_name)
    modal.locator("select").select_option(account_type)
    modal.locator('input[type="number"]').fill(balance)
    modal.locator('input[type="text"][maxlength="3"]').fill(currency)
    modal.locator('button:has-text("Add Account")').click()

    expect(_account_card(page, account_name)).to_be_visible(timeout=10000)


def _create_account_via_api(
    page: Page,
    account_name: str,
    balance: str,
    currency: str = "PLN",
    account_type: str = "Cash",
) -> dict:
    response = page.request.post(
        f"{API_URL}/accounts",
        data={
            "name": account_name,
            "type": account_type,
            "currency": currency,
            "balance": balance,
        },
        headers=_auth_headers(page),
    )
    assert response.status == 201, response.text()
    return response.json()


def _get_accounts_via_api(page: Page) -> list[dict]:
    response = page.request.get(
        f"{API_URL}/accounts",
        headers=_auth_headers(page),
    )
    assert response.status == 200, response.text()
    return response.json()


def _open_transaction_modal(page: Page, account_name: str) -> None:
    card = _account_card(page, account_name)
    expect(card).to_be_visible(timeout=10000)
    card.locator('button:has-text("+ Transaction")').click()
    expect(page.locator('h2:has-text("Add Transaction")')).to_be_visible()


def _create_transaction_via_ui(
    page: Page,
    account_name: str,
    amount: str,
    description: str,
    transaction_type: str,
) -> None:
    _open_transaction_modal(page, account_name)
    modal = page.locator("div.fixed.inset-0").last

    modal.locator(f'button:has-text("{transaction_type}")').click()
    modal.locator('input[type="number"]').fill(amount)
    modal.locator('input[placeholder="e.g. Salary, Groceries"]').fill(description)
    modal.locator('button:has-text("Save")').click()

    expect(page.locator('h2:has-text("Add Transaction")')).not_to_be_visible(timeout=10000)

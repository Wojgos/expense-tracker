"""
8 Playwright E2E journey tests for the Expense Tracker app (localhost:3000).
Each test covers a complete user path through the application.
"""
import re
import uuid
from playwright.sync_api import Page, expect


BASE = "http://localhost:3000"
API = "http://localhost:3000/api"


# ──────────────────────────────── helpers ────────────────────────────────

def _api_login(page: Page, email: str, password: str) -> str:
    """Login via API, return access_token."""
    resp = page.request.post(f"{API}/auth/login", data={
        "email": email, "password": password,
    })
    assert resp.status == 200
    return resp.json()["access_token"]


def _set_token_and_go(page: Page, token: str, path: str = "/"):
    """Inject JWT into localStorage and navigate."""
    page.goto(BASE)
    page.evaluate(f"localStorage.setItem('token', '{token}')")
    page.goto(f"{BASE}{path}")


def _login_ui(page: Page, email: str, password: str):
    """Full UI login: fill form → submit → wait for dashboard."""
    page.goto(f"{BASE}/login")
    page.fill("#email", email)
    page.fill("#password", password)
    page.click("button:has-text('Sign in')")

    page.wait_for_timeout(1500)
    page.goto(BASE)
    expect(page.locator("h1", has_text="My Groups")).to_be_visible(timeout=10_000)


def _quick_auth(page: Page, email: str, password: str):
    token = _api_login(page, email, password)
    _set_token_and_go(page, token)
    expect(page.locator("h1", has_text="My Groups")).to_be_visible(timeout=10_000)


# ────────────────────────────── tests ──────────────────────────────────

# 1. registration → login → dashboard
def test_register_and_login_journey(page: Page, test_user_credentials, _register_test_user):
    """Register a user (API), then log in via the UI and reach the dashboard."""
    creds = test_user_credentials

    page.goto(f"{BASE}/login")
    expect(page.locator("text=Sign in to your account")).to_be_visible()

    page.fill("#email", creds["email"])
    page.fill("#password", creds["password"])
    page.click("button:has-text('Sign in')")

    page.wait_for_timeout(1500)
    page.goto(BASE)

    expect(page.locator("h1", has_text="My Groups")).to_be_visible(timeout=10_000)
    expect(page.locator(f"text={creds['display_name']}")).to_be_visible()
    expect(page.locator("button", has_text="+ New Group")).to_be_visible()


# 2. Login → create group → open it → see group details
def test_create_group_and_view_details_journey(page: Page, test_user_credentials, _register_test_user):
    creds = test_user_credentials
    _quick_auth(page, creds["email"], creds["password"])

    group_name = f"Journey Group {uuid.uuid4().hex[:6]}"

    page.click("button:has-text('+ New Group')")
    expect(page.locator("h2", has_text="New Group")).to_be_visible()
    page.fill("input[placeholder='e.g. Vacation 2026']", group_name)
    page.fill("input[placeholder='Shared expenses for the trip']", "E2E journey test")
    page.click("button:has-text('Create')")

    page.wait_for_timeout(2000)
    page.goto(BASE)
    expect(page.locator("h1", has_text="My Groups")).to_be_visible(timeout=5_000)

    expect(page.locator(f"text={group_name}")).to_be_visible(timeout=5_000)

    page.locator(f"a:has-text('{group_name}')").first.click()

    expect(page.locator("h1", has_text=group_name)).to_be_visible(timeout=5_000)
    expect(page.locator("button", has_text="Expenses")).to_be_visible()
    expect(page.locator("button", has_text="Balances")).to_be_visible()
    expect(page.locator("button", has_text="Recurring")).to_be_visible()
    expect(page.locator("button", has_text=re.compile(r"Members"))).to_be_visible()

    page.click("text=Back to groups")
    expect(page.locator("h1", has_text="My Groups")).to_be_visible(timeout=5_000)


# 3. Login → create group → add expense → verify expense in list → check balances tab
def test_add_expense_and_check_balances_journey(page: Page, test_user_credentials, _register_test_user):
    creds = test_user_credentials
    _quick_auth(page, creds["email"], creds["password"])

    group_name = f"Expense Group {uuid.uuid4().hex[:6]}"

    page.click("button:has-text('+ New Group')")
    page.fill("input[placeholder='e.g. Vacation 2026']", group_name)
    page.click("button:has-text('Create')")
    expect(page.locator(f"text={group_name}")).to_be_visible(timeout=5_000)

    page.locator(f"a:has-text('{group_name}')").first.click()
    expect(page.locator("h1", has_text=group_name)).to_be_visible(timeout=5_000)

    page.click("button:has-text('+ Add Expense')")
    expect(page.locator("h2", has_text="Add Expense")).to_be_visible()

    page.fill("input[placeholder='e.g. Dinner']", "E2E Pizza")
    page.locator("input[type='number'][step='0.01'][min='0.01']").fill("42.50")
    page.click("button[type='submit']")

    expect(page.locator(".space-y-3 >> text=E2E Pizza").first).to_be_visible(timeout=10_000)
    expect(page.locator("text=42.50").first).to_be_visible()

    page.locator("button:has-text('Balances')").click()
    expect(page.locator("h3:has-text('Balances')")).to_be_visible(timeout=5_000)


# 4. Login → navigate to Balances → create account → verify it shows
def test_account_management_journey(page: Page, test_user_credentials, _register_test_user):
    creds = test_user_credentials
    _quick_auth(page, creds["email"], creds["password"])

    page.click("a:has-text('Balances')")
    expect(page.locator("text=Total Balance")).to_be_visible(timeout=5_000)
    expect(page.locator("text=Your Accounts")).to_be_visible()

    page.locator("button:has-text('Add Account')").first.click()
    expect(page.locator("h2", has_text="Add Account")).to_be_visible()

    acct_name = f"E2E Wallet {uuid.uuid4().hex[:4]}"
    page.fill("input[placeholder='e.g. Wallet, Main Bank']", acct_name)
    page.locator("input[type='number'][step='0.01']").fill("250")
    page.locator(".fixed >> button[type='submit']").click()

    expect(page.locator(f"text={acct_name}")).to_be_visible(timeout=5_000)
    expect(page.locator("text=Cash")).to_be_visible()


# 5. Login → create group → navigate all tabs → verify content changes
def test_group_tabs_navigation_journey(page: Page, test_user_credentials, _register_test_user):
    creds = test_user_credentials
    _quick_auth(page, creds["email"], creds["password"])

    group_name = f"Tabs Group {uuid.uuid4().hex[:6]}"

    page.click("button:has-text('+ New Group')")
    page.fill("input[placeholder='e.g. Vacation 2026']", group_name)
    page.click("button:has-text('Create')")

    page.wait_for_timeout(2000)
    page.goto(BASE)
    expect(page.locator("h1", has_text="My Groups")).to_be_visible(timeout=5_000)
    expect(page.locator(f"text={group_name}")).to_be_visible(timeout=5_000)
    page.locator(f"a:has-text('{group_name}')").first.click()
    expect(page.locator("h1", has_text=group_name)).to_be_visible(timeout=5_000)

    expect(page.locator("button:has-text('+ Add Expense')")).to_be_visible()
    expect(page.locator("text=No expenses yet")).to_be_visible()

    page.click("button:has-text('Balances')")
    expect(page.locator("h3:has-text('Balances')")).to_be_visible(timeout=5_000)

    page.click("button:has-text('Recurring')")
    page.wait_for_timeout(500)

    page.click("button:has-text('" + "Members" + "')")
    expect(page.locator(f"text={creds['display_name']}").first).to_be_visible(timeout=5_000)
    expect(page.locator("text=admin").first).to_be_visible()


# 6. Login → verify dashboard → logout → verify redirect → login again
def test_logout_and_relogin_journey(page: Page, test_user_credentials, _register_test_user):
    creds = test_user_credentials
    _quick_auth(page, creds["email"], creds["password"])

    expect(page.locator("h1", has_text="My Groups")).to_be_visible()

    page.click("button:has-text('Logout')")

    expect(page.locator("text=Sign in to your account")).to_be_visible(timeout=5_000)

    page.goto(BASE)
    expect(page.locator("text=Sign in to your account")).to_be_visible(timeout=5_000)

    _login_ui(page, creds["email"], creds["password"])
    expect(page.locator("h1", has_text="My Groups")).to_be_visible()


# 7. Wrong password → error → correct login → dashboard
def test_invalid_credentials_then_success_journey(page: Page, test_user_credentials, _register_test_user):
    creds = test_user_credentials
    page.goto(f"{BASE}/login")

    page.fill("#email", creds["email"])
    page.fill("#password", "WrongPassword999!")
    page.click("button:has-text('Sign in')")

    page.wait_for_timeout(2000)
    expect(page.locator("text=Sign in to your account")).to_be_visible(timeout=5_000)

    expect(page.locator("text=Sign in to your account")).to_be_visible()

    page.fill("#email", creds["email"])
    page.fill("#password", creds["password"])
    page.click("button:has-text('Sign in')")

    page.wait_for_timeout(1500)
    page.goto(BASE)
    expect(page.locator("h1", has_text="My Groups")).to_be_visible(timeout=10_000)


# 8. Unauthenticated user → try multiple protected routes → all redirect to login
def test_unauthenticated_redirects_journey(page: Page):
    page.goto(BASE)
    page.evaluate("localStorage.clear()")

    page.goto(BASE)
    expect(page).to_have_url(re.compile(r"/login"), timeout=10_000)
    expect(page.locator("text=Sign in to your account")).to_be_visible()

    page.goto(f"{BASE}/balances")
    expect(page).to_have_url(re.compile(r"/login"), timeout=10_000)

    page.goto(f"{BASE}/groups/00000000-0000-0000-0000-000000000000")
    expect(page).to_have_url(re.compile(r"/login"), timeout=10_000)

    page.click("text=Sign up")
    expect(page.locator("text=Create your account")).to_be_visible(timeout=5_000)
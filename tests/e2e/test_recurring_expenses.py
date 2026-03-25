import random
import time
from datetime import date

from playwright.sync_api import Page, expect, TimeoutError as PlaywrightTimeoutError

BASE_URL = "http://localhost:3000"


def _login(page: Page, email: str, password: str) -> None:
    page.goto(f"{BASE_URL}/login")
    page.fill('input[id="email"]', email)
    page.fill('input[id="password"]', password)
    page.click('button[type="submit"]')
    page.wait_for_url(f"{BASE_URL}/")


def _create_group_and_open(page: Page) -> str:
    group_name = f"Recurring Group {random.randint(1, 100000)}"
    page.click('button:has-text("+ New Group")')
    page.fill('input[placeholder="e.g. Vacation 2026"]', group_name)
    page.click('button:has-text("Create")')

    expect(page.locator("text=Group created!")).to_be_visible(timeout=10000)
    found = False
    for _ in range(4):
        page.goto(f"{BASE_URL}/")
        link = page.locator("a", has_text=group_name).first
        try:
            expect(link).to_be_visible(timeout=4000)
            link.click()
            found = True
            break
        except PlaywrightTimeoutError:
            continue

    assert found, f"Created group '{group_name}' not visible on dashboard"
    expect(page.locator("h1", has_text=group_name)).to_be_visible(timeout=10000)
    return group_name


def _open_recurring_tab(page: Page) -> None:
    page.click('button:has-text("Recurring")')
    expect(page.locator('button:has-text("+ Add Recurring Expense")')).to_be_visible()


def _open_recurring_modal(page: Page):
    page.click('button:has-text("+ Add Recurring Expense")')
    modal = page.locator("div.fixed.inset-0").last
    expect(modal.locator('h2:has-text("New Recurring Expense")')).to_be_visible()
    return modal


def _fill_and_submit_recurring(
    modal,
    description: str,
    amount: str,
    currency: str = "PLN",
    split_type: str = "equal",
    interval: str = "monthly",
    day_of_month: str = "1",
) -> None:
    modal.locator("input").nth(0).fill(description)
    modal.locator("input[type='number'][step='0.01'][min='0.01']").fill(amount)
    modal.locator("select").nth(0).select_option(currency)
    modal.locator("select").nth(1).select_option(split_type)
    modal.locator("select").nth(2).select_option(interval)

    if interval == "monthly":
        modal.locator("input[type='number'][min='1'][max='28']").fill(day_of_month)

    modal.locator("input[type='date']").fill(date.today().isoformat())
    modal.locator('button:has-text("Create")').click()


def _find_recurring_item(page: Page, description: str):
    for _ in range(4):
        item = page.locator("div.rounded-xl.border.bg-white", has_text=description).first
        try:
            expect(item).to_be_visible(timeout=4000)
            return item
        except PlaywrightTimeoutError:
            page.reload()
            _open_recurring_tab(page)
    raise AssertionError(f"Recurring item '{description}' not visible")


def _auth_headers(page: Page) -> dict[str, str]:
    token = page.evaluate("localStorage.getItem('token')")
    assert token, "Auth token not found in localStorage"
    return {"Authorization": f"Bearer {token}"}


def _current_group_id(page: Page) -> str:
    assert "/groups/" in page.url, f"Unexpected URL for group page: {page.url}"
    return page.url.split("/groups/")[1].split("?")[0]


def _wait_for_recurring_in_api(page: Page, group_id: str, description: str, timeout_seconds: int = 20):
    deadline = time.time() + timeout_seconds
    while time.time() < deadline:
        response = page.request.get(
            f"{BASE_URL}/api/groups/{group_id}/recurring-expenses/",
            headers=_auth_headers(page),
        )
        assert response.status == 200, f"Unexpected status while polling recurring list: {response.status}"
        items = response.json()
        for item in items:
            if item.get("description") == description:
                return item
        page.wait_for_timeout(1000)
    raise AssertionError(f"Recurring item '{description}' not found via API after {timeout_seconds}s")


def _wait_until_recurring_absent_in_api(
    page: Page,
    group_id: str,
    description: str,
    timeout_seconds: int = 20,
) -> None:
    deadline = time.time() + timeout_seconds
    while time.time() < deadline:
        response = page.request.get(
            f"{BASE_URL}/api/groups/{group_id}/recurring-expenses/",
            headers=_auth_headers(page),
        )
        assert response.status == 200, f"Unexpected status while polling recurring list: {response.status}"
        items = response.json()
        if all(item.get("description") != description for item in items):
            return
        page.wait_for_timeout(1000)
    raise AssertionError(f"Recurring item '{description}' still active after {timeout_seconds}s")


def _create_recurring_via_api(
    page: Page,
    group_id: str,
    description: str,
    amount: str,
    currency: str = "PLN",
    split_type: str = "equal",
    interval: str = "monthly",
    day_of_month: int | None = 1,
):
    payload = {
        "description": description,
        "amount": amount,
        "currency": currency,
        "split_type": split_type,
        "interval": interval,
        "day_of_month": day_of_month if interval == "monthly" else None,
        "start_date": date.today().isoformat(),
    }
    response = page.request.post(
        f"{BASE_URL}/api/groups/{group_id}/recurring-expenses/",
        data=payload,
        headers=_auth_headers(page),
    )
    assert response.status == 201, f"Create recurring via API failed: {response.status} {response.text()}"
    return response.json()


def test_tc_rec_001_create_monthly_recurring_success(page: Page, test_users_credentials, _register_test_users):
    user1 = test_users_credentials["user1"]
    _login(page, user1["email"], user1["password"])
    _create_group_and_open(page)
    group_id = _current_group_id(page)
    _open_recurring_tab(page)

    modal = _open_recurring_modal(page)
    _fill_and_submit_recurring(
        modal=modal,
        description="Netflix",
        amount="60.00",
        currency="PLN",
        split_type="equal",
        interval="monthly",
        day_of_month="12",
    )

    expect(page.locator("text=Recurring expense created")).to_be_visible()
    item = _wait_for_recurring_in_api(page, group_id, "Netflix")
    assert item["currency"] == "PLN"
    assert item["interval"] == "monthly"
    assert item["day_of_month"] == 12


def test_tc_rec_002_create_weekly_recurring_success(page: Page, test_users_credentials, _register_test_users):
    user1 = test_users_credentials["user1"]
    _login(page, user1["email"], user1["password"])
    _create_group_and_open(page)
    group_id = _current_group_id(page)
    _open_recurring_tab(page)

    modal = _open_recurring_modal(page)
    _fill_and_submit_recurring(
        modal=modal,
        description="Cleaning service",
        amount="120.00",
        currency="USD",
        split_type="percent",
        interval="weekly",
    )

    expect(page.locator("text=Recurring expense created")).to_be_visible()
    item = _wait_for_recurring_in_api(page, group_id, "Cleaning service")
    assert item["currency"] == "USD"
    assert item["interval"] == "weekly"
    assert item["split_type"] == "percent"


def test_tc_rec_003_deactivate_recurring_success(page: Page, test_users_credentials, _register_test_users):
    user1 = test_users_credentials["user1"]
    _login(page, user1["email"], user1["password"])
    _create_group_and_open(page)
    group_id = _current_group_id(page)

    _create_recurring_via_api(
        page,
        group_id=group_id,
        description="Spotify",
        amount="30.00",
        interval="monthly",
    )

    _open_recurring_tab(page)

    item = _find_recurring_item(page, "Spotify")
    item.locator('button:has-text("Deactivate")').click()

    expect(page.locator("text=Recurring expense deactivated")).to_be_visible()
    _wait_until_recurring_absent_in_api(page, group_id, "Spotify")


def test_tc_rec_004_cancel_recurring_modal(page: Page, test_users_credentials, _register_test_users):
    user1 = test_users_credentials["user1"]
    _login(page, user1["email"], user1["password"])
    _create_group_and_open(page)
    _open_recurring_tab(page)

    expect(page.locator("text=No recurring expenses yet")).to_be_visible()

    modal = _open_recurring_modal(page)
    modal.locator('button:has-text("Cancel")').click()

    expect(page.locator('h2:has-text("New Recurring Expense")')).not_to_be_visible()
    expect(page.locator("text=No recurring expenses yet")).to_be_visible()


def test_tc_rec_005_create_recurring_empty_description(page: Page, test_users_credentials, _register_test_users):
    user1 = test_users_credentials["user1"]
    _login(page, user1["email"], user1["password"])
    _create_group_and_open(page)
    _open_recurring_tab(page)

    modal = _open_recurring_modal(page)
    modal.locator("input[type='number'][step='0.01'][min='0.01']").fill("40.00")
    modal.locator('button:has-text("Create")').click()

    validation_message = modal.locator("input").nth(0).evaluate("node => node.validationMessage")
    assert validation_message.strip() != ""
    expect(page.locator("text=Recurring expense created")).not_to_be_visible()


def test_tc_rec_006_create_recurring_negative_amount(page: Page, test_users_credentials, _register_test_users):
    user1 = test_users_credentials["user1"]
    _login(page, user1["email"], user1["password"])
    _create_group_and_open(page)
    _open_recurring_tab(page)

    modal = _open_recurring_modal(page)
    modal.locator("input").nth(0).fill("Internet")
    modal.locator("input[type='number'][step='0.01'][min='0.01']").fill("-10.00")
    modal.locator('button:has-text("Create")').click()

    validation_message = modal.locator("input[type='number'][step='0.01'][min='0.01']").evaluate(
        "node => node.validationMessage"
    )
    assert validation_message.strip() != ""
    assert "0.01" in validation_message or "0,01" in validation_message
    expect(page.locator("text=Recurring expense created")).not_to_be_visible()


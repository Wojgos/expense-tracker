import random
from decimal import Decimal

from playwright.sync_api import Page, expect
from .conftest import (
    _account_card,
    _balances_register_and_login,
    _create_account_via_api,
    _create_account_via_ui,
    _create_transaction_via_ui,
    _get_accounts_via_api,
)


def test_tc_acc_bal_001_empty_state_for_new_user(page: Page):
    _balances_register_and_login(page)

    expect(page.locator("text=No accounts yet")).to_be_visible()
    expect(page.locator("text=Create your first account to start tracking balances.")).to_be_visible()
    expect(page.locator('button:has-text("Add First Account")')).to_be_visible()


def test_tc_acc_bal_002_create_first_account_from_empty_state(page: Page):
    _balances_register_and_login(page)
    account_name = f"Wallet {random.randint(1, 100000)}"

    _create_account_via_ui(page, account_name, "150.00", trigger_text="Add First Account")

    expect(page.locator("text=No accounts yet")).not_to_be_visible()
    expect(_account_card(page, account_name)).to_contain_text("Cash")

    accounts = _get_accounts_via_api(page)
    created = next(account for account in accounts if account["name"] == account_name)
    assert created["currency"] == "PLN"
    assert Decimal(str(created["balance"])) == Decimal("150.00")


def test_tc_acc_bal_003_create_second_account_from_header_button(page: Page):
    _balances_register_and_login(page)
    first_account = f"Main Wallet {random.randint(1, 100000)}"
    second_account = f"Savings {random.randint(1, 100000)}"

    _create_account_via_ui(page, first_account, "120.00", trigger_text="Add First Account")
    _create_account_via_ui(page, second_account, "80.00", account_type="Savings", trigger_text="Add Account")

    expect(_account_card(page, first_account)).to_be_visible()
    expect(_account_card(page, second_account)).to_be_visible()

    account_names = {account["name"] for account in _get_accounts_via_api(page)}
    assert first_account in account_names
    assert second_account in account_names


def test_tc_acc_bal_004_create_account_with_custom_currency(page: Page):
    _balances_register_and_login(page)
    account_name = f"Euro Wallet {random.randint(1, 100000)}"

    _create_account_via_ui(
        page,
        account_name=account_name,
        balance="321.50",
        currency="EUR",
        account_type="Savings",
        trigger_text="Add First Account",
    )

    card = _account_card(page, account_name)
    expect(card).to_contain_text("Savings")
    expect(card).to_contain_text("€")

    accounts = _get_accounts_via_api(page)
    created = next(account for account in accounts if account["name"] == account_name)
    assert created["currency"] == "EUR"
    assert Decimal(str(created["balance"])) == Decimal("321.50")


def test_tc_acc_bal_005_total_balance_updates_after_multiple_pln_accounts(page: Page):
    _balances_register_and_login(page)

    _create_account_via_api(page, f"Wallet {random.randint(1, 100000)}", "100.00")
    _create_account_via_api(page, f"Card {random.randint(1, 100000)}", "250.00")

    page.reload()
    expect(page.locator("text=Your Accounts")).to_be_visible(timeout=10000)
    expect(page.locator("h1")).to_contain_text("350")


def test_tc_acc_bal_006_privacy_mode_hides_total_and_account_amounts(page: Page):
    _balances_register_and_login(page)
    account_name = f"Private Wallet {random.randint(1, 100000)}"

    _create_account_via_api(page, account_name, "123.45")
    page.reload()
    expect(_account_card(page, account_name)).to_be_visible(timeout=10000)

    page.locator("button.rounded-full").click()

    expect(page.locator("h1")).to_contain_text("*** PLN")
    expect(_account_card(page, account_name)).to_contain_text("*** PLN")


def test_tc_acc_bal_007_privacy_mode_toggle_restores_amounts(page: Page):
    _balances_register_and_login(page)
    account_name = f"Visible Wallet {random.randint(1, 100000)}"

    _create_account_via_api(page, account_name, "123.45")
    page.reload()
    expect(_account_card(page, account_name)).to_be_visible(timeout=10000)

    privacy_button = page.locator("button.rounded-full")
    privacy_button.click()
    expect(page.locator("h1")).to_contain_text("*** PLN")

    privacy_button.click()
    expect(page.locator("h1")).not_to_contain_text("*** PLN")
    expect(_account_card(page, account_name)).not_to_contain_text("*** PLN")
    expect(_account_card(page, account_name)).to_contain_text("123")


def test_tc_acc_bal_008_add_income_transaction_increases_account_balance(page: Page):
    _balances_register_and_login(page)
    account_name = f"Income Wallet {random.randint(1, 100000)}"

    _create_account_via_api(page, account_name, "100.00")
    page.reload()

    _create_transaction_via_ui(
        page,
        account_name=account_name,
        amount="50.00",
        description="Salary",
        transaction_type="Income",
    )

    accounts = _get_accounts_via_api(page)
    account = next(item for item in accounts if item["name"] == account_name)
    assert Decimal(str(account["balance"])) == Decimal("150.00")
    expect(_account_card(page, account_name)).to_contain_text("150")


def test_tc_acc_bal_009_add_expense_transaction_decreases_account_balance(page: Page):
    _balances_register_and_login(page)
    account_name = f"Expense Wallet {random.randint(1, 100000)}"

    _create_account_via_api(page, account_name, "100.00")
    page.reload()

    _create_transaction_via_ui(
        page,
        account_name=account_name,
        amount="40.00",
        description="Groceries",
        transaction_type="Expense",
    )

    accounts = _get_accounts_via_api(page)
    account = next(item for item in accounts if item["name"] == account_name)
    assert Decimal(str(account["balance"])) == Decimal("60.00")
    expect(_account_card(page, account_name)).to_contain_text("60")


def test_tc_acc_bal_010_delete_account_removes_it_from_list(page: Page):
    _balances_register_and_login(page)
    account_name = f"Delete Wallet {random.randint(1, 100000)}"

    _create_account_via_api(page, account_name, "100.00")
    page.reload()
    card = _account_card(page, account_name)
    expect(card).to_be_visible(timeout=10000)

    page.once("dialog", lambda dialog: dialog.accept())
    card.locator('button:has-text("Delete")').click()

    expect(_account_card(page, account_name)).not_to_be_visible(timeout=10000)
    expect(page.locator("text=No accounts yet")).to_be_visible()
    assert _get_accounts_via_api(page) == []

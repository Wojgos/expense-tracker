import pytest
from playwright.sync_api import Page, expect
import random


def test_tc001_add_expense_equal_split(page: Page, test_users_credentials, _register_test_users):
    # Login as user1
    user1_creds = test_users_credentials["user1"]
    page.goto("http://localhost:3000/login")
    page.fill('input[id="email"]', user1_creds["email"])
    page.fill('input[id="password"]', user1_creds["password"])
    page.click('button[type="submit"]')
    page.wait_for_url("http://localhost:3000/")

    # Create a group
    page.click('button:has-text("+ New Group")')
    group_name = f"Test Group {random.randint(1, 10000)}"
    page.fill('input[placeholder="e.g. Vacation 2026"]', group_name)
    page.click('button:has-text("Create")')
    page.click(f'a:has-text("{group_name}")')

    # Add member user2
    user2_creds = test_users_credentials["user2"]
    page.click('button:has-text("Members")')
    page.click('button:has-text("+ Add member")')
    page.fill('input[placeholder="Enter user email..."]', user2_creds["email"])
    page.click('button:has-text("Search")')
    page.wait_for_selector(f'text={user2_creds["display_name"]}')
    page.locator('button:has-text("Add")').nth(1).click()
    page.wait_for_selector(f'text={user2_creds["display_name"]} added to the group')

    # Go back to expenses
    page.click('button:has-text("Expenses")')
    page.click('button:has-text("+ Add Expense")')
    page.fill('input[placeholder="e.g. Dinner"]', "Obiad")
    page.fill('input[type="number"]', "100.00")
    page.locator('input[type="checkbox"]').nth(1).check()
    page.locator('button:has-text("Add Expense")').nth(1).click()

    # Check success
    page.wait_for_selector('text=Expense added!')
    expect(page.locator('text=Expense added!')).to_be_visible()

    # Check modal closed
    expect(page.locator('div[role="dialog"]')).not_to_be_visible()
    expect(page.locator('span:has-text("Obiad")')).to_be_visible()

    # Check balances
    page.click('button:has-text("Balances")')
    expect(page.locator('text=+50.00')).to_be_visible()
    expect(page.locator('text=-50.00')).to_be_visible()


def test_tc002_add_expense_exact_split(page: Page, test_users_credentials, _register_test_users):
    # Login as user1
    user1_creds = test_users_credentials["user1"]
    page.goto("http://localhost:3000/login")
    page.fill('input[id="email"]', user1_creds["email"])
    page.fill('input[id="password"]', user1_creds["password"])
    page.click('button[type="submit"]')
    page.wait_for_url("http://localhost:3000/")

    # Create a group
    page.click('button:has-text("+ New Group")')
    group_name = f"Test Group {random.randint(1, 10000)}"
    page.fill('input[placeholder="e.g. Vacation 2026"]', group_name)
    page.click('button:has-text("Create")')
    page.click(f'a:has-text("{group_name}")')

    # Add member user2
    user2_creds = test_users_credentials["user2"]
    page.click('button:has-text("Members")')
    page.click('button:has-text("+ Add member")')
    page.fill('input[placeholder="Enter user email..."]', user2_creds["email"])
    page.click('button:has-text("Search")')
    page.wait_for_selector(f'text={user2_creds["display_name"]}')
    page.locator('button:has-text("Add")').nth(1).click()
    page.wait_for_selector(f'text={user2_creds["display_name"]} added to the group')

    # Go back to expenses
    page.click('button:has-text("Expenses")')
    page.click('button:has-text("+ Add Expense")')
    page.fill('input[placeholder="e.g. Dinner"]', "Obiad")
    page.fill('input[type="number"]', "150.00")
    page.locator('input[type="checkbox"]').nth(1).check()
    page.click('button:has-text("Exact")')
    page.locator('input[type="number"][step="0.01"][min="0"]').nth(0).fill("50.00")
    page.locator('input[type="number"][step="0.01"][min="0"]').nth(1).fill("100.00")
    page.locator('button:has-text("Add Expense")').nth(1).click()

    # Check success
    page.wait_for_selector('text=Expense added!')
    expect(page.locator('text=Expense added!')).to_be_visible()

    # Check modal closed
    expect(page.locator('div[role="dialog"]')).not_to_be_visible()
    expect(page.locator('span:has-text("Obiad")')).to_be_visible()

    # Check balances
    page.click('button:has-text("Balances")')
    expect(page.locator('text=+100.00')).to_be_visible()
    expect(page.locator('text=-100.00')).to_be_visible()


def test_tc003_add_expense_percent_split(page: Page, test_users_credentials, _register_test_users):
    # Login as user1
    user1_creds = test_users_credentials["user1"]
    page.goto("http://localhost:3000/login")
    page.fill('input[id="email"]', user1_creds["email"])
    page.fill('input[id="password"]', user1_creds["password"])
    page.click('button[type="submit"]')
    page.wait_for_url("http://localhost:3000/")

    # Create a group
    page.click('button:has-text("+ New Group")')
    group_name = f"Test Group {random.randint(1, 10000)}"
    page.fill('input[placeholder="e.g. Vacation 2026"]', group_name)
    page.click('button:has-text("Create")')
    page.click(f'a:has-text("{group_name}")')

    # Add member user2
    user2_creds = test_users_credentials["user2"]
    page.click('button:has-text("Members")')
    page.click('button:has-text("+ Add member")')
    page.fill('input[placeholder="Enter user email..."]', user2_creds["email"])
    page.click('button:has-text("Search")')
    page.wait_for_selector(f'text={user2_creds["display_name"]}')
    page.locator('button:has-text("Add")').nth(1).click()
    page.wait_for_selector(f'text={user2_creds["display_name"]} added to the group')
    page.click('button:has-text("Expenses")')

    # Click Add Expense
    page.click('button:has-text("+ Add Expense")')
    page.fill('input[placeholder="e.g. Dinner"]', "Obiad")
    page.fill('input[type="number"]', "200.00")
    page.locator('input[type="checkbox"]').nth(1).check()
    page.click('button:has-text("Percent")')
    page.locator('input[type="number"][step="0.01"][min="0"]').nth(0).fill("30")
    page.locator('input[type="number"][step="0.01"][min="0"]').nth(1).fill("70")
    page.locator('button:has-text("Add Expense")').nth(1).click()

    # Check success
    page.wait_for_selector('text=Expense added!')
    expect(page.locator('text=Expense added!')).to_be_visible()

    # Check modal closed
    expect(page.locator('div[role="dialog"]')).not_to_be_visible()
    expect(page.locator('span:has-text("Obiad")')).to_be_visible()

    # Check balances
    page.click('button:has-text("Balances")')
    expect(page.locator('text=+140.00')).to_be_visible()
    expect(page.locator('text=-140.00')).to_be_visible()


def test_tc004_add_expense_shares_split(page: Page, test_users_credentials, _register_test_users):
    # Login as user1
    user1_creds = test_users_credentials["user1"]
    page.goto("http://localhost:3000/login")
    page.fill('input[id="email"]', user1_creds["email"])
    page.fill('input[id="password"]', user1_creds["password"])
    page.click('button[type="submit"]')
    page.wait_for_url("http://localhost:3000/")

    # Create a group
    page.click('button:has-text("+ New Group")')
    group_name = f"Test Group {random.randint(1, 10000)}"
    page.fill('input[placeholder="e.g. Vacation 2026"]', group_name)
    page.click('button:has-text("Create")')

    # Navigate to the created group
    page.click(f'a:has-text("{group_name}")')
    page.click('button:has-text("Members")')
    page.click('button:has-text("+ Add member")')
    user2_creds = test_users_credentials["user2"]
    page.fill('input[placeholder="Enter user email..."]', user2_creds["email"])
    page.click('button:has-text("Search")')
    page.wait_for_selector(f'text={user2_creds["display_name"]}')
    page.locator('button:has-text("Add")').nth(1).click()
    page.wait_for_selector(f'text={user2_creds["display_name"]} added to the group')

    # Add member user3
    user3_creds = test_users_credentials["user3"]
    page.click('button:has-text("+ Add member")')
    page.fill('input[placeholder="Enter user email..."]', user3_creds["email"])
    page.click('button:has-text("Search")')
    page.wait_for_selector(f'text={user3_creds["display_name"]}')
    page.locator('button:has-text("Add")').nth(1).click()
    page.wait_for_selector(f'text={user3_creds["display_name"]} added to the group')

    # Go back to expenses
    page.click('button:has-text("Expenses")')
    page.click('button:has-text("+ Add Expense")')
    page.fill('input[placeholder="e.g. Dinner"]', "Obiad")
    page.fill('input[type="number"]', "120.00")
    page.locator('input[type="checkbox"]').nth(1).check()
    page.locator('input[type="checkbox"]').nth(2).check()
    page.click('button:has-text("Shares")')
    page.locator('input[type="number"][step="1"][min="1"]').nth(0).fill("1")
    page.locator('input[type="number"][step="1"][min="1"]').nth(1).fill("2")
    page.locator('input[type="number"][step="1"][min="1"]').nth(2).fill("1")
    page.locator('button:has-text("Add Expense")').nth(1).click()

    # Check success
    page.wait_for_selector('text=Expense added!')
    expect(page.locator('text=Expense added!')).to_be_visible()

    # Check modal closed
    expect(page.locator('div[role="dialog"]')).not_to_be_visible()
    expect(page.locator('span:has-text("Obiad")')).to_be_visible()

    # Check balances
    page.click('button:has-text("Balances")')
    expect(page.locator('text=+90.00')).to_be_visible()
    expect(page.locator('text=-60.00')).to_be_visible()
    expect(page.locator('text=-30.00')).to_be_visible()


def test_tc005_add_expense_negative_amount(page: Page, test_users_credentials, _register_test_users):
    # Login as user1
    user1_creds = test_users_credentials["user1"]
    page.goto("http://localhost:3000/login")
    page.fill('input[id="email"]', user1_creds["email"])
    page.fill('input[id="password"]', user1_creds["password"])
    page.click('button[type="submit"]')
    page.wait_for_url("http://localhost:3000/")

    # Create a group
    page.click('button:has-text("+ New Group")')
    group_name = f"Test Group {random.randint(1, 10000)}"
    page.fill('input[placeholder="e.g. Vacation 2026"]', group_name)
    page.click('button:has-text("Create")')
    page.click(f'a:has-text("{group_name}")')

    # Add member user2
    user2_creds = test_users_credentials["user2"]
    page.click('button:has-text("Members")')
    page.click('button:has-text("+ Add member")')
    page.fill('input[placeholder="Enter user email..."]', user2_creds["email"])
    page.click('button:has-text("Search")')
    page.wait_for_selector(f'text={user2_creds["display_name"]}')
    page.locator('button:has-text("Add")').nth(1).click()
    page.wait_for_selector(f'text={user2_creds["display_name"]} added to the group')

    # Go back to expenses
    page.click('button:has-text("Expenses")')
    page.click('button:has-text("+ Add Expense")')
    page.fill('input[placeholder="e.g. Dinner"]', "Obiad")
    page.fill('input[type="number"]', "-50.00")
    page.locator('button:has-text("Add Expense")').nth(1).click()

    validation_message = page.locator('input[type="number"]').evaluate("node => node.validationMessage")
    assert validation_message == "Wartość nie może być mniejsza niż 0,01."
    expect(page.locator('text=Expense added!')).not_to_be_visible()


def test_tc006_add_expense_no_participants(page: Page, test_users_credentials, _register_test_users):
    # Login as user1
    user1_creds = test_users_credentials["user1"]
    page.goto("http://localhost:3000/login")
    page.fill('input[id="email"]', user1_creds["email"])
    page.fill('input[id="password"]', user1_creds["password"])
    page.click('button[type="submit"]')
    page.wait_for_url("http://localhost:3000/")

    # Create a group
    page.click('button:has-text("+ New Group")')
    group_name = f"Test Group {random.randint(1, 10000)}"
    page.fill('input[placeholder="e.g. Vacation 2026"]', group_name)
    page.click('button:has-text("Create")')
    page.click(f'a:has-text("{group_name}")')

    # Add member user2
    user2_creds = test_users_credentials["user2"]
    page.click('button:has-text("Members")')
    page.click('button:has-text("+ Add member")')
    page.fill('input[placeholder="Enter user email..."]', user2_creds["email"])
    page.click('button:has-text("Search")')
    page.wait_for_selector(f'text={user2_creds["display_name"]}')
    page.locator('button:has-text("Add")').nth(1).click()
    page.wait_for_selector(f'text={user2_creds["display_name"]} added to the group')

    # Go back to expenses
    page.click('button:has-text("Expenses")')
    page.click('button:has-text("+ Add Expense")')

    # Fill modal
    page.fill('input[placeholder="e.g. Dinner"]', "Obiad")
    page.fill('input[type="number"]', "100.00")
    page.locator('input[type="checkbox"]').nth(0).uncheck()
    page.locator('input[type="checkbox"]').nth(1).uncheck()
    page.locator('button:has-text("Add Expense")').nth(1).click()

    # Check failure: modal remains open, no success message
    expect(page.locator('h2:has-text("Add Expense")')).to_be_visible()
    expect(page.locator('text=Expense added!')).not_to_be_visible()


def test_tc007_add_expense_future_date(page: Page, test_users_credentials, _register_test_users):
    # Login as user1
    user1_creds = test_users_credentials["user1"]
    page.goto("http://localhost:3000/login")
    page.fill('input[id="email"]', user1_creds["email"])
    page.fill('input[id="password"]', user1_creds["password"])
    page.click('button[type="submit"]')
    page.wait_for_url("http://localhost:3000/")

    # Create a group
    page.click('button:has-text("+ New Group")')
    group_name = f"Test Group {random.randint(1, 10000)}"
    page.fill('input[placeholder="e.g. Vacation 2026"]', group_name)
    page.click('button:has-text("Create")')
    page.click(f'a:has-text("{group_name}")')

    # Add member user2
    user2_creds = test_users_credentials["user2"]
    page.click('button:has-text("Members")')
    page.click('button:has-text("+ Add member")')
    page.fill('input[placeholder="Enter user email..."]', user2_creds["email"])
    page.click('button:has-text("Search")')
    page.wait_for_selector(f'text={user2_creds["display_name"]}')
    page.locator('button:has-text("Add")').nth(1).click()
    page.wait_for_selector(f'text={user2_creds["display_name"]} added to the group')
    page.click('button:has-text("Expenses")')

    # Click Add Expense
    page.click('button:has-text("+ Add Expense")')
    page.fill('input[placeholder="e.g. Dinner"]', "Przyszły wydatek")
    page.fill('input[type="number"]', "75.00")
    page.fill('input[type="date"]', "2027-04-01")
    page.locator('input[type="checkbox"]').nth(1).check()
    page.locator('button:has-text("Add Expense")').nth(1).click()

    # Check success
    page.wait_for_selector('text=Expense added!')
    expect(page.locator('text=Expense added!')).to_be_visible()

    # Check modal closed
    expect(page.locator('h2:has-text("Add Expense")')).not_to_be_visible()
    expect(page.locator('span:has-text("Przyszły wydatek")')).to_be_visible()


def test_tc008_add_expense_empty_description(page: Page, test_users_credentials, _register_test_users):
    # Login as user1
    user1_creds = test_users_credentials["user1"]
    page.goto("http://localhost:3000/login")
    page.fill('input[id="email"]', user1_creds["email"])
    page.fill('input[id="password"]', user1_creds["password"])
    page.click('button[type="submit"]')
    page.wait_for_url("http://localhost:3000/")

    # Create a group
    page.click('button:has-text("+ New Group")')
    group_name = f"Test Group {random.randint(1, 10000)}"
    page.fill('input[placeholder="e.g. Vacation 2026"]', group_name)
    page.click('button:has-text("Create")')
    page.click(f'a:has-text("{group_name}")')

    # Go to expenses and open add expense modal
    page.click('button:has-text("Expenses")')
    page.click('button:has-text("+ Add Expense")')

    # Leave description empty
    # Fill amount
    page.fill('input[type="number"]', "50.00")
    # Select user1 as participant (should be checked by default)
    page.locator('input[type="checkbox"]').nth(0).check()
    # Click Add Expense
    page.locator('button:has-text("Add Expense")').nth(1).click()

    # Check validation message appears
    validation_message = page.locator('input[placeholder="e.g. Dinner"]').evaluate("node => node.validationMessage")
    assert validation_message == "Wypełnij to pole."

    # Check modal remains open
    expect(page.locator('h2:has-text("Add Expense")')).to_be_visible()

    # Check no success message
    expect(page.locator('text=Expense added!')).not_to_be_visible()

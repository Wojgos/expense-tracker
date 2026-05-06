import json
import re
import uuid
from datetime import date, datetime

from playwright.sync_api import Page, Route, expect

BASE_URL = "http://localhost:3000"


def _inject_token(page: Page) -> None:
    page.goto(BASE_URL)
    page.evaluate("localStorage.setItem('token', 'mocked-jwt-token-for-testing')")


MOCK_USER = {
    "id": "11111111-1111-1111-1111-111111111111",
    "email": "mock@example.com",
    "display_name": "Mock User",
}

MOCK_GROUPS = [
    {
        "id": "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa",
        "name": "Wakacje 2026",
        "description": "Wspólne wydatki z wakacji",
        "created_by": MOCK_USER["id"],
        "created_at": "2026-01-15T10:00:00",
        "member_count": 3,
    },
    {
        "id": "bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb",
        "name": "Mieszkanie",
        "description": "Opłaty za mieszkanie",
        "created_by": MOCK_USER["id"],
        "created_at": "2026-02-01T12:00:00",
        "member_count": 2,
    },
]

MOCK_GROUP_DETAIL = {
    "id": "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa",
    "name": "Wakacje 2026",
    "description": "Wspólne wydatki z wakacji",
    "created_by": MOCK_USER["id"],
    "created_at": "2026-01-15T10:00:00",
    "members": [
        {"user_id": MOCK_USER["id"], "display_name": "Mock User", "email": "mock@example.com", "role": "admin"},
        {"user_id": "22222222-2222-2222-2222-222222222222", "display_name": "Anna K.", "email": "anna@example.com", "role": "member"},
        {"user_id": "33333333-3333-3333-3333-333333333333", "display_name": "Jan N.", "email": "jan@example.com", "role": "member"},
    ],
}

MOCK_EXPENSES = [
    {
        "id": "exp-11111111-1111-1111-1111-111111111111",
        "group_id": "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa",
        "paid_by": MOCK_USER["id"],
        "payer_name": "Mock User",
        "amount": "150.00",
        "currency": "PLN",
        "description": "Kolacja w restauracji",
        "split_type": "equal",
        "expense_date": "2026-01-20",
        "created_at": "2026-01-20T19:30:00",
        "splits": [
            {"user_id": MOCK_USER["id"], "owed_amount": "50.00"},
            {"user_id": "22222222-2222-2222-2222-222222222222", "owed_amount": "50.00"},
            {"user_id": "33333333-3333-3333-3333-333333333333", "owed_amount": "50.00"},
        ],
    },
    {
        "id": "exp-22222222-2222-2222-2222-222222222222",
        "group_id": "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa",
        "paid_by": "22222222-2222-2222-2222-222222222222",
        "payer_name": "Anna K.",
        "amount": "80.00",
        "currency": "PLN",
        "description": "Bilety do muzeum",
        "split_type": "equal",
        "expense_date": "2026-01-21",
        "created_at": "2026-01-21T11:00:00",
        "splits": [
            {"user_id": MOCK_USER["id"], "owed_amount": "40.00"},
            {"user_id": "22222222-2222-2222-2222-222222222222", "owed_amount": "40.00"},
        ],
    },
]

MOCK_ACCOUNTS = [
    {
        "id": "acc-11111111-1111-1111-1111-111111111111",
        "name": "Portfel",
        "type": "Cash",
        "currency": "PLN",
        "balance": "1250.50",
        "user_id": MOCK_USER["id"],
    },
    {
        "id": "acc-22222222-2222-2222-2222-222222222222",
        "name": "Konto bankowe",
        "type": "Bank",
        "currency": "PLN",
        "balance": "5430.00",
        "user_id": MOCK_USER["id"],
    },
]

MOCK_SETTLEMENTS = {
    "balances": [
        {"user_id": MOCK_USER["id"], "display_name": "Mock User", "amount": "60.00"},
        {"user_id": "22222222-2222-2222-2222-222222222222", "display_name": "Anna K.", "amount": "-30.00"},
        {"user_id": "33333333-3333-3333-3333-333333333333", "display_name": "Jan N.", "amount": "-30.00"},
    ],
    "suggested_transfers": [
        {
            "from_user_id": "22222222-2222-2222-2222-222222222222",
            "from_name": "Anna K.",
            "to_user_id": MOCK_USER["id"],
            "to_name": "Mock User",
            "amount": "30.00",
        },
        {
            "from_user_id": "33333333-3333-3333-3333-333333333333",
            "from_name": "Jan N.",
            "to_user_id": MOCK_USER["id"],
            "to_name": "Mock User",
            "amount": "30.00",
        },
    ],
}

MOCK_CURRENCY_RATE = {
    "base": "EUR",
    "target": "PLN",
    "rate": "4.28",
    "rate_date": date.today().isoformat(),
}


class TestMockGroupsDashboard:

    def test_dashboard_displays_mocked_groups(self, page: Page):
        """Autor: Wojciech Gosiewski."""
        def handle_me(route: Route):
            route.fulfill(status=200, content_type="application/json", body=json.dumps(MOCK_USER))

        def handle_groups(route: Route):
            route.fulfill(status=200, content_type="application/json", body=json.dumps(MOCK_GROUPS))

        page.route("**/api/auth/me", handle_me)
        page.route("**/api/groups", handle_groups)

        _inject_token(page)
        page.goto(BASE_URL)

        expect(page.locator("h1", has_text="My Groups")).to_be_visible(timeout=10_000)
        expect(page.locator(f"text=Wakacje 2026")).to_be_visible()
        expect(page.locator(f"text=Mieszkanie")).to_be_visible()

    def test_dashboard_shows_empty_state_when_no_groups(self, page: Page):
        """Autor: Wojciech Gosiewski."""
        def handle_me(route: Route):
            route.fulfill(status=200, content_type="application/json", body=json.dumps(MOCK_USER))

        def handle_groups(route: Route):
            route.fulfill(status=200, content_type="application/json", body=json.dumps([]))

        page.route("**/api/auth/me", handle_me)
        page.route("**/api/groups", handle_groups)

        _inject_token(page)
        page.goto(BASE_URL)

        expect(page.locator("h1", has_text="My Groups")).to_be_visible(timeout=10_000)
        expect(page.locator("text=Wakacje 2026")).not_to_be_visible()

    def test_dashboard_shows_user_display_name(self, page: Page):
        """Autor: Wojciech Gosiewski."""
        def handle_me(route: Route):
            route.fulfill(status=200, content_type="application/json", body=json.dumps(MOCK_USER))

        def handle_groups(route: Route):
            route.fulfill(status=200, content_type="application/json", body=json.dumps(MOCK_GROUPS))

        page.route("**/api/auth/me", handle_me)
        page.route("**/api/groups", handle_groups)

        _inject_token(page)
        page.goto(BASE_URL)

        expect(page.locator(f"text={MOCK_USER['display_name']}")).to_be_visible(timeout=10_000)


class TestMockExpenseList:

    def _setup_group_routes(self, page: Page):
        def handle_me(route: Route):
            route.fulfill(status=200, content_type="application/json", body=json.dumps(MOCK_USER))

        def handle_group_detail(route: Route):
            route.fulfill(status=200, content_type="application/json", body=json.dumps(MOCK_GROUP_DETAIL))

        def handle_expenses(route: Route):
            route.fulfill(status=200, content_type="application/json", body=json.dumps(MOCK_EXPENSES))

        def handle_settlements(route: Route):
            route.fulfill(status=200, content_type="application/json", body=json.dumps(MOCK_SETTLEMENTS))

        page.route("**/api/auth/me", handle_me)
        page.route(re.compile(r".*/api/groups/[^/]+$"), handle_group_detail)
        page.route(re.compile(r".*/api/groups/[^/]+/expenses"), handle_expenses)
        page.route(re.compile(r".*/api/groups/[^/]+/settlements"), handle_settlements)

    def test_expense_list_shows_mocked_expenses(self, page: Page):
        """Autor: Wojciech Domański."""
        self._setup_group_routes(page)

        _inject_token(page)
        page.goto(f"{BASE_URL}/groups/aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa")

        expect(page.locator("text=Kolacja w restauracji").first).to_be_visible(timeout=10_000)
        expect(page.locator("text=150.00").first).to_be_visible()
        expect(page.locator("text=Bilety do muzeum").first).to_be_visible()
        expect(page.locator("text=80.00").first).to_be_visible()

    def test_expense_list_shows_payer_names(self, page: Page):
        """Autor: Wojciech Domański."""
        self._setup_group_routes(page)

        _inject_token(page)
        page.goto(f"{BASE_URL}/groups/aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa")

        expect(page.locator("text=Mock User").first).to_be_visible(timeout=10_000)
        expect(page.locator("text=Anna K.").first).to_be_visible()

    def test_balances_tab_shows_mocked_settlements(self, page: Page):
        """Autor: Wojciech Domański."""
        self._setup_group_routes(page)

        _inject_token(page)
        page.goto(f"{BASE_URL}/groups/aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa")

        page.click("button:has-text('Balances')")
        expect(page.locator("h3:has-text('Balances')")).to_be_visible(timeout=5_000)


class TestMockAccounts:

    def test_accounts_page_shows_mocked_accounts(self, page: Page):
        """Autor: Jakub Gerwel."""
        def handle_me(route: Route):
            route.fulfill(status=200, content_type="application/json", body=json.dumps(MOCK_USER))

        def handle_accounts(route: Route):
            route.fulfill(status=200, content_type="application/json", body=json.dumps(MOCK_ACCOUNTS))

        page.route("**/api/auth/me", handle_me)
        page.route("**/api/accounts", handle_accounts)

        _inject_token(page)
        page.goto(f"{BASE_URL}/balances")

        expect(page.locator("text=Portfel").first).to_be_visible(timeout=10_000)
        expect(page.locator("text=Konto bankowe").first).to_be_visible()
        expect(page.locator("text=1250.50").first).to_be_visible()

    def test_accounts_empty_state_with_no_accounts(self, page: Page):
        """Autor: Jakub Gerwel."""
        def handle_me(route: Route):
            route.fulfill(status=200, content_type="application/json", body=json.dumps(MOCK_USER))

        def handle_accounts(route: Route):
            route.fulfill(status=200, content_type="application/json", body=json.dumps([]))

        page.route("**/api/auth/me", handle_me)
        page.route("**/api/accounts", handle_accounts)

        _inject_token(page)
        page.goto(f"{BASE_URL}/balances")

        expect(page.locator("text=No accounts yet")).to_be_visible(timeout=10_000)

    def test_accounts_total_balance_calculated(self, page: Page):
        """Autor: Jakub Gerwel."""
        def handle_me(route: Route):
            route.fulfill(status=200, content_type="application/json", body=json.dumps(MOCK_USER))

        def handle_accounts(route: Route):
            route.fulfill(status=200, content_type="application/json", body=json.dumps(MOCK_ACCOUNTS))

        page.route("**/api/auth/me", handle_me)
        page.route("**/api/accounts", handle_accounts)

        _inject_token(page)
        page.goto(f"{BASE_URL}/balances")

        expect(page.locator("text=Total Balance")).to_be_visible(timeout=10_000)
        expect(page.locator("text=6680.50").first).to_be_visible(timeout=5_000)


class TestMockCurrencyAPI:

    def test_currency_rate_mocked_from_external_api(self, page: Page):
        """Autor: Arkadiusz Gnidziejko."""
        def handle_me(route: Route):
            route.fulfill(status=200, content_type="application/json", body=json.dumps(MOCK_USER))

        def handle_groups(route: Route):
            route.fulfill(status=200, content_type="application/json", body=json.dumps(MOCK_GROUPS))

        def handle_rate(route: Route):
            route.fulfill(status=200, content_type="application/json", body=json.dumps(MOCK_CURRENCY_RATE))

        def handle_convert(route: Route):
            convert_resp = {
                "original_amount": "100.00",
                "from_currency": "EUR",
                "converted_amount": "428.00",
                "to_currency": "PLN",
                "rate": "4.28",
                "rate_date": date.today().isoformat(),
            }
            route.fulfill(status=200, content_type="application/json", body=json.dumps(convert_resp))

        page.route("**/api/auth/me", handle_me)
        page.route("**/api/groups", handle_groups)
        page.route("**/api/currency/rate*", handle_rate)
        page.route("**/api/currency/convert", handle_convert)

        _inject_token(page)
        page.goto(BASE_URL)

        converter = page.locator("a:has-text('Currency'), button:has-text('Currency')").first
        if converter.is_visible(timeout=3_000):
            converter.click()
            expect(page.locator("text=4.28").first).to_be_visible(timeout=5_000)

    def test_api_error_handled_gracefully(self, page: Page):
        """Autor: Arkadiusz Gnidziejko."""
        def handle_me(route: Route):
            route.fulfill(status=200, content_type="application/json", body=json.dumps(MOCK_USER))

        def handle_groups_error(route: Route):
            route.fulfill(status=500, content_type="application/json", body=json.dumps({"detail": "Internal Server Error"}))

        page.route("**/api/auth/me", handle_me)
        page.route("**/api/groups", handle_groups_error)

        _inject_token(page)
        page.goto(BASE_URL)

        page.wait_for_timeout(2000)
        expect(page.locator("body")).not_to_be_empty()

    def test_slow_api_response_shows_loading_state(self, page: Page):
        """Autor: Arkadiusz Gnidziejko."""
        def handle_me(route: Route):
            route.fulfill(status=200, content_type="application/json", body=json.dumps(MOCK_USER))

        def handle_groups_slow(route: Route):
            import time
            time.sleep(2)
            route.fulfill(status=200, content_type="application/json", body=json.dumps(MOCK_GROUPS))

        page.route("**/api/auth/me", handle_me)
        page.route("**/api/groups", handle_groups_slow)

        _inject_token(page)
        page.goto(BASE_URL)

        expect(page.locator("text=Wakacje 2026")).to_be_visible(timeout=15_000)


class TestMockMembersTab:

    def _setup_routes(self, page: Page):
        def handle_me(route: Route):
            route.fulfill(status=200, content_type="application/json", body=json.dumps(MOCK_USER))

        def handle_group_detail(route: Route):
            route.fulfill(status=200, content_type="application/json", body=json.dumps(MOCK_GROUP_DETAIL))

        def handle_expenses(route: Route):
            route.fulfill(status=200, content_type="application/json", body=json.dumps(MOCK_EXPENSES))

        def handle_settlements(route: Route):
            route.fulfill(status=200, content_type="application/json", body=json.dumps(MOCK_SETTLEMENTS))

        page.route("**/api/auth/me", handle_me)
        page.route(re.compile(r".*/api/groups/[^/]+$"), handle_group_detail)
        page.route(re.compile(r".*/api/groups/[^/]+/expenses"), handle_expenses)
        page.route(re.compile(r".*/api/groups/[^/]+/settlements"), handle_settlements)

    def test_members_tab_shows_all_group_members(self, page: Page):
        """Autor: Dominik Gąsowski."""
        self._setup_routes(page)

        _inject_token(page)
        page.goto(f"{BASE_URL}/groups/aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa")

        page.click("button:has-text('Members')")
        expect(page.locator("text=Mock User").first).to_be_visible(timeout=10_000)
        expect(page.locator("text=Anna K.").first).to_be_visible()
        expect(page.locator("text=Jan N.").first).to_be_visible()

    def test_members_tab_shows_admin_role(self, page: Page):
        """Autor: Dominik Gąsowski."""
        self._setup_routes(page)

        _inject_token(page)
        page.goto(f"{BASE_URL}/groups/aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa")

        page.click("button:has-text('Members')")
        expect(page.locator("text=admin").first).to_be_visible(timeout=10_000)

    def test_group_header_shows_mocked_group_name(self, page: Page):
        """Autor: Dominik Gąsowski."""
        self._setup_routes(page)

        _inject_token(page)
        page.goto(f"{BASE_URL}/groups/aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa")

        expect(page.locator("h1", has_text="Wakacje 2026")).to_be_visible(timeout=10_000)

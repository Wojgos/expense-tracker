import uuid
from datetime import date

import pytest
from playwright.sync_api import Playwright, APIRequestContext

BASE_URL = "http://localhost:8000"


@pytest.fixture(scope="module")
def api_context(playwright: Playwright) -> APIRequestContext:
    context = playwright.request.new_context(base_url=BASE_URL)
    yield context
    context.dispose()


@pytest.fixture(scope="module")
def registered_user(api_context: APIRequestContext) -> dict:
    suffix = uuid.uuid4().hex[:8]
    creds = {
        "email": f"api_test_{suffix}@example.com",
        "password": "SecurePass123!",
        "display_name": f"API User {suffix}",
    }
    resp = api_context.post("/auth/register", data=creds)
    assert resp.status == 201, f"Registration failed: {resp.text()}"
    user_data = resp.json()

    login_resp = api_context.post("/auth/login", data={
        "email": creds["email"],
        "password": creds["password"],
    })
    assert login_resp.status == 200
    token = login_resp.json()["access_token"]

    return {**creds, **user_data, "token": token}


@pytest.fixture(scope="module")
def registered_user2(api_context: APIRequestContext) -> dict:
    suffix = uuid.uuid4().hex[:8]
    creds = {
        "email": f"api_test2_{suffix}@example.com",
        "password": "SecurePass123!",
        "display_name": f"API User2 {suffix}",
    }
    resp = api_context.post("/auth/register", data=creds)
    assert resp.status == 201, f"Registration failed: {resp.text()}"
    user_data = resp.json()

    login_resp = api_context.post("/auth/login", data={
        "email": creds["email"],
        "password": creds["password"],
    })
    assert login_resp.status == 200
    token = login_resp.json()["access_token"]

    return {**creds, **user_data, "token": token}


def _auth(user: dict) -> dict:
    return {"Authorization": f"Bearer {user['token']}"}


class TestAuthAPI:

    def test_register_returns_user_data(self, api_context: APIRequestContext):
        """Autor: Wojciech Gosiewski."""
        suffix = uuid.uuid4().hex[:8]
        resp = api_context.post("/auth/register", data={
            "email": f"reg_test_{suffix}@example.com",
            "password": "TestPass123!",
            "display_name": f"Reg User {suffix}",
        })
        assert resp.status == 201
        body = resp.json()
        assert "id" in body
        assert body["email"] == f"reg_test_{suffix}@example.com"
        assert body["display_name"] == f"Reg User {suffix}"

    def test_register_duplicate_email_returns_409(self, api_context: APIRequestContext, registered_user: dict):
        """Autor: Wojciech Gosiewski."""
        resp = api_context.post("/auth/register", data={
            "email": registered_user["email"],
            "password": "AnotherPass!",
            "display_name": "Duplicate User",
        })
        assert resp.status == 409
        assert "already registered" in resp.json()["detail"]

    def test_login_returns_token(self, api_context: APIRequestContext, registered_user: dict):
        """Autor: Wojciech Gosiewski."""
        resp = api_context.post("/auth/login", data={
            "email": registered_user["email"],
            "password": registered_user["password"],
        })
        assert resp.status == 200
        body = resp.json()
        assert "access_token" in body
        assert body["token_type"] == "bearer"

    def test_login_invalid_password_returns_401(self, api_context: APIRequestContext, registered_user: dict):
        """Autor: Wojciech Gosiewski."""
        resp = api_context.post("/auth/login", data={
            "email": registered_user["email"],
            "password": "WrongPassword999!",
        })
        assert resp.status == 401
        assert "Invalid" in resp.json()["detail"]

    def test_me_returns_current_user(self, api_context: APIRequestContext, registered_user: dict):
        """Autor: Wojciech Domański."""
        resp = api_context.get("/auth/me", headers=_auth(registered_user))
        assert resp.status == 200
        body = resp.json()
        assert body["email"] == registered_user["email"]
        assert body["display_name"] == registered_user["display_name"]

    def test_me_without_token_returns_401(self, api_context: APIRequestContext):
        """Autor: Wojciech Domański."""
        resp = api_context.get("/auth/me")
        assert resp.status == 401


class TestGroupAPI:

    def test_create_group_returns_201(self, api_context: APIRequestContext, registered_user: dict):
        """Autor: Wojciech Domański."""
        resp = api_context.post("/groups", data={
            "name": f"API Test Group {uuid.uuid4().hex[:6]}",
            "description": "Created via API test",
        }, headers=_auth(registered_user))
        assert resp.status == 201
        body = resp.json()
        assert body["name"].startswith("API Test Group")
        assert body["description"] == "Created via API test"
        assert body["created_by"] == registered_user["id"]
        assert len(body["members"]) == 1
        assert body["members"][0]["role"] == "admin"

    def test_add_member_to_group(self, api_context: APIRequestContext, registered_user: dict, registered_user2: dict):
        """Autor: Wojciech Domański."""
        group_resp = api_context.post("/groups", data={
            "name": f"Member Test {uuid.uuid4().hex[:6]}",
        }, headers=_auth(registered_user))
        assert group_resp.status == 201
        group_id = group_resp.json()["id"]

        add_resp = api_context.post(
            f"/groups/{group_id}/members/{registered_user2['id']}",
            headers=_auth(registered_user),
        )
        assert add_resp.status == 200

        get_resp = api_context.get(f"/groups/{group_id}", headers=_auth(registered_user))
        members = get_resp.json()["members"]
        member_ids = [m["user_id"] for m in members]
        assert registered_user2["id"] in member_ids

    def test_non_member_cannot_access_group(self, api_context: APIRequestContext, registered_user: dict, registered_user2: dict):
        """Autor: Jakub Gerwel."""
        group_resp = api_context.post("/groups", data={
            "name": f"Private Group {uuid.uuid4().hex[:6]}",
        }, headers=_auth(registered_user))
        group_id = group_resp.json()["id"]

        get_resp = api_context.get(f"/groups/{group_id}", headers=_auth(registered_user2))
        assert get_resp.status == 403


class TestExpenseAPI:

    @pytest.fixture()
    def group_with_two_members(self, api_context: APIRequestContext, registered_user: dict, registered_user2: dict) -> dict:
        group_resp = api_context.post("/groups", data={
            "name": f"Expense Group {uuid.uuid4().hex[:6]}",
        }, headers=_auth(registered_user))
        group_id = group_resp.json()["id"]

        api_context.post(
            f"/groups/{group_id}/members/{registered_user2['id']}",
            headers=_auth(registered_user),
        )
        return {"group_id": group_id}

    def test_create_expense_equal_split(self, api_context: APIRequestContext, registered_user: dict, registered_user2: dict, group_with_two_members: dict):
        """Autor: Jakub Gerwel."""
        group_id = group_with_two_members["group_id"]
        resp = api_context.post(f"/groups/{group_id}/expenses", data={
            "description": "API Test Dinner",
            "amount": "100.00",
            "currency": "PLN",
            "split_type": "equal",
            "expense_date": date.today().isoformat(),
            "participant_ids": [registered_user["id"], registered_user2["id"]],
        }, headers=_auth(registered_user))
        assert resp.status == 201
        body = resp.json()
        assert body["description"] == "API Test Dinner"
        assert body["amount"] == "100.00" or float(body["amount"]) == 100.0
        assert body["split_type"] == "equal"
        assert len(body["splits"]) == 2

    def test_get_expense_by_id(self, api_context: APIRequestContext, registered_user: dict, registered_user2: dict, group_with_two_members: dict):
        """Autor: Jakub Gerwel."""
        group_id = group_with_two_members["group_id"]
        create_resp = api_context.post(f"/groups/{group_id}/expenses", data={
            "description": "Fetch Test Expense",
            "amount": "75.50",
            "currency": "PLN",
            "split_type": "equal",
            "expense_date": date.today().isoformat(),
            "participant_ids": [registered_user["id"], registered_user2["id"]],
        }, headers=_auth(registered_user))
        expense_id = create_resp.json()["id"]

        get_resp = api_context.get(
            f"/groups/{group_id}/expenses/{expense_id}",
            headers=_auth(registered_user),
        )
        assert get_resp.status == 200
        body = get_resp.json()
        assert body["id"] == expense_id
        assert body["description"] == "Fetch Test Expense"

    def test_delete_expense(self, api_context: APIRequestContext, registered_user: dict, registered_user2: dict, group_with_two_members: dict):
        """Autor: Jakub Gerwel."""
        group_id = group_with_two_members["group_id"]
        create_resp = api_context.post(f"/groups/{group_id}/expenses", data={
            "description": "To Delete",
            "amount": "50.00",
            "currency": "PLN",
            "split_type": "equal",
            "expense_date": date.today().isoformat(),
            "participant_ids": [registered_user["id"], registered_user2["id"]],
        }, headers=_auth(registered_user))
        expense_id = create_resp.json()["id"]

        del_resp = api_context.delete(
            f"/groups/{group_id}/expenses/{expense_id}",
            headers=_auth(registered_user),
        )
        assert del_resp.status == 204 or del_resp.status == 200


class TestAccountAPI:

    def test_create_account(self, api_context: APIRequestContext, registered_user: dict):
        """Autor: Arkadiusz Gnidziejko."""
        resp = api_context.post("/accounts", data={
            "name": f"API Wallet {uuid.uuid4().hex[:4]}",
            "type": "Cash",
            "currency": "PLN",
            "balance": "500.00",
        }, headers=_auth(registered_user))
        assert resp.status == 201
        body = resp.json()
        assert body["currency"] == "PLN"
        assert float(body["balance"]) == 500.0

    def test_list_accounts(self, api_context: APIRequestContext, registered_user: dict):
        """Autor: Arkadiusz Gnidziejko."""
        resp = api_context.get("/accounts", headers=_auth(registered_user))
        assert resp.status == 200
        body = resp.json()
        assert isinstance(body, list)

    def test_create_transaction_income(self, api_context: APIRequestContext, registered_user: dict):
        """Autor: Arkadiusz Gnidziejko."""
        acct_resp = api_context.post("/accounts", data={
            "name": f"Income Test {uuid.uuid4().hex[:4]}",
            "type": "Cash",
            "currency": "PLN",
            "balance": "100.00",
        }, headers=_auth(registered_user))
        account_id = acct_resp.json()["id"]

        tx_resp = api_context.post(f"/accounts/{account_id}/transactions", data={
            "amount": "200.00",
            "currency": "PLN",
            "description": "Salary",
            "transaction_date": date.today().isoformat(),
        }, headers=_auth(registered_user))
        assert tx_resp.status == 201
        assert float(tx_resp.json()["amount"]) == 200.0


class TestSettlementAPI:

    @pytest.fixture()
    def group_with_expense(self, api_context: APIRequestContext, registered_user: dict, registered_user2: dict) -> dict:
        group_resp = api_context.post("/groups", data={
            "name": f"Settlement Group {uuid.uuid4().hex[:6]}",
        }, headers=_auth(registered_user))
        group_id = group_resp.json()["id"]

        api_context.post(
            f"/groups/{group_id}/members/{registered_user2['id']}",
            headers=_auth(registered_user),
        )

        api_context.post(f"/groups/{group_id}/expenses", data={
            "description": "Settlement Test",
            "amount": "200.00",
            "currency": "PLN",
            "split_type": "equal",
            "expense_date": date.today().isoformat(),
            "participant_ids": [registered_user["id"], registered_user2["id"]],
        }, headers=_auth(registered_user))

        return {"group_id": group_id}

    def test_get_settlement_summary(self, api_context: APIRequestContext, registered_user: dict, group_with_expense: dict):
        """Autor: Dominik Gąsowski."""
        group_id = group_with_expense["group_id"]
        resp = api_context.get(
            f"/groups/{group_id}/settlements/",
            headers=_auth(registered_user),
        )
        assert resp.status == 200
        body = resp.json()
        assert "balances" in body
        assert "suggested_transfers" in body

    def test_create_settlement(self, api_context: APIRequestContext, registered_user: dict, registered_user2: dict, group_with_expense: dict):
        """Autor: Dominik Gąsowski."""
        group_id = group_with_expense["group_id"]
        resp = api_context.post(f"/groups/{group_id}/settlements/", data={
            "paid_to": registered_user["id"],
            "amount": "100.00",
        }, headers=_auth(registered_user2))
        assert resp.status == 201

    def test_unauthorized_access_returns_401(self, api_context: APIRequestContext, group_with_expense: dict):
        """Autor: Dominik Gąsowski."""
        group_id = group_with_expense["group_id"]
        resp = api_context.get(f"/groups/{group_id}/settlements/")
        assert resp.status == 401

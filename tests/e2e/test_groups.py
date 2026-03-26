import random

from playwright.sync_api import Page, expect, TimeoutError as PlaywrightTimeoutError

BASE_URL = "http://localhost:3000"


def _login(page: Page, email: str, password: str) -> None:
    page.goto(f"{BASE_URL}/login")
    page.fill('input[id="email"]', email)
    page.fill('input[id="password"]', password)
    page.click('button[type="submit"]')
    page.wait_for_url(f"{BASE_URL}/")


def _logout(page: Page) -> None:
    page.click('button:has-text("Logout")')
    page.wait_for_url(f"{BASE_URL}/login")


def _auth_headers(page: Page) -> dict[str, str]:
    token = page.evaluate("localStorage.getItem('token')")
    assert token, "Auth token not found in localStorage"
    return {"Authorization": f"Bearer {token}"}


def _create_group_and_open(page: Page, group_name: str, description: str | None = None) -> str:
    page.click('button:has-text("+ New Group")')
    page.fill('input[placeholder="e.g. Vacation 2026"]', group_name)
    if description is not None:
        page.fill('input[placeholder="Shared expenses for the trip"]', description)
    page.click('button:has-text("Create")')
    expect(page.locator("text=Group created!")).to_be_visible(timeout=10000)

    for _ in range(4):
        page.goto(f"{BASE_URL}/")
        link = page.locator("a", has_text=group_name).first
        try:
            expect(link).to_be_visible(timeout=4000)
            link.click()
            expect(page.locator("h1", has_text=group_name)).to_be_visible(timeout=10000)
            return page.url.split("/groups/")[1]
        except PlaywrightTimeoutError:
            continue

    raise AssertionError(f"Group '{group_name}' not visible on dashboard")


def _open_members_tab(page: Page) -> None:
    page.click('button:has-text("Members")')
    expect(page.locator('h1')).to_be_visible()


def _add_member_from_modal(page: Page, email: str, display_name: str) -> None:
    page.click('button:has-text("+ Add member")')
    modal = page.locator("div.fixed.inset-0").last
    modal.locator('input[placeholder="Enter user email..."]').fill(email)
    modal.locator('button:has-text("Search")').click()
    expect(modal.locator("p.font-medium", has_text=display_name)).to_be_visible(timeout=10000)
    modal.locator('button:has-text("Add")').click()


def _get_group_api(page: Page, group_id: str) -> dict:
    response = page.request.get(
        f"{BASE_URL}/api/groups/{group_id}",
        headers=_auth_headers(page),
    )
    assert response.status == 200, response.text()
    return response.json()


def _member_role(group_json: dict, user_id: str) -> str | None:
    for member in group_json["members"]:
        if member["user_id"] == user_id:
            return member["role"]
    return None


def test_tc_grp_001_create_group_creator_is_admin(page: Page, test_users_credentials, _register_test_users):
    user1 = test_users_credentials["user1"]
    reg_user1 = _register_test_users["user1"]
    _login(page, user1["email"], user1["password"])

    group_name = f"Group CRUD {random.randint(1, 100000)}"
    group_id = _create_group_and_open(page, group_name)

    group_json = _get_group_api(page, group_id)
    assert group_json["name"] == group_name
    assert group_json["description"] is None
    assert _member_role(group_json, reg_user1["id"]) == "admin"


def test_tc_grp_002_admin_can_edit_group_name_and_description(page: Page, test_users_credentials, _register_test_users):
    user1 = test_users_credentials["user1"]
    _login(page, user1["email"], user1["password"])

    group_name = f"Group Edit {random.randint(1, 100000)}"
    group_id = _create_group_and_open(page, group_name, "Opis startowy")

    page.click('button:has-text("Edit")')
    page.locator('input').nth(0).fill(f"{group_name} Updated")
    page.locator('input[placeholder="Description (optional)"]').fill("Nowy opis")
    page.click('button:has-text("Save")')

    expect(page.locator("text=Group updated")).to_be_visible()
    expect(page.locator("h1", has_text=f"{group_name} Updated")).to_be_visible()
    expect(page.locator("text=Nowy opis")).to_be_visible()

    group_json = _get_group_api(page, group_id)
    assert group_json["name"] == f"{group_name} Updated"
    assert group_json["description"] == "Nowy opis"


def test_tc_grp_003_admin_can_add_member_with_default_member_role(page: Page, test_users_credentials, _register_test_users):
    user1 = test_users_credentials["user1"]
    user2 = test_users_credentials["user2"]
    reg_user2 = _register_test_users["user2"]

    _login(page, user1["email"], user1["password"])
    group_name = f"Group Add Member {random.randint(1, 100000)}"
    group_id = _create_group_and_open(page, group_name)

    _open_members_tab(page)
    _add_member_from_modal(page, user2["email"], user2["display_name"])

    expect(page.locator(f'text={user2["display_name"]} added to the group')).to_be_visible()

    group_json = _get_group_api(page, group_id)
    assert _member_role(group_json, reg_user2["id"]) == "member"


def test_tc_grp_004_admin_can_remove_member(page: Page, test_users_credentials, _register_test_users):
    user1 = test_users_credentials["user1"]
    user2 = test_users_credentials["user2"]
    reg_user2 = _register_test_users["user2"]

    _login(page, user1["email"], user1["password"])
    group_name = f"Group Remove Member {random.randint(1, 100000)}"
    group_id = _create_group_and_open(page, group_name)

    _open_members_tab(page)
    _add_member_from_modal(page, user2["email"], user2["display_name"])
    expect(page.locator(f'text={user2["display_name"]} added to the group')).to_be_visible()

    page.once("dialog", lambda dialog: dialog.accept())
    member_row = page.locator("div.rounded-xl.border.border-gray-200", has_text=user2["display_name"]).first
    member_row.locator('button:has-text("Remove")').click()

    expect(page.locator(f'text={user2["display_name"]} removed')).to_be_visible()

    group_json = _get_group_api(page, group_id)
    assert _member_role(group_json, reg_user2["id"]) is None


def test_tc_grp_005_adding_same_member_twice_returns_conflict_message(page: Page, test_users_credentials, _register_test_users):
    user1 = test_users_credentials["user1"]
    user2 = test_users_credentials["user2"]

    _login(page, user1["email"], user1["password"])
    group_name = f"Group Duplicate Member {random.randint(1, 100000)}"
    _create_group_and_open(page, group_name)

    _open_members_tab(page)
    _add_member_from_modal(page, user2["email"], user2["display_name"])
    expect(page.locator(f'text={user2["display_name"]} added to the group')).to_be_visible()

    _add_member_from_modal(page, user2["email"], user2["display_name"])
    expect(page.locator("text=User is already a member")).to_be_visible()


def test_tc_grp_006_non_admin_cannot_edit_delete_or_add_members(page: Page, test_users_credentials, _register_test_users):
    user1 = test_users_credentials["user1"]
    user2 = test_users_credentials["user2"]
    reg_user3 = _register_test_users["user3"]

    _login(page, user1["email"], user1["password"])
    group_name = f"Group Permissions {random.randint(1, 100000)}"
    group_id = _create_group_and_open(page, group_name)

    _open_members_tab(page)
    _add_member_from_modal(page, user2["email"], user2["display_name"])
    expect(page.locator(f'text={user2["display_name"]} added to the group')).to_be_visible()

    _logout(page)
    _login(page, user2["email"], user2["password"])

    page.goto(f"{BASE_URL}/")
    page.locator("a", has_text=group_name).first.click()
    expect(page.locator("h1", has_text=group_name)).to_be_visible()

    expect(page.locator('button:has-text("Edit")')).to_have_count(0)
    expect(page.locator('button:has-text("Delete")')).to_have_count(0)

    _open_members_tab(page)
    expect(page.locator('button:has-text("+ Add member")')).to_have_count(0)

    patch_resp = page.request.patch(
        f"{BASE_URL}/api/groups/{group_id}",
        data={"name": "Should not work"},
        headers=_auth_headers(page),
    )
    assert patch_resp.status == 403

    add_resp = page.request.post(
        f"{BASE_URL}/api/groups/{group_id}/members/{reg_user3['id']}",
        headers=_auth_headers(page),
    )
    assert add_resp.status == 403


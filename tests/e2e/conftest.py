import pytest
from playwright.sync_api import Playwright, Browser, Page


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

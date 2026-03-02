"""
Fixtures E2E — Playwright centralisé.
Toute la configuration (viewport, locale, headless, timeouts) est ici.
Les tests n'ont qu'à utiliser la fixture `page` ou `browser_context`.
"""

import os

import pytest
from playwright.sync_api import sync_playwright

TEST_FRONTEND_URL = os.getenv("TEST_FRONTEND_URL", "http://localhost:5173")

VIEWPORT = {"width": 1280, "height": 720}
LOCALE = "fr-FR"
HEADLESS = os.getenv("PLAYWRIGHT_HEADLESS", "true").lower() != "false"
DEFAULT_NAV_TIMEOUT = 15_000
DEFAULT_EXPECT_TIMEOUT = 10_000


@pytest.fixture(scope="module")
def frontend_url():
    return TEST_FRONTEND_URL


@pytest.fixture(scope="module")
def browser():
    """Lance un navigateur Chromium partagé pour le module."""
    with sync_playwright() as pw:
        b = pw.chromium.launch(headless=HEADLESS)
        yield b
        b.close()


@pytest.fixture(scope="function")
def browser_context(browser):
    """Contexte isolé par test (cookies, storage vierges)."""
    ctx = browser.new_context(
        viewport=VIEWPORT,
        locale=LOCALE,
    )
    ctx.set_default_navigation_timeout(DEFAULT_NAV_TIMEOUT)
    ctx.set_default_timeout(DEFAULT_EXPECT_TIMEOUT)
    yield ctx
    ctx.close()


@pytest.fixture(scope="function")
def page(browser_context):
    """Page prête à l'emploi, nettoyée après chaque test."""
    p = browser_context.new_page()
    yield p
    p.close()

"""
Tests E2E — page Settings, statut watchdog.
"""

import re

import pytest
from playwright.sync_api import expect

pytestmark = [pytest.mark.e2e]


def test_settings_page_loads_and_sync_visible(page, frontend_url):
    """Page /settings charge, section sync visible."""
    page.goto(f"{frontend_url}/settings", wait_until="networkidle")
    expect(page.locator("[data-testid='settings-sync-status']")).to_be_visible()
    expect(page).to_have_title(re.compile(r".+"))


def test_settings_navigation_from_navbar(page, frontend_url):
    """Navigation Scan → Settings via navbar."""
    page.goto(f"{frontend_url}/scan", wait_until="networkidle")
    page.locator("[data-testid='nav-settings']").click()
    page.wait_for_url("**/settings**", timeout=5000)
    expect(page.locator("[data-testid='settings-sync-status']")).to_be_visible()

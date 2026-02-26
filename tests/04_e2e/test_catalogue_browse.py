"""
Tests E2E — navigation catalogue, filtres, recherche.
"""

import re

import pytest
from playwright.sync_api import expect

pytestmark = [pytest.mark.e2e]


def test_catalogue_page_loads_and_search_visible(page, frontend_url):
    """Page /catalogue charge, champ recherche visible."""
    page.goto(f"{frontend_url}/catalogue", wait_until="networkidle")
    expect(page.locator("[data-testid='catalogue-search']")).to_be_visible()
    expect(page).to_have_title(re.compile(r".+"))


def test_catalogue_navigation_from_navbar(page, frontend_url):
    """Navigation Scan → Catalogue via navbar."""
    page.goto(f"{frontend_url}/scan", wait_until="networkidle")
    page.locator("[data-testid='nav-catalogue']").click()
    page.wait_for_url("**/catalogue**", timeout=5000)
    expect(page.locator("[data-testid='catalogue-search']")).to_be_visible()


def test_catalogue_search_filter(page, frontend_url):
    """Recherche dans le catalogue."""
    page.goto(f"{frontend_url}/catalogue", wait_until="networkidle")
    search = page.locator("[data-testid='catalogue-search']")
    search.fill("ciment")
    search.press("Enter")
    page.wait_for_timeout(500)

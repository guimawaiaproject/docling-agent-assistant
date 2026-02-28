"""Tests pour Orchestrator (detect_mime + logique pipeline) — zéro mock."""
from backend.core.orchestrator import COST_PER_MILLION, Orchestrator


class TestDetectMime:
    def test_pdf_by_extension(self):
        assert Orchestrator._detect_mime("facture.pdf", b"") == "application/pdf"

    def test_jpg_by_extension(self):
        assert Orchestrator._detect_mime("photo.jpg", b"") == "image/jpeg"

    def test_jpeg_by_extension(self):
        assert Orchestrator._detect_mime("photo.jpeg", b"") == "image/jpeg"

    def test_png_by_extension(self):
        assert Orchestrator._detect_mime("scan.png", b"") == "image/png"

    def test_webp_by_extension(self):
        assert Orchestrator._detect_mime("img.webp", b"") == "image/webp"

    def test_heic_by_extension(self):
        assert Orchestrator._detect_mime("photo.heic", b"") == "image/heic"

    def test_pdf_by_magic_bytes(self):
        assert Orchestrator._detect_mime("noext", b"%PDF-1.4 blah") == "application/pdf"

    def test_jpeg_by_magic_bytes(self):
        assert Orchestrator._detect_mime("noext", b"\xff\xd8\xff\xe0rest") == "image/jpeg"

    def test_png_by_magic_bytes(self):
        assert Orchestrator._detect_mime("noext", b"\x89PNG\r\n\x1a\nrest") == "image/png"

    def test_unknown_defaults_to_jpeg(self):
        assert Orchestrator._detect_mime("unknown.xyz", b"\x00\x01\x02") == "image/jpeg"

    def test_case_insensitive_extension(self):
        assert Orchestrator._detect_mime("FILE.PDF", b"") == "application/pdf"
        assert Orchestrator._detect_mime("PHOTO.JPG", b"") == "image/jpeg"

    def test_no_extension(self):
        assert Orchestrator._detect_mime("justname", b"random") == "image/jpeg"


class TestCostCalculation:
    def test_cost_per_million_keys(self):
        assert "gemini-3-flash-preview" in COST_PER_MILLION
        assert "gemini-2.5-flash" in COST_PER_MILLION
        assert "gemini-3.1-pro-preview" in COST_PER_MILLION

    def test_cost_values_positive(self):
        for model, cost in COST_PER_MILLION.items():
            assert cost > 0, f"{model} has non-positive cost"

    def test_flash_cheaper_than_pro(self):
        assert COST_PER_MILLION["gemini-3-flash-preview"] < COST_PER_MILLION["gemini-3.1-pro-preview"]

"""
Tests unitaires des validateurs db_manager — zéro mock.
_parse_date, _upsert_params.
"""

from datetime import date, datetime

from core.db_manager import _parse_date, _upsert_params


class TestParseDate:
    def test_none_returns_none(self):
        assert _parse_date(None) is None

    def test_empty_string_returns_none(self):
        assert _parse_date("") is None
        assert _parse_date("  ") is None

    def test_date_object_passthrough(self):
        d = date(2023, 10, 24)
        assert _parse_date(d) == d

    def test_datetime_object_returns_date(self):
        dt = datetime(2023, 10, 24, 15, 30)
        assert _parse_date(dt) == date(2023, 10, 24)

    def test_format_dd_mm_yyyy(self):
        assert _parse_date("24/10/2023") == date(2023, 10, 24)

    def test_format_yyyy_mm_dd(self):
        assert _parse_date("2023-10-24") == date(2023, 10, 24)

    def test_format_dd_mm_yyyy_dash(self):
        assert _parse_date("24-10-2023") == date(2023, 10, 24)

    def test_format_dd_mm_yyyy_dot(self):
        assert _parse_date("24.10.2023") == date(2023, 10, 24)

    def test_unparseable_returns_none(self):
        assert _parse_date("not a date") is None
        assert _parse_date("2023/10/24") is None
        assert _parse_date("Oct 24, 2023") is None


class TestUpsertParams:
    def test_basic_product(self):
        product = {
            "fournisseur": "BigMat",
            "designation_raw": "CIMENT 42.5R",
            "designation_fr": "Ciment 42.5R",
            "famille": "Maçonnerie",
            "unite": "sac",
            "prix_brut_ht": 12.50,
            "remise_pct": 10.0,
            "prix_remise_ht": 11.25,
            "prix_ttc_iva21": 13.61,
            "numero_facture": "F-001",
            "date_facture": "24/10/2023",
            "confidence": "high",
        }
        params = _upsert_params(product, "pc", user_id=1)
        assert params[0] == 1  # user_id
        assert params[1] == "BigMat"
        assert params[2] == "CIMENT 42.5R"
        assert params[6] == 12.50  # prix_brut_ht
        assert params[11] == date(2023, 10, 24)
        assert params[13] == "pc"

    def test_minimal_product_defaults(self):
        product = {}
        params = _upsert_params(product, "mobile", user_id=None)
        assert params[0] is None  # user_id
        assert params[1] == ""
        assert params[4] == "Autre"
        assert params[5] == "unité"
        assert params[6] == 0.0
        assert params[11] is None
        assert params[13] == "mobile"

    def test_none_values_handled(self):
        product = {
            "prix_brut_ht": None,
            "remise_pct": None,
            "date_facture": None,
        }
        params = _upsert_params(product, "watchdog", user_id=None)
        assert params[6] == 0.0  # prix_brut_ht
        assert params[7] == 0.0  # remise_pct
        assert params[11] is None  # date

#!/usr/bin/env python3
"""
Script E2E — Test de l'API Docling Agent avec factures réelles.
Usage: python scripts/test_api_e2e.py [--base-url URL] [--skip-extraction]
L'API doit être démarrée (python api.py) avant d'exécuter ce script.
"""
import argparse
import json
import sys
import time
from pathlib import Path

# Ajouter la racine du projet au path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

try:
    import requests
except ImportError:
    print("❌ requests manquant. Exécuter: pip install requests")
    sys.exit(1)


def find_pdfs() -> list[Path]:
    """Trouve les PDFs dans Docling_Factures/Traitees/ ou dossiers de secours."""
    candidates = [
        PROJECT_ROOT / "Docling_Factures" / "Traitees",
        PROJECT_ROOT / "Docling_Factures",
        Path("./Docling_Factures/Traitees"),
        Path("./Docling_Factures"),
    ]
    for d in candidates:
        if not d.is_absolute():
            d = PROJECT_ROOT / d
        if d.exists():
            pdfs = list(d.glob("**/*.pdf"))
            if pdfs:
                return pdfs[:3]  # Max 3 pour le test
    return []


def run_tests(base_url: str, skip_extraction: bool) -> bool:
    """Exécute tous les tests. Retourne True si tout OK."""
    base_url = base_url.rstrip("/")
    ok_count = 0
    fail_count = 0

    def ok(msg: str):
        nonlocal ok_count
        ok_count += 1
        print(f"  [OK] {msg}")

    def _safe(s: str) -> str:
        """Encode pour eviter UnicodeEncodeError sur Windows cp1252."""
        if not s:
            return ""
        return s.encode("ascii", "replace").decode()

    def fail(msg: str, detail: str = ""):
        nonlocal fail_count
        fail_count += 1
        try:
            print(f"  [FAIL] {_safe(msg)}")
            if detail:
                print(f"     {_safe(str(detail))}")
        except UnicodeEncodeError:
            print(f"  [FAIL] {msg!r}")

    print("\n" + "=" * 60)
    print("  DOCLING AGENT — Test E2E API")
    print("=" * 60)
    print(f"  Base URL: {base_url}\n")

    # ─── 1. Health ───────────────────────────────────────────────
    print("[1/8] Health check...")
    try:
        r = requests.get(f"{base_url}/health", timeout=10)
        if r.status_code == 200 and r.json().get("status") == "ok":
            ok("Health OK")
        else:
            fail("Health", f"status={r.status_code} body={r.text[:200]}")
    except requests.RequestException as e:
        fail("Health", str(e))
        print("\n[!] L'API ne repond pas. Demarrez-la avec: python api.py")
        return False

    # ─── 2. Root ──────────────────────────────────────────────────
    print("\n[2/8] Root endpoint...")
    try:
        r = requests.get(f"{base_url}/", timeout=5)
        if r.status_code == 200 and "Docling" in str(r.json().get("message", "")):
            ok("Root OK")
        else:
            fail("Root", f"status={r.status_code}")
    except Exception as e:
        fail("Root", str(e))

    # ─── 3. Catalogue ─────────────────────────────────────────────
    print("\n[3/8] Catalogue...")
    try:
        r = requests.get(f"{base_url}/api/v1/catalogue", timeout=10)
        if r.status_code == 200:
            data = r.json()
            if "products" in data:
                ok(f"Catalogue OK ({len(data['products'])} produits)")
            else:
                fail("Catalogue", "clé 'products' manquante")
        else:
            fail("Catalogue", f"status={r.status_code}")
    except Exception as e:
        fail("Catalogue", str(e))

    # ─── 4. Fournisseurs ──────────────────────────────────────────
    print("\n[4/8] Fournisseurs...")
    try:
        r = requests.get(f"{base_url}/api/v1/catalogue/fournisseurs", timeout=10)
        if r.status_code == 200:
            data = r.json()
            fournisseurs = data.get("fournisseurs", data) if isinstance(data, dict) else data
            ok(f"Fournisseurs OK ({len(fournisseurs) if isinstance(fournisseurs, list) else '?'})")
        else:
            fail("Fournisseurs", f"status={r.status_code}")
    except Exception as e:
        fail("Fournisseurs", str(e))

    # ─── 5. Stats ──────────────────────────────────────────────────
    print("\n[5/8] Stats...")
    try:
        r = requests.get(f"{base_url}/api/v1/stats", timeout=10)
        if r.status_code == 200:
            data = r.json()
            ok(f"Stats OK (total_produits={data.get('total_produits', '?')})")
        else:
            fail("Stats", f"status={r.status_code}")
    except Exception as e:
        fail("Stats", str(e))

    # ─── 6. History ───────────────────────────────────────────────
    print("\n[6/8] History...")
    try:
        r = requests.get(f"{base_url}/api/v1/history", timeout=10)
        if r.status_code == 200:
            data = r.json()
            history = data.get("history", [])
            ok(f"History OK ({len(history)} entrées)")
        else:
            fail("History", f"status={r.status_code}")
    except Exception as e:
        fail("History", str(e))

    # ─── 7. Sync status ────────────────────────────────────────────
    print("\n[7/8] Sync status...")
    try:
        r = requests.get(f"{base_url}/api/v1/sync/status", timeout=10)
        if r.status_code == 200:
            ok("Sync status OK")
        else:
            fail("Sync status", f"status={r.status_code}")
    except Exception as e:
        fail("Sync status", str(e))

    # ─── 8. Extraction IA (PDF) ───────────────────────────────────
    print("\n[8/8] Extraction IA (upload + polling)...")
    if skip_extraction:
        print("  [SKIP] Ignore (--skip-extraction)")
    else:
        pdfs = find_pdfs()
        if not pdfs:
            fail("Aucun PDF trouve dans Docling_Factures/Traitees/")
        else:
            pdf_path = pdfs[0]
            try:
                with open(pdf_path, "rb") as f:
                    files = {"file": (pdf_path.name, f, "application/pdf")}
                    data = {"model": "gemini-2.5-flash", "source": "pc"}
                    r = requests.post(
                        f"{base_url}/api/v1/invoices/process",
                        files=files,
                        data=data,
                        timeout=30,
                    )
                if r.status_code != 202:
                    fail("Process", f"status={r.status_code} (attendu 202) body={r.text[:300]}")
                else:
                    job = r.json()
                    job_id = job.get("job_id")
                    if not job_id:
                        fail("Process", "job_id manquant")
                    else:
                        ok(f"Upload OK -> job_id={job_id[:8]}...")
                        # Polling
                        max_wait = 120
                        step = 3
                        elapsed = 0
                        while elapsed < max_wait:
                            time.sleep(step)
                            elapsed += step
                            rs = requests.get(
                                f"{base_url}/api/v1/invoices/status/{job_id}",
                                timeout=10,
                            )
                            if rs.status_code != 200:
                                fail("Status poll", f"status={rs.status_code}")
                                break
                            st = rs.json()
                            status = st.get("status", "")
                            if status == "completed":
                                res = st.get("result")
                                if isinstance(res, str):
                                    res = json.loads(res) if res else {}
                                products = (res or {}).get("products", []) if isinstance(res, dict) else []
                                ok(f"Extraction terminee ({len(products)} produits)")
                                break
                            if status == "error":
                                fail("Extraction", st.get("error", "Erreur inconnue"))
                                break
                            print(f"     ... {_safe(status)} ({elapsed}s)")
                        else:
                            fail("Extraction", "Timeout polling")
            except FileNotFoundError:
                fail("PDF", f"Fichier introuvable: {pdf_path}")
            except requests.RequestException as e:
                fail("Request", str(e))
            except Exception as e:
                fail("Extraction", str(e))

    # ─── Résumé ───────────────────────────────────────────────────
    print("\n" + "=" * 60)
    total = ok_count + fail_count
    print(f"  Résultat: {ok_count}/{total} tests OK")
    if fail_count > 0:
        print("  [!] Des tests ont echoue.")
    else:
        print("  [OK] Tous les tests sont passes.")
    print("=" * 60 + "\n")
    return fail_count == 0


def main():
    parser = argparse.ArgumentParser(description="Test E2E API Docling Agent")
    parser.add_argument(
        "--base-url",
        default="http://localhost:8000",
        help="URL de base de l'API (défaut: http://localhost:8000)",
    )
    parser.add_argument(
        "--skip-extraction",
        action="store_true",
        help="Ne pas tester l'extraction IA (évite d'appeler Gemini)",
    )
    args = parser.parse_args()
    success = run_tests(args.base_url, args.skip_extraction)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()

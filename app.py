"""
Docling Agent v2 — Catalogue BTP (Frontend Client)
Streamlit UI that communicates with the FastAPI backend.
"""
import os
import io
import time
import requests
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed

import streamlit as st
import pandas as pd
from PIL import Image
from dotenv import load_dotenv

# --- SETUP ---
load_dotenv()
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(name)s] %(levelname)s: %(message)s")
logger = logging.getLogger("DoclingFrontend")

API_URL = os.getenv("API_URL", "http://localhost:8000")
API_KEYS_ENV = os.getenv("API_KEYS", "")
API_KEY = API_KEYS_ENV.split(",")[0] if API_KEYS_ENV else ""
HEADERS = {"X-API-Key": API_KEY} if API_KEY else {}

# --- PAGE CONFIG ---
st.set_page_config(
    page_title="Docling Agent — Catalogue BTP",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# --- CUSTOM CSS ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    .stApp { font-family: 'Inter', sans-serif; }
    .main-title { font-size: 2rem; font-weight: 700; color: #0F172A; margin-bottom: 0.2rem; }
    .sub-title { font-size: 1rem; color: #64748B; margin-bottom: 1.5rem; }
    .metric-card {
        background: linear-gradient(135deg, #059669 0%, #10B981 100%);
        color: white; padding: 1.2rem; border-radius: 12px; text-align: center;
    }
    .metric-card h3 { margin: 0; font-size: 2rem; font-weight: 700; }
    .metric-card p { margin: 0.3rem 0 0; font-size: 0.85rem; opacity: 0.9; }
    #MainMenu {visibility: hidden;}
    .docling-card {
        display: flex;
        align-items: center;
        padding: 10px;
        margin-bottom: 8px;
        border-radius: 8px;
        background: #FFFFFF;
        border: 1px solid #E2E8F0;
        box-shadow: 0 1px 2px rgba(0,0,0,0.05);
        transition: all 0.2s;
    }
    .docling-card:hover {
        background: #F8FAFC;
        border-color: #CBD5E1;
        transform: translateY(-1px);
    }
    .file-icon {
        width: 32px;
        height: 32px;
        border-radius: 4px;
        background: #0078D4;
        color: white;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 0.6rem;
        font-weight: bold;
        margin-right: 12px;
        flex-shrink: 0;
    }
    .file-status {
        font-size: 0.7rem;
        color: #64748B;
        margin-top: 2px;
    }
    .status-dot {
        height: 8px;
        width: 8px;
        border-radius: 50%;
        display: inline-block;
        margin-right: 4px;
    }
</style>
""", unsafe_allow_html=True)


# --- HELPERS ---
@st.cache_data(ttl=10)
def fetch_stats():
    try:
        res = requests.get(f"{API_URL}/api/v1/stats", headers=HEADERS, timeout=5)
        if res.status_code == 200:
            return res.json()
    except Exception as e:
        logger.error(f"Failed to fetch stats: {e}")
    return {"products": 0, "invoices": 0, "families": 0}

@st.cache_data(ttl=1)
def fetch_watcher_activity():
    try:
        res = requests.get(f"{API_URL}/api/v1/watcher/activity", headers=HEADERS, timeout=3)
        if res.status_code == 200:
            return res.json().get("activity", [])
    except Exception:
        pass
    return []

@st.cache_data(ttl=1)
def fetch_catalogue():
    try:
        res = requests.get(f"{API_URL}/api/v1/catalogue", headers=HEADERS, timeout=10)
        if res.status_code == 200:
            data = res.json().get("products", [])
            df = pd.DataFrame(data)
            return df
    except Exception as e:
        logger.error(f"Failed to fetch catalogue: {e}")
    return pd.DataFrame()

def optimize_image(file_bytes, max_size=2000):
    """Compress image before sending to API to reduce payload & latency."""
    try:
        img = Image.open(io.BytesIO(file_bytes))
        # Compress only images, PDFs return as is
        if img.format == "PDF":
            return file_bytes, "application/pdf"

        if img.mode in ("RGBA", "P"):
            img = img.convert("RGB")

        if img.width > max_size or img.height > max_size:
            img.thumbnail((max_size, max_size), Image.Resampling.LANCZOS)

        out = io.BytesIO()
        img.save(out, format="WebP", quality=80)
        return out.getvalue(), "image/webp"
    except Exception as e:
        logger.warning(f"Optimization skipped (not an image or error): {e}")
        return file_bytes, None # Keep original

def process_single_file(file_name, file_bytes, file_type):
    """Uploads a single file to the API."""
    try:
        # Optimize if it's an image
        if file_type and file_type.startswith("image/"):
            optimized_bytes, new_type = optimize_image(file_bytes)
            if new_type:
                file_bytes = optimized_bytes
                file_type = new_type

        files = {"file": (file_name, file_bytes, file_type)}
        res = requests.post(f"{API_URL}/api/v1/invoices/process", files=files, headers=HEADERS, timeout=60)

        if res.status_code == 200:
            return file_name, True, res.json()
        else:
            error_msg = res.json().get("detail", res.text)
            return file_name, False, error_msg
    except Exception as e:
        return file_name, False, str(e)


# --- SIDEBAR ---
with st.sidebar:
    st.markdown("### 🛡️ Docling Agent v2")
    st.divider()

    # Check API Health
    api_online = False
    try:
        health_res = requests.get(f"{API_URL}/health", timeout=3)
        if health_res.status_code == 200:
            api_online = True
            st.success("🟢 API Connectée")
        else:
            st.warning("🟠 API: Réponse inattendue")
    except Exception:
        st.error("🔴 API Déconnectée")
        st.caption(f"Impossible de joindre {API_URL}")

    st.divider()
    stats = fetch_stats()
    nb_factures = stats.get("invoices", 0)

    st.markdown("### 📊 Statistiques")
    c1, c2, c3 = st.columns(3)
    c1.metric("📦", stats.get("products", 0), help="Produits extraits")
    c2.metric("📄", nb_factures, help="Factures traitées")
    c3.metric("📁", stats.get("families", 0), help="Familles BTP")

    st.divider()
    st.markdown("### 💸 Coûts & Serveurs")

    # Estimation coût Gemini 2.5 Flash (~0.0001$ par facture de 2 pages en moyenne avec context caching visuel)
    cost_estimation = nb_factures * 0.0001

    col_c1, col_c2 = st.columns(2)
    col_c1.metric("Cloud API", f"{cost_estimation:.4f} $", help="Coût estimé Google Gemini 2.5 Flash (Environ 0.0001$ par facture incluant Vision)")
    col_c2.metric("Serveur", "0.00 $", help="Neon (DB) et Render (API) en version gratuite (Free Tier)")

    st.divider()
    st.markdown("### ⚙️ Vitesse de Traitement")

    speed_metric = st.session_state.get("last_speed", 0.0)
    if speed_metric > 0:
        st.metric("Vitesse Turbo (Dernier Lot)", f"{speed_metric:.2f} doc/sec", delta="Temps réel", delta_color="normal")
    else:
        st.metric("Vitesse Turbo", "N/A", help="Lancez un traitement pour voir la vitesse mesurée.")

    max_workers_setting = st.slider(
        "⚡️ Agressivité Parallèle",
        min_value=1, max_value=12, value=5,
        help="Nombre de processus lancés simultanément vers l'API Gemini."
    )

    st.divider()
    if st.button("🔄 Rafraîchir les données", type="secondary"):
        fetch_stats.clear()
        fetch_catalogue.clear()
        st.rerun()

    st.divider()
    st.divider()
    st.markdown("### 🛡️ Activité Docling Agent")
    activity = fetch_watcher_activity()
    if activity:
        for item in activity:
            # Determine dot color
            status = item.get("status", "")
            dot_color = "#3B82F6" # Blue for processing
            if "Terminé" in status: dot_color = "#10B981" # Green
            if "Erreur" in status: dot_color = "#EF4444" # Red

            ext = item.get("ext", "FILE")
            size = item.get("size", "")

            # Use background colors based on extension
            bg_color = "#0078D4"
            if ext in ["PDF"]: bg_color = "#F40F02" # Adobe Red
            if ext in ["JPG", "JPEG", "PNG", "WEBP"]: bg_color = "#107C10" # Photo Green

            st.markdown(f"""
                <div class="docling-card">
                    <div class="file-icon" style="background: {bg_color};">{ext}</div>
                    <div class="file-info">
                        <div class="file-name" title="{item['filename']}">{item['filename']}</div>
                        <div class="file-status">
                            <span class="status-dot" style="background: {dot_color};"></span>
                            {status} • {item['time']} {f'• {size}' if size else ''}
                        </div>
                    </div>
                </div>
            """, unsafe_allow_html=True)
    else:
        st.caption("Aucune activité récente.")


# --- TABS ---
tab1, tab2, tab3 = st.tabs(["🚀 Traitement", "📦 Catalogue (Interactif)", "ℹ️ À Propos"])

# === TAB 1: PROCESSING ===
with tab1:
    st.markdown('<div class="main-title">🚀 Traitement Rapide (Parallélisé)</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-title">Uploadez des factures. Envoi simultané et compression des images à la volée.</div>', unsafe_allow_html=True)

    if not api_online:
        st.error("⚠️ L'API backend n'est pas accessible. Veuillez vérifier que le serveur tourne.")

    uploaded = st.file_uploader(
        "Déposez vos factures ici",
        type=["pdf", "jpg", "jpeg", "png", "webp"],
        accept_multiple_files=True,
    )

    if uploaded and api_online and st.button("🚀 Lancer le Traitement", type="primary", use_container_width=True):
        total_added, total_updated, total_cached = 0, 0, 0

        # UI Progress elements
        progress_bar = st.progress(0)
        status_text = st.empty()

        results_container = st.container()

        start_time = time.time()

        with ThreadPoolExecutor(max_workers=max_workers_setting) as executor:
            # Submit all tasks
            future_to_file = {
                executor.submit(process_single_file, f.name, f.read(), f.type): f.name
                for f in uploaded
            }

            completed = 0
            for future in as_completed(future_to_file):
                file_name = future_to_file[future]
                completed += 1
                progress_bar.progress(completed / len(uploaded))
                status_text.text(f"Traitement : {completed}/{len(uploaded)} fichiers...")

                try:
                    name, success, data = future.result()
                    with results_container:
                        # Fix UI Overlap: Do not use st.status in parallel, use simple success/warning alerts.
                        if success:
                            if data.get("was_cached"):
                                st.success(f"⏩ {name} : Déjà traité")
                                total_cached += 1
                            elif data.get("products_added", 0) + data.get("products_updated", 0) > 0:
                                added = data["products_added"]
                                updated = data["products_updated"]
                                st.success(f"✅ {name} : {added} nouveaux, {updated} MAJ")
                                total_added += added
                                total_updated += updated
                            else:
                                st.warning(f"⚠️ {name} : Aucun produit extrait")
                        else:
                            st.error(f"❌ {name} : Erreur: {data}")
                except Exception as exc:
                    with results_container:
                        st.error(f"❌ {file_name} : Erreur fatale: {exc}")

        duration = time.time() - start_time
        speed = len(uploaded) / duration if duration > 0 else 0
        st.session_state["last_speed"] = speed
        status_text.text(f"Terminé en {duration:.1f} secondes ! ({speed:.2f} doc/s) ⚡️")

        # Force refresh metrics and catalogue after upload
        fetch_stats.clear()
        fetch_catalogue.clear()

        st.divider()
        cols = st.columns(3)
        with cols[0]:
            st.markdown(f'<div class="metric-card"><h3>{total_added}</h3><p>Nouveaux produits</p></div>', unsafe_allow_html=True)
        with cols[1]:
            st.markdown(f'<div class="metric-card"><h3>{total_updated}</h3><p>Prix mis à jour</p></div>', unsafe_allow_html=True)
        with cols[2]:
            st.markdown(f'<div class="metric-card"><h3>{total_cached}</h3><p>Déjà traités</p></div>', unsafe_allow_html=True)

    elif not uploaded:
        st.markdown(
            '<div style="text-align:center; padding:3rem; color:#94A3B8;">'
            '<p style="font-size:3rem;">📄</p>'
            '<p style="font-size:1.1rem; font-weight:500;">Glissez-déposez vos factures PDF ou photos ici</p>'
            '</div>', unsafe_allow_html=True)


# === TAB 2: CATALOGUE ===
with tab2:
    st.markdown('<div class="main-title">📦 Catalogue Produits (Interactif)</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-title">Double-cliquez sur une cellule pour modifier la base de données.</div>', unsafe_allow_html=True)

    df = fetch_catalogue()

    if df is None or df.empty:
        st.info("Aucun produit. Uploadez des factures dans l'onglet Traitement ou vérifiez l'API.")
    else:
        col1, col2, col3 = st.columns([2, 1, 1])
        with col1:
            search = st.text_input("🔍 Rechercher", placeholder="Ciment, Portland, treillis...")
        with col2:
            familles = ["Toutes"] + sorted(df["famille"].dropna().unique().tolist()) if "famille" in df else ["Toutes"]
            famille_filter = st.selectbox("Famille", familles)
        with col3:
            fournisseurs = ["Tous"] + sorted(df["fournisseur"].dropna().unique().tolist()) if "fournisseur" in df else ["Tous"]
            fournisseur_filter = st.selectbox("Fournisseur", fournisseurs)

        filtered = df.copy()
        if search and "designation_raw" in filtered and "designation_fr" in filtered:
            mask = (
                filtered["designation_raw"].str.contains(search, case=False, na=False)
                | filtered["designation_fr"].str.contains(search, case=False, na=False)
            )
            filtered = filtered[mask]
        if famille_filter != "Toutes" and "famille" in filtered:
            filtered = filtered[filtered["famille"] == famille_filter]
        if fournisseur_filter != "Tous" and "fournisseur" in filtered:
            filtered = filtered[filtered["fournisseur"] == fournisseur_filter]

        display_cols = {
            "id": "ID",
            "fournisseur": "Fournisseur",
            "designation_raw": "Désignation (Català)",
            "designation_fr": "Désignation (FR)",
            "famille": "Famille",
            "unite": "Unité",
            "prix_brut_ht": "P.U. Brut HT",
            "remise_pct": "Remise %",
            "prix_remise_ht": "P.U. Remisé HT",
            "prix_ttc_iva21": "P.U. IVA 21%",
            "numero_facture": "N° Facture",
            "date_facture": "Date Facture",
        }

        # Keep only existing columns
        existing_cols = {k: v for k, v in display_cols.items() if k in filtered.columns}
        display_df = filtered[list(existing_cols.keys())].rename(columns=existing_cols)

        # We process edits here using st.data_editor
        edited_df = st.data_editor(
            display_df,
            use_container_width=True,
            hide_index=True,
            height=600,
            column_config={
                "ID": None, # Hide ID from UI
                "Fournisseur": st.column_config.Column(disabled=True),
                "Désignation (Català)": st.column_config.Column(disabled=True),
                "N° Facture": st.column_config.Column(disabled=True),
                "Date Facture": st.column_config.Column(disabled=True),
            },
            key="catalogue_editor",
            num_rows="fixed"
        )

        # Check if edits happened
        editor_state = st.session_state.get("catalogue_editor", {})
        if editor_state.get("edited_rows"):
            for row_idx, edits in editor_state["edited_rows"].items():
                real_row_idx = filtered.index[row_idx]
                product_id = int(filtered.loc[real_row_idx, "id"])

                # Reverse translate from UI Name to Backend Name
                reverse_cols = {v: k for k, v in existing_cols.items()}

                backend_updates = {}
                for col_name, new_val in edits.items():
                    if col_name in reverse_cols:
                        backend_updates[reverse_cols[col_name]] = new_val

                if backend_updates:
                    res = requests.put(f"{API_URL}/api/v1/products/{product_id}", json=backend_updates, headers=HEADERS)
                    if res.status_code == 200:
                        st.toast(f"✅ Produit MAJ ({backend_updates})", icon="💾")
                    else:
                        st.error(f"❌ Erreur sauvegarde: {res.text}")

            # Since we processed edits, clear the state and refresh
            fetch_catalogue.clear()
            st.rerun()

        st.caption(f"{len(filtered)} produits sur {len(df)}")

        st.divider()
        c1, c2 = st.columns(2)
        with c1:
            buf = io.BytesIO()
            display_df.drop(columns=["ID"], errors="ignore").to_excel(buf, index=False, engine="openpyxl")
            st.download_button("📥 Export Excel", buf.getvalue(),
                               "catalogue_produits.xlsx",
                               mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
        with c2:
            st.download_button("📄 Export CSV",
                               display_df.drop(columns=["ID"], errors="ignore").to_csv(index=False).encode("utf-8"),
                               "catalogue_produits.csv", mime="text/csv")


# === TAB 3: ABOUT ===
with tab3:
    st.markdown("### 🏛 Architecture Cloud 2026")
    st.write("Ceci est le client Web (Streamlit) officiel pour l'API REST de Docling Agent.")
    st.code(f"API Backend actuelle : {API_URL}")

    st.markdown("""
    #### ⚙️ Fonctionnement
    1. **Upload Parallèle** : Compressé (WebP) et envoyé via ThreadPool (jusqu'à 10 fichiers en même temps)
    2. **Analyse IA** : L'API contacte Google Gemini 2.5 Flash pour l'extraction OCR & Structure
    3. **Stockage** : PostgreSQL (Neon) stocke ou met à jour les prix
    4. **Catalogue** : Récupéré via GET `/api/v1/catalogue` (avec CRUD via `PUT`)
    """)

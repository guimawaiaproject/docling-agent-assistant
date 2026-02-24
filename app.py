"""
Docling Agent v2 — Catalogue BTP
Extraction IA de factures via Gemini multimodal.
"""
import os
import sys
import io
import logging

import streamlit as st
import pandas as pd
from dotenv import load_dotenv

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from backend.core.config import get_config
from backend.core.db_manager import DBManager
from backend.core.orchestrator import ExtractionOrchestrator

# --- SETUP ---
load_dotenv()
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(name)s] %(levelname)s: %(message)s")
logger = logging.getLogger("DoclingAgent")

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
    footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)


# --- INIT ---
config = get_config()
db = DBManager(config.db_path)
orch = ExtractionOrchestrator(config=config, db_manager=db)


# --- SIDEBAR ---
with st.sidebar:
    st.markdown("### 🛡️ Docling Agent v2")
    st.divider()

    if config.has_gemini_key:
        st.success("🟢 Gemini API connectée")
    else:
        st.error("🔴 Gemini API manquante")
        st.caption("Ajoutez `GEMINI_API_KEY` dans `.env`")

    if config.has_google_config:
        st.success("☁️ Google Cloud connecté")
    else:
        st.info("☁️ Google Cloud non configuré")

    st.divider()
    stats = db.get_stats()
    st.metric("📦 Produits", stats["products"])
    st.metric("📄 Factures", stats["invoices"])
    st.metric("📁 Familles", stats["families"])

    st.divider()
    if st.button("🗑 Réinitialiser la base", type="secondary"):
        if st.session_state.get("confirm_reset"):
            db.reset_database()
            st.session_state["confirm_reset"] = False
            st.toast("Base de données vidée.", icon="🗑")
            st.rerun()
        else:
            st.session_state["confirm_reset"] = True
            st.warning("Cliquez à nouveau pour confirmer.")


# --- TABS ---
tab1, tab2, tab3 = st.tabs(["🚀 Traitement", "📦 Catalogue", "ℹ️ À Propos"])

# === TAB 1: PROCESSING ===
with tab1:
    st.markdown('<div class="main-title">🚀 Traitement de Factures</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-title">Uploadez des factures PDF ou des photos — Gemini extrait tout en quelques secondes.</div>', unsafe_allow_html=True)

    uploaded = st.file_uploader(
        "Déposez vos factures ici",
        type=["pdf", "jpg", "jpeg", "png", "webp", "heic"],
        accept_multiple_files=True,
    )

    if uploaded and st.button("🚀 Lancer le Traitement", type="primary", use_container_width=True):
        total_added, total_updated, total_cached = 0, 0, 0

        for file in uploaded:
            file_bytes = file.read()

            with st.status(f"📄 {file.name}", expanded=True) as status:
                def on_status(msg):
                    st.write(msg)

                try:
                    result = orch.process_file(file_bytes, file.name, on_status=on_status)

                    if result.was_cached:
                        status.update(label=f"⏩ {file.name} — déjà traité", state="complete")
                        total_cached += 1
                    elif result.products_added + result.products_updated > 0:
                        status.update(
                            label=f"✅ {file.name} — {result.products_added} ajoutés, {result.products_updated} mis à jour",
                            state="complete",
                        )
                        total_added += result.products_added
                        total_updated += result.products_updated
                    else:
                        status.update(label=f"⚠️ {file.name} — aucun produit extrait", state="error")

                except Exception as e:
                    logger.error(f"Error processing {file.name}: {e}", exc_info=True)
                    st.error(f"❌ Erreur: {e}")
                    status.update(label=f"❌ {file.name} — erreur", state="error")

        st.divider()
        cols = st.columns(3)
        with cols[0]:
            st.markdown(f'<div class="metric-card"><h3>{total_added}</h3><p>Nouveaux produits</p></div>', unsafe_allow_html=True)
        with cols[1]:
            st.markdown(f'<div class="metric-card"><h3>{total_updated}</h3><p>Prix mis à jour</p></div>', unsafe_allow_html=True)
        with cols[2]:
            st.markdown(f'<div class="metric-card"><h3>{total_cached}</h3><p>Déjà traités</p></div>', unsafe_allow_html=True)

        st.toast(f"Traitement terminé : {total_added + total_updated} produits", icon="✅")

    elif not uploaded:
        st.markdown(
            '<div style="text-align:center; padding:3rem; color:#94A3B8;">'
            '<p style="font-size:3rem;">📄</p>'
            '<p style="font-size:1.1rem; font-weight:500;">Glissez-déposez vos factures PDF ou photos ici</p>'
            '</div>', unsafe_allow_html=True)


# === TAB 2: CATALOGUE ===
with tab2:
    st.markdown('<div class="main-title">📦 Catalogue Produits</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-title">Votre base de prix matériaux, mise à jour à chaque facture.</div>', unsafe_allow_html=True)

    df = db.get_catalogue()

    if df.empty:
        st.info("Aucun produit. Uploadez des factures dans l'onglet Traitement.")
    else:
        col1, col2, col3 = st.columns([2, 1, 1])
        with col1:
            search = st.text_input("🔍 Rechercher", placeholder="Ciment, Portland, treillis...")
        with col2:
            familles = ["Toutes"] + sorted(df["famille"].dropna().unique().tolist())
            famille_filter = st.selectbox("Famille", familles)
        with col3:
            fournisseurs = ["Tous"] + sorted(df["fournisseur"].dropna().unique().tolist())
            fournisseur_filter = st.selectbox("Fournisseur", fournisseurs)

        filtered = df.copy()
        if search:
            mask = (
                filtered["designation_raw"].str.contains(search, case=False, na=False)
                | filtered["designation_fr"].str.contains(search, case=False, na=False)
            )
            filtered = filtered[mask]
        if famille_filter != "Toutes":
            filtered = filtered[filtered["famille"] == famille_filter]
        if fournisseur_filter != "Tous":
            filtered = filtered[filtered["fournisseur"] == fournisseur_filter]

        display_cols = {
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
        available = [c for c in display_cols if c in filtered.columns]
        display_df = filtered[available].rename(columns=display_cols)

        st.dataframe(display_df, use_container_width=True, hide_index=True)
        st.caption(f"{len(filtered)} produits sur {len(df)}")

        st.divider()
        c1, c2 = st.columns(2)
        with c1:
            buf = io.BytesIO()
            display_df.to_excel(buf, index=False, engine="openpyxl")
            st.download_button("📥 Export Excel", buf.getvalue(),
                               "catalogue_produits.xlsx",
                               mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
        with c2:
            st.download_button("📄 Export CSV",
                               display_df.to_csv(index=False).encode("utf-8"),
                               "catalogue_produits.csv", mime="text/csv")


# === TAB 3: ABOUT ===
with tab3:
    st.markdown('<div class="main-title">ℹ️ À Propos</div>', unsafe_allow_html=True)
    st.markdown("""
    ### Pipeline
    ```
    📸 Photo / PDF facture
        ↓
    🧠 Gemini 2.0 Flash (extraction + traduction FR + classification)
        ↓
    🗄️ SQLite (dédoublonnage produit, mise à jour des prix)
        ↓
    ☁️ Google Drive + Sheets (archivage & sync cloud)
        ↓
    📊 Catalogue produits + Export Excel
    ```

    ### Tech Stack
    | Composant | Technologie |
    |---|---|
    | **IA** | Gemini 2.0 Flash (multimodal) |
    | **Frontend** | Streamlit |
    | **Base locale** | SQLite (WAL mode) |
    | **Cloud** | Google Drive + Google Sheets |

    ### Version
    **v2.0** — Pipeline 100% Gemini, catalogue produits
    """)

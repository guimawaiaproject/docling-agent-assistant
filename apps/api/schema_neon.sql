-- ============================================================
-- DOCLING AGENT v3 — Schéma Neon PostgreSQL
-- À exécuter dans Neon Console → SQL Editor
-- ============================================================

-- Extensions
-- (vector extension retirée, pas utilisée) Recherche sémantique future (devis IA)
CREATE EXTENSION IF NOT EXISTS pg_trgm;     -- Recherche floue ES/CA/FR

-- ─── Nettoyage (décommenter pour reset complet) ──────────────
-- DROP TABLE IF EXISTS factures CASCADE;
-- DROP TABLE IF EXISTS produits CASCADE;
-- DROP TABLE IF EXISTS fournisseurs CASCADE;

-- ─── Utilisateurs (multi-tenant — doit précéder produits/factures/jobs) ─
CREATE TABLE IF NOT EXISTS users (
  id            SERIAL PRIMARY KEY,
  email         VARCHAR(255) UNIQUE NOT NULL,
  password_hash TEXT NOT NULL,
  display_name  VARCHAR(200),
  role          VARCHAR(20) DEFAULT 'user',   -- user | admin
  created_at    TIMESTAMPTZ DEFAULT NOW()
);

-- ─── Fournisseurs ─────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS fournisseurs (
  id         SERIAL PRIMARY KEY,
  nom        VARCHAR(200) UNIQUE NOT NULL,
  pays       VARCHAR(10)  DEFAULT 'ES',
  langue     VARCHAR(10)  DEFAULT 'ca',   -- ca | es | fr
  created_at TIMESTAMPTZ  DEFAULT NOW()
);

-- ─── Produits ─────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS produits (
  id               SERIAL PRIMARY KEY,
  user_id          INTEGER REFERENCES users(id) ON DELETE CASCADE,
  fournisseur      VARCHAR(200) NOT NULL,
  designation_raw  TEXT         NOT NULL,  -- Original CA/ES
  designation_fr   TEXT         NOT NULL,  -- Traduit FR
  famille          VARCHAR(100),
  unite            VARCHAR(50),
  prix_brut_ht     NUMERIC(10,4) DEFAULT 0,
  remise_pct       NUMERIC(5,2)  DEFAULT 0,
  prix_remise_ht   NUMERIC(10,4) DEFAULT 0,
  prix_ttc_iva21   NUMERIC(10,4) DEFAULT 0,
  numero_facture   VARCHAR(100),
  date_facture     DATE,
  confidence       VARCHAR(10)   DEFAULT 'high',   -- high | low
  source           VARCHAR(20)   DEFAULT 'pc',      -- pc | mobile | watchdog
  created_at       TIMESTAMPTZ   DEFAULT NOW(),
  updated_at       TIMESTAMPTZ   DEFAULT NOW(),

  -- Anti-doublon : même désignation originale + même fournisseur + user = upsert prix
  UNIQUE(designation_raw, fournisseur, user_id)
);

-- ─── Jobs (extraction async, persistance pour survie redémarrage) ─
CREATE TABLE IF NOT EXISTS jobs (
  job_id     UUID PRIMARY KEY,
  user_id    INTEGER REFERENCES users(id) ON DELETE CASCADE,
  status     VARCHAR(20) DEFAULT 'processing',  -- processing | completed | error
  result     JSONB,
  error      TEXT,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_jobs_created ON jobs(created_at DESC);

-- ─── Factures (historique audit) ──────────────────────────────
CREATE TABLE IF NOT EXISTS factures (
  id                  SERIAL PRIMARY KEY,
  user_id             INTEGER REFERENCES users(id) ON DELETE CASCADE,
  filename            VARCHAR(500),
  statut              VARCHAR(20)  DEFAULT 'traite',  -- traite | erreur | en_cours
  nb_produits_extraits INTEGER     DEFAULT 0,
  cout_api_usd        NUMERIC(8,6) DEFAULT 0,
  modele_ia           VARCHAR(50)  DEFAULT 'gemini-3-flash',
  source              VARCHAR(20)  DEFAULT 'pc',      -- pc | mobile | watchdog
  pdf_url             TEXT,                             -- URL cloud S3 du fichier original
  created_at          TIMESTAMPTZ  DEFAULT NOW()
);

-- ─── Index performances ────────────────────────────────────────

-- Multi-tenant : filtre user_id
CREATE INDEX IF NOT EXISTS idx_produits_user_id ON produits(user_id);
CREATE INDEX IF NOT EXISTS idx_produits_user_famille ON produits(user_id, famille);
CREATE INDEX IF NOT EXISTS idx_produits_user_fournisseur ON produits(user_id, fournisseur);
CREATE INDEX IF NOT EXISTS idx_factures_user_id ON factures(user_id);
CREATE INDEX IF NOT EXISTS idx_factures_user_date ON factures(user_id, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_jobs_user_id ON jobs(user_id);

-- Filtre famille (le plus utilisé)
CREATE INDEX IF NOT EXISTS idx_produits_famille
  ON produits(famille);

-- Filtre fournisseur
CREATE INDEX IF NOT EXISTS idx_produits_fournisseur
  ON produits(fournisseur);

-- Cursor pagination (tri par date desc)
CREATE INDEX IF NOT EXISTS idx_produits_updated
  ON produits(updated_at DESC);

-- Recherche floue sur designation ORIGINALE (CA/ES)
-- → trouve "CEMENTO" quand on tape "ciment"
CREATE INDEX IF NOT EXISTS idx_trgm_raw
  ON produits USING GIN (designation_raw gin_trgm_ops);

-- Recherche floue sur designation FRANÇAISE
-- → trouve "Ciment Portland" quand on tape "portland"
CREATE INDEX IF NOT EXISTS idx_trgm_fr
  ON produits USING GIN (designation_fr gin_trgm_ops);

-- Recherche combinée ILIKE rapide
CREATE INDEX IF NOT EXISTS idx_produits_search_combined
  ON produits USING GIN (
    (designation_raw || ' ' || designation_fr || ' ' || fournisseur) gin_trgm_ops
  );

-- ─── Trigger updated_at auto ──────────────────────────────────
CREATE OR REPLACE FUNCTION trigger_set_updated_at()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = NOW();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS set_updated_at ON produits;
CREATE TRIGGER set_updated_at
  BEFORE UPDATE ON produits
  FOR EACH ROW EXECUTE FUNCTION trigger_set_updated_at();

-- ─── Vider les données existantes (garder la structure) ────────
-- TRUNCATE TABLE produits RESTART IDENTITY;
-- TRUNCATE TABLE factures RESTART IDENTITY;

-- --- Historique de prix (track price changes) ------------------
CREATE TABLE IF NOT EXISTS prix_historique (
  id          SERIAL PRIMARY KEY,
  produit_id  INTEGER REFERENCES produits(id) ON DELETE CASCADE,
  fournisseur VARCHAR(200) NOT NULL,
  designation_fr TEXT NOT NULL,
  prix_ht     NUMERIC(10,4) NOT NULL,
  prix_brut   NUMERIC(10,4),
  remise_pct  NUMERIC(5,2) DEFAULT 0,
  facture_id  INTEGER REFERENCES factures(id) ON DELETE SET NULL,
  recorded_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_prixhist_produit
  ON prix_historique(produit_id, recorded_at DESC);

# 🎨 AUDIT UX/UI EXPERT SENIOR 2026
# Docling Agent v3 — Application BTP extraction factures IA

**Référentiel :** Standards Notion, Linear, Figma, Vercel, Stripe, Superhuman
**Date :** 26 février 2026
**Méthodologie :** Analyse exhaustive du code source `docling-pwa/src/` + persona chef de chantier BTP 45 ans, mobile, mains sales, soleil

---

## 📊 SYNTHÈSE EXÉCUTIVE

L'application Docling Agent v3 offre une base fonctionnelle solide (scan, validation, catalogue, devis, historique) avec une PWA installable et un mode offline. **Cependant, elle reste en dessous des standards SaaS B2B 2026** sur plusieurs axes critiques : onboarding inexistant, absence de command palette, settings très limités, et expérience mobile perfectible. Le chef de chantier BTP non-technique serait rapidement perdu sans accompagnement.

**Score global estimé : 5.8/10** — Acceptable pour un MVP, insuffisant pour rivaliser avec Stripe/Linear.

---

## 1. 🏠 ONBOARDING & FIRST-TIME EXPERIENCE

### Problèmes détectés

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
[ONBOARDING] — 🔴 BLOQUANT
📍 Localisation : App.jsx L48 — redirection / → /scan sans contexte
🔍 Problème UX : Un nouvel utilisateur arrive sur /scan sans aucune explication. Pas de page d'accueil, pas de "Getting started", pas de checklist.
🏆 Standard concurrent : Notion affiche une checklist gamifiée en sidebar. Linear crée automatiquement un premier projet. Stripe affiche "Complete your account setup".
⚠️ Impact utilisateur : Confusion totale. Le chef de chantier ne sait pas quoi faire. Abandon probable en < 30 secondes.
✅ Solution 2026 : Page d'accueil dédiée avec CTA "Scanner ma première facture" + checklist (1. Scanner 2. Valider 3. Consulter le catalogue). Optionnel : modal de bienvenue au premier chargement.
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
[CATALOGUE VIDE] — 🟠 FRICTION
📍 Localisation : CataloguePage.jsx L318-322
🔍 Problème UX : Empty state minimaliste : "Aucun produit trouvé" + icône Package. Pas de CTA pour scanner, pas d'explication.
🏆 Standard concurrent : Linear : "Create your first issue" avec bouton évident. Notion : "Add a page to get started".
⚠️ Impact utilisateur : L'utilisateur ne sait pas qu'il doit d'abord scanner des factures.
✅ Solution 2026 : Empty state riche : "Votre catalogue est vide. Scannez une facture pour commencer." + bouton "Scanner une facture" → /scan. Illustration ou icône engageante.
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
[HISTORIQUE VIDE] — 🟠 FRICTION
📍 Localisation : HistoryPage.jsx L159-163
🔍 Problème UX : "Aucune facture traitée pour l'instant" sans CTA.
🏆 Standard concurrent : Vercel : "Deploy your first project" avec bouton.
⚠️ Impact utilisateur : Même problème — pas de guidance.
✅ Solution 2026 : "Aucune facture encore. Scannez votre première facture pour commencer." + CTA vers /scan.
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
[DEVIS VIDE] — 🟡 POLISH
📍 Localisation : DevisPage.jsx — pas d'empty state explicite pour "produits sélectionnés"
🔍 Problème UX : La section produits sélectionnés n'apparaît qu'après ajout. Pas de message "Ajoutez des produits depuis le catalogue ci-dessous" quand selected.length === 0.
🏆 Standard concurrent : Pennylane : guide pas à pas pour créer un devis.
⚠️ Impact utilisateur : L'ordre de lecture (entreprise/client en haut, recherche produits en bas) peut dérouter.
✅ Solution 2026 : Zone "Panier devis" toujours visible avec "0 produit" et message "Recherchez et ajoutez des produits ci-dessous".
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
[TOOLTIPS / HINTS] — 🟠 FRICTION
📍 Localisation : Global — aucun tooltip sur les icônes ou actions
🔍 Problème UX : Icônes sans label au survol. Bouton "Sélectionner un dossier" — pas d'explication sur le comportement récursif.
🏆 Standard concurrent : Stripe : chaque paramètre a une description. Linear : tooltips sur les actions.
⚠️ Impact utilisateur : Découvrabilité faible. Fonctionnalités cachées.
✅ Solution 2026 : title="" ou composant Tooltip sur chaque bouton icon-only. Hint "Recherche les PDF dans tous les sous-dossiers" sur le bouton dossier.
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

**Réponse aux questions :**
- **Un utilisateur BTP non-technique peut-il comprendre l'app en < 2 minutes ?** → **Non.** Aucun onboarding, pas de CTA évident sur les empty states.
- **Que se passe-t-il sur Catalogue si aucun produit ?** → Message "Aucun produit trouvé" sans action suggérée.
- **Y a-t-il un CTA évident pour démarrer ?** → Le bouton "Photographier une facture" sur /scan est visible, mais l'utilisateur peut ne jamais y arriver s'il explore d'abord Catalogue ou Historique.

---

## 2. 🧭 NAVIGATION & INFORMATION ARCHITECTURE

### Problèmes détectés

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
[NAVBAR] — 🟡 POLISH
📍 Localisation : Navbar.jsx — bottom nav fixe
🔍 Problème UX : Ordre : Scanner, Catalogue, Devis, Historique, Réglages. La page Validation n'est pas dans la nav (accessible uniquement après un scan). Pas de logo cliquable.
🏆 Standard concurrent : Linear : cmd+K pour tout. Notion : sidebar avec favoris. L'ordre devrait refléter la fréquence d'usage.
⚠️ Impact utilisateur : Après un scan, l'utilisateur est redirigé vers Validation — pas de lien direct dans la nav. Risque de perte de contexte.
✅ Solution 2026 : Ajouter un indicateur "Validation en attente" dans la nav quand extractedProducts.length > 0. Logo/titre cliquable → /scan.
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
[PAS DE COMMAND PALETTE] — 🟠 FRICTION
📍 Localisation : Global — absent
🔍 Problème UX : Aucun raccourci cmd+K. Navigation entièrement par clics.
🏆 Standard concurrent : Linear, Raycast, Notion : command palette pour naviguer et exécuter des actions.
⚠️ Impact utilisateur : Utilisateurs power users frustrés. Pas de "scanner depuis n'importe où".
✅ Solution 2026 : cmd+K (ou ctrl+K) ouvre une palette avec : "Nouveau scan", "Aller au catalogue", "Comparer les prix", "Créer un devis", etc.
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
[PAS DE BREADCRUMB] — 🟡 POLISH
📍 Localisation : Pages profondes (Validation, Devis, Settings)
🔍 Problème UX : Pas de breadcrumb. Sur mobile, pas de "retour" contextuel.
🏆 Standard concurrent : Vercel : breadcrumb sur les sous-pages.
⚠️ Impact utilisateur : Perte de repères sur les pages secondaires.
✅ Solution 2026 : Breadcrumb discret : Scan > Validation. Ou bouton "Retour au scan" sur Validation.
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
[COMPARAISON CACHÉE] — 🟠 FRICTION
📍 Localisation : CataloguePage.jsx L298-306 — bouton "Comparer" dans le header
🔍 Problème UX : La comparaison de prix est accessible uniquement depuis le Catalogue, via un bouton "Comparer" qui ouvre une modal. Pas visible dans la nav.
🏆 Standard concurrent : Stripe : analytics et comparaisons accessibles depuis le dashboard principal.
⚠️ Impact utilisateur : Fonctionnalité peu découvrable. Combien de clics pour aller du scan à la comparaison ? Scan → Validation → Catalogue → Comparer = 4+ actions.
✅ Solution 2026 : Raccourci dans la nav ou command palette. Ou page dédiée /compare avec accès direct.
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

**Réponse aux questions :**
- **Combien de clics scan → comparaison ?** → Scan → Valider → Catalogue → Clic "Comparer" → Recherche = 5+ clics.
- **Raccourci pour scanner depuis n'importe où ?** → Non.
- **Navigation mobile aussi efficace que desktop ?** → Bottom nav correcte sur mobile, mais pas de swipe ou gestures. Pas de différenciation desktop (sidebar) vs mobile (bottom bar).

---

## 3. 📸 PAGE SCAN — FLUX PRINCIPAL

### Points positifs
- Drag & drop fonctionnel (react-dropzone)
- États : pending, uploading, processing, done, error
- Progress bar par fichier
- Support offline avec queue IndexedDB
- Bouton caméra pour mobile
- Pipeline visuel (upload → ai → validate → save) sur overlay caméra

### Problèmes détectés

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
[DROPZONE NO CLICK] — 🟠 FRICTION
📍 Localisation : ScanPage.jsx L209 — `noClick: true`
🔍 Problème UX : La dropzone n'ouvre pas le sélecteur de fichiers au clic. L'utilisateur doit cliquer sur "Parcourir les fichiers". Sur mobile, zone de drop peu utile.
🏆 Standard concurrent : Stripe : clic sur la zone = ouvrir le picker.
⚠️ Impact utilisateur : Découvrabilité réduite. Le chef de chantier peut ne pas voir le bouton "Parcourir".
✅ Solution 2026 : `noClick: false` pour que le clic sur la zone ouvre le picker. Ou zone plus grande et plus évidente.
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
[MESSAGE TRAITEMENT GÉNÉRIQUE] — 🟡 POLISH
📍 Localisation : ScanPage.jsx L331-336 — "Analyse IA en cours...", "Validation des données..."
🔍 Problème UX : Pas de message granulaire type "Analyse de la page 2/4...". Pas d'estimation de temps.
🏆 Standard concurrent : Vercel : logs en temps réel avec étapes. Stripe : "Uploading... 45% — ~2 min remaining".
⚠️ Impact utilisateur : Anxiété pendant l'attente. Pas de feedback sur la progression réelle.
✅ Solution 2026 : Si l'API renvoie une progression (pages traitées), l'afficher. Sinon : "Analyse en cours... (généralement 30-60 s)".
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
[PAS DE SKELETON LOADER] — 🟡 POLISH
📍 Localisation : ScanPage — spinner Loader2 pendant le traitement
🔍 Problème UX : Spinner générique. Pas de skeleton qui préfigure le contenu (liste de produits).
🏆 Standard concurrent : Linear, Stripe : skeleton loader qui ressemble au contenu final.
⚠️ Impact utilisateur : Perception de lenteur. Pas de préfiguration du résultat.
✅ Solution 2026 : Skeleton de cartes produits pendant le processing. Ou animation de "document en cours d'analyse" avec icône facture.
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
[PAS D'ANNULATION BATCH] — 🟠 FRICTION
📍 Localisation : ScanPage.jsx L272-292 — startBatch
🔍 Problème UX : Une fois "Lancer" cliqué, pas de bouton "Annuler" pour arrêter le traitement en cours.
🏆 Standard concurrent : Vercel : annulation du déploiement. Superhuman : annulation possible.
⚠️ Impact utilisateur : Si l'utilisateur a lancé 20 fichiers par erreur, il doit attendre la fin.
✅ Solution 2026 : Bouton "Annuler" pendant stats.running > 0. Utiliser abortRef pour annuler les requêtes en cours.
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
[TOAST SUCCÈS SANS ACTION] — 🟡 POLISH
📍 Localisation : ScanPage.jsx L291 — toast.success après batch
🔍 Problème UX : Toast "X fichier(s) traité(s) — Y produits ajoutés" sans action "Voir les résultats" ou "Aller à la validation".
🏆 Standard concurrent : Stripe : toast avec bouton "Voir le paiement".
⚠️ Impact utilisateur : L'utilisateur doit naviguer manuellement.
✅ Solution 2026 : toast.success avec action : "Voir le catalogue" ou "Valider les produits". Sonner supporte les actions.
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
[FLUX BATCH vs CAMÉRA INCOHÉRENT] — 🟠 FRICTION
📍 Localisation : ScanPage.jsx
🔍 Problème UX : Caméra → redirection automatique vers /validation. Batch → reste sur /scan, pas de redirection. L'utilisateur doit manuellement aller en validation ou au catalogue.
🏆 Standard concurrent : Flux unifié : après traitement, proposition "Valider" ou "Voir le catalogue".
⚠️ Impact utilisateur : Comportement différent selon le mode (caméra vs batch). Confusion.
✅ Solution 2026 : Après batch terminé, afficher un CTA "Valider les produits" ou "Voir le catalogue" avec redirection. Ou modal "Traitement terminé — Que faire ?" avec 2 boutons.
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

**États couverts :**
- ✅ Idle
- ✅ Uploading
- ✅ Processing
- ✅ Success (done)
- ⚠️ Partial success : pas de distinction visuelle (produits avec confidence low sont visibles en validation, pas en scan)
- ✅ Error
- ✅ Offline

---

## 4. ✅ PAGE VALIDATION — REVIEW & EDIT

### Points positifs
- Champs low confidence visuellement distincts (border amber)
- Édition inline (pas de modal)
- Indicateur "Vérification recommandée" pour low confidence
- Lightbox pour agrandir la facture

### Problèmes détectés

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
[CONFIDENCE SCORE PAS VISIBLE] — 🟠 FRICTION
📍 Localisation : ValidationPage.jsx L116-117 — seulement isLow (confidence === 'low')
🔍 Problème UX : Pas de badge high/medium/low par ligne. Seul "low" est mis en évidence. Pas de score numérique.
🏆 Standard concurrent : Notion AI : suggestions en surbrillance avec accept/reject. Score de confiance visible.
⚠️ Impact utilisateur : L'utilisateur ne sait pas quels champs sont "medium" (incertains mais pas low).
✅ Solution 2026 : Badge coloré par ligne : 🟢 High, 🟡 Medium, 🔴 Low. Ou indicateur discret à côté de chaque champ modifié par l'IA.
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
[PAS DE DIFF DÉTECTÉ vs MODIFIÉ] — 🟡 POLISH
📍 Localisation : ValidationPage.jsx — updateProduct modifie en mémoire
🔍 Problème UX : Aucune distinction visuelle entre "valeur détectée par IA" et "valeur modifiée manuellement".
🏆 Standard concurrent : Google Docs suggestions : vert = ajouté, rouge = supprimé.
⚠️ Impact utilisateur : Impossible de voir ce qui a été corrigé. Pas d'audit trail.
✅ Solution 2026 : Stocker originalValue et marquer les champs modifiés (ex: bordure bleue ou icône "modifié").
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
[PAS DE TOUT VALIDER] — 🟡 POLISH
📍 Localisation : ValidationPage.jsx
🔍 Problème UX : Pas de bouton "Tout valider" ou "Valider sans modification". Chaque produit doit être parcouru.
🏆 Standard concurrent : Notion : "Accept all" sur les suggestions.
⚠️ Impact utilisateur : Si 20 produits et tous corrects, 20 scrolls + 1 clic Enregistrer. Lent.
✅ Solution 2026 : Bouton "Tout valider tel quel" qui enregistre sans modification. Ou "Valider les X produits à haute confiance" en un clic.
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
[PAS D'INDICATEUR DE PROGRESSION] — 🟡 POLISH
📍 Localisation : ValidationPage.jsx L93
🔍 Problème UX : "X produits extraits" mais pas "Y/Z validés" ou "Y modifiés".
🏆 Standard concurrent : Linear : indicateur de progression sur les tâches.
⚠️ Impact utilisateur : Pas de sentiment d'avancement.
✅ Solution 2026 : "5/12 lignes validées" ou "12 produits — 2 modifiés". Résumé avant enregistrement : "15 validés, 2 modifiés, total HT : 4 250€".
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
[PAS DE RACCOURCIS CLAVIER] — 🟡 POLISH
📍 Localisation : ValidationPage.jsx
🔍 Problème UX : Pas de Enter pour valider, Escape pour annuler une édition.
🏆 Standard concurrent : Linear : keyboard-first. Airtable : Enter/Escape sur les cellules.
⚠️ Impact utilisateur : Power users ralentis.
✅ Solution 2026 : Enter = focus champ suivant ou valider. Escape = annuler la modification du champ en cours.
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
[FAMILLES SANS OPTION VIDE] — 🟠 FRICTION
📍 Localisation : ValidationPage.jsx L176-184 — select famille
🔍 Problème UX : Le select utilise FAMILLES qui n'a pas d'option "—" ou vide. Si le produit n'a pas de famille détectée, la première option est sélectionnée par défaut.
🏆 Standard concurrent : Formulaires : option vide pour "Non renseigné".
⚠️ Impact utilisateur : Données incorrectes si l'utilisateur ne vérifie pas.
✅ Solution 2026 : Ajouter <option value="">— Choisir —</option> en premier.
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

---

## 5. 📚 PAGE CATALOGUE — DATA TABLE

### Points positifs
- Recherche temps réel (debounce 400ms)
- Filtres famille + fournisseur
- Tri multi-colonnes
- Vue cartes / tableau
- Export CSV et Excel
- Virtualisation (react-virtual) pour les grandes listes
- Sticky header
- PriceBar (min, moy, max)
- Load more (pagination cursor)

### Problèmes détectés

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
[PAS DE HIGHLIGHT RECHERCHE] — 🟡 POLISH
📍 Localisation : CataloguePage.jsx — recherche
🔍 Problème UX : La recherche filtre les résultats mais ne met pas en surbrillance le terme recherché dans les lignes.
🏆 Standard concurrent : Vercel : highlight des termes dans les résultats. Notion : surlignage.
⚠️ Impact utilisateur : Difficile de voir pourquoi un produit correspond.
✅ Solution 2026 : Highlight du terme recherché dans designation_fr (ex: <mark>ciment</mark>).
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
[COLONNES NON REDIMENSIONNABLES] — 🟡 POLISH
📍 Localisation : CataloguePage.jsx L324-348 — table
🔍 Problème UX : Colonnes en flex/w fixe. Pas de resize.
🏆 Standard concurrent : Airtable : colonnes redimensionnables.
⚠️ Impact utilisateur : Sur desktop, impossible d'adapter la vue.
✅ Solution 2026 : Colonnes redimensionnables (resize handle) ou column visibility toggle.
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
[PAS DE BULK ACTIONS] — 🟠 FRICTION
📍 Localisation : CataloguePage.jsx
🔍 Problème UX : Pas de sélection multiple. Pas de "Supprimer en masse" ou "Exporter la sélection".
🏆 Standard concurrent : Linear : bulk actions sur les issues. Airtable : sélection multiple.
⚠️ Impact utilisateur : Gestion de catalogue fastidieuse pour les nettoyages.
✅ Solution 2026 : Checkbox par ligne + barre d'actions "Supprimer la sélection", "Exporter en CSV".
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
[PAS D'ACTIONS RAPIDES AU HOVER] — 🟡 POLISH
📍 Localisation : CataloguePage.jsx L363-371 (table), L363-384 (cards)
🔍 Problème UX : Au survol d'une ligne/carte, pas d'actions rapides (éditer, comparer, ajouter au devis).
🏆 Standard concurrent : Linear : actions au hover. Notion : menu contextuel.
⚠️ Impact utilisateur : Clics supplémentaires pour chaque action.
✅ Solution 2026 : Row hover : icônes "Comparer", "Ajouter au devis", "Voir l'historique".
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
[FILTRES NON PERSISTANTS] — 🟡 POLISH
📍 Localisation : CataloguePage.jsx L134-135 — famille, fournisseur en state local
🔍 Problème UX : Les filtres sont réinitialisés au rechargement ou changement de page.
🏆 Standard concurrent : Linear : filtres persistants dans l'URL ou localStorage.
⚠️ Impact utilisateur : Re-saisir les filtres à chaque visite.
✅ Solution 2026 : Persister les filtres (URL query params ou localStorage).
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
[PAS DE TAGS VISUELS FILTRES] — 🟡 POLISH
📍 Localisation : CataloguePage.jsx L273-321
🔍 Problème UX : Filtres dans des selects. Pas de chips "Famille: Plomberie ×" pour montrer les filtres actifs.
🏆 Standard concurrent : Vercel : filtres facettes avec tags. Airtable : filter builder visuel.
⚠️ Impact utilisateur : Pas de feedback clair sur les filtres actifs.
✅ Solution 2026 : Chips "Famille: Plomberie ×" et "Fournisseur: BigMat ×" cliquables pour retirer.
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
[EMPTY STATE RECHERCHE] — 🟡 POLISH
📍 Localisation : CataloguePage.jsx L318-322
🔍 Problème UX : "Aucun produit trouvé" s'affiche aussi quand des filtres/recherche excluent tout. Pas de "Réinitialiser les filtres".
🏆 Standard concurrent : Aucun résultat → "Essayez d'élargir votre recherche" + bouton reset.
⚠️ Impact utilisateur : L'utilisateur peut croire que le catalogue est vide.
✅ Solution 2026 : Si search || famille !== 'Toutes' || fournisseur !== 'Tous' : "Aucun résultat pour ces critères. Réinitialiser les filtres ?"
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

---

## 6. 📊 PAGE COMPARAISON PRIX — MODAL

### Points positifs
- Graphique AreaChart (Recharts)
- Tooltips sur le graphique
- Meilleur prix mis en évidence (vert)
- Barre de comparaison relative
- Recherche avec debounce
- Focus trap et Escape

### Problèmes détectés

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
[AXES PEU LISIBLES] — 🟡 POLISH
📍 Localisation : CompareModal.jsx L205-206 — fontSize: 9
🔍 Problème UX : Labels des axes en 9px, peu lisibles sur mobile.
🏆 Standard concurrent : Stripe : graphiques avec labels clairs. Vercel Analytics : axes bien formatés.
⚠️ Impact utilisateur : Difficile de lire les valeurs sur petit écran.
✅ Solution 2026 : Augmenter la taille des labels. Ou responsive : plus grand sur desktop.
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
[PAS DE TENDANCE %] — 🟡 POLISH
📍 Localisation : CompareModal.jsx
🔍 Problème UX : Pas d'indicateur "↑ +12% vs mois dernier" sur les produits.
🏆 Standard concurrent : Vercel Analytics : tendance en % coloré. Stripe : delta de période.
⚠️ Impact utilisateur : L'utilisateur doit interpréter le graphique lui-même.
✅ Solution 2026 : Calculer la variation (premier vs dernier prix) et afficher "↑ +12%" ou "↓ -5%" en vert/rouge.
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
[EMPTY STATE DONNÉES INSUFFISANTES] — 🟡 POLISH
📍 Localisation : CompareModal.jsx L183-186
🔍 Problème UX : "Recherchez un produit pour comparer les prix" quand vide. Mais si résultats avec peu d'historique, pas de message.
🏆 Standard concurrent : Linear : "Pas assez de données pour afficher la tendance".
⚠️ Impact utilisateur : Graphique vide ou avec 1 point = peu informatif.
✅ Solution 2026 : Si chartData.length < 2 : "Historique insuffisant pour afficher la tendance. Scannez plus de factures."
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
[PAS D'EXPORT GRAPHIQUE] — 🔵 DÉLICE
📍 Localisation : CompareModal.jsx
🔍 Problème UX : Pas d'export PNG/PDF du graphique.
🏆 Standard concurrent : Stripe : export des rapports.
⚠️ Impact utilisateur : Impossible de partager la comparaison.
✅ Solution 2026 : Bouton "Exporter en PNG" utilisant html2canvas ou l'API Recharts.
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

---

## 7. 📝 PAGE DEVIS — GÉNÉRATION

### Points positifs
- Recherche produits avec filtre
- Ajout au panier avec quantité
- Calcul total HT
- TVA configurable
- Remise globale % ou €
- Numérotation auto (localStorage)
- Génération PDF (jspdf)

### Problèmes détectés

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
[PAS D'APERÇU PDF TEMPS RÉEL] — 🟠 FRICTION
📍 Localisation : DevisPage.jsx
🔍 Problème UX : Pas de preview PDF pendant la saisie. L'utilisateur génère puis ouvre le PDF pour voir le rendu.
🏆 Standard concurrent : Pennylane, Indy : aperçu PDF live. Stripe Invoicing : preview.
⚠️ Impact utilisateur : Allers-retours pour ajuster la mise en page ou les infos.
✅ Solution 2026 : Split view : formulaire à gauche, iframe ou canvas PDF à droite. Mise à jour en temps réel.
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
[PAS D'AUTOCOMPLETE DEPUIS CATALOGUE] — 🟡 POLISH
📍 Localisation : DevisPage.jsx L246-256 — liste de boutons
🔍 Problème UX : La recherche filtre la liste, mais pas d'autocomplete type combobox (saisie partielle + suggestions).
🏆 Standard concurrent : Formulaires modernes : autocomplete avec dropdown.
⚠️ Impact utilisateur : Scroll dans une liste de 50 produits. Pas de saisie rapide.
✅ Solution 2026 : Input avec dropdown d'autocomplete. Ou combobox accessible.
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
[TVA UNIQUE] — 🟠 FRICTION
📍 Localisation : DevisPage.jsx L15 — tvaRate unique
🔍 Problème UX : Un seul taux TVA pour tout le devis. En BTP : 20% matériaux, 10% travaux, 5.5% rénovation.
🏆 Standard concurrent : Logiciels de devis BTP : TVA par ligne.
⚠️ Impact utilisateur : Devis incorrect pour les chantiers mixtes.
✅ Solution 2026 : Taux TVA par ligne (ou par famille). Ou au minimum : sélecteur "TVA 20% / 10% / 5.5%" avec répartition.
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
[PAS DE SAUVEGARDE BROUILLON] — 🟠 FRICTION
📍 Localisation : DevisPage.jsx
🔍 Problème UX : Pas d'autosave. Si l'utilisateur quitte la page, tout est perdu.
🏆 Standard concurrent : Stripe : brouillons automatiques. Notion : sauvegarde continue.
⚠️ Impact utilisateur : Perte de travail en cas d'erreur ou fermeture accidentelle.
✅ Solution 2026 : Sauvegarder le devis en cours dans localStorage ou backend. Restaurer au retour.
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
[PAS D'ENVOI EMAIL] — 🟡 POLISH
📍 Localisation : DevisPage.jsx — generateDevisPDF
🔍 Problème UX : Le PDF est téléchargé. Pas d'option "Envoyer par email".
🏆 Standard concurrent : Stripe : envoi direct. Pennylane : envoi au client.
⚠️ Impact utilisateur : Workflow manuel : télécharger → ouvrir mail → joindre.
✅ Solution 2026 : Bouton "Envoyer au client" avec champ email. Backend ou mailto: avec pièce jointe (limité).
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
[PDF SANS LOGO] — 🟡 POLISH
📍 Localisation : devisGenerator.js
🔍 Problème UX : Le PDF utilise uniquement le nom de l'entreprise en texte. Pas de logo personnalisable.
🏆 Standard concurrent : Stripe : logo personnalisable. Devis pro : logo en en-tête.
⚠️ Impact utilisateur : PDF peu professionnel pour une entreprise avec charte graphique.
✅ Solution 2026 : Paramètre logo (URL ou base64) dans les options. Affichage en en-tête du PDF.
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
[ORDRE UX DEVIS] — 🟡 POLISH
📍 Localisation : DevisPage.jsx L97-256
🔍 Problème UX : L'ordre est : entreprise/client/n° → panier (si produits) → recherche → liste produits. La recherche est en bas. Sur mobile, l'utilisateur doit scroller pour ajouter des produits.
🏆 Standard concurrent : Flow linéaire : 1) Client 2) Produits 3) Totaux 4) Générer.
⚠️ Impact utilisateur : Ordre contre-intuitif. Le panier devrait être proche de la recherche.
✅ Solution 2026 : Réorganiser : En-tête (entreprise, client, n°) → Recherche + Liste produits (compact) → Panier (sticky ou visible) → Générer.
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

---

## 8. ⚙️ PAGE SETTINGS — CONFIGURATION

### Problèmes détectés (checklist exhaustive)

| Section | Paramètre | Présent | Note |
|---------|-----------|---------|------|
| **Profil & Compte** | Nom/prénom | ❌ | Absent |
| | Email modifiable | ❌ | Absent |
| | Mot de passe | ❌ | Absent |
| | Photo de profil | ❌ | Absent |
| | Suppression compte | ❌ | Absent |
| **Notifications** | Email (scan terminé, etc.) | ❌ | Absent |
| | Push PWA | ❌ | Absent |
| | Fréquence rapports | ❌ | Absent |
| **Intégrations** | Clé API Gemini | ❌ | Hardcodée backend |
| | S3/R2 | ❌ | Backend |
| | Webhook | ❌ | Absent |
| **Apparence** | Thème dark/light/auto | ❌ | Dark only |
| | Langue FR/EN | ❌ | FR only |
| | Format date | ❌ | Absent |
| | Devise/format prix | ❌ | EUR hardcodé |
| **Données** | Export RGPD | ❌ | Absent |
| | Import catalogue CSV/Excel | ❌ | Absent |
| | Reset catalogue | ❌ | Absent |
| **BTP spécifique** | Taux TVA par défaut | ❌ | VITE_TVA_RATE env |
| | Mentions légales devis | ❌ | Absent |
| | Numérotation devis | ❌ | Format fixe DEV-YYYY-NNN |
| | Logo entreprise | ❌ | Absent |

**Ce qui existe :**
- Connexion API (test)
- Modèle IA (Gemini 3 Flash, 3.1 Pro, 2.5 Flash)
- Watchdog/Dossier Magique (si backend le fournit)
- About (version, stack)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
[SETTINGS CRITIQUES MANQUANTS] — 🔴 BLOQUANT
📍 Localisation : SettingsPage.jsx
🔍 Problème UX : Impossible de configurer la clé Gemini, la TVA, le logo, la numérotation des devis depuis l'UI. Tout est en variables d'environnement ou hardcodé.
🏆 Standard concurrent : Linear, Vercel, Stripe : chaque paramètre métier configurable.
⚠️ Impact utilisateur : Déploiement ou modification du code pour changer un paramètre. Bloquant pour un SaaS multi-tenant.
✅ Solution 2026 : Settings organisés par section. Au minimum : TVA par défaut, format numérotation devis, nom entreprise par défaut. Clé API si architecture le permet (sinon backend proxy).
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
[PAS D'EXPORT RGPD] — 🟠 FRICTION
📍 Localisation : Global
🔍 Problème UX : Aucun bouton "Exporter mes données" (obligation RGPD).
🏆 Standard concurrent : Tous les SaaS : export des données personnelles.
⚠️ Impact utilisateur : Non-conformité RGPD. Risque juridique.
✅ Solution 2026 : Bouton "Exporter mes données" dans Settings → Données. Génère un ZIP avec catalogue, historique, paramètres.
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
[PAS DE DARK/LIGHT MODE] — 🟡 POLISH
📍 Localisation : index.css, App.jsx — bg-slate-950 partout
🔍 Problème UX : Thème dark uniquement. Pas de light mode.
🏆 Standard concurrent : Tous les produits 2026 : dark/light/auto.
⚠️ Impact utilisateur : Sur chantier en plein soleil, le dark peut être moins lisible.
✅ Solution 2026 : Toggle thème dans Settings. CSS variables pour les couleurs. Media prefers-color-scheme pour auto.
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

---

## 9. 📱 EXPÉRIENCE MOBILE & PWA

### Points positifs
- Bottom navigation (adaptée mobile)
- PWA avec manifest (standalone, portrait)
- Mode offline avec queue
- Bouton caméra avec capture="environment"
- Safe area (padding-bottom env(safe-area-inset-bottom))
- Touch targets raisonnables

### Problèmes détectés

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
[TABLEAU CATALOGUE SUR MOBILE] — 🟠 FRICTION
📍 Localisation : CataloguePage.jsx L324 — min-w-[800px]
🔍 Problème UX : La vue tableau a une largeur min 800px. Sur mobile, scroll horizontal. Peu lisible.
🏆 Standard concurrent : Notion mobile : vue adaptée. Linear mobile : liste simplifiée.
⚠️ Impact utilisateur : Le chef de chantier sur téléphone doit scroller horizontalement. Vue cartes par défaut serait mieux.
✅ Solution 2026 : Sur mobile (< 640px), forcer la vue cartes par défaut. Ou tableau responsive avec colonnes masquées.
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
[PAS DE BOTTOM SHEET SUR MOBILE] — 🟡 POLISH
📍 Localisation : CompareModal.jsx L126 — rounded-t-3xl sm:rounded-3xl
🔍 Problème UX : La modal comparaison s'adapte (full width bottom sur mobile) mais pas de gestion du swipe down pour fermer.
🏆 Standard concurrent : Modals mobiles : swipe down to close. Bottom sheet pattern.
⚠️ Impact utilisateur : Doit toucher le X pour fermer. Moins naturel.
✅ Solution 2026 : Détecter swipe down pour fermer. Ou handle visuel en haut de la modal.
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
[PAS DE SUGGESTION INSTALLATION PWA] — 🟡 POLISH
📍 Localisation : main.jsx, vite.config.js
🔍 Problème UX : PWA configurée mais pas de prompt "Installer l'application" au bon moment (ex: après 2-3 scans réussis).
🏆 Standard concurrent : PWA best practice : beforeinstallprompt, afficher après engagement.
⚠️ Impact utilisateur : L'utilisateur peut ne jamais installer la PWA.
✅ Solution 2026 : Détecter beforeinstallprompt. Afficher un banner "Installer Docling pour un accès rapide sur votre téléphone" après N scans. Ne pas être intrusif.
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
[QUEUE OFFLINE PEU VISIBLE] — 🟡 POLISH
📍 Localisation : ScanPage.jsx L346-366
🔍 Problème UX : Bandeau "Hors ligne — X en attente" en haut. Mais pas de badge sur l'icône PWA si scans en attente.
🏆 Standard concurrent : Badge sur l'icône d'app si notifications/actions en attente.
⚠️ Impact utilisateur : L'utilisateur peut oublier les fichiers en attente.
✅ Solution 2026 : Badge sur le favicon/manifest si pendingCount > 0. Ou notification "X fichiers en attente de sync".
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
[PAS DE SWIPE ACTIONS] — 🔵 DÉLICE
📍 Localisation : CataloguePage, HistoryPage
🔍 Problème UX : Pas de swipe gauche/droite sur les listes (ex: swipe = supprimer, swipe = comparer).
🏆 Standard concurrent : Linear mobile : swipe actions. Gmail : swipe pour archiver.
⚠️ Impact utilisateur : Actions moins rapides sur mobile.
✅ Solution 2026 : Swipe actions sur les cartes produit et historique. Lib: react-swipeable ou custom.
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

**Réponse :** Le chef de chantier avec mains sales et soleil peut utiliser l'app, mais la vue tableau catalogue sera pénible. La caméra fonctionne. Le bouton "Photographier" est assez grand. Pas de swipe pour les actions rapides.

---

## 10. 🎨 DESIGN SYSTEM & COHÉRENCE VISUELLE

### Points positifs
- Tailwind utilisé de manière cohérente
- Palette slate + emerald + amber
- Lucide React partout (icônes cohérentes)
- Framer Motion pour les animations
- Composants réutilisés (motion.button, etc.)

### Problèmes détectés

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
[PAS DE TOKENS CSS] — 🟡 POLISH
📍 Localisation : index.css — couleurs en dur
🔍 Problème UX : Couleurs en classes Tailwind (slate-950, emerald-500). Pas de variables CSS pour une palette centralisée.
🏆 Standard concurrent : Linear, Stripe : design tokens (--color-primary, --spacing-md).
⚠️ Impact utilisateur : Thème switching impossible. Cohérence maintenue manuellement.
✅ Solution 2026 : CSS variables pour primary, secondary, background, text. Tailwind peut les référencer.
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
[ESPACEMENTS INCONSISTANTS] — 🟡 POLISH
📍 Localisation : Plusieurs pages — p-5, p-4, px-4, etc.
🔍 Problème UX : Mélange de p-5, p-4, px-3, py-2.5. Pas d'échelle stricte (4, 8, 16, 24, 32).
🏆 Standard concurrent : Design systems : scale 4px. 4, 8, 12, 16, 24, 32, 48.
⚠️ Impact utilisateur : Légère incohérence visuelle.
✅ Solution 2026 : Définir une scale (--space-1 à --space-12) et l'utiliser partout.
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
[COMPOSANTS NON ATOMIQUES] — 🟡 POLISH
📍 Localisation : Global — pas de dossier components/ui
🔍 Problème UX : Pas de Button, Input, Badge, Card, Modal réutilisables. Chaque page recrée des styles.
🏆 Standard concurrent : Stripe : composants réutilisables. Design system modulaire.
⚠️ Impact utilisateur : Inconsistances (boutons légèrement différents d'une page à l'autre).
✅ Solution 2026 : Créer Button, Input, Card, Badge, Modal. Variants (primary, secondary, ghost).
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
[LOADING SKELETON GÉNÉRIQUE] — 🟡 POLISH
📍 Localisation : App.jsx L17-22, plusieurs pages
🔍 Problème UX : Spinner unique pour le page loader. Pas de skeleton qui préfigure le contenu.
🏆 Standard concurrent : Linear : skeleton de la liste. Stripe : skeleton du tableau.
⚠️ Impact utilisateur : Perception de lenteur. Pas de structure visible pendant le chargement.
✅ Solution 2026 : Skeleton par page (ex: Catalogue : lignes de tableau en gris animé).
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
[TOAST POSITION] — 🟡 POLISH
📍 Localisation : App.jsx L63-74 — position="top-center"
🔍 Problème UX : Toasts en haut au centre. Standard 2026 : bas droite pour ne pas masquer le header.
🏆 Standard concurrent : Stripe, Linear : bottom-right.
⚠️ Impact utilisateur : Toasts peuvent masquer le titre ou des infos importantes.
✅ Solution 2026 : position="bottom-right" ou "bottom-center".
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

---

## 11. 💬 FEEDBACK & MICRO-INTERACTIONS

### Points positifs
- Toasts (sonner) sur les actions
- Vibrate sur succès (mobile)
- whileTap sur les boutons (framer-motion)
- Animations AnimatePresence sur les listes

### Problèmes détectés

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
[VALIDATION FORMULAIRE AU SUBMIT SEULEMENT] — 🟡 POLISH
📍 Localisation : LoginPage, RegisterPage, DevisPage
🔍 Problème UX : Validation (email, password) au submit. Pas de feedback en temps réel (icône check/x pendant la saisie).
🏆 Standard concurrent : Stripe : validation inline. Champs avec état valid/invalid en direct.
⚠️ Impact utilisateur : Erreurs découvertes tard. Frustration.
✅ Solution 2026 : Validation onBlur ou onChange (debounced). Icône ✓ vert si valide, ✗ rouge si invalide.
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
[PAS DE CONFIRMATION DESTRUCTIVE] — 🟠 FRICTION
📍 Localisation : ScanPage clearQueue, ValidationPage handleRemove, etc.
🔍 Problème UX : Suppression sans confirmation. clearQueue vide toute la file. handleRemove retire un produit sans "Êtes-vous sûr ?".
🏆 Standard concurrent : Actions destructives : modal de confirmation. Stripe : "Delete?" avec input de confirmation pour les actions critiques.
⚠️ Impact utilisateur : Suppression accidentelle. Perte de données.
✅ Solution 2026 : Modal "Vider la file ? X fichiers seront annulés." pour clearQueue. Pour removeProduct, optionnel (moins critique).
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
[SUCCÈS SCAN PEU SATISFAISANT] — 🔵 DÉLICE
📍 Localisation : ScanPage — toast + vibrate
🔍 Problème UX : Toast + vibration. Pas d'animation type checkmark ou confetti.
🏆 Standard concurrent : Superhuman : animation satisfaisante. Linear : micro-animation de succès.
⚠️ Impact utilisateur : Feedback correct mais pas mémorable.
✅ Solution 2026 : Animation checkmark vert qui scale. Ou confetti léger pour un premier scan réussi.
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
[BOUTONS LOADING INCONSISTANTS] — 🟡 POLISH
📍 Localisation : Plusieurs pages
🔍 Problème UX : Parfois spinner, parfois "Enregistrement...". Pas de pattern uniforme.
🏆 Standard concurrent : Bouton → spinner inline + texte "En cours..." + disabled.
⚠️ Impact utilisateur : Cohérence visuelle.
✅ Solution 2026 : Composant Button avec prop loading. Toujours spinner + texte modifié.
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

---

## 12. 🔍 RECHERCHE & DISCOVERABILITY

### Problèmes détectés

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
[PAS DE COMMAND PALETTE] — 🟠 FRICTION
📍 Localisation : Global
🔍 Problème UX : Aucun cmd+K. Pas de recherche globale.
🏆 Standard concurrent : Linear, Notion, Figma : command palette.
⚠️ Impact utilisateur : Navigation lente. Fonctionnalités cachées.
✅ Solution 2026 : cmd+K ouvre une palette. Recherche de pages + actions (Nouveau scan, Comparer, etc.).
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
[PAS DE DOC RACCOURCIS] — 🟡 POLISH
📍 Localisation : Global
🔍 Problème UX : Aucun raccourci clavier documenté. Pas de "?" d'aide.
🏆 Standard concurrent : Raycast : ? pour afficher les raccourcis. Notion : / pour les blocs.
⚠️ Impact utilisateur : Power users ne découvrent pas les raccourcis.
✅ Solution 2026 : ? ou clic sur "Aide" ouvre un modal avec les raccourcis. Au minimum : Escape pour fermer les modals (déjà fait dans CompareModal).
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
[PAS DE TOOLTIPS ICÔNES] — 🟡 POLISH
📍 Localisation : Navbar, boutons icon-only
🔍 Problème UX : NavLink avec icône + texte. Mais boutons comme "Parcourir", "Sélectionner un dossier" ont du texte. Les icônes seules (RefreshCw, etc.) n'ont pas de title.
🏆 Standard concurrent : Chaque icône seule doit avoir un tooltip.
⚠️ Impact utilisateur : Accessibilité. Découvrabilité.
✅ Solution 2026 : aria-label ou title sur tous les boutons icon-only.
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

---

## 📊 LIVRABLES FINAUX

### 1. TABLEAU RÉCAPITULATIF

| Page | Problème | Sévérité | Effort | Priorité |
|------|----------|----------|--------|----------|
| Onboarding | Pas de first-time experience | 🔴 | M | P0 |
| Catalogue | Empty state sans CTA | 🟠 | S | P0 |
| Catalogue | Pas de bulk actions | 🟠 | M | P1 |
| Scan | Flux batch vs caméra incohérent | 🟠 | M | P0 |
| Scan | Pas d'annulation batch | 🟠 | S | P1 |
| Validation | Pas d'option vide famille | 🟠 | S | P0 |
| Validation | Pas de "Tout valider" | 🟡 | M | P2 |
| Devis | Pas d'aperçu PDF temps réel | 🟠 | L | P1 |
| Devis | TVA unique | 🟠 | M | P1 |
| Devis | Pas de sauvegarde brouillon | 🟠 | M | P1 |
| Settings | Paramètres critiques manquants | 🔴 | L | P0 |
| Settings | Pas d'export RGPD | 🟠 | M | P0 |
| Global | Pas de command palette | 🟠 | M | P1 |
| Global | Pas de dark/light mode | 🟡 | M | P2 |
| Mobile | Tableau catalogue non adapté | 🟠 | M | P1 |
| Design | Toast top-center | 🟡 | S | P2 |
| Design | Pas de confirmation destructive | 🟠 | S | P1 |

*Effort : S=petit (<2h), M=moyen (2-8h), L=grand (>8h)*

---

### 2. SCORE UX/UI PAR PAGE /10

| Page | Score | Commentaire |
|------|-------|-------------|
| Page Scan | 6.5/10 | Bonne base, flux batch à améliorer, pas d'annulation |
| Page Validation | 6/10 | Édition correcte, manque indicateurs et raccourcis |
| Page Catalogue | 6.5/10 | Bonne table, manque bulk actions et empty state riche |
| Page Comparaison | 6/10 | Graphique OK, manque tendance % et export |
| Page Devis | 5/10 | Fonctionnel mais pas de preview, TVA unique, pas de brouillon |
| Page Settings | 3/10 | Très limité, paramètres critiques absents |
| Navigation globale | 5.5/10 | Bottom nav correcte, pas de cmd+K, comparaison cachée |
| Mobile/PWA | 6/10 | Utilisable, tableau à adapter, pas de swipe |
| Design system | 5.5/10 | Cohérent mais pas de tokens, pas de composants atomiques |
| **Score global** | **5.8/10** | MVP fonctionnel, en dessous des standards 2026 |

---

### 3. TOP 10 AMÉLIORATIONS PAR IMPACT

1. **Empty states avec CTA** (Catalogue, Historique) — Impact: 🔴 Effort: S — Nouveaux utilisateurs guidés
2. **Flux batch → CTA après traitement** (Scan) — Impact: 🔴 Effort: S — Cohérence du flux
3. **Option vide dans select Famille** (Validation) — Impact: 🟠 Effort: S — Données correctes
4. **Export RGPD + Settings TVA/numérotation** — Impact: 🔴 Effort: M — Conformité et configurabilité
5. **Confirmation avant clearQueue** (Scan) — Impact: 🟠 Effort: S — Éviter pertes accidentelles
6. **Command palette cmd+K** — Impact: 🟠 Effort: M — Power users, découvrabilité
7. **Vue cartes par défaut sur mobile** (Catalogue) — Impact: 🟠 Effort: S — Chef chantier mobile
8. **Sauvegarde brouillon devis** — Impact: 🟠 Effort: M — Éviter perte de travail
9. **Toast avec action "Voir le catalogue"** (Scan) — Impact: 🟡 Effort: S — Navigation rapide
10. **Preview PDF devis** — Impact: 🟠 Effort: L — Qualité perçue

---

### 4. SETTINGS MANQUANTS

**Liste exhaustive des paramètres qui devraient être configurables depuis l'UI :**

- [ ] Nom / prénom utilisateur
- [ ] Email (avec confirmation)
- [ ] Mot de passe
- [ ] Photo de profil
- [ ] Suppression de compte
- [ ] Notifications email (scan terminé, erreur, rapport)
- [ ] Notifications push PWA
- [ ] Fréquence des rapports
- [ ] Clé API Gemini (si architecture multi-tenant)
- [ ] Connexion S3/R2
- [ ] Webhook URL
- [ ] Thème (dark/light/auto)
- [ ] Langue (FR/EN)
- [ ] Format de date
- [ ] Devise et format de prix
- [ ] Export données RGPD
- [ ] Import catalogue CSV/Excel
- [ ] Reset catalogue
- [ ] Taux TVA par défaut (5.5%, 10%, 20%)
- [ ] Mentions légales devis
- [ ] Numérotation devis (préfixe, format)
- [ ] Logo entreprise pour PDF

---

### 5. QUICK WINS (< 2h chacun)

1. **Empty state Catalogue** : Ajouter texte + bouton "Scanner une facture" → /scan
2. **Empty state Historique** : Idem
3. **Option vide Famille** : `<option value="">— Choisir —</option>` en premier dans le select
4. **Toast position** : `position="bottom-right"` dans App.jsx
5. **Dropzone clickable** : `noClick: false` dans useDropzone
6. **Confirmation clearQueue** : `window.confirm` ou modal simple avant clearQueue
7. **Vue cartes par défaut mobile** : `useState(window.innerWidth < 640 ? 'cards' : 'table')`
8. **Toast avec action** : `toast.success('...', { action: { label: 'Voir le catalogue', onClick: () => navigate('/catalogue') } })`
9. **aria-label** sur tous les boutons icon-only (RefreshCw, Trash2, etc.)
10. **Filtres Catalogue** : Si search ou filtre actif et 0 résultats → "Réinitialiser les filtres" avec bouton

---

### 6. ROADMAP UX SUGGÉRÉE

**Sprint 1 (1-2 semaines) — Corrections bloquantes**
- Empty states avec CTA (Catalogue, Historique, Devis)
- Option vide Famille
- Export RGPD (bouton + endpoint backend)
- Settings : TVA par défaut, format numérotation devis
- Flux batch : CTA après traitement (Valider / Catalogue)

**Sprint 2 (2-3 semaines) — Réduction des frictions**
- Command palette cmd+K
- Confirmation actions destructives
- Sauvegarde brouillon devis
- Vue mobile Catalogue (cartes par défaut)
- Toast avec actions
- Annulation batch en cours

**Sprint 3 (3-4 semaines) — Polish et délices**
- Preview PDF devis temps réel
- TVA multi-taux par ligne
- Dark/light mode
- Composants atomiques (Button, Input, Card)
- Skeleton loaders par page
- Swipe actions sur mobile
- Badge PWA si fichiers en attente

---

## 🎯 CONCLUSION

Docling Agent v3 est un **MVP fonctionnel** avec une base technique solide (PWA, offline, virtualisation, animations). Pour atteindre le niveau des référentiels Stripe/Linear/Notion, les priorités sont :

1. **Onboarding et empty states** — Un utilisateur doit comprendre en < 2 min quoi faire
2. **Settings configurables** — TVA, numérotation, export RGPD
3. **Cohérence des flux** — Batch et caméra doivent mener au même résultat
4. **Mobile-first** — Le chef de chantier est la cible : vue adaptée, actions rapides
5. **Design system** — Tokens, composants, thème pour la maintenabilité

L'application peut passer de **5.8/10 à 7.5/10** avec le Sprint 1 et 2. Le Sprint 3 apporterait le polish nécessaire pour rivaliser avec les géants.

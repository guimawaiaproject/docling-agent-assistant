# Rapport d'opportunités Spline — Docling

> Généré par `python scripts/analyze_spline_opportunities.py`

**85 opportunités** détectées.

## Résumé par priorité

- **haute** : 31
- **moyenne** : 34
- **basse** : 20

## Intégrations réalisées

| Page/Composant | Zone | Type | Scène |
|----------------|------|------|-------|
| **ScanPage** | Header | hero | Cube 3D (24×24) |
| **CataloguePage** | Empty state « Aucun produit trouvé » | empty-state | Document/objet minimal |
| **HistoryPage** | Empty state « Aucune facture traitée » | empty-state | Document/objet minimal |
| **CompareModal** | Empty state « Recherchez un produit pour comparer » | empty-state | Document/objet minimal |
| **DevisPage** | Header | hero | Document/objet minimal |
| **SettingsPage** | Header | hero | Document/objet minimal |
| **ValidationPage** | Header | hero | Document/objet minimal |
| **ErrorBoundary** | Zone erreur (remplace icône) | hero | Document/objet minimal |

**Règle appliquée** : max 2 embeds Spline par page. Scène commune : `6Wq1Q7YGyM-iab9i` (document/cube minimal).

### Opportunités restantes (priorité haute)

- **LoginPage** / **RegisterPage** : hero — non prioritaire (accès dev sans login)
- **CataloguePage** : hero titre principal (déjà empty-state intégré)
- **DevisPage** : empty-state quand `selected.length === 0` (toast actuel)
- **ScanPage** : empty-states multiples (pending, dropzone, etc.)
- **Modals** : batch done, lightbox — priorité moyenne

## Détail des opportunités

### docling-pwa\src\App.jsx

- **Ligne 11** — [haute] landing
  - Page scan — hero ou onboarding 3D
  - Extrait : `om './config/features'  const ScanPage       = lazy(() => import('./pa...`

- **Ligne 55** — [haute] landing
  - Page scan — hero ou onboarding 3D
  - Extrait : `<Route path="/scan"       element={<ScanPage />} />                   ...`

### docling-pwa\src\components\CompareModal.jsx

- **Ligne 38** — [haute] empty-state
  - Empty state — illustration 3D légère
  - Extrait : `USABLE)]         if (focusable.length === 0) return         const firs...`

- **Ligne 80** — [haute] empty-state
  - Empty state — illustration 3D légère
  - Extrait : `|| [])       if (data.results?.length === 0) toast.info('Aucun produit...`

- **Ligne 181** — [haute] empty-state
  - Empty state — illustration 3D légère
  - Extrait : `uto p-4">             {results.length === 0 && !loading && (          ...`

### docling-pwa\src\components\ErrorBoundary.jsx

- **Ligne 31** — [haute] hero
  - Titre principal — candidat pour logo 3D ou scène hero
  - Extrait : `</div>              <h1 className="text-xl font-black text-slate-100 m...`

### docling-pwa\src\pages\CataloguePage.jsx

- **Ligne 22** — [haute] empty-state
  - Empty state — illustration 3D légère
  - Extrait : `lter(v => v > 0)    if (prices.length === 0) return null    const min ...`

- **Ligne 252** — [haute] hero
  - Titre principal — candidat pour logo 3D ou scène hero
  - Extrait : `t-emerald-400" />             <h1 className="text-xl font-black text-s...`

- **Ligne 332** — [haute] empty-state
  - Empty state — illustration 3D légère
  - Extrait : `gé') }}             disabled={filtered.length === 0}             class...`

- **Ligne 342** — [haute] empty-state
  - Empty state — illustration 3D légère
  - Extrait : `gé') }}             disabled={filtered.length === 0}             class...`

- **Ligne 367** — [haute] empty-state
  - Empty state — illustration 3D légère
  - Extrait : `" />         </div>       ) : filtered.length === 0 ? (         <div c...`

- **Ligne 373** — [haute] empty-state
  - Message vide — zone pour 3D
  - Extrait : `-lg font-bold text-slate-400">Aucun produit trouvé</h2>             <p...`

- **Ligne 376** — [haute] empty-state
  - Message vide — zone pour 3D
  - Extrait : `rch.trim()                 ? 'Aucun résultat pour ces filtres. Réiniti...`

### docling-pwa\src\pages\DevisPage.jsx

- **Ligne 143** — [haute] empty-state
  - Empty state — illustration 3D légère
  - Extrait : `ate = () => {     if (selected.length === 0) {       toast.error('Ajou...`

- **Ligne 166** — [haute] hero
  - Titre principal — candidat pour logo 3D ou scène hero
  - Extrait : `lassName="pt-4 pb-5">         <h1 className="text-2xl font-black text-...`

### docling-pwa\src\pages\HistoryPage.jsx

- **Ligne 119** — [haute] hero
  - Titre principal — candidat pour logo 3D ou scène hero
  - Extrait : `een">         <div>           <h1 className="text-2xl font-black text-...`

- **Ligne 163** — [haute] empty-state
  - Empty state — illustration 3D légère
  - Extrait : `ariant="history" />       ) : history.length === 0 ? (         <div cl...`

- **Ligne 169** — [haute] empty-state
  - Message vide — zone pour 3D
  - Extrait : `-lg font-bold text-slate-400">Aucune facture traitée</h2>             ...`

### docling-pwa\src\pages\LoginPage.jsx

- **Ligne 57** — [haute] hero
  - Titre principal — candidat pour logo 3D ou scène hero
  - Extrait : `me="w-full max-w-sm">         <h1 className="text-2xl font-black text-...`

### docling-pwa\src\pages\RegisterPage.jsx

- **Ligne 60** — [haute] hero
  - Titre principal — candidat pour logo 3D ou scène hero
  - Extrait : `me="w-full max-w-sm">         <h1 className="text-2xl font-black text-...`

### docling-pwa\src\pages\ScanPage.jsx

- **Ligne 66** — [haute] landing
  - Page scan — hero ou onboarding 3D
  - Extrait : `}, ]  export default function ScanPage() {   const navigate        = u...`

- **Ligne 123** — [haute] empty-state
  - Empty state — illustration 3D légère
  - Extrait : `ndingUploads()     if (pending.length === 0) return     setSyncInProgr...`

- **Ligne 178** — [haute] empty-state
  - Empty state — illustration 3D légère
  - Extrait : `es) => {     if (acceptedFiles.length === 0) return     addToQueue(acc...`

- **Ligne 188** — [haute] empty-state
  - Empty state — illustration 3D légère
  - Extrait : `ry(dirHandle)         if (pdfs.length === 0) {           toast.warning...`

- **Ligne 208** — [haute] empty-state
  - Empty state — illustration 3D légère
  - Extrait : `target.value = ''     if (pdfs.length === 0) {       toast.warning('Au...`

- **Ligne 287** — [haute] empty-state
  - Empty state — illustration 3D légère
  - Extrait : `=== 'pending')     if (pending.length === 0) { toast.error('Aucun fich...`

- **Ligne 552** — [haute] hero
  - Titre principal — candidat pour logo 3D ou scène hero
  - Extrait : `een">         <div>           <h1 className="text-2xl font-black text-...`

### docling-pwa\src\pages\SettingsPage.jsx

- **Ligne 116** — [haute] hero
  - Titre principal — candidat pour logo 3D ou scène hero
  - Extrait : `lassName="pt-4 pb-6">         <h1 className="text-2xl font-black text-...`

### docling-pwa\src\pages\ValidationPage.jsx

- **Ligne 34** — [haute] empty-state
  - Empty state — illustration 3D légère
  - Extrait : `)    if (!products || products.length === 0) {     return <Navigate to...`

- **Ligne 95** — [haute] hero
  - Titre principal — candidat pour logo 3D ou scène hero
  - Extrait : `-4 pb-5 text-center">         <h1 className="text-2xl font-black text-...`

- **Ligne 265** — [haute] empty-state
  - Empty state — illustration 3D légère
  - Extrait : `disabled={isSaving || products.length === 0}           data-testid="va...`

### docling-pwa\src\App.jsx

- **Ligne 12** — [moyenne] workflow
  - Validation — feedback visuel 3D
  - Extrait : `rt('./pages/ScanPage')) const ValidationPage = lazy(() => import('./pa...`

- **Ligne 13** — [moyenne] showcase
  - Catalogue — mockup ou icône 3D
  - Extrait : `pages/ValidationPage')) const CataloguePage  = lazy(() => import('./pa...`

- **Ligne 56** — [moyenne] workflow
  - Validation — feedback visuel 3D
  - Extrait : `<Route path="/validation" element={<ValidationPage />} />             ...`

- **Ligne 57** — [moyenne] showcase
  - Catalogue — mockup ou icône 3D
  - Extrait : `<Route path="/catalogue"  element={<CataloguePage />} />              ...`

### docling-pwa\src\components\CompareModal.jsx

- **Ligne 11** — [moyenne] modal
  - Modal — accent 3D possible
  - Extrait : `xport default function CompareModal({ isOpen, onClose, triggerRef, ini...`

- **Ligne 17** — [moyenne] modal
  - Modal — accent 3D possible
  - Extrait : `nceRef = useRef(null)   const dialogRef = useRef(null)   const previou...`

- **Ligne 35** — [moyenne] modal
  - Modal — accent 3D possible
  - Extrait : `ey === 'Tab') {         const dialog = dialogRef.current         if (!...`

- **Ligne 36** — [moyenne] modal
  - Modal — accent 3D possible
  - Extrait : `ialogRef.current         if (!dialog) return         const focusable =...`

- **Ligne 37** — [moyenne] modal
  - Modal — accent 3D possible
  - Extrait : `const focusable = [...dialog.querySelectorAll(FOCUSABLE)]         if (...`

- **Ligne 132** — [moyenne] modal
  - Modal — accent 3D possible
  - Extrait : `<motion.div           ref={dialogRef}           role="dialog"         ...`

- **Ligne 133** — [moyenne] modal
  - Modal — accent 3D possible
  - Extrait : `f={dialogRef}           role="dialog"           aria-modal="true"     ...`

- **Ligne 134** — [moyenne] modal
  - Modal — accent 3D possible
  - Extrait : `role="dialog"           aria-modal="true"           aria-labelledby="c...`

- **Ligne 135** — [moyenne] modal
  - Modal — accent 3D possible
  - Extrait : `aria-labelledby="compare-modal-title"           initial={{ y: 100, opa...`

- **Ligne 145** — [moyenne] modal
  - Modal — accent 3D possible
  - Extrait : `<h2 id="compare-modal-title" className="text-lg font-black text-slate-...`

### docling-pwa\src\components\SkeletonCard.jsx

- **Ligne 3** — [moyenne] showcase
  - Catalogue — mockup ou icône 3D
  - Extrait : `r*N  * Réutilisable pour App, CataloguePage, HistoryPage  */ export de...`

### docling-pwa\src\pages\CataloguePage.jsx

- **Ligne 12** — [moyenne] modal
  - Modal — accent 3D possible
  - Extrait : `'../config/api' import CompareModal from '../components/CompareModal' ...`

- **Ligne 133** — [moyenne] showcase
  - Catalogue — mockup ou icône 3D
  - Extrait : `100  export default function CataloguePage() {   const navigate = useN...`

- **Ligne 388** — [moyenne] cta
  - CTA principal — icône 3D
  - Extrait : `ge size={16} />               Scanner une facture             </button...`

- **Ligne 532** — [moyenne] modal
  - Modal — accent 3D possible
  - Extrait : `</div>       )}       <CompareModal         isOpen={compareOpen}      ...`

### docling-pwa\src\pages\HistoryPage.jsx

- **Ligne 180** — [moyenne] cta
  - CTA principal — icône 3D
  - Extrait : `kage size={16} />             Scanner une facture           </button> ...`

### docling-pwa\src\pages\ScanPage.jsx

- **Ligne 85** — [moyenne] modal
  - Modal — accent 3D possible
  - Extrait : `bComplete)    const [batchDoneModal, setBatchDoneModal] = useState(nul...`

- **Ligne 304** — [moyenne] modal
  - Modal — accent 3D possible
  - Extrait : `getSource())     setBatchDoneModal({ count: total })     toast.success...`

- **Ligne 395** — [moyenne] modal
  - Modal — accent 3D possible
  - Extrait : `] p-5">        {/* Batch done modal */}       <AnimatePresence>       ...`

- **Ligne 397** — [moyenne] modal
  - Modal — accent 3D possible
  - Extrait : `tePresence>         {batchDoneModal && (           <motion.div        ...`

- **Ligne 403** — [moyenne] modal
  - Modal — accent 3D possible
  - Extrait : `onClick={() => setBatchDoneModal(null)}           >             <motio...`

- **Ligne 415** — [moyenne] modal
  - Modal — accent 3D possible
  - Extrait : `>                   {batchDoneModal.count} produit{batchDoneModal.coun...`

- **Ligne 422** — [moyenne] modal
  - Modal — accent 3D possible
  - Extrait : `onClick={() => { setBatchDoneModal(null); navigate('/validation') }}`

- **Ligne 430** — [moyenne] modal
  - Modal — accent 3D possible
  - Extrait : `onClick={() => { setBatchDoneModal(null); navigate('/catalogue') }}`

- **Ligne 582** — [moyenne] cta
  - CTA principal — icône 3D
  - Extrait : `<Camera size={26} />         Photographier une Facture       </motion....`

- **Ligne 735** — [moyenne] cta
  - CTA principal — icône 3D
  - Extrait : `data-testid="scan-lancer-btn"             className="flex-1 py-4 bg-em...`

- **Ligne 741** — [moyenne] cta
  - CTA principal — icône 3D
  - Extrait : `: <><UploadCloud size={18} /> Lancer ({stats.pending} fichier{stats.pe...`

### docling-pwa\src\pages\ValidationPage.jsx

- **Ligne 13** — [moyenne] workflow
  - Validation — feedback visuel 3D
  - Extrait : `21')  export default function ValidationPage() {   const navigate = us...`

- **Ligne 66** — [moyenne] modal
  - Modal — accent 3D possible
  - Extrait : `<motion.div             role="dialog"             aria-modal="true"   ...`

- **Ligne 67** — [moyenne] modal
  - Modal — accent 3D possible
  - Extrait : `ole="dialog"             aria-modal="true"             aria-label="Ape...`

### docling-pwa\src\components\CompareModal.jsx

- **Ligne 182** — [basse] centered
  - Section centrée — espace pour 3D
  - Extrait : `(               <p className="text-center text-slate-600 text-sm py-8"...`

### docling-pwa\src\components\ErrorBoundary.jsx

- **Ligne 26** — [basse] centered
  - Section centrée — espace pour 3D
  - Extrait : `iv className="max-w-sm w-full text-center">             <div className...`

### docling-pwa\src\components\Navbar.jsx

- **Ligne 20** — [basse] centered
  - Section centrée — espace pour 3D
  - Extrait : `isActive }) =>     `relative flex flex-col items-center gap-1 transiti...`

### docling-pwa\src\pages\CataloguePage.jsx

- **Ligne 368** — [basse] centered
  - Section centrée — espace pour 3D
  - Extrait : `<div className="flex-1 flex flex-col items-center justify-center text-...`

- **Ligne 372** — [basse] centered
  - Section centrée — espace pour 3D
  - Extrait : `iv>           <div className="text-center space-y-2">             <h2 ...`

### docling-pwa\src\pages\DevisPage.jsx

- **Ligne 271** — [basse] centered
  - Section centrée — espace pour 3D
  - Extrait : `font-bold text-slate-200 w-8 text-center">{s.quantite}</span>         ...`

### docling-pwa\src\pages\HistoryPage.jsx

- **Ligne 164** — [basse] centered
  - Section centrée — espace pour 3D
  - Extrait : `0 ? (         <div className="flex flex-col items-center pt-12 text-sl...`

- **Ligne 168** — [basse] centered
  - Section centrée — espace pour 3D
  - Extrait : `iv>           <div className="text-center space-y-2">             <h2 ...`

- **Ligne 274** — [basse] centered
  - Section centrée — espace pour 3D
  - Extrait : `rder-slate-800 rounded-xl p-3 text-center">       <div className={`tex...`

### docling-pwa\src\pages\LoginPage.jsx

- **Ligne 55** — [basse] centered
  - Section centrée — espace pour 3D
  - Extrait : `<div className="min-h-screen flex flex-col items-center justify-center...`

- **Ligne 107** — [basse] centered
  - Section centrée — espace pour 3D
  - Extrait : `>          <p className="mt-6 text-center text-sm text-slate-500">    ...`

### docling-pwa\src\pages\RegisterPage.jsx

- **Ligne 58** — [basse] centered
  - Section centrée — espace pour 3D
  - Extrait : `<div className="min-h-screen flex flex-col items-center justify-center...`

- **Ligne 127** — [basse] centered
  - Section centrée — espace pour 3D
  - Extrait : `>          <p className="mt-6 text-center text-sm text-slate-500">    ...`

### docling-pwa\src\pages\ScanPage.jsx

- **Ligne 412** — [basse] centered
  - Section centrée — espace pour 3D
  - Extrait : `<div className="text-center mb-6">                 <CheckCircle2 size=...`

- **Ligne 449** — [basse] centered
  - Section centrée — espace pour 3D
  - Extrait : `slate-950/95 backdrop-blur-lg flex flex-col items-center justify-cente...`

- **Ligne 590** — [basse] centered
  - Section centrée — espace pour 3D
  - Extrait : `ll duration-200 p-8           flex flex-col items-center justify-cente...`

- **Ligne 602** — [basse] centered
  - Section centrée — espace pour 3D
  - Extrait : `/>         <div className="text-center">           <p className={`font...`

- **Ligne 648** — [basse] centered
  - Section centrée — espace pour 3D
  - Extrait : `g-slate-800/80 rounded-xl p-3 text-center border border-slate-700/50 s...`

### docling-pwa\src\pages\SettingsPage.jsx

- **Ligne 403** — [basse] centered
  - Section centrée — espace pour 3D
  - Extrait : `slate-800/50 rounded-xl p-2.5 text-center">       <div className="flex...`

### docling-pwa\src\pages\ValidationPage.jsx

- **Ligne 94** — [basse] centered
  - Section centrée — espace pour 3D
  - Extrait : `<div className="pt-4 pb-5 text-center">         <h1 className="text-2x...`

## Types de composants Spline recommandés

| Type | Usage | Source |
|------|-------|--------|
| hero | Titre, landing | Library, Community |
| empty-state | États vides | Scène légère, icône 3D |
| logo | Branding | 3D Logo, Spell AI |
| showcase | Produit, démo | 3D Mockup |
| cta | Boutons importants | 3D Icons |

## Prochaines étapes

1. Choisir une opportunité prioritaire
2. Créer ou remixer une scène sur [spline.design](https://spline.design/)
3. Exporter en React et intégrer via l'agent Spline Expert

Référence : `.cursor/agents/spline-expert.md`

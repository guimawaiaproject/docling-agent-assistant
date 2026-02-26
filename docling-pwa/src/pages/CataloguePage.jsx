import { useVirtualizer } from '@tanstack/react-virtual'
import {
    Download, FileSpreadsheet, Filter,
    Loader2, Package, RefreshCw, Search, SortAsc, SortDesc, Users
} from 'lucide-react'
import { useCallback, useEffect, useMemo, useRef, useState } from 'react'
import { toast } from 'sonner'
import * as XLSX from 'xlsx'
import apiClient from '../services/apiClient'
import { ENDPOINTS } from '../config/api'
import CompareModal from '../components/CompareModal'
import { FAMILLES_AVEC_TOUTES } from '../constants/categories'

function PriceBar({ products }) {
  const prices = products
    .map(p => parseFloat(p.prix_remise_ht) || 0)
    .filter(v => v > 0)

  if (prices.length === 0) return null

  const min = Math.min(...prices)
  const max = Math.max(...prices)
  const avg = prices.reduce((a, b) => a + b, 0) / prices.length

  return (
    <div className="flex items-center gap-3 px-1 py-2">
      {[
        { label: 'Min', val: min, color: 'text-emerald-400' },
        { label: 'Moy', val: avg, color: 'text-blue-400' },
        { label: 'Max', val: max, color: 'text-amber-400' },
      ].map(({ label, val, color }) => (
        <div key={label} className="flex items-center gap-1.5">
          <span className="text-[9px] font-bold uppercase tracking-wider text-slate-500">{label}</span>
          <span className={`text-xs font-black ${color}`}>{val.toFixed(2)} €</span>
        </div>
      ))}
    </div>
  )
}

// Colonnes du tableau desktop
const COLUMNS = [
  { key: 'designation_fr',  label: 'Désignation',   width: 'flex-[3]',   sortable: true },
  { key: 'famille',         label: 'Famille',        width: 'flex-[1.5]', sortable: true },
  { key: 'fournisseur',     label: 'Fournisseur',    width: 'flex-[1.5]', sortable: true },
  { key: 'unite',           label: 'Unité',          width: 'w-14',       sortable: false },
  { key: 'prix_brut_ht',    label: 'Brut HT',        width: 'w-20 text-right', sortable: true },
  { key: 'remise_pct',      label: 'Remise',         width: 'w-16 text-right', sortable: false },
  { key: 'prix_remise_ht',  label: 'Net HT',         width: 'w-20 text-right', sortable: true },
  { key: 'prix_ttc_iva21',  label: 'TTC',            width: 'w-20 text-right', sortable: true },
]

// ─── Export CSV pur JS ──────────────────────────────────────────────────────
function exportCSV(data) {
  const headers = ['Désignation FR','Désignation RAW','Famille','Fournisseur','Unité',
                   'Prix Brut HT','Remise %','Prix Net HT','Prix TTC IVA21%',
                   'N° Facture','Date Facture']
  const rows = data.map(p => [
    p.designation_fr, p.designation_raw, p.famille, p.fournisseur, p.unite,
    p.prix_brut_ht, p.remise_pct, p.prix_remise_ht, p.prix_ttc_iva21,
    p.numero_facture, p.date_facture
  ])

  const csvContent = [headers, ...rows]
    .map(row => row.map(cell => {
      let s = String(cell ?? '')
      if (/^[=+\-@\t\r]/.test(s)) s = "'" + s
      return s.includes(',') || s.includes('"') ? `"${s.replace(/"/g, '""')}"` : s
    }).join(','))
    .join('\n')

  const blob = new Blob(['\uFEFF' + csvContent], { type: 'text/csv;charset=utf-8' })
  const url  = URL.createObjectURL(blob)
  const a    = document.createElement('a')
  a.href     = url
  a.download = `catalogue_btp_${new Date().toISOString().slice(0,10)}.csv`
  a.click()
  URL.revokeObjectURL(url)
}

// ─── Export Excel avec xlsx ─────────────────────────────────────────────────
function exportExcel(data) {
  const rows = data.map(p => ({
    'Désignation FR':       p.designation_fr,
    'Désignation RAW':      p.designation_raw,
    'Famille':              p.famille,
    'Fournisseur':          p.fournisseur,
    'Unité':                p.unite,
    'Prix Brut HT (€)':    parseFloat(p.prix_brut_ht) || 0,
    'Remise (%)':           parseFloat(p.remise_pct) || 0,
    'Prix Net HT (€)':     parseFloat(p.prix_remise_ht) || 0,
    'Prix TTC IVA21% (€)': parseFloat(p.prix_ttc_iva21) || 0,
    'N° Facture':           p.numero_facture,
    'Date Facture':         p.date_facture,
  }))

  const ws = XLSX.utils.json_to_sheet(rows)

  // Largeurs colonnes
  ws['!cols'] = [
    {wch:40},{wch:40},{wch:16},{wch:22},{wch:8},
    {wch:14},{wch:10},{wch:14},{wch:14},{wch:16},{wch:14}
  ]

  const wb = XLSX.utils.book_new()
  XLSX.utils.book_append_sheet(wb, ws, 'Catalogue BTP')
  XLSX.writeFile(wb, `catalogue_btp_${new Date().toISOString().slice(0,10)}.xlsx`)
}

export default function CataloguePage() {
  const [allProducts, setAllProducts]   = useState([])
  const [fournisseurs, setFournisseurs] = useState([])
  const [search,      setSearch]        = useState('')
  const [famille,     setFamille]       = useState('Toutes')
  const [fournisseur, setFournisseur]   = useState('Tous')
  const [loading,     setLoading]       = useState(true)
  const [sortKey,     setSortKey]       = useState('designation_fr')
  const [sortDir,     setSortDir]       = useState('asc')
  const [view,        setView]          = useState('cards')
  const [compareOpen, setCompareOpen]   = useState(false)

  const parentRef = useRef(null)
  const compareTriggerRef = useRef(null)

  const fetchCatalogue = useCallback(async () => {
    setLoading(true)
    try {
      const [catRes, fournRes] = await Promise.all([
        apiClient.get(ENDPOINTS.catalogue),
        apiClient.get(ENDPOINTS.fournisseurs),
      ])
      const products = Array.isArray(catRes.data) ? catRes.data : (catRes.data.products || [])
      setAllProducts(products)
      setFournisseurs(fournRes.data.fournisseurs || [])
    } catch {
      toast.error('Impossible de charger le catalogue')
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => { fetchCatalogue() }, [fetchCatalogue])

  const filtered = useMemo(() => {
    let out = [...allProducts]

    if (search.trim()) {
      const q = search.toLowerCase()
      out = out.filter(p =>
        p.designation_fr?.toLowerCase().includes(q) ||
        p.designation_raw?.toLowerCase().includes(q) ||
        p.fournisseur?.toLowerCase().includes(q)
      )
    }

    if (famille !== 'Toutes') {
      out = out.filter(p => p.famille === famille)
    }

    if (fournisseur !== 'Tous') {
      out = out.filter(p => p.fournisseur === fournisseur)
    }

    out.sort((a, b) => {
      const va = a[sortKey] ?? ''
      const vb = b[sortKey] ?? ''
      const num = typeof va === 'number' || !isNaN(parseFloat(va))
      if (num) {
        return sortDir === 'asc'
          ? parseFloat(va) - parseFloat(vb)
          : parseFloat(vb) - parseFloat(va)
      }
      return sortDir === 'asc'
        ? String(va).localeCompare(String(vb), 'fr')
        : String(vb).localeCompare(String(va), 'fr')
    })

    return out
  }, [allProducts, search, famille, fournisseur, sortKey, sortDir])

  // ─── Virtualisation ─────────────────────────────────────────────
  const virtualizer = useVirtualizer({
    count:          filtered.length,
    getScrollElement: () => parentRef.current,
    estimateSize:   () => view === 'table' ? 44 : 88,
    overscan:       8,
  })

  const toggleSort = (key) => {
    if (sortKey === key) setSortDir(d => d === 'asc' ? 'desc' : 'asc')
    else { setSortKey(key); setSortDir('asc') }
  }

  const SortIcon = ({ col }) => {
    if (!col.sortable) return null
    if (sortKey !== col.key) return <SortAsc size={12} className="text-slate-600 ml-1" />
    return sortDir === 'asc'
      ? <SortAsc size={12} className="text-emerald-400 ml-1" />
      : <SortDesc size={12} className="text-emerald-400 ml-1" />
  }

  return (
    <div className="flex flex-col h-screen bg-slate-950">

      {/* ── Header sticky ─────────────────────────────────────── */}
      <div className="shrink-0 px-4 pt-4 pb-3 bg-slate-950 border-b border-slate-800">

        <div className="flex items-center justify-between mb-3">
          <div className="flex items-center gap-2">
            <Package size={20} className="text-emerald-400" />
            <h1 className="text-xl font-black text-slate-100">Catalogue</h1>
            <span className="text-xs font-bold bg-slate-800 text-slate-400 px-2 py-0.5 rounded-full">
              {filtered.length}
            </span>
          </div>

          <div className="flex items-center gap-2">
            {/* Toggle view */}
            <button
              onClick={() => setView(v => v === 'cards' ? 'table' : 'cards')}
              aria-label={view === 'cards' ? 'Passer en vue tableau' : 'Passer en vue cartes'}
              className="text-[10px] font-bold uppercase tracking-wider text-slate-500
                hover:text-slate-300 bg-slate-800 px-2 py-1.5 rounded-lg border border-slate-700 transition-colors"
            >
              {view === 'cards' ? 'Tableau' : 'Cartes'}
            </button>

            <button
              onClick={fetchCatalogue}
              aria-label="Actualiser le catalogue"
              className="p-2 text-slate-500 hover:text-slate-300 bg-slate-800 rounded-lg border border-slate-700 transition-colors"
            >
              <RefreshCw size={14} />
            </button>
          </div>
        </div>

        {/* Recherche + Filtres */}
        <div className="flex gap-2">
          <div className="relative flex-1">
            <label htmlFor="catalogue-search" className="sr-only">Rechercher dans le catalogue</label>
            <Search size={15} className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-500 pointer-events-none" />
            <input
              id="catalogue-search"
              value={search}
              onChange={e => setSearch(e.target.value)}
              placeholder="Recherche..."
              data-testid="catalogue-search"
              className="w-full bg-slate-900 border border-slate-700 rounded-xl py-2.5 pl-9 pr-4
                text-sm text-slate-200 placeholder-slate-600
                focus:outline-none focus:border-emerald-500/60 focus:bg-slate-800 transition-all"
            />
          </div>
          <div className="relative w-24 shrink-0">
            <Filter size={13} className="absolute left-2.5 top-1/2 -translate-y-1/2 text-slate-500 pointer-events-none" />
            <select
              value={famille}
              onChange={e => setFamille(e.target.value)}
              aria-label="Filtrer par famille"
              className="w-full bg-slate-900 border border-slate-700 rounded-xl py-2.5 pl-7 pr-2
                text-xs text-slate-300 font-medium appearance-none
                focus:outline-none focus:border-emerald-500/60 transition-all"
            >
              {FAMILLES_AVEC_TOUTES.map(f => <option key={f} value={f}>{f}</option>)}
            </select>
          </div>
          {fournisseurs.length > 0 && (
            <div className="relative w-24 shrink-0">
              <Users size={13} className="absolute left-2.5 top-1/2 -translate-y-1/2 text-slate-500 pointer-events-none" />
              <select
                value={fournisseur}
                onChange={e => setFournisseur(e.target.value)}
                aria-label="Filtrer par fournisseur"
                className="w-full bg-slate-900 border border-slate-700 rounded-xl py-2.5 pl-7 pr-2
                  text-xs text-slate-300 font-medium appearance-none
                  focus:outline-none focus:border-emerald-500/60 transition-all"
              >
                <option value="Tous">Fournis.</option>
                {fournisseurs.map(f => <option key={f} value={f}>{f}</option>)}
              </select>
            </div>
          )}
        </div>

        <PriceBar products={filtered} />

        {/* Export buttons */}
        <div className="flex gap-2 mt-2">
          <button
            onClick={() => { exportExcel(filtered); toast.success('Export Excel téléchargé') }}
            disabled={filtered.length === 0}
            className="flex items-center gap-1.5 px-3 py-2 bg-emerald-700/30 hover:bg-emerald-700/50
              text-emerald-400 border border-emerald-700/40 rounded-xl text-xs font-bold
              disabled:opacity-30 transition-colors"
          >
            <FileSpreadsheet size={13} />
            Excel
          </button>
          <button
            onClick={() => { exportCSV(filtered); toast.success('Export CSV téléchargé') }}
            disabled={filtered.length === 0}
            className="flex items-center gap-1.5 px-3 py-2 bg-blue-700/30 hover:bg-blue-700/50
              text-blue-400 border border-blue-700/40 rounded-xl text-xs font-bold
              disabled:opacity-30 transition-colors"
          >
            <Download size={13} />
            CSV
          </button>
          <button
            ref={compareTriggerRef}
            onClick={() => setCompareOpen(true)}
            className="flex items-center gap-1.5 px-3 py-2 bg-purple-700/30 hover:bg-purple-700/50
              text-purple-400 border border-purple-700/40 rounded-xl text-xs font-bold
              transition-colors"
          >
            Comparer
          </button>
        </div>
      </div>

      {/* ── Contenu virtualisé ────────────────────────────────── */}
      {loading ? (
        <div className="flex-1 flex items-center justify-center">
          <Loader2 className="w-8 h-8 text-emerald-500 animate-spin" />
        </div>
      ) : filtered.length === 0 ? (
        <div className="flex-1 flex flex-col items-center justify-center text-slate-600 gap-3">
          <Package size={48} className="opacity-20" />
          <p className="text-sm font-medium">Aucun produit trouvé</p>
        </div>
      ) : (
        <div ref={parentRef} className="flex-1 overflow-auto">

          {/* ── VUE TABLE ────────────────────────────────────── */}
          {view === 'table' && (
            <table className="min-w-[800px] w-full border-collapse">
              <thead className="sticky top-0 z-10 bg-slate-900">
                <tr className="border-b border-slate-800">
                  {COLUMNS.map(col => (
                    <th
                      key={col.key}
                      scope="col"
                      onClick={() => col.sortable && toggleSort(col.key)}
                      aria-sort={sortKey === col.key ? (sortDir === 'asc' ? 'ascending' : 'descending') : undefined}
                      className={`${col.width} px-3 py-2 text-left text-[10px] font-black uppercase tracking-widest
                        text-slate-500 hover:text-slate-300 transition-colors ${col.sortable ? 'cursor-pointer' : 'cursor-default'}`}
                    >
                      <span className="flex items-center">
                        {col.label}
                        <SortIcon col={col} />
                      </span>
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody>
                <tr><td colSpan={COLUMNS.length} style={{ height: `${virtualizer.getTotalSize()}px`, position: 'relative', padding: 0 }}>
                  {virtualizer.getVirtualItems().map(vRow => {
                    const p = filtered[vRow.index]
                    return (
                      <div
                        key={vRow.key}
                        role="row"
                        data-index={vRow.index}
                        ref={virtualizer.measureElement}
                        style={{ position: 'absolute', top: 0, left: 0, width: '100%', transform: `translateY(${vRow.start}px)`, display: 'flex' }}
                        className="items-center px-3 py-2.5 border-b border-slate-800/60
                          hover:bg-slate-800/50 transition-colors text-xs"
                      >
                        <span role="cell" className="flex-[3] text-slate-200 font-medium truncate pr-2">{p.designation_fr}</span>
                        <span role="cell" className="flex-[1.5] text-slate-400 truncate pr-2">{p.famille}</span>
                        <span role="cell" className="flex-[1.5] text-slate-500 truncate pr-2">{p.fournisseur}</span>
                        <span role="cell" className="w-14 text-slate-500">{p.unite}</span>
                        <span role="cell" className="w-20 text-right text-slate-400">{parseFloat(p.prix_brut_ht||0).toFixed(2)}</span>
                        <span role="cell" className="w-16 text-right text-amber-500/80">
                          {p.remise_pct > 0 ? `-${p.remise_pct}%` : '—'}
                        </span>
                        <span role="cell" className="w-20 text-right text-emerald-400 font-bold">{parseFloat(p.prix_remise_ht||0).toFixed(2)}</span>
                        <span role="cell" className="w-20 text-right text-slate-400">{parseFloat(p.prix_ttc_iva21||0).toFixed(2)}</span>
                      </div>
                    )
                  })}
                </td></tr>
              </tbody>
            </table>
          )}

          {/* ── VUE CARTES (mobile-first) ─────────────────────── */}
          {view === 'cards' && (
            <div
              style={{ height: `${virtualizer.getTotalSize()}px`, position: 'relative' }}
              className="px-4 pt-2"
            >
              {virtualizer.getVirtualItems().map(vRow => {
                const p = filtered[vRow.index]
                return (
                  <div
                    key={vRow.key}
                    data-index={vRow.index}
                    ref={virtualizer.measureElement}
                    style={{ position: 'absolute', top: 0, left: 0, right: 0, transform: `translateY(${vRow.start}px)` }}
                    className="px-4 py-2"
                  >
                    <div className="p-3.5 bg-slate-900 border border-slate-800 rounded-2xl
                      hover:border-slate-700 transition-colors">
                      <div className="flex justify-between items-start gap-2">
                        <p className="font-bold text-slate-200 text-sm leading-snug flex-1">{p.designation_fr}</p>
                        <div className="text-right shrink-0">
                          <span className="block text-emerald-400 font-black text-base">
                            {parseFloat(p.prix_remise_ht||0).toFixed(2)} €
                          </span>
                          <span className="text-[10px] text-slate-500 font-bold">/{p.unite}</span>
                        </div>
                      </div>

                      <div className="flex items-center gap-2 mt-2.5 flex-wrap">
                        <span className="text-[10px] font-bold uppercase tracking-wider bg-slate-800 text-slate-400 px-2 py-1 rounded-md">
                          {p.famille}
                        </span>
                        <span className="text-xs text-slate-600 font-medium">{p.fournisseur}</span>

                        {p.remise_pct > 0 && (
                          <span className="text-[10px] font-bold text-amber-500 bg-amber-500/10 px-2 py-1 rounded-md ml-auto">
                            -{p.remise_pct}%
                          </span>
                        )}

                        {p.numero_facture && (
                          <span className="text-[10px] text-slate-600 truncate max-w-[90px]">
                            #{p.numero_facture}
                          </span>
                        )}
                      </div>
                    </div>
                  </div>
                )
              })}
            </div>
          )}
        </div>
      )}
      <CompareModal
        isOpen={compareOpen}
        onClose={() => setCompareOpen(false)}
        triggerRef={compareTriggerRef}
      />
    </div>
  )
}

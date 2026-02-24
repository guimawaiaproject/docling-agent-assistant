import axios from 'axios'
import { AnimatePresence, motion } from 'framer-motion'
import { Filter, Loader2, Package, Search } from 'lucide-react'
import { useEffect, useState } from 'react'
import { ENDPOINTS } from '../config/api'

const FAMILLES = ['Toutes','Armature','Cloison','Climatisation','Plomberie',
  'Électricité','Menuiserie','Couverture','Carrelage','Isolation','Peinture','Outillage','Consommable','Autre']

export default function CataloguePage() {
  const [products, setProducts] = useState([])
  const [search, setSearch] = useState('')
  const [famille, setFamille] = useState('Toutes')
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    // Petit debounce manuel simple pour éviter de spammer l'API à chaque frappe
    const delayDebounce = setTimeout(() => {
      fetchCatalogue()
    }, 300)
    return () => clearTimeout(delayDebounce)
  }, [search, famille])

  const fetchCatalogue = async () => {
    setLoading(true)
    try {
      const params = {}
      if (search) params.search = search
      if (famille !== 'Toutes') params.famille = famille

      const { data } = await axios.get(ENDPOINTS.catalogue, { params })
      setProducts(data.products || []) // data.products selon ton retour API (Pilier 2)
    } catch (err) {
      console.error(err)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="p-4 bg-slate-50 min-h-screen">
      <div className="sticky top-0 bg-slate-50/90 backdrop-blur-md pt-2 pb-4 z-10">
        <h1 className="text-2xl font-black text-slate-800 flex items-center gap-2 mb-4">
          <Package className="text-blue-600" />
          Catalogue
          <span className="text-sm font-medium bg-blue-100 text-blue-700 px-2 py-0.5 rounded-full ml-auto">
            {products.length} réf.
          </span>
        </h1>

        <div className="flex gap-2">
          <div className="relative flex-1">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" size={18} />
            <input
              value={search}
              onChange={e => setSearch(e.target.value)}
              placeholder="Ciment, treillis..."
              className="w-full border border-slate-200 bg-white rounded-xl py-3 pl-10 pr-4 text-sm font-medium text-slate-800 focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 transition-all shadow-sm"
            />
          </div>

          <div className="relative w-1/3 min-w-[110px]">
            <Filter className="absolute left-2.5 top-1/2 -translate-y-1/2 text-slate-400 pointer-events-none" size={16} />
            <select
              value={famille}
              onChange={e => setFamille(e.target.value)}
              className="w-full border border-slate-200 bg-white rounded-xl py-3 pl-8 pr-2 text-sm font-medium text-slate-700 focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 transition-all shadow-sm appearance-none"
            >
              {FAMILLES.map(f => <option key={f} value={f}>{f}</option>)}
            </select>
          </div>
        </div>
      </div>

      <div className="mt-2 space-y-3 pb-8">
        <AnimatePresence mode="popLayout">
          {loading ? (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="flex justify-center pt-12"
            >
              <Loader2 className="w-8 h-8 text-blue-500 animate-spin" />
            </motion.div>
          ) : products.length === 0 ? (
            <motion.div
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              className="text-center pt-12 text-slate-400"
            >
              <Package size={48} className="mx-auto mb-3 opacity-20" />
              <p>Aucun produit trouvé</p>
            </motion.div>
          ) : (
            products.map((p, i) => (
              <motion.div
                layout
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.2, delay: Math.min(i * 0.03, 0.3) }}
                key={p.id}
                className="p-4 border border-slate-100 rounded-2xl bg-white shadow-[0_2px_10px_-3px_rgba(0,0,0,0.05)]"
              >
                <div className="flex justify-between items-start gap-3">
                  <h3 className="font-bold text-slate-800 text-sm leading-snug flex-1">
                    {p.designation_fr}
                  </h3>
                  <div className="text-right shrink-0">
                    <span className="block text-green-600 font-black text-base whitespace-nowrap">
                      {parseFloat(p.prix_remise_ht).toFixed(2)} €
                    </span>
                    <span className="text-[10px] text-slate-400 font-bold uppercase tracking-wider">
                      / {p.unite}
                    </span>
                  </div>
                </div>

                <div className="flex items-center gap-2 mt-3 pt-3 border-t border-slate-50">
                  <span className="text-[10px] uppercase font-bold tracking-wider bg-slate-100 text-slate-600 px-2 py-1 rounded-md">
                    {p.famille}
                  </span>
                  <span className="text-xs font-medium text-slate-400 truncate">
                    {p.fournisseur}
                  </span>
                </div>
              </motion.div>
            ))
          )}
        </AnimatePresence>
      </div>
    </div>
  )
}

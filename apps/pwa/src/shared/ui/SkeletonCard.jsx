/**
 * Skeleton loader — pattern Emmet : div.rounded-xl.border*N
 * Réutilisable pour App, CataloguePage, HistoryPage
 */
export default function SkeletonCard({ count = 4, variant = 'card' }) {
  const configs = {
    card: {
      grid: 'grid gap-4 grid-cols-1 sm:grid-cols-2',
      item: 'rounded-xl bg-slate-800/80 border border-slate-700/50 overflow-hidden',
      image: 'h-24 bg-slate-700/50 animate-pulse',
      body: 'p-4 space-y-2',
      line1: 'h-4 bg-slate-700/50 rounded animate-pulse',
      line2: 'h-3 bg-slate-700/50 rounded animate-pulse',
      widths: { line1: '80%', line2: '50%' },
    },
    catalogue: {
      grid: 'grid gap-3 p-2 sm:grid-cols-2',
      item: 'rounded-xl bg-slate-800/60 border border-slate-700/50 overflow-hidden animate-pulse',
      image: 'h-20 bg-slate-700/50',
      body: 'p-3 space-y-2',
      line1: 'h-4 bg-slate-700/50 rounded w-[80%]',
      line2: 'h-3 bg-slate-700/50 rounded w-[50%]',
    },
    history: {
      grid: 'grid gap-3 sm:grid-cols-2 pt-4',
      item: 'rounded-xl bg-slate-800/60 border border-slate-700/50 p-4 animate-pulse',
      image: null,
      body: 'space-y-0',
      line1: 'h-4 bg-slate-700/50 rounded w-[75%] mb-3',
      line2: 'h-3 bg-slate-700/50 rounded w-[50%]',
    },
  }

  const c = configs[variant] || configs.card
  const items = Array.from({ length: count }, (_, i) => i + 1)

  return (
    <div className={c.grid} role="status" aria-label="Chargement">
      {items.map((itemId) => (
        <div key={`skeleton-${variant}-${itemId}`} className={c.item}>
          {c.image && <div className={c.image} />}
          <div className={c.body}>
            <div className={c.line1} {...(c.widths && { style: { width: c.widths.line1 } })} />
            <div className={c.line2} {...(c.widths && { style: { width: c.widths.line2 } })} />
          </div>
        </div>
      ))}
    </div>
  )
}

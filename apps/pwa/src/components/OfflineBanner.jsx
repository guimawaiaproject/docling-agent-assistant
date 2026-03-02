/**
 * Bannière fixe en haut de l'écran : fichiers en attente (hors ligne).
 * Visible sur toutes les pages quand offline ou pending > 0.
 */
import { AlertCircle, PackagePlus } from 'lucide-react'
import { useCallback, useEffect, useState } from 'react'
import { getPendingCount } from '@/shared/lib/offlineQueue'

export default function OfflineBanner() {
  const [pendingCount, setPendingCount] = useState(0)
  const [isOnline, setIsOnline] = useState(typeof navigator !== 'undefined' ? navigator.onLine : true)

  const refresh = useCallback(async () => {
    try {
      const count = await getPendingCount()
      setPendingCount(count)
    } catch {
      setPendingCount(0)
    }
  }, [])

  useEffect(() => {
    const onOnline = () => {
      setIsOnline(true)
      refresh()
    }
    const onOffline = () => setIsOnline(false)
    const onQueueUpdated = () => refresh()
    window.addEventListener('online', onOnline)
    window.addEventListener('offline', onOffline)
    window.addEventListener('docling-offline-queue-updated', onQueueUpdated)
    queueMicrotask(() => refresh())
    return () => {
      window.removeEventListener('online', onOnline)
      window.removeEventListener('offline', onOffline)
      window.removeEventListener('docling-offline-queue-updated', onQueueUpdated)
    }
  }, [refresh])

  if (isOnline && pendingCount === 0) return null

  return (
    <div
      className="fixed top-0 left-0 right-0 z-[60] flex items-center justify-center gap-2
        bg-amber-600/90 backdrop-blur-xl text-white text-sm font-bold px-4 py-2.5
        border-b border-amber-500/40 shadow-lg"
      role="status"
      aria-live="polite"
    >
      {!isOnline ? (
        <>
          <AlertCircle size={18} />
          Hors ligne — {pendingCount} fichier(s) en attente
        </>
      ) : (
        <>
          <PackagePlus size={18} />
          {pendingCount} fichier(s) en attente — synchronisation automatique au retour en ligne
        </>
      )}
    </div>
  )
}

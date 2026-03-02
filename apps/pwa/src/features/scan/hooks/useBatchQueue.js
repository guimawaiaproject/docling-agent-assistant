import { useMemo } from 'react'
import { useDoclingStore } from '../../../store/useStore'

/**
 * Hook pour la gestion de la file d'attente batch (scan).
 * Utilise le store Zustand.
 */
export function useBatchQueue() {
  const batchQueue = useDoclingStore((s) => s.batchQueue)
  const addToQueue = useDoclingStore((s) => s.addToQueue)
  const updateItem = useDoclingStore((s) => s.updateQueueItem)
  const removeFromQueue = useDoclingStore((s) => s.removeFromQueue)
  const clearQueue = useDoclingStore((s) => s.clearQueue)

  const stats = useMemo(
    () => ({
      total: batchQueue.length,
      pending: batchQueue.filter((i) => i.status === 'pending').length,
      done: batchQueue.filter((i) => i.status === 'done').length,
      error: batchQueue.filter((i) => i.status === 'error').length,
      running: batchQueue.filter((i) => ['uploading', 'processing'].includes(i.status)).length,
    }),
    [batchQueue]
  )

  const totalProducts = useMemo(
    () => batchQueue.reduce((acc, i) => acc + (i.productsAdded || 0), 0),
    [batchQueue]
  )

  return {
    batchQueue,
    stats,
    totalProducts,
    addToQueue,
    updateItem,
    removeFromQueue,
    clearQueue,
  }
}

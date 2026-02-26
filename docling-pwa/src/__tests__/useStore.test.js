import { beforeEach, describe, expect, test } from 'vitest'
import { useDoclingStore, AI_MODELS } from '../store/useStore'

// Helper: reset store between tests
function resetStore() {
  useDoclingStore.setState({
    selectedModel: 'gemini-3-flash-preview',
    currentJob: null,
    extractedProducts: [],
    currentInvoice: null,
    batchQueue: [],
  })
}

describe('useDoclingStore', () => {
  beforeEach(() => {
    resetStore()
  })

  // ── Model selection ──────────────────────────────────────────────────────
  describe('model selection', () => {
    test('default model is gemini-3-flash-preview', () => {
      const { selectedModel } = useDoclingStore.getState()
      expect(selectedModel).toBe('gemini-3-flash-preview')
    })

    test('setModel updates selectedModel', () => {
      useDoclingStore.getState().setModel('gemini-2.5-flash')
      expect(useDoclingStore.getState().selectedModel).toBe('gemini-2.5-flash')
    })

    test('AI_MODELS exports at least one model with recommended flag', () => {
      expect(AI_MODELS.length).toBeGreaterThan(0)
      const recommended = AI_MODELS.filter((m) => m.recommended)
      expect(recommended.length).toBeGreaterThanOrEqual(1)
    })
  })

  // ── Job lifecycle ─────────────────────────────────────────────────────────
  describe('job lifecycle', () => {
    test('setJobStart stores jobId and fileUrl', () => {
      useDoclingStore.getState().setJobStart('job-abc', 'blob://preview.pdf')
      const state = useDoclingStore.getState()
      expect(state.currentJob).toBe('job-abc')
      expect(state.currentInvoice).toBe('blob://preview.pdf')
      expect(state.extractedProducts).toEqual([])
    })

    test('setJobComplete stores products and clears currentJob', () => {
      useDoclingStore.getState().setJobStart('job-xyz', 'blob://x.pdf')
      useDoclingStore.getState().setJobComplete([
        { id: 1, designation_fr: 'Ciment', fournisseur: 'BigMat', prix_remise_ht: 12.5 },
      ])
      const state = useDoclingStore.getState()
      expect(state.extractedProducts).toHaveLength(1)
      expect(state.extractedProducts[0].designation_fr).toBe('Ciment')
      expect(state.currentJob).toBeNull()
    })

    test('setJobComplete with null/undefined products produces empty array', () => {
      useDoclingStore.getState().setJobComplete(null)
      expect(useDoclingStore.getState().extractedProducts).toEqual([])
    })

    test('each product gets a _key assigned', () => {
      useDoclingStore.getState().setJobComplete([
        { designation_fr: 'Tube cuivre', fournisseur: 'Metalp', prix_remise_ht: 5 },
      ])
      const [p] = useDoclingStore.getState().extractedProducts
      expect(p._key).toBeDefined()
      expect(typeof p._key).toBe('string')
    })

    test('clearJob resets currentJob, extractedProducts, currentInvoice', () => {
      useDoclingStore.getState().setJobStart('j1', 'blob://f.pdf')
      useDoclingStore.getState().clearJob()
      const state = useDoclingStore.getState()
      expect(state.currentJob).toBeNull()
      expect(state.extractedProducts).toEqual([])
      expect(state.currentInvoice).toBeNull()
    })
  })

  // ── Product operations ────────────────────────────────────────────────────
  describe('product operations', () => {
    beforeEach(() => {
      useDoclingStore.getState().setJobComplete([
        { id: 10, designation_fr: 'Ciment 42.5R', fournisseur: 'BigMat', prix_remise_ht: 11 },
        { id: 11, designation_fr: 'Sable 0/4', fournisseur: 'Lafarge', prix_remise_ht: 8 },
      ])
    })

    test('updateProduct modifies a single field by index', () => {
      useDoclingStore.getState().updateProduct(0, 'prix_remise_ht', 9.99)
      const products = useDoclingStore.getState().extractedProducts
      expect(products[0].prix_remise_ht).toBe(9.99)
      expect(products[1].prix_remise_ht).toBe(8)
    })

    test('removeProduct removes item by index and shifts others', () => {
      useDoclingStore.getState().removeProduct(0)
      const products = useDoclingStore.getState().extractedProducts
      expect(products).toHaveLength(1)
      expect(products[0].designation_fr).toBe('Sable 0/4')
    })
  })

  // ── Batch queue ───────────────────────────────────────────────────────────
  describe('batch queue', () => {
    const makeFile = (name, size = 1024) =>
      new File(['x'.repeat(size)], name, { type: 'application/pdf' })

    test('addToQueue adds new files', () => {
      const files = [makeFile('a.pdf'), makeFile('b.pdf')]
      useDoclingStore.getState().addToQueue(files)
      const { batchQueue } = useDoclingStore.getState()
      expect(batchQueue).toHaveLength(2)
      expect(batchQueue[0].status).toBe('pending')
    })

    test('addToQueue deduplicates by name+size', () => {
      const file = makeFile('dup.pdf', 2048)
      useDoclingStore.getState().addToQueue([file])
      useDoclingStore.getState().addToQueue([file])
      expect(useDoclingStore.getState().batchQueue).toHaveLength(1)
    })

    test('updateQueueItem patches a specific item', () => {
      const file = makeFile('update.pdf')
      useDoclingStore.getState().addToQueue([file])
      const { id } = useDoclingStore.getState().batchQueue[0]
      useDoclingStore.getState().updateQueueItem(id, { status: 'processing', progress: 50 })
      const item = useDoclingStore.getState().batchQueue[0]
      expect(item.status).toBe('processing')
      expect(item.progress).toBe(50)
    })

    test('removeFromQueue removes item by id', () => {
      useDoclingStore.getState().addToQueue([makeFile('rm.pdf')])
      const { id } = useDoclingStore.getState().batchQueue[0]
      useDoclingStore.getState().removeFromQueue(id)
      expect(useDoclingStore.getState().batchQueue).toHaveLength(0)
    })

    test('clearQueue empties the queue', () => {
      useDoclingStore.getState().addToQueue([makeFile('x.pdf'), makeFile('y.pdf')])
      useDoclingStore.getState().clearQueue()
      expect(useDoclingStore.getState().batchQueue).toHaveLength(0)
    })

    test('retryItem resets error items to pending', () => {
      useDoclingStore.getState().addToQueue([makeFile('retry.pdf')])
      const { id } = useDoclingStore.getState().batchQueue[0]
      useDoclingStore.getState().updateQueueItem(id, { status: 'error', error: 'oops' })
      useDoclingStore.getState().retryItem(id)
      const item = useDoclingStore.getState().batchQueue.find((i) => i.id === id)
      expect(item.status).toBe('pending')
      expect(item.error).toBeNull()
    })

    test('retryAllErrors resets all error items', () => {
      useDoclingStore.getState().addToQueue([makeFile('e1.pdf'), makeFile('e2.pdf')])
      const ids = useDoclingStore.getState().batchQueue.map((i) => i.id)
      ids.forEach((id) =>
        useDoclingStore.getState().updateQueueItem(id, { status: 'error', error: 'fail' })
      )
      useDoclingStore.getState().retryAllErrors()
      const statuses = useDoclingStore.getState().batchQueue.map((i) => i.status)
      expect(statuses.every((s) => s === 'pending')).toBe(true)
    })
  })
})

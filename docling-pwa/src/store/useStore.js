import { create } from 'zustand'
import { devtools, persist } from 'zustand/middleware'

export const AI_MODELS = [
  { id: 'gemini-3-flash-preview',     label: 'Gemini 3 Flash',      badge: 'Ultra-Rapide',    recommended: true },
  { id: 'gemini-3.1-pro-preview',     label: 'Gemini 3.1 Pro',      badge: 'Precision Max',   recommended: false },
  { id: 'gemini-2.5-flash',           label: 'Gemini 2.5 Flash',    badge: 'Stable',          recommended: false },
]

let _idCounter = 0

export const useDoclingStore = create(
  devtools(
    persist(
      (set, get) => ({

        selectedModel: 'gemini-3-flash-preview',
        setModel: (modelId) => set({ selectedModel: modelId }),

        currentJob: null,
        extractedProducts: [],
        currentInvoice: null,
        pendingSource: 'pc',

        setJobStart: (jobId, fileUrl) => set({
          currentJob: jobId,
          currentInvoice: fileUrl,
          extractedProducts: []
        }),

        setJobComplete: (products, source = 'pc') => set({
          extractedProducts: (products || []).map((p, i) => ({
            ...p,
            _key: p.id ?? p._key ?? `val-${(p.designation_raw || p.designation_fr || '').slice(0, 30)}-${(p.fournisseur || '').slice(0, 20)}-${i}-${Date.now()}`
          })),
          currentJob: null,
          pendingSource: source
        }),

        updateProduct: (index, field, value) => set((state) => ({
          extractedProducts: state.extractedProducts.map((p, i) =>
            i === index ? { ...p, [field]: value } : p
          )
        })),

        clearJob: () => set({
          currentJob: null,
          extractedProducts: [],
          currentInvoice: null,
          pendingSource: 'pc'
        }),

        removeProduct: (index) => set((state) => ({
          extractedProducts: state.extractedProducts.filter((_, i) => i !== index)
        })),

        // ---------- BATCH QUEUE (optimised) ----------
        batchQueue: [],

        addToQueue: (files) => set((state) => {
          const existing = new Set(state.batchQueue.map(i => `${i.name}__${i.size}`))
          const fresh = files.filter(f => !existing.has(`${f.name}__${f.size}`))
          if (fresh.length === 0) return state
          return {
            batchQueue: [
              ...state.batchQueue,
              ...fresh.map((file) => ({
                id: `b${Date.now()}-${++_idCounter}`,
                file,
                compressedFile: null,
                name: file.name,
                size: file.size,
                status: 'pending',
                progress: 0,
                error: null,
                productsAdded: 0,
              }))
            ]
          }
        }),

        setCompressed: (id, compressedFile) => set((state) => ({
          batchQueue: state.batchQueue.map((item) =>
            item.id === id ? { ...item, compressedFile, status: 'pending' } : item
          )
        })),

        updateQueueItem: (id, patch) => set((state) => ({
          batchQueue: state.batchQueue.map((item) =>
            item.id === id ? { ...item, ...patch } : item
          )
        })),

        retryItem: (id) => set((state) => ({
          batchQueue: state.batchQueue.map((item) =>
            item.id === id && item.status === 'error'
              ? { ...item, status: 'pending', progress: 0, error: null }
              : item
          )
        })),

        retryAllErrors: () => set((state) => ({
          batchQueue: state.batchQueue.map((item) =>
            item.status === 'error'
              ? { ...item, status: 'pending', progress: 0, error: null }
              : item
          )
        })),

        clearQueue: () => set({ batchQueue: [] }),

        removeFromQueue: (id) => set((state) => ({
          batchQueue: state.batchQueue.filter((item) => item.id !== id)
        })),
      }),

      {
        name: 'docling-storage-v2',
        partialize: (state) => ({
          selectedModel: state.selectedModel,
        })
      }
    ),
    { name: 'DoclingStore' }
  )
)

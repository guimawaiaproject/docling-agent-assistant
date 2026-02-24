import { create } from 'zustand'
import { devtools, persist } from 'zustand/middleware'

export const useDoclingStore = create(
  devtools(
    persist(
      (set) => ({
        // État de l'analyse en cours
        currentJob: null,
        extractedProducts: [],
        currentInvoice: null,

        // Actions
        setJobStart: (jobId, fileUrl) => set({
          currentJob: jobId,
          currentInvoice: fileUrl,
          extractedProducts: []
        }),

        setJobComplete: (products) => set({
          extractedProducts: products,
          currentJob: null
        }),

        updateProduct: (index, field, value) => set((state) => ({
          extractedProducts: state.extractedProducts.map((p, i) =>
            i === index ? { ...p, [field]: value } : p
          )
        })),

        clearJob: () => set({
          currentJob: null,
          extractedProducts: [],
          currentInvoice: null
        })
      }),
      {
        name: 'docling-storage',
      }
    )
  )
)

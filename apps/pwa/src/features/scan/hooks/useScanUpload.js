import { useCallback, useEffect, useRef, useState } from 'react'
import { useDropzone } from 'react-dropzone'
import { useNavigate } from 'react-router-dom'
import { toast } from 'sonner'
import apiClient from '@/shared/lib/apiClient'
import { ENDPOINTS } from '@/shared/config/api'
import { compressToWebP } from '@/shared/lib/imageService'
import {
  enqueueUpload,
  getPendingCount,
  getPendingUploads,
  removePendingUpload,
} from '@/shared/lib/offlineQueue'
import { useDoclingStore } from '../../../store/useStore'
import { useBatchQueue } from './useBatchQueue'

const CONCURRENCY = 3

function getSource() {
  const ua = navigator.userAgent || ''
  const isMobile = /Android|iPhone|iPad|iPod|webOS|BlackBerry|IEMobile|Opera Mini/i.test(ua)
  return isMobile ? 'mobile' : 'pc'
}

/** Collecte récursivement tous les PDF d'un FileSystemDirectoryHandle */
async function collectPdfsFromDirectory(handle) {
  const files = []
  for await (const [, entry] of handle.entries()) {
    if (entry.kind === 'file') {
      const name = entry.name || ''
      if (name.toLowerCase().endsWith('.pdf')) {
        files.push(await entry.getFile())
      }
    } else if (entry.kind === 'directory') {
      const subFiles = await collectPdfsFromDirectory(entry)
      files.push(...subFiles)
    }
  }
  return files
}

export const supportsDirectoryPicker =
  typeof window !== 'undefined' && 'showDirectoryPicker' in window

/**
 * Hook pour la logique d'upload (dropzone, dossier, caméra) et traitement API.
 */
export function useScanUpload() {
  const navigate = useNavigate()
  const folderInputRef = useRef()
  const isProcessingRef = useRef(false)
  const abortRef = useRef(null)

  const selectedModel = useDoclingStore((s) => s.selectedModel)
  const setJobStart = useDoclingStore((s) => s.setJobStart)
  const setJobComplete = useDoclingStore((s) => s.setJobComplete)

  const {
    batchQueue,
    stats,
    totalProducts,
    addToQueue,
    updateItem,
    removeFromQueue,
    clearQueue,
  } = useBatchQueue()

  const [batchDoneModal, setBatchDoneModal] = useState(null)
  const [cameraOverlay, setCameraOverlay] = useState(null)
  const prevPreviewRef = useRef(null)

  const [pendingCount, setPendingCount] = useState(0)
  const [syncInProgress, setSyncInProgress] = useState(false)
  const [isOnline, setIsOnline] = useState(
    typeof navigator !== 'undefined' ? navigator.onLine : true
  )

  useEffect(() => {
    return () => {
      abortRef.current?.abort()
    }
  }, [])

  const refreshPendingCount = useCallback(async () => {
    try {
      const count = await getPendingCount()
      setPendingCount(count)
    } catch {
      setPendingCount(0)
    }
  }, [])

  const syncPendingUploads = useCallback(async () => {
    if (!navigator.onLine || syncInProgress) return
    const pending = await getPendingUploads()
    if (pending.length === 0) return
    setSyncInProgress(true)
    toast.info(`Synchronisation de ${pending.length} fichier(s)...`)
    for (const item of pending) {
      try {
        const file = new File(
          [item.fileData],
          item.fileName || 'facture',
          { type: item.fileType || 'application/pdf' }
        )
        const toUpload = file.type.startsWith('image/')
          ? await compressToWebP(file)
          : file
        const formData = new FormData()
        formData.append('file', toUpload)
        formData.append('model', item.model || selectedModel)
        formData.append('source', item.source || getSource())
        await apiClient.post(ENDPOINTS.process, formData)
        await removePendingUpload(item.id)
        toast.success(`${item.fileName} synchronisé`)
      } catch (err) {
        if (err.response?.status === 401) {
          toast.error('Reconnectez-vous pour synchroniser vos fichiers en attente')
          break
        }
        toast.error(`Erreur sync ${item.fileName}: ${err.message}`)
      }
    }
    setSyncInProgress(false)
    await refreshPendingCount()
  }, [refreshPendingCount, selectedModel, syncInProgress])

  useEffect(() => {
    refreshPendingCount()
  }, [refreshPendingCount])

  useEffect(() => {
    const onOnline = async () => {
      setIsOnline(true)
      await refreshPendingCount()
      const count = await getPendingCount()
      if (count > 0) {
        syncPendingUploads()
      }
    }
    const onOffline = () => setIsOnline(false)
    window.addEventListener('online', onOnline)
    window.addEventListener('offline', onOffline)
    return () => {
      window.removeEventListener('online', onOnline)
      window.removeEventListener('offline', onOffline)
    }
  }, [refreshPendingCount, syncPendingUploads])

  useEffect(() => {
    const url = cameraOverlay?.previewUrl
    if (prevPreviewRef.current && prevPreviewRef.current !== url) {
      URL.revokeObjectURL(prevPreviewRef.current)
    }
    prevPreviewRef.current = url || null
    return () => {
      if (prevPreviewRef.current) {
        URL.revokeObjectURL(prevPreviewRef.current)
        prevPreviewRef.current = null
      }
    }
  }, [cameraOverlay?.previewUrl])

  const onDrop = useCallback(
    (acceptedFiles) => {
      if (acceptedFiles.length === 0) return
      addToQueue(acceptedFiles)
    },
    [addToQueue]
  )

  const handleSelectFolder = useCallback(async () => {
    if (supportsDirectoryPicker) {
      try {
        const dirHandle = await window.showDirectoryPicker({ mode: 'read' })
        toast.info('Scan des PDF en cours...')
        const pdfs = await collectPdfsFromDirectory(dirHandle)
        if (pdfs.length === 0) {
          toast.warning('Aucun fichier PDF trouvé dans ce dossier')
          return
        }
        addToQueue(pdfs)
        toast.success(`${pdfs.length} PDF ajouté${pdfs.length > 1 ? 's' : ''} à la file`)
      } catch (err) {
        if (err.name === 'AbortError') return
        toast.error(`Dossier : ${err.message}`)
      }
    } else if (folderInputRef?.current) {
      folderInputRef.current.accept = '.pdf'
      folderInputRef.current.click()
    }
  }, [addToQueue])

  const handleFolderInputChange = useCallback(
    (e) => {
      const files = e.target.files ? Array.from(e.target.files) : []
      const pdfs = files.filter((f) => f.name.toLowerCase().endsWith('.pdf'))
      e.target.value = ''
      if (pdfs.length === 0) {
        toast.warning('Aucun fichier PDF trouvé dans ce dossier')
        return
      }
      addToQueue(pdfs)
      toast.success(`${pdfs.length} PDF ajouté${pdfs.length > 1 ? 's' : ''} à la file`)
    },
    [addToQueue]
  )

  const { getRootProps, getInputProps, isDragActive, open } = useDropzone({
    onDrop,
    accept: {
      'application/pdf': ['.pdf'],
      'image/*': ['.jpg', '.jpeg', '.png', '.webp'],
    },
    multiple: true,
    maxSize: 200 * 1024 * 1024,
    noClick: false,
  })

  const processItem = useCallback(
    async (item, pollIntervalMs = 5000) => {
      const ctrl = new AbortController()
      abortRef.current = ctrl
      try {
        if (!navigator.onLine) {
          await enqueueUpload(item.file, selectedModel, getSource())
          removeFromQueue(item.id)
          await refreshPendingCount()
          toast.info(`${item.name || item.file?.name} en attente de synchronisation`)
          return
        }
        updateItem(item.id, { status: 'uploading', progress: 10 })
        const fileToUpload = item.file.type.startsWith('image/')
          ? await compressToWebP(item.file)
          : item.file
        updateItem(item.id, { progress: 30 })

        const formData = new FormData()
        formData.append('file', fileToUpload)
        formData.append('model', selectedModel)
        formData.append('source', getSource())
        updateItem(item.id, { status: 'processing', progress: 50 })

        const { data: jobInfo } = await apiClient.post(ENDPOINTS.process, formData, {
          signal: ctrl.signal,
        })
        if (!jobInfo.job_id) throw new Error('Pas de Job ID reçu')

        let attempts = 0
        const maxAttempts = 60
        while (attempts < maxAttempts) {
          const { data: status } = await apiClient.get(ENDPOINTS.status(jobInfo.job_id), {
            signal: ctrl.signal,
          })
          if (status.status === 'completed') {
            const products = status.result?.products || []
            updateItem(item.id, {
              status: 'done',
              progress: 100,
              productsAdded: products.length,
              products,
              facture_id: status.result?.facture_id,
              pdf_url: status.result?.pdf_url,
            })
            return
          }
          if (status.status === 'error') {
            throw new Error(status.error || "Erreur lors de l'extraction IA")
          }
          const waitProgress = 50 + Math.min(45, attempts * 2)
          updateItem(item.id, { progress: waitProgress })
          attempts++
          await new Promise((r) => setTimeout(r, pollIntervalMs))
        }
        throw new Error("Timeout : l'analyse prend trop de temps")
      } catch (err) {
        if (err.name === 'CanceledError' || ctrl.signal.aborted) {
          updateItem(item.id, { status: 'pending', progress: 0 })
          return
        }
        updateItem(item.id, {
          status: 'error',
          progress: 0,
          error: err.message || 'Erreur inconnue',
        })
      }
    },
    [
      selectedModel,
      updateItem,
      removeFromQueue,
      refreshPendingCount,
    ]
  )

  const startBatch = useCallback(async () => {
    if (isProcessingRef.current) return
    const pending = batchQueue.filter((i) => i.status === 'pending')
    if (pending.length === 0) {
      toast.error('Aucun fichier en attente')
      return
    }

    isProcessingRef.current = true
    const pollMs = pending.length > 10 ? 8000 : 5000
    toast.info(`Traitement de ${pending.length} fichier(s)...`)

    for (let i = 0; i < pending.length; i += CONCURRENCY) {
      const chunk = pending.slice(i, i + CONCURRENCY)
      await Promise.all(chunk.map((item) => processItem(item, pollMs)))
    }

    isProcessingRef.current = false
    const queue = useDoclingStore.getState().batchQueue
    const done = queue.filter((i) => i.status === 'done').length
    const total = queue.reduce((acc, i) => acc + (i.productsAdded || 0), 0)
    const allProducts = queue.filter((i) => i.status === 'done').flatMap((i) => i.products || [])
    if (allProducts.length > 0) setJobComplete(allProducts, getSource())
    setBatchDoneModal({ count: total })
    toast.success(`${done} fichier(s) traité(s) — ${total} produits extraits`, {
      action: {
        label: 'Voir le catalogue',
        onClick: () => navigate('/catalogue'),
      },
    })
    if (navigator.vibrate) navigator.vibrate([100, 50, 100])
  }, [batchQueue, processItem, setJobComplete, navigate])

  const handleCameraFile = useCallback(
    async (e) => {
      const file = e.target.files[0]
      e.target.value = ''
      if (!file) return

      abortRef.current?.abort()
      const ctrl = new AbortController()
      abortRef.current = ctrl

      const fileUrl = URL.createObjectURL(file)
      setCameraOverlay({ previewUrl: fileUrl, step: 'upload', error: null })
      setJobStart('camera', fileUrl)

      if (!navigator.onLine) {
        try {
          await enqueueUpload(file, selectedModel, getSource())
          await refreshPendingCount()
          setCameraOverlay(null)
          toast.success('Photo enregistrée, sera synchronisée au retour en ligne')
        } catch (err) {
          setCameraOverlay((prev) => ({ ...prev, step: 'error', error: err.message }))
          toast.error(`Erreur : ${err.message}`)
        }
        return
      }

      try {
        const toUpload = await compressToWebP(file)
        setCameraOverlay((prev) => ({ ...prev, step: 'ai' }))

        const formData = new FormData()
        formData.append('file', toUpload)
        formData.append('model', selectedModel)
        formData.append('source', getSource())

        const { data: jobInfo } = await apiClient.post(ENDPOINTS.process, formData, {
          signal: ctrl.signal,
        })
        if (!jobInfo.job_id) throw new Error('Pas de Job ID reçu')

        setCameraOverlay((prev) => ({ ...prev, step: 'validate' }))

        let attempts = 0
        while (attempts < 60) {
          const { data: status } = await apiClient.get(ENDPOINTS.status(jobInfo.job_id), {
            signal: ctrl.signal,
          })
          if (status.status === 'completed') {
            setCameraOverlay((prev) => ({ ...prev, step: 'done' }))
            setJobComplete(status.result.products, getSource())
            if (navigator.vibrate) navigator.vibrate([100, 50, 100])
            await new Promise((r) => setTimeout(r, 600))
            setCameraOverlay(null)
            navigate('/validation', { replace: true })
            return
          }
          if (status.status === 'error') throw new Error(status.error)
          attempts++
          await new Promise((r) => setTimeout(r, 3000))
        }
        throw new Error('Timeout caméra')
      } catch (err) {
        if (err.name === 'CanceledError' || ctrl.signal.aborted) return
        setCameraOverlay((prev) => ({ ...prev, step: 'error', error: err.message }))
        toast.error(`Erreur : ${err.message}`)
        setTimeout(() => setCameraOverlay(null), 3000)
      }
    },
    [selectedModel, setJobStart, setJobComplete, refreshPendingCount, navigate]
  )

  return {
    getRootProps,
    getInputProps,
    isDragActive,
    open,
    folderInputRef,
    onDrop,
    handleSelectFolder,
    handleFolderInputChange,
    processItem,
    startBatch,
    handleCameraFile,
    batchQueue,
    stats,
    totalProducts,
    addToQueue,
    updateItem,
    removeFromQueue,
    clearQueue,
    batchDoneModal,
    setBatchDoneModal,
    cameraOverlay,
    pendingCount,
    syncInProgress,
    isOnline,
  }
}

import { AnimatePresence, motion } from 'framer-motion'
import { AlertCircle, Camera, CheckCircle2, FolderOpen, FileUp, Loader2, PackagePlus, Trash2, UploadCloud, X, Zap, Database, Sparkles } from 'lucide-react'
import { useCallback, useEffect, useRef, useState } from 'react'
import { useDropzone } from 'react-dropzone'
import { useNavigate } from 'react-router-dom'
import { toast } from 'sonner'
import apiClient from '../services/apiClient'
import { ENDPOINTS } from '../config/api'
import { compressToWebP } from '../services/imageService'
import {
  enqueueUpload,
  getPendingCount,
  getPendingUploads,
  removePendingUpload,
} from '../services/offlineQueue'
import { useDoclingStore } from '../store/useStore'

const CONCURRENCY = 3

function getSource() {
  const ua = navigator.userAgent || ''
  const isMobile = /Android|iPhone|iPad|iPod|webOS|BlackBerry|IEMobile|Opera Mini/i.test(ua)
  return isMobile ? 'mobile' : 'pc'
}

function formatSize(bytes) {
  if (bytes < 1024) return `${bytes} o`
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(0)} Ko`
  return `${(bytes / 1024 / 1024).toFixed(1)} Mo`
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

const supportsDirectoryPicker = typeof window !== 'undefined' && 'showDirectoryPicker' in window

const STATUS_CONFIG = {
  pending:    { color: 'text-slate-400', bg: 'bg-slate-800',   label: 'En attente' },
  uploading:  { color: 'text-blue-400',  bg: 'bg-blue-500/20', label: 'Envoi...' },
  processing: { color: 'text-amber-400', bg: 'bg-amber-500/20',label: 'Analyse IA...' },
  done:       { color: 'text-emerald-400',bg: 'bg-emerald-500/20', label: 'Termin\u00e9' },
  error:      { color: 'text-red-400',   bg: 'bg-red-500/20',  label: 'Erreur' },
}

const PIPELINE_STEPS = [
  { key: 'upload',    label: 'Envoi',       icon: UploadCloud },
  { key: 'ai',        label: 'Analyse IA',  icon: Sparkles },
  { key: 'validate',  label: 'Validation',  icon: Zap },
  { key: 'save',      label: 'Sauvegarde',  icon: Database },
]

export default function ScanPage() {
  const navigate        = useNavigate()
  const inputRef        = useRef()
  const folderInputRef  = useRef()
  const isProcessingRef = useRef(false)
  const abortRef        = useRef(null)

  useEffect(() => {
    return () => { abortRef.current?.abort() }
  }, [])

  const batchQueue     = useDoclingStore(s => s.batchQueue)
  const addToQueue     = useDoclingStore(s => s.addToQueue)
  const updateItem     = useDoclingStore(s => s.updateQueueItem)
  const removeFromQueue= useDoclingStore(s => s.removeFromQueue)
  const clearQueue     = useDoclingStore(s => s.clearQueue)
  const setJobStart    = useDoclingStore(s => s.setJobStart)
  const setJobComplete = useDoclingStore(s => s.setJobComplete)
  const selectedModel  = useDoclingStore(s => s.selectedModel)

  // Camera overlay state
  const [cameraOverlay, setCameraOverlay] = useState(null)
  const prevPreviewRef = useRef(null)

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

  // Offline sync state
  const [pendingCount, setPendingCount] = useState(0)
  const [syncInProgress, setSyncInProgress] = useState(false)
  const [isOnline, setIsOnline] = useState(typeof navigator !== 'undefined' ? navigator.onLine : true)

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

  const onDrop = useCallback((acceptedFiles) => {
    if (acceptedFiles.length === 0) return
    addToQueue(acceptedFiles)
  }, [addToQueue])

  const handleSelectFolder = async () => {
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
  }

  const handleFolderInputChange = (e) => {
    const files = e.target.files ? Array.from(e.target.files) : []
    const pdfs = files.filter(f => f.name.toLowerCase().endsWith('.pdf'))
    e.target.value = ''
    if (pdfs.length === 0) {
      toast.warning('Aucun fichier PDF trouvé dans ce dossier')
      return
    }
    addToQueue(pdfs)
    toast.success(`${pdfs.length} PDF ajouté${pdfs.length > 1 ? 's' : ''} à la file`)
  }

  const { getRootProps, getInputProps, isDragActive, open } = useDropzone({
    onDrop,
    accept: {
      'application/pdf': ['.pdf'],
      'image/*': ['.jpg', '.jpeg', '.png', '.webp']
    },
    multiple: true,
    maxSize: 200 * 1024 * 1024,
    noClick: true
  })

  const processItem = async (item, pollIntervalMs = 5000) => {
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

      const { data: jobInfo } = await apiClient.post(ENDPOINTS.process, formData, { signal: ctrl.signal })
      if (!jobInfo.job_id) throw new Error('Pas de Job ID re\u00e7u')

      let attempts = 0
      const maxAttempts = 60
      while (attempts < maxAttempts) {
        const { data: status } = await apiClient.get(ENDPOINTS.status(jobInfo.job_id), { signal: ctrl.signal })
        if (status.status === 'completed') {
          updateItem(item.id, {
            status: 'done', progress: 100,
            productsAdded: status.result?.products?.length || 0
          })
          return
        }
        if (status.status === 'error') {
          throw new Error(status.error || "Erreur lors de l'extraction IA")
        }
        const waitProgress = 50 + Math.min(45, attempts * 2)
        updateItem(item.id, { progress: waitProgress })
        attempts++
        await new Promise(r => setTimeout(r, pollIntervalMs))
      }
      throw new Error("Timeout : l'analyse prend trop de temps")
    } catch (err) {
      if (err.name === 'CanceledError' || ctrl.signal.aborted) return
      updateItem(item.id, { status: 'error', progress: 0, error: err.message || 'Erreur inconnue' })
    }
  }

  const startBatch = async () => {
    if (isProcessingRef.current) return
    const pending = batchQueue.filter(i => i.status === 'pending')
    if (pending.length === 0) { toast.error('Aucun fichier en attente'); return }

    isProcessingRef.current = true
    const pollMs = pending.length > 10 ? 8000 : 5000
    toast.info(`Traitement de ${pending.length} fichier(s)...`)

    for (let i = 0; i < pending.length; i += CONCURRENCY) {
      const chunk = pending.slice(i, i + CONCURRENCY)
      await Promise.all(chunk.map(item => processItem(item, pollMs)))
    }

    isProcessingRef.current = false
    const queue = useDoclingStore.getState().batchQueue
    const done  = queue.filter(i => i.status === 'done').length
    const total = queue.reduce((acc, i) => acc + (i.productsAdded || 0), 0)
    toast.success(`${done} fichier(s) trait\u00e9(s) \u2014 ${total} produits ajout\u00e9s`)
    if (navigator.vibrate) navigator.vibrate([100, 50, 100])
  }

  const handleCameraFile = async (e) => {
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
        setCameraOverlay(prev => ({ ...prev, step: 'error', error: err.message }))
        toast.error(`Erreur : ${err.message}`)
      }
      return
    }

    try {
      const toUpload = await compressToWebP(file)
      setCameraOverlay(prev => ({ ...prev, step: 'ai' }))

      const formData = new FormData()
      formData.append('file', toUpload)
      formData.append('model', selectedModel)
      formData.append('source', getSource())

      const { data: jobInfo } = await apiClient.post(ENDPOINTS.process, formData, { signal: ctrl.signal })
      if (!jobInfo.job_id) throw new Error('Pas de Job ID re\u00e7u')

      setCameraOverlay(prev => ({ ...prev, step: 'validate' }))

      let attempts = 0
      while (attempts < 60) {
        const { data: status } = await apiClient.get(ENDPOINTS.status(jobInfo.job_id), { signal: ctrl.signal })
        if (status.status === 'completed') {
          setCameraOverlay(prev => ({ ...prev, step: 'done' }))
          setJobComplete(status.result.products)
          if (navigator.vibrate) navigator.vibrate([100, 50, 100])
          await new Promise(r => setTimeout(r, 600))
          setCameraOverlay(null)
          navigate('/validation', { replace: true })
          return
        }
        if (status.status === 'error') throw new Error(status.error)
        attempts++
        await new Promise(r => setTimeout(r, 3000))
      }
      throw new Error('Timeout cam\u00e9ra')
    } catch (err) {
      if (err.name === 'CanceledError' || ctrl.signal.aborted) return
      setCameraOverlay(prev => ({ ...prev, step: 'error', error: err.message }))
      toast.error(`Erreur : ${err.message}`)
      setTimeout(() => setCameraOverlay(null), 3000)
    }
  }

  const stats = {
    total:   batchQueue.length,
    pending: batchQueue.filter(i => i.status === 'pending').length,
    done:    batchQueue.filter(i => i.status === 'done').length,
    error:   batchQueue.filter(i => i.status === 'error').length,
    running: batchQueue.filter(i => ['uploading','processing'].includes(i.status)).length,
  }
  const totalProducts = batchQueue.reduce((acc, i) => acc + (i.productsAdded || 0), 0)

  const currentStepIdx = cameraOverlay
    ? PIPELINE_STEPS.findIndex(s => s.key === cameraOverlay.step)
    : -1

  return (
    <div className="min-h-screen bg-slate-950 p-5">

      {/* Camera processing overlay */}
      <AnimatePresence>
        {cameraOverlay && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 z-50 bg-slate-950/95 backdrop-blur-lg flex flex-col items-center justify-center p-6"
          >
            {/* Preview image */}
            <motion.div
              initial={{ scale: 0.9, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              className="w-full max-w-xs rounded-3xl overflow-hidden border-2 border-slate-700 mb-8 shadow-2xl"
            >
              <img src={cameraOverlay.previewUrl} alt="Facture" className="w-full h-48 object-cover" />
            </motion.div>

            {/* Pipeline steps */}
            <div className="flex items-center gap-2 mb-6">
              {PIPELINE_STEPS.map((s, i) => {
                const Icon = s.icon
                const isActive = i === currentStepIdx
                const isDone = i < currentStepIdx || cameraOverlay.step === 'done'
                const isError = cameraOverlay.step === 'error' && i === currentStepIdx

                return (
                  <div key={s.key} className="flex items-center gap-2">
                    <motion.div
                      animate={isActive ? { scale: [1, 1.15, 1] } : {}}
                      transition={isActive ? { repeat: Infinity, duration: 1.2 } : {}}
                      className={`w-10 h-10 rounded-full flex items-center justify-center transition-all duration-300 ${
                        isError ? 'bg-red-500/20 border-2 border-red-500' :
                        isDone ? 'bg-emerald-500/20 border-2 border-emerald-500' :
                        isActive ? 'bg-blue-500/20 border-2 border-blue-500' :
                        'bg-slate-800 border-2 border-slate-700'
                      }`}
                    >
                      {isDone && !isActive ? (
                        <CheckCircle2 size={18} className="text-emerald-400" />
                      ) : isError ? (
                        <AlertCircle size={18} className="text-red-400" />
                      ) : (
                        <Icon size={18} className={isActive ? 'text-blue-400' : 'text-slate-500'} />
                      )}
                    </motion.div>
                    {i < PIPELINE_STEPS.length - 1 && (
                      <div className={`w-6 h-0.5 rounded-full transition-colors duration-300 ${
                        i < currentStepIdx ? 'bg-emerald-500' : 'bg-slate-700'
                      }`} />
                    )}
                  </div>
                )
              })}
            </div>

            {/* Step label */}
            <motion.p
              key={cameraOverlay.step}
              initial={{ opacity: 0, y: 5 }}
              animate={{ opacity: 1, y: 0 }}
              className={`text-sm font-bold ${
                cameraOverlay.step === 'error' ? 'text-red-400' :
                cameraOverlay.step === 'done' ? 'text-emerald-400' :
                'text-slate-300'
              }`}
            >
              {cameraOverlay.step === 'upload' && 'Compression et envoi...'}
              {cameraOverlay.step === 'ai' && 'Analyse IA en cours...'}
              {cameraOverlay.step === 'validate' && 'Validation des donn\u00e9es...'}
              {cameraOverlay.step === 'save' && 'Sauvegarde en base...'}
              {cameraOverlay.step === 'done' && 'Extraction termin\u00e9e !'}
              {cameraOverlay.step === 'error' && (cameraOverlay.error || 'Erreur inconnue')}
            </motion.p>

            {cameraOverlay.step !== 'error' && cameraOverlay.step !== 'done' && (
              <Loader2 size={24} className="text-blue-400 animate-spin mt-4" />
            )}
          </motion.div>
        )}
      </AnimatePresence>

      {/* Offline / Sync indicator */}
      {(!isOnline || pendingCount > 0 || syncInProgress) && (
        <div className="mb-4 flex items-center gap-2 px-4 py-2.5 rounded-xl border
          bg-amber-500/10 border-amber-500/30 text-amber-400 text-sm font-semibold">
          {!isOnline && (
            <>
              <AlertCircle size={18} />
              Hors ligne — {pendingCount} en attente
            </>
          )}
          {isOnline && syncInProgress && (
            <>
              <Loader2 size={18} className="animate-spin" />
              Synchronisation en cours...
            </>
          )}
          {isOnline && !syncInProgress && pendingCount > 0 && (
            <>
              <PackagePlus size={18} />
              {pendingCount} fichier(s) en attente — sync automatique
            </>
          )}
        </div>
      )}

      {/* Header */}
      <div className="pt-4 pb-5 flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-black text-slate-100 tracking-tight">Docling Agent</h1>
          <p className="text-xs text-slate-500 mt-0.5 font-medium uppercase tracking-widest">
            Scanner de Factures BTP
          </p>
        </div>
        {batchQueue.length > 0 && (
          <motion.span
            initial={{ scale: 0 }}
            animate={{ scale: 1 }}
            className="text-xs font-black bg-emerald-500/20 text-emerald-400 px-3 py-1.5 rounded-full"
          >
            {stats.done}/{stats.total}
          </motion.span>
        )}
      </div>

      {/* Camera button */}
      <motion.button
        whileTap={{ scale: 0.97 }}
        onClick={() => {
          if (!inputRef?.current) return
          inputRef.current.accept = 'image/*'
          inputRef.current.setAttribute('capture', 'environment')
          inputRef.current.click()
        }}
        className="w-full mb-4 py-5 bg-gradient-to-r from-blue-600 to-indigo-600 rounded-3xl
          flex items-center justify-center gap-3 text-lg font-bold text-white
          shadow-[0_0_30px_rgba(99,102,241,0.3)] active:shadow-none transition-shadow"
      >
        <Camera size={26} />
        Photographier une Facture
      </motion.button>

      {/* DropZone */}
      <div
        {...getRootProps()}
        data-testid="scan-dropzone"
        className={`relative rounded-3xl border-2 border-dashed transition-all duration-200 p-6
          flex flex-col items-center justify-center gap-3 mb-5 cursor-default
          ${isDragActive
            ? 'border-emerald-500 bg-emerald-500/10 scale-[1.01]'
            : 'border-slate-700 bg-slate-900/50 hover:border-slate-600'
          }`}
      >
        <input {...getInputProps()} />
        <UploadCloud
          size={36}
          className={`transition-colors ${isDragActive ? 'text-emerald-400' : 'text-slate-600'}`}
        />
        <div className="text-center">
          <p className={`font-bold text-sm ${isDragActive ? 'text-emerald-300' : 'text-slate-400'}`}>
            {isDragActive ? 'Rel\u00e2chez pour ajouter' : 'Glisser-d\u00e9poser des PDF / images'}
          </p>
          <p className="text-xs text-slate-600 mt-1">ou s\u00e9lectionner un dossier (PDF r\u00e9cursif)</p>
        </div>
        <div className="flex flex-wrap items-center justify-center gap-2">
          <motion.button
            whileTap={{ scale: 0.95 }}
            onClick={(e) => { e.stopPropagation(); open() }}
            data-testid="scan-upload-btn"
            className="flex items-center gap-2 px-4 py-2.5 bg-slate-800 hover:bg-slate-700
              text-slate-200 rounded-xl text-sm font-semibold border border-slate-700 transition-colors"
          >
            <FileUp size={16} />
            Parcourir les fichiers
          </motion.button>
          <motion.button
            whileTap={{ scale: 0.95 }}
            onClick={(e) => { e.stopPropagation(); handleSelectFolder() }}
            className="flex items-center gap-2 px-4 py-2.5 bg-indigo-600/80 hover:bg-indigo-600
              text-white rounded-xl text-sm font-semibold border border-indigo-500/50 transition-colors"
          >
            <FolderOpen size={16} />
            Sélectionner un dossier
          </motion.button>
        </div>
      </div>

      {/* File Queue */}
      <AnimatePresence>
        {batchQueue.length > 0 && (
          <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -10 }}
            className="mb-5"
          >
            {stats.total > 1 && (
              <div className="grid grid-cols-4 gap-2 mb-3">
                {[
                  { label: 'Total',    val: stats.total,   color: 'text-slate-400' },
                  { label: 'En cours', val: stats.running, color: 'text-amber-400' },
                  { label: 'OK',       val: stats.done,    color: 'text-emerald-400' },
                  { label: 'Produits', val: totalProducts, color: 'text-blue-400' },
                ].map(({ label, val, color }) => (
                  <div key={label} className="bg-slate-900 rounded-xl p-2.5 text-center border border-slate-800">
                    <div className={`text-lg font-black ${color}`}>{val}</div>
                    <div className="text-[9px] text-slate-500 uppercase font-bold tracking-wider mt-0.5">{label}</div>
                  </div>
                ))}
              </div>
            )}

            {stats.total > 0 && (
              <div className="h-1.5 bg-slate-800 rounded-full mb-3 overflow-hidden">
                <motion.div
                  className="h-full bg-gradient-to-r from-blue-500 to-emerald-500 rounded-full"
                  animate={{ width: `${(stats.done / stats.total) * 100}%` }}
                  transition={{ duration: 0.5 }}
                />
              </div>
            )}

            <div className="space-y-2 max-h-64 overflow-y-auto pr-1">
              <AnimatePresence>
                {batchQueue.map((item) => {
                  const cfg = STATUS_CONFIG[item.status] || STATUS_CONFIG.pending
                  return (
                    <motion.div
                      key={item.id}
                      layout
                      initial={{ opacity: 0, height: 0 }}
                      animate={{ opacity: 1, height: 'auto' }}
                      exit={{ opacity: 0, height: 0 }}
                      className="bg-slate-900 border border-slate-800 rounded-xl px-3 py-2.5 flex items-center gap-3"
                    >
                      <div className={`shrink-0 ${cfg.color}`}>
                        {item.status === 'done'
                          ? <CheckCircle2 size={18} />
                          : item.status === 'error'
                          ? <AlertCircle size={18} />
                          : ['uploading','processing'].includes(item.status)
                          ? <Loader2 size={18} className="animate-spin" />
                          : <PackagePlus size={18} className="text-slate-600" />
                        }
                      </div>
                      <div className="flex-1 min-w-0">
                        <p className="text-xs font-semibold text-slate-300 truncate">{item.name || item.file?.name || 'Fichier'}</p>
                        <div className="flex items-center gap-2 mt-0.5">
                          <span className={`text-[9px] font-bold uppercase tracking-wider ${cfg.color}`}>
                            {cfg.label}
                          </span>
                          {item.status === 'done' && item.productsAdded > 0 && (
                            <span className="text-[9px] text-emerald-500 font-bold">
                              +{item.productsAdded} produits
                            </span>
                          )}
                          {item.status === 'error' && (
                            <span className="text-[9px] text-red-400 truncate">{item.error}</span>
                          )}
                          <span className="text-[9px] text-slate-600 ml-auto">{formatSize(item.size)}</span>
                        </div>
                        {['uploading','processing'].includes(item.status) && (
                          <div className="h-0.5 bg-slate-800 rounded-full mt-1.5 overflow-hidden">
                            <motion.div
                              className="h-full bg-blue-500 rounded-full"
                              animate={{ width: `${item.progress}%` }}
                            />
                          </div>
                        )}
                      </div>
                      {(item.status === 'pending' || item.status === 'error') && (
                        <button onClick={() => removeFromQueue(item.id)} aria-label="Retirer de la file" className="text-slate-600 hover:text-red-400 transition-colors shrink-0">
                          <X size={16} />
                        </button>
                      )}
                    </motion.div>
                  )
                })}
              </AnimatePresence>
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Batch actions */}
      {batchQueue.length > 0 && (
        <div className="flex gap-3">
          <motion.button
            whileTap={{ scale: 0.95 }}
            onClick={startBatch}
            disabled={stats.pending === 0 || stats.running > 0}
            data-testid="scan-lancer-btn"
            className="flex-1 py-4 bg-emerald-600 hover:bg-emerald-500 disabled:opacity-40
              text-white rounded-2xl font-bold text-sm flex items-center justify-center gap-2 transition-colors"
          >
            {stats.running > 0
              ? <><Loader2 size={18} className="animate-spin" /> Traitement en cours...</>
              : <><UploadCloud size={18} /> Lancer ({stats.pending} fichier{stats.pending > 1 ? 's' : ''})</>
            }
          </motion.button>
          <motion.button
            whileTap={{ scale: 0.95 }}
            onClick={clearQueue}
            disabled={stats.running > 0}
            aria-label="Vider la file"
            className="px-4 py-4 bg-slate-800 hover:bg-slate-700 disabled:opacity-40
              text-slate-400 rounded-2xl border border-slate-700 transition-colors"
          >
            <Trash2 size={18} />
          </motion.button>
        </div>
      )}

      <input ref={inputRef} type="file" className="hidden" onChange={handleCameraFile} />
      <input
        ref={folderInputRef}
        type="file"
        className="hidden"
        webkitdirectory=""
        multiple
        accept=".pdf"
        onChange={handleFolderInputChange}
      />
    </div>
  )
}
import { AnimatePresence, motion } from 'framer-motion'
import {
  AlertCircle,
  Camera,
  CheckCircle2,
  Database,
  FolderOpen,
  Loader2,
  Package,
  PackagePlus,
  Sparkles,
  UploadCloud,
  Zap,
} from 'lucide-react'
import { useRef } from 'react'
import { useNavigate } from 'react-router-dom'
import SplineScene from '../../components/SplineScene'
import BatchQueue from './components/BatchQueue'
import UploadZone from './components/UploadZone'
import { useScanUpload } from './hooks/useScanUpload'

const PIPELINE_STEPS = [
  { key: 'upload', label: 'Envoi', icon: UploadCloud },
  { key: 'ai', label: 'Analyse IA', icon: Sparkles },
  { key: 'validate', label: 'Validation', icon: Zap },
  { key: 'save', label: 'Sauvegarde', icon: Database },
]

export default function ScanPage() {
  const navigate = useNavigate()
  const inputRef = useRef()

  const {
    getRootProps,
    getInputProps,
    isDragActive,
    open,
    folderInputRef,
    handleSelectFolder,
    handleFolderInputChange,
    startBatch,
    handleCameraFile,
    batchQueue,
    stats,
    totalProducts,
    removeFromQueue,
    clearQueue,
    batchDoneModal,
    setBatchDoneModal,
    cameraOverlay,
    pendingCount,
    syncInProgress,
    isOnline,
  } = useScanUpload()

  const currentStepIdx = cameraOverlay
    ? PIPELINE_STEPS.findIndex((s) => s.key === cameraOverlay.step)
    : -1

  return (
    <div className="min-h-screen bg-[#121212] p-5">
      {/* Batch done modal */}
      <AnimatePresence>
        {batchDoneModal && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 z-50 bg-slate-950/90 backdrop-blur flex items-center justify-center p-6"
            onClick={() => setBatchDoneModal(null)}
          >
            <motion.div
              initial={{ scale: 0.9, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              exit={{ scale: 0.9, opacity: 0 }}
              onClick={(e) => e.stopPropagation()}
              className="bg-slate-900 border border-slate-700 rounded-2xl p-6 max-w-sm w-full shadow-2xl"
            >
              <div className="text-center mb-6">
                <CheckCircle2 size={48} className="text-emerald-400 mx-auto mb-3" />
                <h2 className="text-xl font-black text-slate-100 mb-1">
                  {batchDoneModal.count} produit{batchDoneModal.count > 1 ? 's' : ''} extrait
                  {batchDoneModal.count > 1 ? 's' : ''}
                </h2>
                <p className="text-sm text-slate-500">Que souhaitez-vous faire ?</p>
              </div>
              <div className="flex flex-col gap-3">
                <motion.button
                  whileTap={{ scale: 0.98 }}
                  onClick={() => {
                    setBatchDoneModal(null)
                    navigate('/validation')
                  }}
                  className="w-full py-3.5 bg-emerald-600 hover:bg-emerald-500 text-white rounded-xl font-bold text-sm flex items-center justify-center gap-2"
                >
                  <Zap size={18} />
                  Valider les produits
                </motion.button>
                <motion.button
                  whileTap={{ scale: 0.98 }}
                  onClick={() => {
                    setBatchDoneModal(null)
                    navigate('/catalogue')
                  }}
                  className="w-full py-3.5 bg-slate-800 hover:bg-slate-700 text-slate-300 rounded-xl font-bold text-sm flex items-center justify-center gap-2 border border-slate-700"
                >
                  <Package size={18} />
                  Voir le catalogue
                </motion.button>
                <motion.button
                  whileTap={{ scale: 0.98 }}
                  onClick={() => {
                    setBatchDoneModal(null)
                    navigate('/history')
                  }}
                  className="w-full py-3.5 bg-slate-800/60 hover:bg-slate-800 text-slate-400 rounded-xl font-bold text-sm flex items-center justify-center gap-2 border border-slate-700"
                >
                  <FolderOpen size={18} />
                  Voir le PDF des factures
                </motion.button>
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Camera processing overlay */}
      <AnimatePresence>
        {cameraOverlay && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 z-50 bg-slate-950/95 backdrop-blur-lg flex flex-col items-center justify-center p-6"
          >
            <motion.div
              initial={{ scale: 0.9, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              className="w-full max-w-xs rounded-3xl overflow-hidden border-2 border-slate-700 mb-8 shadow-2xl"
            >
              <img
                src={cameraOverlay.previewUrl}
                alt="Facture"
                className="w-full h-48 object-cover"
              />
            </motion.div>

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
                        isError
                          ? 'bg-red-500/20 border-2 border-red-500'
                          : isDone
                            ? 'bg-emerald-500/20 border-2 border-emerald-500'
                            : isActive
                              ? 'bg-blue-500/20 border-2 border-blue-500'
                              : 'bg-slate-800 border-2 border-slate-700'
                      }`}
                    >
                      {isDone && !isActive ? (
                        <CheckCircle2 size={18} className="text-emerald-400" />
                      ) : isError ? (
                        <AlertCircle size={18} className="text-red-400" />
                      ) : (
                        <Icon
                          size={18}
                          className={isActive ? 'text-blue-400' : 'text-slate-500'}
                        />
                      )}
                    </motion.div>
                    {i < PIPELINE_STEPS.length - 1 && (
                      <div
                        className={`w-6 h-0.5 rounded-full transition-colors duration-300 ${
                          i < currentStepIdx ? 'bg-emerald-500' : 'bg-slate-700'
                        }`}
                      />
                    )}
                  </div>
                )
              })}
            </div>

            <motion.p
              key={cameraOverlay.step}
              initial={{ opacity: 0, y: 5 }}
              animate={{ opacity: 1, y: 0 }}
              className={`text-sm font-bold ${
                cameraOverlay.step === 'error'
                  ? 'text-red-400'
                  : cameraOverlay.step === 'done'
                    ? 'text-emerald-400'
                    : 'text-slate-300'
              }`}
            >
              {cameraOverlay.step === 'upload' && 'Compression et envoi...'}
              {cameraOverlay.step === 'ai' && 'Analyse IA en cours...'}
              {cameraOverlay.step === 'validate' && 'Validation des données...'}
              {cameraOverlay.step === 'save' && 'Sauvegarde en base...'}
              {cameraOverlay.step === 'done' && 'Extraction terminée !'}
              {cameraOverlay.step === 'error' &&
                (cameraOverlay.error || 'Erreur inconnue')}
            </motion.p>

            {cameraOverlay.step !== 'error' && cameraOverlay.step !== 'done' && (
              <Loader2 size={24} className="text-blue-400 animate-spin mt-4" />
            )}
          </motion.div>
        )}
      </AnimatePresence>

      {/* Offline / Sync indicator */}
      {(!isOnline || pendingCount > 0 || syncInProgress) && (
        <div className="mb-4 flex items-center gap-2 px-4 py-2.5 rounded-xl border bg-amber-500/10 border-amber-500/30 text-amber-400 text-sm font-semibold">
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

      {/* Header + Hero Spline */}
      <div className="pt-4 pb-5 flex items-center justify-between gap-4">
        <div className="w-24 h-24 shrink-0 rounded-xl overflow-hidden">
          <SplineScene
            sceneUrl="https://prod.spline.design/9951u9cumiw2Ehj8/scene.splinecode"
            className="w-full h-full min-h-0"
          />
        </div>
        <div className="flex-1 min-w-0">
          <h1 className="text-2xl font-black text-slate-100 tracking-tight">
            Docling Agent
          </h1>
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
        className="w-full mb-4 py-5 bg-gradient-to-r from-blue-600 to-indigo-600 rounded-3xl flex items-center justify-center gap-3 text-lg font-bold text-white shadow-[0_0_30px_rgba(99,102,241,0.3)] active:shadow-none transition-shadow"
      >
        <Camera size={26} />
        Photographier une Facture
      </motion.button>

      {/* DropZone */}
      <UploadZone
        getRootProps={getRootProps}
        getInputProps={getInputProps}
        isDragActive={isDragActive}
        open={open}
        onSelectFolder={handleSelectFolder}
        folderInputRef={folderInputRef}
        onFolderInputChange={handleFolderInputChange}
      />

      {/* File Queue */}
      <BatchQueue
        batchQueue={batchQueue}
        stats={stats}
        totalProducts={totalProducts}
        removeFromQueue={removeFromQueue}
        clearQueue={clearQueue}
        startBatch={startBatch}
      />

      <input ref={inputRef} type="file" className="hidden" onChange={handleCameraFile} />
    </div>
  )
}

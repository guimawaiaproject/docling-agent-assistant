import axios from 'axios'
import { AnimatePresence, motion } from 'framer-motion'
import { Camera, FileUp, Loader2 } from 'lucide-react'
import { useRef, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { ENDPOINTS } from '../config/api'
import { compressToWebP } from '../services/imageService'
import { useDoclingStore } from '../store/useStore'

export default function ScanPage() {
  const navigate = useNavigate()
  const inputRef = useRef()
  const [status, setStatus] = useState('idle')
  const [progressMsg, setProgressMsg] = useState('')

  const setJobStart = useDoclingStore(state => state.setJobStart)
  const setJobComplete = useDoclingStore(state => state.setJobComplete)

  const handleFile = async (e) => {
    const file = e.target.files[0]
    if (!file) return

    setStatus('processing')
    setProgressMsg('Compression de la photo (WebP)...')

    // Garde l'image originale pour affichage local immédiat
    const fileUrl = URL.createObjectURL(file)
    const toUpload = file.type.startsWith('image/') ? await compressToWebP(file) : file

    uploadAndProcess(toUpload, fileUrl)
  }

  const uploadAndProcess = async (fileToUpload, displayUrl) => {
    try {
      setProgressMsg('Envoi au serveur et Analyse IA en cours...')

      // Zustand stocke temporairement la facture pour l'affichage visuel
      setJobStart('processing_now', displayUrl)

      const formData = new FormData()
      formData.append('file', fileToUpload)

      // Appel unifié : le backend de ce projet processe et répond de façon asynchrone HTTP
      const { data } = await axios.post(ENDPOINTS.process, formData)

      if (data.success) {
        // Enregistre les produits retournés dans Zustand
        setJobComplete(data.products)

        // Haptique native mobile si supporté (petit bip physique positif)
        if (navigator.vibrate) navigator.vibrate([100])

        // Redirection vers Validation
        navigate('/validation', { replace: true })
      } else {
        throw new Error("L'API a répondu mais le success est false")
      }

    } catch (err) {
      console.error(err)
      setStatus('error')
      setProgressMsg("Une erreur serveur est survenue lors de l'analyse.")
      if (navigator.vibrate) navigator.vibrate([200, 100, 200]) // Erreur haptique
    }
  }

  const openCamera = () => {
    inputRef.current.accept = 'image/*'
    inputRef.current.setAttribute('capture', 'environment')
    inputRef.current.click()
  }

  const openFileBrowser = () => {
    inputRef.current.accept = '.pdf,image/*'
    inputRef.current.removeAttribute('capture')
    inputRef.current.click()
  }

  return (
    <div className="flex flex-col items-center justify-center min-h-[85vh] p-6 gap-6">

      <div className="text-center mb-8">
        <h1 className="text-3xl font-extrabold text-slate-800 tracking-tight">Docling Agent</h1>
        <p className="text-slate-500 mt-2 font-medium">Scanner de Factures BTP</p>
      </div>

      <AnimatePresence mode="wait">
        {status === 'idle' || status === 'error' ? (
          <motion.div
            key="buttons"
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, scale: 0.9 }}
            className="w-full max-w-sm flex flex-col gap-4"
          >
            {status === 'error' && (
              <div className="bg-red-50 text-red-600 p-4 rounded-2xl text-center text-sm mb-4 border border-red-100">
                {progressMsg}
              </div>
            )}

            <motion.button
              whileTap={{ scale: 0.95 }}
              onClick={openCamera}
              className="flex items-center justify-center gap-3 w-full py-5 bg-gradient-to-r from-blue-600 to-indigo-600 text-white rounded-3xl text-xl font-bold shadow-[0_8px_30px_rgb(0,0,0,0.12)]"
            >
              <Camera size={28} />
              Prendre la Facture
            </motion.button>

            <motion.button
              whileTap={{ scale: 0.95 }}
              onClick={openFileBrowser}
              className="flex items-center justify-center gap-3 w-full py-4 bg-white text-slate-700 border-2 border-slate-200 rounded-3xl text-lg font-semibold shadow-sm"
            >
              <FileUp size={24} />
              Choisir un PDF ou Image
            </motion.button>
          </motion.div>
        ) : (
          <motion.div
            key="loader"
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            className="flex flex-col items-center gap-6 mt-10"
          >
            <div className="relative">
              <Loader2 size={64} className="animate-spin text-blue-500" />
              <div className="absolute inset-0 flex items-center justify-center">
                <span className="text-xs font-bold text-blue-500">IA</span>
              </div>
            </div>
            <p className="text-slate-600 font-medium text-center animate-pulse">
              {progressMsg}
            </p>
          </motion.div>
        )}
      </AnimatePresence>

      <input
        ref={inputRef}
        type="file"
        className="hidden"
        onChange={handleFile}
      />
    </div>
  )
}

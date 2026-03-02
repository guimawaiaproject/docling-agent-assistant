import { FileUp, FolderOpen, UploadCloud } from 'lucide-react'
import { motion } from 'framer-motion'

/**
 * Zone de dépôt (dropzone) pour PDF et images.
 * UI uniquement — la logique est fournie par useScanUpload.
 */
export default function UploadZone({
  getRootProps,
  getInputProps,
  isDragActive,
  open,
  onSelectFolder,
  folderInputRef,
  onFolderInputChange,
}) {
  return (
    <div
      {...getRootProps()}
      data-testid="scan-dropzone"
      className={`relative rounded-2xl border-2 border-dashed transition-all duration-200 p-8
        flex flex-col items-center justify-center gap-4 mb-5 cursor-default
        bg-slate-800/40 backdrop-blur-sm
        ${isDragActive
          ? 'border-emerald-500 bg-emerald-500/10 scale-[1.01] shadow-[0_0_0_1px_rgba(52,211,153,0.2)]'
          : 'border-slate-600/80 hover:border-slate-500 hover:bg-slate-800/60'
        }`}
    >
      <input {...getInputProps()} />
      <UploadCloud
        size={36}
        className={`transition-colors ${isDragActive ? 'text-emerald-400' : 'text-slate-600'}`}
      />
      <div className="text-center">
        <p className={`font-bold text-sm ${isDragActive ? 'text-emerald-300' : 'text-slate-400'}`}>
          {isDragActive ? 'Relâchez pour ajouter' : 'Glisser-déposer des PDF / images'}
        </p>
        <p className="text-xs text-slate-600 mt-1">ou sélectionner un dossier (PDF récursif)</p>
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
          onClick={(e) => { e.stopPropagation(); onSelectFolder() }}
          className="flex items-center gap-2 px-4 py-2.5 bg-indigo-600/80 hover:bg-indigo-600
            text-white rounded-xl text-sm font-semibold border border-indigo-500/50 transition-colors"
        >
          <FolderOpen size={16} />
          Sélectionner un dossier
        </motion.button>
      </div>
      <input
        ref={folderInputRef}
        type="file"
        className="hidden"
        webkitdirectory=""
        multiple
        accept=".pdf"
        onChange={onFolderInputChange}
      />
    </div>
  )
}

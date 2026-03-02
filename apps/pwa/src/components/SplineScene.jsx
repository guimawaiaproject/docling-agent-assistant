/**
 * SplineScene — intégration Spline 3D
 * Catalogue : .cursor/agents/references/spline-catalog.json
 */
import { useRef, Suspense, lazy } from 'react'

const Spline = lazy(() => import('@splinetool/react-spline'))

export default function SplineScene({ sceneUrl, className, onLoad, fallback }) {
  const splineRef = useRef()
  const defaultFallback = (
    <div className="h-48 w-full animate-pulse bg-slate-800/60 rounded-xl flex items-center justify-center">
      <span className="text-slate-500 text-xs">Chargement 3D...</span>
    </div>
  )
  return (
    <Suspense fallback={fallback ?? defaultFallback}>
      <Spline
        scene={sceneUrl}
        onLoad={(s) => { splineRef.current = s; onLoad?.(s) }}
        className={className ?? 'w-full h-48 min-h-[192px] rounded-xl overflow-hidden'}
        renderOnDemand
      />
    </Suspense>
  )
}

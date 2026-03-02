/**
 * EmptyStateIllustration — illustration SVG pour empty states
 * Alternative fiable à Spline quand la scène 3D ne charge pas.
 */
export default function EmptyStateIllustration({ className = '' }) {
  return (
    <div
      className={`flex items-center justify-center rounded-xl bg-slate-800/40 border border-slate-700/50 ${className}`}
      aria-hidden
    >
      <svg
        viewBox="0 0 120 80"
        className="w-full h-full max-h-[160px] text-slate-600"
        fill="none"
        xmlns="http://www.w3.org/2000/svg"
      >
        {/* Document / feuille */}
        <path
          d="M35 15 L35 55 L55 55 L75 35 L75 15 Z"
          stroke="currentColor"
          strokeWidth="1.5"
          strokeLinecap="round"
          strokeLinejoin="round"
          opacity="0.6"
        />
        <path
          d="M55 55 L55 35 L75 35"
          stroke="currentColor"
          strokeWidth="1.5"
          strokeLinecap="round"
          strokeLinejoin="round"
          opacity="0.6"
        />
        {/* Lignes texte */}
        <line x1="42" y1="25" x2="68" y2="25" stroke="currentColor" strokeWidth="1" opacity="0.4" />
        <line x1="42" y1="32" x2="65" y2="32" stroke="currentColor" strokeWidth="1" opacity="0.4" />
        <line x1="42" y1="39" x2="60" y2="39" stroke="currentColor" strokeWidth="1" opacity="0.4" />
        {/* Boîte / colis */}
        <rect
          x="50"
          y="45"
          width="30"
          height="22"
          rx="2"
          stroke="currentColor"
          strokeWidth="1.5"
          strokeLinecap="round"
          strokeLinejoin="round"
          opacity="0.5"
        />
        <path
          d="M50 52 L65 45 L80 52 L65 59 Z"
          stroke="currentColor"
          strokeWidth="1.2"
          strokeLinecap="round"
          strokeLinejoin="round"
          opacity="0.5"
        />
        {/* Accent emerald */}
        <circle cx="90" cy="25" r="4" fill="rgb(16 185 129)" opacity="0.6" />
      </svg>
    </div>
  )
}

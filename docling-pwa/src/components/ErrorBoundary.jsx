import { Component } from 'react'
import { AlertTriangle, RotateCcw } from 'lucide-react'

export default class ErrorBoundary extends Component {
  constructor(props) {
    super(props)
    this.state = { hasError: false, error: null }
  }

  static getDerivedStateFromError(error) {
    return { hasError: true, error }
  }

  componentDidCatch(error, info) {
    console.error('[ErrorBoundary]', error, info.componentStack)
  }

  handleReset = () => {
    this.setState({ hasError: false, error: null })
  }

  render() {
    if (this.state.hasError) {
      return (
        <div className="min-h-screen bg-slate-950 flex items-center justify-center p-6">
          <div className="max-w-sm w-full text-center">
            <div className="w-16 h-16 mx-auto mb-6 rounded-full bg-red-500/10 border-2 border-red-500/40 flex items-center justify-center">
              <AlertTriangle size={28} className="text-red-400" />
            </div>

            <h1 className="text-xl font-black text-slate-100 mb-2">
              Quelque chose s'est mal passé
            </h1>
            <p className="text-sm text-slate-500 mb-6 leading-relaxed">
              Une erreur inattendue est survenue. Vous pouvez essayer de recharger
              la page ou revenir à l'accueil.
            </p>

            {import.meta.env.DEV && this.state.error && (
              <pre className="text-left text-xs text-red-400/80 bg-slate-900 border border-slate-800 rounded-xl p-3 mb-6 overflow-auto max-h-32">
                {this.state.error.message}
              </pre>
            )}

            <div className="flex gap-3 justify-center">
              <button
                onClick={this.handleReset}
                className="flex items-center gap-2 px-5 py-3 bg-emerald-600 hover:bg-emerald-500
                  text-white rounded-xl font-bold text-sm transition-colors"
              >
                <RotateCcw size={16} />
                Réessayer
              </button>
              <a
                href="/"
                className="flex items-center px-5 py-3 bg-slate-800 hover:bg-slate-700
                  text-slate-300 rounded-xl font-bold text-sm border border-slate-700 transition-colors"
              >
                Accueil
              </a>
            </div>
          </div>
        </div>
      )
    }

    return this.props.children
  }
}

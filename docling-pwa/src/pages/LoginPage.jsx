import { useCallback, useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { toast } from 'sonner'
import apiClient from '../services/apiClient'
import { ENDPOINTS } from '../config/api'

function validateEmail(email) {
  return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email || '')
}

function validatePassword(password) {
  return (password || '').length >= 8
}

export default function LoginPage() {
  const navigate = useNavigate()
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [loading, setLoading] = useState(false)

  const handleSubmit = useCallback(async (e) => {
    e.preventDefault()
    if (!validateEmail(email)) {
      toast.error('Email invalide')
      return
    }
    if (!validatePassword(password)) {
      toast.error('Mot de passe : 8 car. min, 1 majuscule, 1 chiffre')
      return
    }
    setLoading(true)
    try {
      const formData = new FormData()
      formData.append('email', email)
      formData.append('password', password)
      const { data } = await apiClient.post(ENDPOINTS.login, formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
        withCredentials: true,
      })
      if (data?.user_id) {
        toast.success('Connexion réussie')
        navigate('/scan', { replace: true })
      } else {
        toast.error('Réponse invalide du serveur')
      }
    } catch (err) {
      const msg = err.response?.data?.detail || err.message || 'Erreur de connexion'
      toast.error(typeof msg === 'string' ? msg : 'Email ou mot de passe incorrect')
    } finally {
      setLoading(false)
    }
  }, [email, password, navigate])

  return (
    <div className="min-h-screen flex flex-col items-center justify-center p-6 bg-slate-950">
      <div className="w-full max-w-sm">
        <h1 className="text-2xl font-black text-slate-100 mb-1">Connexion</h1>
        <p className="text-sm text-slate-500 mb-6">Accédez à votre catalogue BTP</p>

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label htmlFor="login-email" className="block text-xs font-bold text-slate-400 uppercase tracking-wider mb-1.5">
              Email
            </label>
            <input
              id="login-email"
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="vous@exemple.com"
              autoComplete="email"
              required
              className="w-full bg-slate-900 border border-slate-700 rounded-xl py-3 px-4
                text-slate-200 placeholder-slate-600
                focus:outline-none focus:border-emerald-500/60 transition-all"
            />
          </div>

          <div>
            <label htmlFor="login-password" className="block text-xs font-bold text-slate-400 uppercase tracking-wider mb-1.5">
              Mot de passe
            </label>
            <input
              id="login-password"
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="••••••••"
              autoComplete="current-password"
              required
              className="w-full bg-slate-900 border border-slate-700 rounded-xl py-3 px-4
                text-slate-200 placeholder-slate-600
                focus:outline-none focus:border-emerald-500/60 transition-all"
            />
          </div>

          <button
            type="submit"
            disabled={loading}
            className="w-full py-3 bg-emerald-600 hover:bg-emerald-500 disabled:opacity-50
              text-white font-bold rounded-xl transition-colors"
          >
            {loading ? 'Connexion...' : 'Se connecter'}
          </button>
        </form>

        <p className="mt-6 text-center text-sm text-slate-500">
          Pas encore de compte ?{' '}
          <Link to="/register" className="text-emerald-400 font-bold hover:underline">
            S'inscrire
          </Link>
        </p>
      </div>
    </div>
  )
}

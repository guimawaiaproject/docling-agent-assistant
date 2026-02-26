import { Navigate, useLocation } from 'react-router-dom'

const TOKEN_KEY = 'docling-token'

export default function ProtectedRoute({ children }) {
  const location = useLocation()
  const token = localStorage.getItem(TOKEN_KEY)

  if (!token) {
    return <Navigate to="/login" state={{ from: location }} replace />
  }

  return children
}

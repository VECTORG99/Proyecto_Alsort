import { useState, useEffect } from 'react'
import Login from './components/Login'
import Dashboard from './components/Dashboard'
import { getMe, clearSession } from './services/api'
import { LoadingProvider } from './context/LoadingContext'
import { ToastProvider } from './context/ToastContext'
import type { UserInfo } from './types'

export default function App() {
  const [user, setUser] = useState<UserInfo | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    const params = new URLSearchParams(window.location.search)
    const session = params.get('session')
    const err = params.get('error')

    if (err) {
      setError('Autorización denegada. Debes aceptar los permisos para usar Alsort.')
      window.history.replaceState({}, '', '/')
      setLoading(false)
      return
    }

    if (session) {
      localStorage.setItem('alsort_session_id', session)
      window.history.replaceState({}, '', '/')
    }

    const stored = localStorage.getItem('alsort_session_id')
    if (stored) {
      getMe()
        .then((u) => setUser(u))
        .catch(() => {
          clearSession()
          setError('Sesión expirada. Inicia sesión de nuevo.')
        })
        .finally(() => setLoading(false))
    } else {
      setLoading(false)
    }
  }, [])

  if (loading) {
    return <div className="loading">Conectando...</div>
  }

  if (error) {
    return <div className="error">{error}</div>
  }

  return (
    <LoadingProvider>
      <ToastProvider>
        {!user ? <Login /> : <Dashboard user={user} />}
      </ToastProvider>
    </LoadingProvider>
  )
}

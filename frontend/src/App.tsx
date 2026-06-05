import { useState, useEffect } from 'react'
import Login from './components/Login'
import Dashboard from './components/Dashboard'
import { getMe } from './services/api'
import type { UserInfo } from './types'

export default function App() {
  const [user, setUser] = useState<UserInfo | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    const session = new URLSearchParams(window.location.search).get('session')
    if (session) {
      getMe()
        .then((u) => {
          setUser(u)
          window.history.replaceState({}, '', '/')
        })
        .catch(() => setError('Sesión inválida. Inicia sesión de nuevo.'))
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

  if (!user) {
    return <Login />
  }

  return <Dashboard user={user} />
}

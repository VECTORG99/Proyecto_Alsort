import { createContext, useContext, useState, type ReactNode } from 'react'

interface LoadingContextType {
  isLoading: boolean
  message: string
  startLoading: (msg: string) => void
  stopLoading: () => void
}

const LoadingContext = createContext<LoadingContextType | null>(null)

export function LoadingProvider({ children }: { children: ReactNode }) {
  const [isLoading, setIsLoading] = useState(false)
  const [message, setMessage] = useState('')

  function startLoading(msg: string) {
    setMessage(msg)
    setIsLoading(true)
  }

  function stopLoading() {
    setIsLoading(false)
    setMessage('')
  }

  return (
    <LoadingContext.Provider value={{ isLoading, message, startLoading, stopLoading }}>
      {isLoading && (
        <div className="loading-overlay">
          <div className="loading-spinner" />
          <span className="loading-message">{message}</span>
        </div>
      )}
      <div className={isLoading ? 'loading-active' : ''}>
        {children}
      </div>
    </LoadingContext.Provider>
  )
}

export function useLoading(): LoadingContextType {
  const ctx = useContext(LoadingContext)
  if (!ctx) throw new Error('useLoading must be used within LoadingProvider')
  return ctx
}

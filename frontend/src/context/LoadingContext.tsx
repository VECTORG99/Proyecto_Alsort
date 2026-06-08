import { createContext, useContext, useState, useCallback, type ReactNode } from 'react'

interface LoadingContextType {
  isLoading: boolean
  message: string
  startLoading: (msg: string) => void
  stopLoading: () => void
}

const LoadingContext = createContext<LoadingContextType | null>(null)

export function LoadingProvider({ children }: { children: ReactNode }) {
  const [loadingCount, setLoadingCount] = useState(0)
  const [message, setMessage] = useState('')
  const isLoading = loadingCount > 0

  const startLoading = useCallback((msg: string) => {
    setMessage(msg)
    setLoadingCount(c => c + 1)
  }, [])

  const stopLoading = useCallback(() => {
    setLoadingCount(c => Math.max(0, c - 1))
  }, [])

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

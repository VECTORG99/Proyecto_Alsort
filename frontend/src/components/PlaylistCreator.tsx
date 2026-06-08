import { useState } from 'react'
import { createPlaylist } from '../services/api'
import { useLoading } from '../context/LoadingContext'
import { useToast } from '../context/ToastContext'
import type { FilterRequest } from '../types'

interface PlaylistCreatorProps {
  filterRequest: FilterRequest
  totalTracks: number
}

export default function PlaylistCreator({ filterRequest, totalTracks }: PlaylistCreatorProps) {
  const { startLoading, stopLoading, isLoading } = useLoading()
  const { addToast } = useToast()
  const [name, setName] = useState('')
  const [description, setDescription] = useState('')
  const [public_, setPublic_] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const displayTotal = totalTracks > 10000 ? `${totalTracks} (máx. 10.000)` : totalTracks

  async function handleCreate() {
    if (!name.trim()) {
      setError('El nombre de la playlist es obligatorio')
      return
    }
    if (totalTracks === 0) {
      setError('No hay canciones para agregar a la playlist')
      return
    }

    startLoading('Creando playlist en Spotify...')
    setError(null)

    try {
      const res = await createPlaylist({
        name: name.trim(),
        description: description.trim(),
        public: public_,
        filter_criteria: filterRequest,
      })
      const truncated = res?.truncated ?? false
      const playlistName = res?.name ?? name.trim()
      let msg = `Playlist "${playlistName}" creada.`
      if (truncated) {
        const totalAdded = res?.total_added ?? 0
        const totalMatched = res?.total_matched ?? 0
        msg += ` Se agregaron ${totalAdded} de ${totalMatched} canciones (límite 10.000).`
      }
      addToast(msg, truncated ? 'info' : 'success')
      setName('')
      setDescription('')
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Error al crear la playlist')
    } finally {
      stopLoading()
    }
  }

  return (
    <div className="playlist-creator">
      <h3>Crear Playlist</h3>
      {error && <div className="error-msg">{error}</div>}
      <div className="form-group">
        <label>Nombre de la playlist</label>
        <input
          type="text"
          value={name}
          onChange={(e) => setName(e.target.value)}
          placeholder="Mi playlist filtrada"
          disabled={isLoading}
        />
      </div>
      <div className="form-group">
        <label>Descripción (opcional)</label>
        <textarea
          value={description}
          onChange={(e) => setDescription(e.target.value)}
          placeholder="Playlist creada con Alsort"
          rows={2}
          disabled={isLoading}
        />
      </div>
      <div className="form-group checkbox">
        <label>
          <input
            type="checkbox"
            checked={public_}
            onChange={(e) => setPublic_(e.target.checked)}
            disabled={isLoading}
          />
          Playlist pública
        </label>
      </div>
      {totalTracks > 10000 && (
        <div className="truncation-msg">
          Solo se agregarán las primeras 10.000 canciones de {totalTracks} (límite de Spotify).
        </div>
      )}
      <button
        className="btn-create"
        onClick={handleCreate}
        disabled={isLoading || totalTracks === 0}
      >
        {isLoading ? 'Creando...' : `Crear Playlist (${displayTotal} canc.)`}
      </button>
    </div>
  )
}

import { useState } from 'react'
import { createPlaylist } from '../services/api'
import type { FilterRequest } from '../types'

interface PlaylistCreatorProps {
  filterRequest: FilterRequest
  totalTracks: number
}

export default function PlaylistCreator({ filterRequest, totalTracks }: PlaylistCreatorProps) {
  const [name, setName] = useState('')
  const [description, setDescription] = useState('')
  const [public_, setPublic_] = useState(true)
  const [creating, setCreating] = useState(false)
  const [result, setResult] = useState<string | null>(null)
  const [error, setError] = useState<string | null>(null)

  async function handleCreate() {
    if (!name.trim()) {
      setError('El nombre de la playlist es obligatorio')
      return
    }
    if (totalTracks === 0) {
      setError('No hay canciones para agregar a la playlist')
      return
    }

    setCreating(true)
    setError(null)
    setResult(null)

    try {
      const res = await createPlaylist({
        name: name.trim(),
        description: description.trim(),
        public: public_,
        filter_criteria: filterRequest,
      })
      setResult(`Playlist "${res.name}" creada exitosamente en tu cuenta de Spotify.`)
      setName('')
      setDescription('')
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Error al crear la playlist')
    } finally {
      setCreating(false)
    }
  }

  return (
    <div className="playlist-creator">
      <h3>Crear Playlist</h3>
      {result && <div className="success-msg">{result}</div>}
      {error && <div className="error-msg">{error}</div>}
      <div className="form-group">
        <label>Nombre de la playlist</label>
        <input
          type="text"
          value={name}
          onChange={(e) => setName(e.target.value)}
          placeholder="Mi playlist filtrada"
          disabled={creating}
        />
      </div>
      <div className="form-group">
        <label>Descripción (opcional)</label>
        <textarea
          value={description}
          onChange={(e) => setDescription(e.target.value)}
          placeholder="Playlist creada con Alsort"
          rows={2}
          disabled={creating}
        />
      </div>
      <div className="form-group checkbox">
        <label>
          <input
            type="checkbox"
            checked={public_}
            onChange={(e) => setPublic_(e.target.checked)}
            disabled={creating}
          />
          Playlist pública
        </label>
      </div>
      <button
        className="btn-create"
        onClick={handleCreate}
        disabled={creating || totalTracks === 0}
      >
        {creating ? 'Creando...' : `Crear Playlist (${totalTracks} canciones)`}
      </button>
    </div>
  )
}

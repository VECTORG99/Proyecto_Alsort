import { useState, useMemo } from 'react'
import type { Track, SortField, SortOrder } from '../types'
import { SORT_OPTIONS } from '../types'
import { useLoading } from '../context/LoadingContext'

interface SongListProps {
  tracks: Track[]
  total: number
  page: number
  pageSize: number
  pageSizes: number[]
  sortBy: SortField | null
  sortOrder: SortOrder
  onPageChange: (page: number) => void
  onPageSizeChange: (pageSize: number) => void
  onSortChange: (sortBy: SortField | null, sortOrder: SortOrder) => void
}

function formatDuration(ms: number): string {
  const min = Math.floor(ms / 60000)
  const sec = Math.floor((ms % 60000) / 1000)
  return `${min}:${sec.toString().padStart(2, '0')}`
}

function SkeletonCard() {
  return (
    <div className="song-card skeleton">
      <div className="skeleton-art" />
      <div className="song-info">
        <div className="skeleton-line w60" />
        <div className="skeleton-line w40" />
        <div className="skeleton-line w30" />
      </div>
      <div className="song-stats">
        <div className="skeleton-line w20" />
        <div className="skeleton-line w20" />
      </div>
    </div>
  )
}

export default function SongList({
  tracks, total, page, pageSize, pageSizes,
  sortBy, sortOrder,
  onPageChange, onPageSizeChange, onSortChange,
}: SongListProps) {
  const { isLoading } = useLoading()
  const [search, setSearch] = useState('')

  const filteredTracks = useMemo(() => {
    if (!search.trim()) return tracks
    const q = search.toLowerCase()
    return tracks.filter(
      (t) =>
        t.track_name.toLowerCase().includes(q) ||
        t.artists.toLowerCase().includes(q) ||
        t.album.toLowerCase().includes(q),
    )
  }, [tracks, search])

  const displayTotal = search.trim() ? filteredTracks.length : total
  const displayFrom = displayTotal === 0 ? 0 : page * pageSize + 1
  const displayTo = Math.min((page + 1) * pageSize, displayTotal)
  const totalPages = Math.max(1, Math.ceil(displayTotal / pageSize))

  if (isLoading) {
    return (
      <div className="songlist">
        <div className="songlist-header"><h2>Cargando...</h2></div>
        <div className="songlist-grid">
          {Array.from({ length: 6 }).map((_, i) => <SkeletonCard key={i} />)}
        </div>
      </div>
    )
  }

  if (tracks.length === 0) {
    return <div className="songlist-empty">No hay canciones. Sincroniza tus likes o ajusta los filtros.</div>
  }

  return (
    <div className="songlist">
      <div className="songlist-header">
        <h2>{search.trim() ? `Resultados (${filteredTracks.length} de ${total})` : `Resultados (${total} canciones)`}</h2>
        <div className="songlist-toolbar">
          <input
            className="search-input"
            type="text"
            placeholder="Buscar en resultados..."
            aria-label="Buscar en resultados"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
          />
          <select
            className="sort-select"
            value={sortBy ?? ''}
            onChange={(e) => {
              const val = e.target.value as SortField | ''
              onSortChange(val || null, sortOrder)
            }}
          >
            <option value="">Sin orden</option>
            {SORT_OPTIONS.map((o) => (
              <option key={o.value} value={o.value}>{o.label}</option>
            ))}
          </select>
          {sortBy && (
            <button
              className="btn-sort-order"
              onClick={() => onSortChange(sortBy, sortOrder === 'asc' ? 'desc' : 'asc')}
              title={sortOrder === 'asc' ? 'Ascendente' : 'Descendente'}
            >
              {sortOrder === 'asc' ? '↑' : '↓'}
            </button>
          )}
        </div>
      </div>

      {filteredTracks.length === 0 && search && (
        <div className="songlist-empty">Sin resultados para "{search}"</div>
      )}

      <div className="songlist-grid">
        {filteredTracks.map((track) => (
          <div key={track.id} className="song-card">
            {track.album_image_url && (
              <img
                src={track.album_image_url}
                alt={track.album}
                className="song-album-art"
                loading="lazy"
              />
            )}
            <div className="song-info">
              <div className="song-name" title={track.track_name}>{track.track_name}</div>
              <div className="song-artist" title={track.artists}>{track.artists}</div>
              <div className="song-meta">
                <span>{formatDuration(track.duration_ms)}</span>
                {track.year && <span>{track.year}</span>}
                {track.tempo && <span>{Math.round(track.tempo)} BPM</span>}
              </div>
            </div>
            <div className="song-stats">
              {track.popularity > 0 && (
                <div className="stat" title="Popularidad">
                  <span className="stat-label">Pop</span>
                  <span className="stat-value">{track.popularity}%</span>
                </div>
              )}
              {track.instrumentalness !== null && (
                <div className="stat" title="Instrumentalidad">
                  <span className="stat-label">Inst</span>
                  <span className="stat-value">{(track.instrumentalness * 100).toFixed(0)}%</span>
                </div>
              )}
              {track.acousticness !== null && (
                <div className="stat" title="Acousticidad">
                  <span className="stat-label">Acou</span>
                  <span className="stat-value">{(track.acousticness * 100).toFixed(0)}%</span>
                </div>
              )}
            </div>
          </div>
        ))}
      </div>

      <div className="pagination">
        <div className="pagination-info">
          {search.trim() ? `${filteredTracks.length} coincidencias` : `${displayFrom}–${displayTo} de ${total}`}
        </div>
        <div className="pagination-controls">
          {!search.trim() && (
            <>
              <select
                className="page-size-select"
                value={pageSize}
                onChange={(e) => onPageSizeChange(Number(e.target.value))}
              >
                {pageSizes.map((s) => (
                  <option key={s} value={s}>{s} / pág</option>
                ))}
              </select>
              <button
                className="btn-page"
                onClick={() => onPageChange(page - 1)}
                disabled={page <= 0}
              >‹ Anterior</button>
              <span className="page-indicator">{page + 1} de {totalPages}</span>
              <button
                className="btn-page"
                onClick={() => onPageChange(page + 1)}
                disabled={page + 1 >= totalPages}
              >Siguiente ›</button>
            </>
          )}
          {search.trim() && (
            <span className="page-indicator">Búsqueda local — cambia los filtros o la búsqueda</span>
          )}
        </div>
      </div>
    </div>
  )
}

import type { Track } from '../types'

interface SongListProps {
  tracks: Track[]
  total: number
  loading: boolean
}

function formatDuration(ms: number): string {
  const min = Math.floor(ms / 60000)
  const sec = Math.floor((ms % 60000) / 1000)
  return `${min}:${sec.toString().padStart(2, '0')}`
}

export default function SongList({ tracks, total, loading }: SongListProps) {
  if (loading) {
    return <div className="songlist-loading">Cargando canciones...</div>
  }

  if (tracks.length === 0) {
    return <div className="songlist-empty">No hay canciones. Sincroniza tus likes o ajusta los filtros.</div>
  }

  return (
    <div className="songlist">
      <div className="songlist-header">
        <h2>Resultados ({total} canciones)</h2>
      </div>
      <div className="songlist-grid">
        {tracks.map((track) => (
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
              {track.instrumentalness !== null && track.instrumentalness !== undefined && (
                <div className="stat" title="Instrumentalidad">
                  <span className="stat-label">Inst</span>
                  <span className="stat-value">{(track.instrumentalness * 100).toFixed(0)}%</span>
                </div>
              )}
              {track.acousticness !== null && track.acousticness !== undefined && (
                <div className="stat" title="Acousticidad">
                  <span className="stat-label">Acou</span>
                  <span className="stat-value">{(track.acousticness * 100).toFixed(0)}%</span>
                </div>
              )}
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}

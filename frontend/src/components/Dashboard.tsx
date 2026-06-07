import { useState, useEffect, useCallback } from 'react'
import type { UserInfo, Track, FilterCriterion, FilterRequest } from '../types'
import { syncTracks, filterTracks } from '../services/api'
import { useLoading } from '../context/LoadingContext'
import FilterPanel from './FilterPanel'
import SongList from './SongList'
import PlaylistCreator from './PlaylistCreator'

interface DashboardProps {
  user: UserInfo
}

export default function Dashboard({ user }: DashboardProps) {
  const { startLoading, stopLoading } = useLoading()
  const [tracks, setTracks] = useState<Track[]>([])
  const [total, setTotal] = useState(0)
  const [syncMsg, setSyncMsg] = useState<string | null>(null)
  const [currentFilterReq, setCurrentFilterReq] = useState<FilterRequest>({
    and_filters: [],
    or_filters: [],
    limit: 50,
    offset: 0,
  })

  const fetchFiltered = useCallback(async (andFilters: FilterCriterion[], orFilters: FilterCriterion[]) => {
    startLoading('Filtrando canciones...')
    try {
      const req: FilterRequest = {
        and_filters: andFilters,
        or_filters: orFilters,
        limit: 200,
        offset: 0,
      }
      setCurrentFilterReq(req)
      const res = await filterTracks(req)
      setTracks(res.tracks)
      setTotal(res.total)
    } catch (e) {
      console.error('Filter error:', e)
    } finally {
      stopLoading()
    }
  }, [startLoading, stopLoading])

  useEffect(() => {
    fetchFiltered([], [])
  }, [fetchFiltered])

  async function handleSync() {
    startLoading('Sincronizando canciones de Spotify...')
    setSyncMsg(null)
    try {
      const res = await syncTracks()
      setSyncMsg(`${res.synced} canciones sincronizadas`)
      fetchFiltered([], [])
    } catch (e) {
      setSyncMsg('Error al sincronizar')
    } finally {
      stopLoading()
    }
  }

  return (
    <div className="dashboard">
      <header className="dashboard-header">
        <div className="header-left">
          <h1>Alsort</h1>
          <span className="user-info">{user.display_name || user.spotify_id}</span>
        </div>
        <div className="header-right">
          {syncMsg && <span className="sync-msg">{syncMsg}</span>}
          <button className="btn-sync" onClick={handleSync}>
            Sincronizar likes
          </button>
        </div>
      </header>

      <div className="dashboard-content">
        <aside className="sidebar">
          <FilterPanel onApply={fetchFiltered} />
          <PlaylistCreator
            filterRequest={currentFilterReq}
            totalTracks={total}
          />
        </aside>
        <main className="main-content">
          <SongList tracks={tracks} total={total} />
        </main>
      </div>
    </div>
  )
}

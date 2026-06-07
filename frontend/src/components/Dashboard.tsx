import { useState, useEffect, useCallback, useRef } from 'react'
import type { UserInfo, Track, FilterCriterion, FilterRequest } from '../types'
import { syncTracks, filterTracks } from '../services/api'
import { useLoading } from '../context/LoadingContext'
import FilterPanel from './FilterPanel'
import SongList from './SongList'
import PlaylistCreator from './PlaylistCreator'

const PAGE_SIZES = [50, 100, 200]

interface DashboardProps {
  user: UserInfo
}

export default function Dashboard({ user }: DashboardProps) {
  const { startLoading, stopLoading } = useLoading()
  const [tracks, setTracks] = useState<Track[]>([])
  const [total, setTotal] = useState(0)
  const [syncMsg, setSyncMsg] = useState<string | null>(null)
  const [pageSize, setPageSize] = useState(100)
  const [page, setPage] = useState(0)
  const currentFilters = useRef<{ and: FilterCriterion[]; or: FilterCriterion[] }>({ and: [], or: [] })

  const fetchFiltered = useCallback(async (
    andFilters: FilterCriterion[],
    orFilters: FilterCriterion[],
    newPage?: number,
    newPageSize?: number,
  ) => {
    startLoading('Filtrando canciones...')
    const size = newPageSize ?? pageSize
    const pg = newPage ?? 0
    currentFilters.current = { and: andFilters, or: orFilters }
    try {
      const req: FilterRequest = {
        and_filters: andFilters,
        or_filters: orFilters,
        limit: size,
        offset: pg * size,
      }
      const res = await filterTracks(req)
      setTracks(res.tracks)
      setTotal(res.total)
      setPage(pg)
    } catch (e) {
      console.error('Filter error:', e)
    } finally {
      stopLoading()
    }
  }, [startLoading, stopLoading, pageSize])

  function goToPage(newPage: number) {
    fetchFiltered(
      currentFilters.current.and,
      currentFilters.current.or,
      newPage,
    )
  }

  function changePageSize(newSize: number) {
    setPageSize(newSize)
    fetchFiltered(
      currentFilters.current.and,
      currentFilters.current.or,
      0,
      newSize,
    )
  }

  useEffect(() => {
    fetchFiltered([], [], 0, pageSize)
  }, []) // eslint-disable-line react-hooks/exhaustive-deps

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
          <FilterPanel onApply={(andF, orF) => fetchFiltered(andF, orF, 0)} />
          <PlaylistCreator
            filterRequest={{
              and_filters: currentFilters.current.and,
              or_filters: currentFilters.current.or,
              limit: 10000,
              offset: 0,
            }}
            totalTracks={total}
          />
        </aside>
        <main className="main-content">
          <SongList
            tracks={tracks}
            total={total}
            page={page}
            pageSize={pageSize}
            pageSizes={PAGE_SIZES}
            onPageChange={goToPage}
            onPageSizeChange={changePageSize}
          />
        </main>
      </div>
    </div>
  )
}

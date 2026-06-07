import { useState, useEffect, useCallback, useRef } from 'react'
import type { UserInfo, Track, FilterCriterion, FilterRequest, SortField, SortOrder } from '../types'
import { syncTracks, filterTracks } from '../services/api'
import { useLoading } from '../context/LoadingContext'
import { useToast } from '../context/ToastContext'
import FilterPanel from './FilterPanel'
import SongList from './SongList'
import PlaylistCreator from './PlaylistCreator'

const PAGE_SIZES = [50, 100, 200]

interface DashboardProps {
  user: UserInfo
}

export default function Dashboard({ user }: DashboardProps) {
  const { startLoading, stopLoading } = useLoading()
  const { addToast } = useToast()
  const [tracks, setTracks] = useState<Track[]>([])
  const [total, setTotal] = useState(0)
  const [pageSize, setPageSize] = useState(100)
  const [page, setPage] = useState(0)
  const [sortBy, setSortBy] = useState<SortField | null>(null)
  const [sortOrder, setSortOrder] = useState<SortOrder>('desc')
  const currentFilters = useRef<{ and: FilterCriterion[]; or: FilterCriterion[] }>({ and: [], or: [] })

  const fetchFiltered = useCallback(async (
    andFilters: FilterCriterion[],
    orFilters: FilterCriterion[],
    newPage?: number,
    newPageSize?: number,
    newSortBy?: SortField | null,
    newSortOrder?: SortOrder,
  ) => {
    startLoading('Filtrando canciones...')
    const size = newPageSize ?? pageSize
    const pg = newPage ?? 0
    const sb = newSortBy !== undefined ? newSortBy : sortBy
    const so = newSortOrder !== undefined ? newSortOrder : sortOrder
    currentFilters.current = { and: andFilters, or: orFilters }
    try {
      const req: FilterRequest = {
        and_filters: andFilters,
        or_filters: orFilters,
        limit: size,
        offset: pg * size,
        sort_by: sb,
        sort_order: so,
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
  }, [startLoading, stopLoading, pageSize, sortBy, sortOrder])

  function goToPage(newPage: number) {
    fetchFiltered(currentFilters.current.and, currentFilters.current.or, newPage)
  }

  function changePageSize(newSize: number) {
    setPageSize(newSize)
    fetchFiltered(currentFilters.current.and, currentFilters.current.or, 0, newSize)
  }

  function handleSortChange(newSortBy: SortField | null, newSortOrder: SortOrder) {
    setSortBy(newSortBy)
    setSortOrder(newSortOrder)
    fetchFiltered(currentFilters.current.and, currentFilters.current.or, 0, pageSize, newSortBy, newSortOrder)
  }

  useEffect(() => {
    fetchFiltered([], [], 0, pageSize)
  }, []) // eslint-disable-line react-hooks/exhaustive-deps

  async function handleSync() {
    startLoading('Sincronizando canciones de Spotify...')
    try {
      const res = await syncTracks()
      addToast(`${res.synced} canciones sincronizadas`, 'success')
      fetchFiltered([], [], 0, pageSize, sortBy, sortOrder)
    } catch (e) {
      addToast('Error al sincronizar', 'error')
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
          <button className="btn-sync" onClick={handleSync}>
            Sincronizar likes
          </button>
        </div>
      </header>

      <div className="dashboard-content">
        <aside className="sidebar">
          <FilterPanel onApply={(andF, orF) => fetchFiltered(andF, orF, 0, pageSize, null, sortOrder)} />
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
            sortBy={sortBy}
            sortOrder={sortOrder}
            onPageChange={goToPage}
            onPageSizeChange={changePageSize}
            onSortChange={handleSortChange}
          />
        </main>
      </div>
    </div>
  )
}

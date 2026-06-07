import type {
  UserInfo,
  FilterRequest,
  FilterResponse,
  CreatePlaylistRequest,
} from '../types'

const API_BASE = 'http://localhost:8000'
const SESSION_KEY = 'alsort_session_id'

function getSessionId(): string | null {
  const params = new URLSearchParams(window.location.search)
  const fromUrl = params.get('session')
  if (fromUrl) {
    localStorage.setItem(SESSION_KEY, fromUrl)
    return fromUrl
  }
  return localStorage.getItem(SESSION_KEY)
}

export function clearSession(): void {
  localStorage.removeItem(SESSION_KEY)
}

function headers(): Record<string, string> {
  const h: Record<string, string> = { 'Content-Type': 'application/json' }
  const sid = getSessionId()
  if (sid) {
    h['X-Session-Id'] = sid
  }
  return h
}

export async function getMe(): Promise<UserInfo> {
  const res = await fetch(`${API_BASE}/auth/me`, { headers: headers() })
  if (!res.ok) throw new Error('Not authenticated')
  return res.json()
}

export async function syncTracks(): Promise<{ synced: number }> {
  const res = await fetch(`${API_BASE}/api/tracks/sync`, {
    method: 'POST',
    headers: headers(),
  })
  if (!res.ok) throw new Error('Sync failed')
  return res.json()
}

export async function filterTracks(req: FilterRequest): Promise<FilterResponse> {
  const res = await fetch(`${API_BASE}/api/tracks/filter`, {
    method: 'POST',
    headers: headers(),
    body: JSON.stringify(req),
  })
  if (!res.ok) throw new Error('Filter failed')
  return res.json()
}

export async function createPlaylist(req: CreatePlaylistRequest): Promise<{ playlist: unknown; name: string; total_matched: number; total_added: number; truncated: boolean }> {
  const res = await fetch(`${API_BASE}/api/playlists`, {
    method: 'POST',
    headers: headers(),
    body: JSON.stringify(req),
  })
  if (!res.ok) {
    const err = await res.text()
    throw new Error(err)
  }
  return res.json()
}

export function getLoginUrl(): string {
  return `${API_BASE}/auth/login`
}

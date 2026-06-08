import type {
  UserInfo,
  FilterRequest,
  FilterResponse,
  CreatePlaylistRequest,
} from '../types'

const API_BASE = import.meta.env.VITE_API_URL ?? ''
const SESSION_KEY = 'alsort_session_id'

function getSessionId(): string | null {
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

export async function getMe(signal?: AbortSignal): Promise<UserInfo> {
  const res = await fetch(`${API_BASE}/auth/me`, { headers: headers(), signal })
  if (!res.ok) throw new Error('Not authenticated')
  return res.json()
}

export async function syncTracks(signal?: AbortSignal): Promise<{ synced: number }> {
  const res = await fetch(`${API_BASE}/api/tracks/sync`, {
    method: 'POST',
    headers: headers(),
    signal,
  })
  if (!res.ok) {
    const text = await res.text().catch(() => 'Sync failed')
    throw new Error(text)
  }
  return res.json()
}

export async function filterTracks(req: FilterRequest, signal?: AbortSignal): Promise<FilterResponse> {
  const res = await fetch(`${API_BASE}/api/tracks/filter`, {
    method: 'POST',
    headers: headers(),
    body: JSON.stringify(req),
    signal,
  })
  if (!res.ok) {
    const text = await res.text().catch(() => 'Filter failed')
    throw new Error(text)
  }
  return res.json()
}

export async function createPlaylist(req: CreatePlaylistRequest, signal?: AbortSignal) {
  const res = await fetch(`${API_BASE}/api/playlists`, {
    method: 'POST',
    headers: headers(),
    body: JSON.stringify(req),
    signal,
  })
  if (!res.ok) {
    const text = await res.text().catch(() => 'Playlist creation failed')
    throw new Error(text)
  }
  return res.json()
}

export function getLoginUrl(): string {
  return `${API_BASE}/auth/login`
}

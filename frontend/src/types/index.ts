export interface Track {
  id: string
  track_id: string
  track_name: string
  artists: string
  album: string
  album_image_url: string | null
  duration_ms: number
  explicit: boolean
  popularity: number
  genres: string | null
  year: number | null
  instrumentalness: number | null
  acousticness: number | null
  tempo: number | null
}

export interface FilterCriterion {
  type: FilterType
  operator: FilterOperator
  value: FilterValue
}

export type FilterType =
  | 'year' | 'popularity' | 'duration_ms' | 'explicit'
  | 'artist' | 'album' | 'genre'
  | 'instrumentalness' | 'acousticness' | 'tempo' | 'workout'

export type FilterOperator =
  | '=' | '>' | '<' | '>=' | '<=' | 'between' | 'contains'

export type FilterValue = string | number | boolean | [number, number]

export type SortField = 'year' | 'popularity' | 'duration_ms' | 'tempo' | 'energy' | 'danceability' | 'track_name' | 'artists'
export type SortOrder = 'asc' | 'desc'

export interface FilterRequest {
  and_filters: FilterCriterion[]
  or_filters: FilterCriterion[]
  limit: number
  offset: number
  sort_by?: SortField | null
  sort_order?: SortOrder
}

export const SORT_OPTIONS: { value: SortField; label: string }[] = [
  { value: 'popularity', label: 'Popularidad' },
  { value: 'year', label: 'Año' },
  { value: 'tempo', label: 'Tempo (BPM)' },
  { value: 'duration_ms', label: 'Duración' },
  { value: 'energy', label: 'Energía' },
  { value: 'danceability', label: 'Danceability' },
  { value: 'track_name', label: 'Nombre' },
  { value: 'artists', label: 'Artista' },
]

export interface FilterResponse {
  tracks: Track[]
  total: number
  limit: number
  offset: number
}

export interface CreatePlaylistRequest {
  name: string
  description: string
  public: boolean
  filter_criteria: FilterRequest
}

export interface UserInfo {
  id: string
  spotify_id: string
  display_name: string | null
}

export const FILTER_LABELS: Record<FilterType, string> = {
  year: 'Año',
  popularity: 'Popularidad',
  duration_ms: 'Duración (ms)',
  explicit: 'Explícito',
  artist: 'Artista',
  album: 'Álbum',
  genre: 'Género',
  instrumentalness: 'Instrumentalidad',
  acousticness: 'Acousticidad',
  tempo: 'Tempo (BPM)',
  workout: 'Workout',
}

export const FILTER_OPERATORS: Record<FilterType, FilterOperator[]> = {
  year: ['=', '>', '<', '>=', '<=', 'between'],
  popularity: ['=', '>', '<', '>=', '<='],
  duration_ms: ['>', '<', 'between'],
  explicit: ['='],
  artist: ['contains', '='],
  album: ['contains', '='],
  genre: ['contains', '='],
  instrumentalness: ['>', '<', '>=', '<='],
  acousticness: ['>', '<', '>=', '<='],
  tempo: ['>', '<', '>=', '<=', 'between'],
  workout: ['='],
}

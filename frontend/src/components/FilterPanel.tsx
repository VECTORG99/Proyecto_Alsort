import { useState, useCallback } from 'react'
import type { FilterCriterion, FilterType, FilterOperator, FilterValue } from '../types'
import { FILTER_LABELS, FILTER_OPERATORS } from '../types'
import { useLoading } from '../context/LoadingContext'

interface FilterPanelProps {
  onApply: (andFilters: FilterCriterion[], orFilters: FilterCriterion[]) => void
}

const FILTER_TYPES: FilterType[] = [
  'year', 'popularity', 'duration_ms', 'explicit',
  'artist', 'album', 'genre',
  'instrumentalness', 'acousticness', 'tempo', 'workout',
]

let filterIdCounter = 0

function getDefaultValue(type: FilterType, operator: FilterOperator): FilterValue {
  const currentYear = new Date().getFullYear()
  if (operator === 'between') {
    return type === 'year' ? [currentYear - 10, currentYear] :
           type === 'duration_ms' ? [60000, 300000] :
           type === 'tempo' ? [80, 160] : [0, 1]
  }
  if (type === 'explicit') return true
  if (type === 'workout') return true
  if (type === 'artist' || type === 'album' || type === 'genre') return ''
  if (type === 'year') return currentYear
  if (type === 'duration_ms') return 180000
  if (type === 'popularity') return 50
  if (type === 'instrumentalness' || type === 'acousticness') return 0.5
  if (type === 'tempo') return 120
  return ''
}

export default function FilterPanel({ onApply }: FilterPanelProps) {
  const { isLoading } = useLoading()
  const [andFilters, setAndFilters] = useState<FilterCriterionWithKey[]>([])
  const [orFilters, setOrFilters] = useState<FilterCriterionWithKey[]>([])

  const addFilter = useCallback((group: 'and' | 'or') => {
    const type: FilterType = 'year'
    const operator = FILTER_OPERATORS[type][0]
    const criterion: FilterCriterionWithKey = {
      type, operator, value: getDefaultValue(type, operator), _key: filterIdCounter++,
    }
    if (group === 'and') {
      setAndFilters((prev) => [...prev, criterion])
    } else {
      setOrFilters((prev) => [...prev, criterion])
    }
  }, [])

  const updateFilter = useCallback((
    group: 'and' | 'or',
    key: number,
    updates: Partial<FilterCriterion>
  ) => {
    const setter = group === 'and' ? setAndFilters : setOrFilters
    setter((prev) => {
      const idx = prev.findIndex(f => f._key === key)
      if (idx === -1) return prev
      const next = [...prev]
      const current = { ...next[idx] }

      if (updates.type && updates.type !== current.type) {
        const op = FILTER_OPERATORS[updates.type][0]
        current.type = updates.type
        current.operator = op
        current.value = getDefaultValue(updates.type, op)
      }
      if (updates.operator && updates.operator !== current.operator) {
        current.operator = updates.operator
        current.value = getDefaultValue(current.type, updates.operator)
      }
      if (updates.value !== undefined) {
        current.value = updates.value
      }
      next[idx] = current
      return next
    })
  }, [])

  const removeFilter = useCallback((group: 'and' | 'or', key: number) => {
    const setter = group === 'and' ? setAndFilters : setOrFilters
    setter((prev) => prev.filter(f => f._key !== key))
  }, [])

  function handleApply() {
    onApply(andFilters, orFilters)
  }

  return (
    <div className="filter-panel">
      <h2>Filtros</h2>

      <FilterGroup
        label="Filtros AND (todos deben cumplirse)"
        filters={andFilters}
        group="and"
        onAdd={() => addFilter('and')}
        onUpdate={(i, u) => updateFilter('and', i, u)}
        onRemove={(i) => removeFilter('and', i)}
      />

      <FilterGroup
        label="Filtros OR (al menos uno debe cumplirse)"
        filters={orFilters}
        group="or"
        onAdd={() => addFilter('or')}
        onUpdate={(i, u) => updateFilter('or', i, u)}
        onRemove={(i) => removeFilter('or', i)}
      />

      <button className="btn-apply" onClick={handleApply} disabled={isLoading}>
        {isLoading ? 'Filtrando...' : 'Aplicar Filtros'}
      </button>
    </div>
  )
}

type FilterCriterionWithKey = FilterCriterion & { _key: number }

interface FilterGroupProps {
  label: string
  filters: FilterCriterionWithKey[]
  group: 'and' | 'or'
  onAdd: () => void
  onUpdate: (index: number, updates: Partial<FilterCriterion>) => void
  onRemove: (index: number) => void
}

function FilterGroup({ label, filters, group, onAdd, onUpdate, onRemove }: FilterGroupProps) {
  return (
    <div className="filter-group">
      <div className="filter-group-header">
        <span>{label}</span>
        <button className="btn-add-filter" onClick={onAdd}>+ Añadir filtro</button>
      </div>
      {filters.length === 0 && <p className="filter-empty">Sin filtros. Añade uno para empezar.</p>}
      {filters.map((filter) => (
        <FilterRow
          key={filter._key}
          criterion={filter}
          onChange={(updates) => onUpdate(filter._key, updates)}
          onRemove={() => onRemove(filter._key)}
        />
      ))}
    </div>
  )
}

interface FilterRowProps {
  criterion: FilterCriterion
  onChange: (updates: Partial<FilterCriterion>) => void
  onRemove: () => void
}

function FilterRow({ criterion, onChange, onRemove }: FilterRowProps) {
  const operators = FILTER_OPERATORS[criterion.type]

  return (
    <div className="filter-row">
      <select
        value={criterion.type}
        onChange={(e) => onChange({ type: e.target.value as FilterType })}
      >
        {FILTER_TYPES.map((t) => (
          <option key={t} value={t}>{FILTER_LABELS[t]}</option>
        ))}
      </select>

      <select
        value={criterion.operator}
        onChange={(e) => onChange({ operator: e.target.value as FilterOperator })}
      >
        {operators.map((op) => (
          <option key={op} value={op}>{op}</option>
        ))}
      </select>

      <FilterValueInput
        type={criterion.type}
        operator={criterion.operator}
        value={criterion.value}
        onChange={(v) => onChange({ value: v })}
      />

      <button className="btn-remove-filter" onClick={onRemove} title="Eliminar filtro">✕</button>
    </div>
  )
}

interface FilterValueInputProps {
  type: FilterType
  operator: FilterOperator
  value: FilterValue
  onChange: (value: FilterValue) => void
}

function FilterValueInput({ type, operator, value, onChange }: FilterValueInputProps) {
  if (type === 'explicit' || type === 'workout') {
    return (
      <select value={value ? 'true' : 'false'} onChange={(e) => onChange(e.target.value === 'true')}>
        <option value="true">Sí</option>
        <option value="false">No</option>
      </select>
    )
  }

  if (operator === 'between') {
    const arr = (Array.isArray(value) ? value : [0, 100]) as [number, number]
    return (
      <span className="filter-range">
        <input
          type="number"
          value={arr[0]}
          onChange={(e) => onChange([Number(e.target.value), arr[1]])}
          className="range-input"
        />
        <span>—</span>
        <input
          type="number"
          value={arr[1]}
          onChange={(e) => onChange([arr[0], Number(e.target.value)])}
          className="range-input"
        />
      </span>
    )
  }

  if (type === 'artist' || type === 'album' || type === 'genre') {
    return (
      <input
        type="text"
        value={value as string}
        onChange={(e) => onChange(e.target.value)}
        placeholder={`Buscar ${FILTER_LABELS[type].toLowerCase()}...`}
      />
    )
  }

  if (type === 'instrumentalness' || type === 'acousticness') {
    return (
      <input
        type="number"
        min={0}
        max={1}
        step={0.01}
        value={value as number}
        onChange={(e) => onChange(Number(e.target.value))}
      />
    )
  }

  return (
    <input
      type="number"
      value={value as number}
      onChange={(e) => onChange(Number(e.target.value))}
    />
  )
}

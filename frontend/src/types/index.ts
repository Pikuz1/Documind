// Mirrors the backend's Pydantic response models (backend/app/api/schemas.py).

export interface DocumentInfo {
  id: string
  filename: string
  page_count: number
  chunk_count: number
  created_at: string
}

export interface Source {
  page: number
  text: string
  score: number
}

export interface QueryResult {
  answer: string
  sources: Source[]
  top_score: number | null
  latency_ms: number
}

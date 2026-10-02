import type { DocumentInfo, QueryResult } from '../types'

export class ApiError extends Error {
  readonly status: number

  constructor(status: number, message: string) {
    super(message)
    this.name = 'ApiError'
    this.status = status
  }
}

export function describeError(error: unknown): string {
  return error instanceof Error ? error.message : 'Something went wrong. Please try again.'
}

async function errorMessage(res: Response): Promise<string> {
  const body: unknown = await res.json().catch(() => null)
  // FastAPI sends a string detail for our errors, but a list of field errors for 422s.
  if (body && typeof body === 'object' && 'detail' in body && typeof body.detail === 'string') {
    return body.detail
  }
  return `Request failed (${res.status})`
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  let res: Response
  try {
    res = await fetch(`/api${path}`, init)
  } catch {
    throw new ApiError(0, 'Could not reach the server. Is the backend running?')
  }
  if (!res.ok) {
    throw new ApiError(res.status, await errorMessage(res))
  }
  return (res.status === 204 ? undefined : await res.json()) as T
}

export const api = {
  listDocuments: () => request<DocumentInfo[]>('/documents'),

  uploadDocument: (file: File) => {
    const form = new FormData()
    form.append('file', file)
    // No Content-Type header: the browser sets multipart/form-data with the boundary itself.
    return request<DocumentInfo>('/documents', { method: 'POST', body: form })
  },

  deleteDocument: (id: string) =>
    request<void>(`/documents/${encodeURIComponent(id)}`, { method: 'DELETE' }),

  ask: (documentId: string, question: string) =>
    request<QueryResult>('/query', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ document_id: documentId, question }),
    }),
}

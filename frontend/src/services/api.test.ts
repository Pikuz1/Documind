import { afterEach, beforeEach, describe, expect, it, vi, type MockInstance } from 'vitest'
import type { DocumentInfo, QueryResult } from '../types'
import { ApiError, api, describeError } from './api'

const doc: DocumentInfo = {
  id: 'doc-1',
  filename: 'contract.pdf',
  page_count: 2,
  chunk_count: 2,
  created_at: '2026-10-01 12:00:00',
}

const result: QueryResult = {
  answer: 'Three months (p. 1).',
  sources: [{ page: 1, text: 'Notice period: three months.', score: 0.61 }],
  top_score: 0.61,
  latency_ms: 42,
}

function jsonResponse(body: unknown, status = 200): Response {
  return new Response(JSON.stringify(body), {
    status,
    headers: { 'Content-Type': 'application/json' },
  })
}

let fetchSpy: MockInstance<typeof fetch>

beforeEach(() => {
  fetchSpy = vi.spyOn(globalThis, 'fetch')
})

afterEach(() => {
  vi.restoreAllMocks()
})

function lastRequest(): [string, RequestInit | undefined] {
  const [url, init] = fetchSpy.mock.calls.at(-1)!
  return [String(url), init]
}

describe('api', () => {
  it('lists documents', async () => {
    fetchSpy.mockResolvedValue(jsonResponse([doc]))

    await expect(api.listDocuments()).resolves.toEqual([doc])
    expect(lastRequest()).toEqual(['/api/documents', undefined])
  })

  it('uploads a document as multipart form data', async () => {
    fetchSpy.mockResolvedValue(jsonResponse(doc, 201))
    const file = new File(['%PDF-'], 'contract.pdf', { type: 'application/pdf' })

    await expect(api.uploadDocument(file)).resolves.toEqual(doc)

    const [url, init] = lastRequest()
    expect(url).toBe('/api/documents')
    expect(init?.method).toBe('POST')
    expect(init?.body).toBeInstanceOf(FormData)
    expect((init!.body as FormData).get('file')).toBe(file)
    expect(init?.headers).toBeUndefined()
  })

  it('deletes a document and resolves to undefined on 204', async () => {
    fetchSpy.mockResolvedValue(new Response(null, { status: 204 }))

    await expect(api.deleteDocument('doc 1/x')).resolves.toBeUndefined()
    expect(lastRequest()).toEqual(['/api/documents/doc%201%2Fx', { method: 'DELETE' }])
  })

  it('asks a question as JSON', async () => {
    fetchSpy.mockResolvedValue(jsonResponse(result))

    await expect(api.ask('doc-1', 'What is the notice period?')).resolves.toEqual(result)

    const [url, init] = lastRequest()
    expect(url).toBe('/api/query')
    expect(init?.method).toBe('POST')
    expect(init?.headers).toEqual({ 'Content-Type': 'application/json' })
    expect(JSON.parse(init?.body as string)).toEqual({
      document_id: 'doc-1',
      question: 'What is the notice period?',
    })
  })

  it('uses the server detail message for API errors', async () => {
    fetchSpy.mockResolvedValue(jsonResponse({ detail: 'Document not found' }, 404))

    const error = await api.listDocuments().catch((e: unknown) => e)

    expect(error).toBeInstanceOf(ApiError)
    expect(error).toMatchObject({ status: 404, message: 'Document not found' })
  })

  it('falls back to a generic message for validation error lists', async () => {
    fetchSpy.mockResolvedValue(jsonResponse({ detail: [{ msg: 'Field required' }] }, 422))

    await expect(api.listDocuments()).rejects.toMatchObject({
      status: 422,
      message: 'Request failed (422)',
    })
  })

  it('falls back to a generic message when the body is not JSON', async () => {
    fetchSpy.mockResolvedValue(new Response('Bad Gateway', { status: 502 }))

    await expect(api.listDocuments()).rejects.toMatchObject({
      status: 502,
      message: 'Request failed (502)',
    })
  })

  it('reports an unreachable server as an ApiError', async () => {
    fetchSpy.mockRejectedValue(new TypeError('Failed to fetch'))

    await expect(api.listDocuments()).rejects.toMatchObject({
      name: 'ApiError',
      status: 0,
      message: 'Could not reach the server. Is the backend running?',
    })
  })
})

describe('describeError', () => {
  it('uses the message of an Error', () => {
    expect(describeError(new ApiError(404, 'Document not found'))).toBe('Document not found')
  })

  it('falls back to a generic message for anything else', () => {
    expect(describeError('boom')).toBe('Something went wrong. Please try again.')
  })
})

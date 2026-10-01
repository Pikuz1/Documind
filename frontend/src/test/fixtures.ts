import type { DocumentInfo, QueryResult } from '../types'

export const contract: DocumentInfo = {
  id: 'doc-1',
  filename: 'employment_contract.pdf',
  page_count: 6,
  chunk_count: 12,
  created_at: '2026-10-02 09:00:00',
}

export const lease: DocumentInfo = {
  id: 'doc-2',
  filename: 'rental_agreement.pdf',
  page_count: 4,
  chunk_count: 8,
  created_at: '2026-10-01 18:30:00',
}

export const answer: QueryResult = {
  answer: 'The notice period is three months to the end of the month (p. 6).',
  sources: [
    { page: 6, text: 'Nach Ablauf der Probezeit beträgt die Kündigungsfrist drei Monate.', score: 0.61 },
    { page: 2, text: 'Während der Probezeit gilt eine Frist von zwei Wochen.', score: 0.48 },
  ],
  top_score: 0.61,
  latency_ms: 840,
}

export const notFound: QueryResult = {
  answer: 'I could not find this in the document.',
  sources: [],
  top_score: null,
  latency_ms: 35,
}

export function pdfFile(name = 'contract.pdf'): File {
  return new File(['%PDF-1.4'], name, { type: 'application/pdf' })
}

/** A promise you resolve or reject from the test, to control timing. */
export function deferred<T>() {
  let resolve!: (value: T) => void
  let reject!: (reason: unknown) => void
  const promise = new Promise<T>((res, rej) => {
    resolve = res
    reject = rej
  })
  return { promise, resolve, reject }
}

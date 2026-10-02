import { useCallback, useState } from 'react'
import { api, describeError } from '../services/api'
import type { QueryResult } from '../types'

interface Outcome {
  documentId: string
  result: QueryResult | null
  error: string | null
}

export function useAsk(documentId: string | null) {
  // Each outcome remembers its document, so switching documents hides it without an effect,
  // and an answer that arrives after a switch never shows up under the wrong document.
  const [outcome, setOutcome] = useState<Outcome | null>(null)
  const [pendingId, setPendingId] = useState<string | null>(null)

  const ask = useCallback(
    async (question: string) => {
      if (!documentId) return
      setPendingId(documentId)
      try {
        const result = await api.ask(documentId, question)
        setOutcome({ documentId, result, error: null })
      } catch (e) {
        setOutcome({ documentId, result: null, error: describeError(e) })
      } finally {
        setPendingId((current) => (current === documentId ? null : current))
      }
    },
    [documentId],
  )

  const current = outcome?.documentId === documentId ? outcome : null
  return {
    ask,
    result: current?.result ?? null,
    error: current?.error ?? null,
    loading: documentId !== null && pendingId === documentId,
  }
}

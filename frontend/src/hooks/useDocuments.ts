import { useCallback, useEffect, useState } from 'react'
import { api, describeError } from '../services/api'
import type { DocumentInfo } from '../types'

export function useDocuments() {
  const [documents, setDocuments] = useState<DocumentInfo[]>([])
  const [selectedId, setSelectedId] = useState<string | null>(null)
  const [loading, setLoading] = useState(true)
  const [uploading, setUploading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    let active = true // ignore the response if the component unmounted meanwhile
    api
      .listDocuments()
      .then((docs) => {
        if (!active) return
        setDocuments(docs)
        setSelectedId(docs[0]?.id ?? null) // newest first, so this is the latest upload
      })
      .catch((e: unknown) => active && setError(describeError(e)))
      .finally(() => active && setLoading(false))
    return () => {
      active = false
    }
  }, [])

  const upload = useCallback(async (file: File) => {
    setUploading(true)
    setError(null)
    try {
      const doc = await api.uploadDocument(file)
      setDocuments((docs) => [doc, ...docs])
      setSelectedId(doc.id)
    } catch (e) {
      setError(describeError(e))
    } finally {
      setUploading(false)
    }
  }, [])

  const remove = useCallback(async (id: string) => {
    setError(null)
    try {
      await api.deleteDocument(id)
      setDocuments((docs) => docs.filter((doc) => doc.id !== id))
      setSelectedId((current) => (current === id ? null : current))
    } catch (e) {
      setError(describeError(e))
    }
  }, [])

  return { documents, selectedId, select: setSelectedId, upload, remove, loading, uploading, error }
}

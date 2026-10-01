import type { DocumentInfo } from '../types'

export interface DocumentListProps {
  documents: DocumentInfo[]
  selectedId: string | null
  onSelect: (id: string) => void
  onDelete: (id: string) => void
  loading: boolean
}

export function DocumentList({
  documents,
  selectedId,
  onSelect,
  onDelete,
  loading,
}: DocumentListProps) {
  if (loading) {
    return (
      <p role="status" className="text-sm text-slate-500">
        Loading documents…
      </p>
    )
  }
  if (documents.length === 0) {
    return <p className="text-sm text-slate-500">No documents yet. Upload a PDF to get started.</p>
  }

  return (
    <ul aria-label="Documents" className="flex flex-col gap-1">
      {documents.map((doc) => {
        const selected = doc.id === selectedId
        return (
          <li
            key={doc.id}
            className={`flex items-center gap-2 rounded-md border px-3 py-2 ${
              selected ? 'border-slate-800 bg-slate-100' : 'border-transparent hover:bg-slate-50'
            }`}
          >
            <button
              type="button"
              onClick={() => onSelect(doc.id)}
              aria-current={selected ? 'true' : undefined}
              className="flex min-w-0 flex-1 flex-col text-left"
            >
              <span className="truncate font-medium text-slate-900">{doc.filename}</span>
              <span className="text-xs text-slate-500">
                {doc.page_count} {doc.page_count === 1 ? 'page' : 'pages'}
              </span>
            </button>
            <button
              type="button"
              onClick={() => onDelete(doc.id)}
              aria-label={`Delete ${doc.filename}`}
              className="rounded px-2 py-1 text-sm text-slate-500 hover:bg-red-50 hover:text-red-700"
            >
              Delete
            </button>
          </li>
        )
      })}
    </ul>
  )
}

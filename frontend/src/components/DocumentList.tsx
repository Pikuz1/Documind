import type { DocumentListProps } from '../types/components'
import { formatUploadDate, pluralize } from '../utils/format'
import { DocumentIcon, TrashIcon } from './Icons'

export function DocumentList({
  documents,
  selectedId,
  onSelect,
  onDelete,
  loading,
}: DocumentListProps) {
  if (loading) {
    return (
      <div role="status" className="flex flex-col gap-2">
        <span className="sr-only">Loading documents…</span>
        {[0, 1].map((row) => (
          <div key={row} className="h-14 animate-pulse rounded-xl bg-slate-100" />
        ))}
      </div>
    )
  }
  if (documents.length === 0) {
    return (
      <p className="rounded-xl bg-slate-50 px-3 py-4 text-center text-sm text-slate-500">
        No documents yet. Upload a PDF to get started.
      </p>
    )
  }

  return (
    <ul aria-label="Documents" className="flex flex-col gap-1.5">
      {documents.map((doc) => {
        const selected = doc.id === selectedId
        return (
          <li
            key={doc.id}
            className={`group flex items-center gap-1 rounded-xl border transition ${
              selected
                ? 'border-indigo-200 bg-indigo-50 shadow-sm'
                : 'border-transparent hover:border-slate-200 hover:bg-slate-50'
            }`}
          >
            <button
              type="button"
              onClick={() => onSelect(doc.id)}
              aria-current={selected ? 'true' : undefined}
              className="flex min-w-0 flex-1 items-center gap-3 rounded-xl px-3 py-2.5 text-left focus:outline-none focus-visible:ring-2 focus-visible:ring-indigo-300"
            >
              <span
                className={`grid size-9 shrink-0 place-items-center rounded-lg ${
                  selected ? 'bg-indigo-600 text-white' : 'bg-slate-100 text-slate-500'
                }`}
              >
                <DocumentIcon className="size-5" />
              </span>
              <span className="flex min-w-0 flex-col">
                <span className="truncate text-sm font-medium text-slate-900">{doc.filename}</span>
                <span className="text-xs text-slate-500">
                  {pluralize(doc.page_count, 'page')} · {formatUploadDate(doc.created_at)}
                </span>
              </span>
            </button>
            <button
              type="button"
              onClick={() => onDelete(doc.id)}
              aria-label={`Delete ${doc.filename}`}
              title="Delete"
              className="mr-1 rounded-lg p-3.5 text-slate-400 sm:mr-1.5 sm:p-2 transition hover:bg-red-50 hover:text-red-600 focus:opacity-100 focus:outline-none focus-visible:ring-2 focus-visible:ring-red-200 sm:opacity-0 sm:group-hover:opacity-100"
            >
              <TrashIcon className="size-4" />
            </button>
          </li>
        )
      })}
    </ul>
  )
}

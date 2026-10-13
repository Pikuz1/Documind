import { useState, type ChangeEvent, type DragEvent } from 'react'
import type { UploadZoneProps } from '../types/components'
import { AlertIcon, Spinner, UploadIcon } from './Icons'

function isPdf(file: File): boolean {
  return file.type === 'application/pdf' || file.name.toLowerCase().endsWith('.pdf')
}

export function UploadZone({ onUpload, uploading, error }: UploadZoneProps) {
  const [dragging, setDragging] = useState(false)
  const [rejected, setRejected] = useState<string | null>(null)

  function handleFile(file: File | undefined) {
    if (!file || uploading) return
    if (!isPdf(file)) {
      setRejected(`"${file.name}" is not a PDF.`)
      return
    }
    setRejected(null)
    onUpload(file)
  }

  function handleChange(event: ChangeEvent<HTMLInputElement>) {
    handleFile(event.target.files?.[0])
    event.target.value = '' // lets the same file be picked again after an error
  }

  function handleDrop(event: DragEvent<HTMLLabelElement>) {
    event.preventDefault()
    setDragging(false)
    handleFile(event.dataTransfer.files[0])
  }

  function handleDragOver(event: DragEvent<HTMLLabelElement>) {
    event.preventDefault() // required, otherwise the browser opens the dropped file
    setDragging(true)
  }

  const message = rejected ?? error

  return (
    <div className="flex flex-col gap-2">
      <label
        onDragOver={handleDragOver}
        onDragLeave={() => setDragging(false)}
        onDrop={handleDrop}
        aria-busy={uploading}
        className={`group flex cursor-pointer items-center gap-4 rounded-2xl border-2 border-dashed bg-white px-4 py-4 text-left shadow-sm sm:flex-col sm:gap-3 sm:px-5 sm:py-7 sm:text-center transition focus-within:ring-4 focus-within:ring-indigo-100 ${
          dragging
            ? 'border-indigo-500 bg-indigo-50'
            : 'border-slate-200 hover:border-indigo-300 hover:bg-indigo-50/40'
        } ${uploading ? 'cursor-wait' : ''}`}
      >
        <span
          className={`grid size-11 shrink-0 place-items-center rounded-full transition sm:size-12 ${
            dragging ? 'bg-indigo-600 text-white' : 'bg-indigo-50 text-indigo-600'
          }`}
        >
          {uploading ? <Spinner className="size-5" /> : <UploadIcon className="size-6" />}
        </span>
        <span className="flex flex-col gap-0.5">
          <span className="font-semibold text-slate-900">
            {uploading ? 'Uploading and indexing…' : 'Upload a contract'}
          </span>
          <span className="text-sm text-slate-500">
            {uploading ? (
              'Reading the pages and finding the clauses'
            ) : (
              <>
                <span className="sm:hidden">Tap to choose a PDF</span>
                <span className="hidden sm:inline">Drop a PDF here or click to browse</span>
              </>
            )}
          </span>
        </span>
        <span className="hidden rounded-full bg-slate-100 px-2.5 py-0.5 text-xs font-medium text-slate-600 sm:inline">
          German or English · PDF
        </span>
        <input
          type="file"
          accept="application/pdf,.pdf"
          onChange={handleChange}
          disabled={uploading}
          data-testid="upload-input"
          className="sr-only"
        />
      </label>
      {message && (
        <p
          role="alert"
          className="flex items-start gap-2 rounded-xl border border-red-200 bg-red-50 px-3 py-2.5 text-sm text-red-800"
        >
          <AlertIcon className="mt-0.5 size-4 shrink-0" />
          <span>{message}</span>
        </p>
      )}
    </div>
  )
}

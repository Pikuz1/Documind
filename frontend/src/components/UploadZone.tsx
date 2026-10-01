import { useState, type ChangeEvent, type DragEvent } from 'react'

export interface UploadZoneProps {
  onUpload: (file: File) => void
  uploading: boolean
  error: string | null
}

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
        className={`flex cursor-pointer flex-col items-center gap-1 rounded-lg border-2 border-dashed px-4 py-6 text-center transition-colors focus-within:ring-2 focus-within:ring-slate-400 ${
          dragging ? 'border-slate-700 bg-slate-100' : 'border-slate-300 hover:border-slate-500'
        } ${uploading ? 'cursor-wait opacity-70' : ''}`}
      >
        <span className="font-medium text-slate-800">
          {uploading ? 'Uploading and indexing…' : 'Drop a PDF or click to upload'}
        </span>
        <span className="text-sm text-slate-500">German or English contracts</span>
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
        <p role="alert" className="text-sm text-red-700">
          {message}
        </p>
      )}
    </div>
  )
}

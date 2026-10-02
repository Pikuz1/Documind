// Props of the UI components in src/components.
import type { DocumentInfo, QueryResult } from '.'

export interface UploadZoneProps {
  onUpload: (file: File) => void
  uploading: boolean
  error: string | null
}

export interface DocumentListProps {
  documents: DocumentInfo[]
  selectedId: string | null
  onSelect: (id: string) => void
  onDelete: (id: string) => void
  loading: boolean
}

export interface QuestionFormProps {
  onAsk: (question: string) => void
  loading: boolean
  disabled?: boolean
}

export interface AnswerCardProps {
  result: QueryResult | null
  loading: boolean
  error: string | null
}

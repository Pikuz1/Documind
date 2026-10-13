// Props of the UI components in src/components.
import type { ReactNode } from 'react'
import type { DocumentInfo, QueryResult, Source } from '.'

export interface IconProps {
  className?: string
}

export interface SvgProps extends IconProps {
  children: ReactNode
}

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

export interface SourceItemProps {
  source: Source
  /** Set on the first source of each page, so citation badges can link to it. */
  anchorId?: string
}

export interface CitedTextProps {
  text: string
  /** Pages that have a source passage below; only these citations become links. */
  linkedPages: Set<number>
}

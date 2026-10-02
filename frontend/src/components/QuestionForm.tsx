import { useState, type FormEvent, type KeyboardEvent } from 'react'
import type { QuestionFormProps } from '../types/components'

const MAX_LENGTH = 500 // matches QueryIn.question on the backend

export function QuestionForm({ onAsk, loading, disabled = false }: QuestionFormProps) {
  const [question, setQuestion] = useState('')
  const trimmed = question.trim()
  const canSubmit = trimmed.length > 0 && !loading && !disabled

  function submit() {
    if (canSubmit) onAsk(trimmed)
  }

  function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    submit()
  }

  function handleKeyDown(event: KeyboardEvent<HTMLTextAreaElement>) {
    // Enter sends, Shift+Enter adds a line; never send while an IME is composing.
    if (event.key === 'Enter' && !event.shiftKey && !event.nativeEvent.isComposing) {
      event.preventDefault()
      submit()
    }
  }

  return (
    <form onSubmit={handleSubmit} className="flex flex-col gap-2">
      <label htmlFor="question" className="text-sm font-medium text-slate-700">
        Ask a question about this contract
      </label>
      <textarea
        id="question"
        value={question}
        onChange={(event) => setQuestion(event.target.value)}
        onKeyDown={handleKeyDown}
        maxLength={MAX_LENGTH}
        rows={3}
        disabled={disabled}
        placeholder="e.g. What is the notice period? / Wie lange ist die Kündigungsfrist?"
        data-testid="question-input"
        className="resize-y rounded-md border border-slate-300 px-3 py-2 text-slate-900 focus:border-slate-500 focus:outline-none focus:ring-2 focus:ring-slate-200 disabled:bg-slate-50"
      />
      <div className="flex items-center justify-between">
        <span className="text-xs text-slate-500">
          {question.length}/{MAX_LENGTH} · Enter to ask, Shift+Enter for a new line
        </span>
        <button
          type="submit"
          disabled={!canSubmit}
          data-testid="ask-button"
          className="rounded-md bg-slate-900 px-4 py-2 text-sm font-medium text-white hover:bg-slate-700 disabled:cursor-not-allowed disabled:bg-slate-300"
        >
          {loading ? 'Asking…' : 'Ask'}
        </button>
      </div>
    </form>
  )
}

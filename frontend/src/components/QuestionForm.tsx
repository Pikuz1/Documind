import { useState, type FormEvent, type KeyboardEvent } from 'react'
import type { QuestionFormProps } from '../types/components'
import { SendIcon, Spinner } from './Icons'

const MAX_LENGTH = 500 // matches QueryIn.question on the backend

const SUGGESTED_QUESTIONS = [
  'What is the notice period?',
  'How many vacation days do I get?',
  'Wie lange ist die Probezeit?',
]

export function QuestionForm({ onAsk, loading, disabled = false }: QuestionFormProps) {
  const [question, setQuestion] = useState('')
  const trimmed = question.trim()
  const canSubmit = trimmed.length > 0 && !loading && !disabled

  function submit() {
    if (canSubmit) onAsk(trimmed)
  }

  function askSuggestion(suggestion: string) {
    setQuestion(suggestion)
    onAsk(suggestion)
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
    <form onSubmit={handleSubmit} className="flex flex-col gap-3">
      <label htmlFor="question" className="text-sm font-semibold text-slate-800">
        Ask a question about this contract
      </label>
      <div className="relative rounded-2xl border border-slate-200 bg-white shadow-sm transition focus-within:border-indigo-400 focus-within:ring-4 focus-within:ring-indigo-100">
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
          className="block w-full resize-none rounded-2xl bg-transparent px-4 pt-3 pb-16 text-slate-900 sm:pb-12 placeholder:text-slate-400 focus:outline-none disabled:cursor-not-allowed"
        />
        <div className="absolute inset-x-3 bottom-2.5 flex items-center justify-between gap-2">
          <span className="text-xs text-slate-400">
            {question.length}/{MAX_LENGTH}
            <span className="hidden sm:inline"> · Enter to ask, Shift+Enter for a new line</span>
          </span>
          <button
            type="submit"
            disabled={!canSubmit}
            data-testid="ask-button"
            className="inline-flex min-h-11 items-center gap-1.5 rounded-xl bg-indigo-600 px-4 py-2 text-sm sm:min-h-0 font-semibold text-white shadow-sm transition hover:bg-indigo-500 focus:outline-none focus-visible:ring-4 focus-visible:ring-indigo-200 disabled:cursor-not-allowed disabled:bg-slate-200 disabled:text-slate-400 disabled:shadow-none"
          >
            {loading ? <Spinner /> : <SendIcon className="size-4" />}
            {loading ? 'Asking…' : 'Ask'}
          </button>
        </div>
      </div>
      {question.length === 0 && !disabled && (
        <div className="flex flex-wrap items-center gap-2">
          <span className="text-xs font-medium text-slate-500">Try:</span>
          {SUGGESTED_QUESTIONS.map((suggestion) => (
            <button
              key={suggestion}
              type="button"
              onClick={() => askSuggestion(suggestion)}
              disabled={loading}
              className="min-h-11 rounded-full border border-slate-200 bg-white px-3.5 py-1 text-xs sm:min-h-0 font-medium text-slate-600 transition hover:border-indigo-300 hover:bg-indigo-50 hover:text-indigo-700 disabled:cursor-not-allowed disabled:opacity-50"
            >
              {suggestion}
            </button>
          ))}
        </div>
      )}
    </form>
  )
}

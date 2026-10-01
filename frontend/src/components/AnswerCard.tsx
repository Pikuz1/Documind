import type { QueryResult, Source } from '../types'

export interface AnswerCardProps {
  result: QueryResult | null
  loading: boolean
  error: string | null
}

function formatLatency(ms: number): string {
  return ms < 1000 ? `${ms} ms` : `${(ms / 1000).toFixed(1)} s`
}

function SourceItem({ source }: { source: Source }) {
  const percent = Math.round(source.score * 100)
  return (
    <li data-testid="source-item" className="flex flex-col gap-1 rounded-md bg-slate-50 p-3">
      <div className="flex items-center gap-3 text-sm">
        <span className="font-medium text-slate-800">Page {source.page}</span>
        <div
          role="meter"
          aria-label={`Relevance of page ${source.page}`}
          aria-valuemin={0}
          aria-valuemax={100}
          aria-valuenow={percent}
          aria-valuetext={`${percent}%`}
          className="h-1.5 w-24 overflow-hidden rounded-full bg-slate-200"
        >
          <div className="h-full bg-slate-700" style={{ width: `${percent}%` }} />
        </div>
        <span className="text-xs text-slate-500">{percent}% relevant</span>
      </div>
      <p className="whitespace-pre-line text-sm text-slate-600">{source.text}</p>
    </li>
  )
}

export function AnswerCard({ result, loading, error }: AnswerCardProps) {
  if (loading) {
    return (
      <div
        data-testid="answer-skeleton"
        aria-busy="true"
        className="flex animate-pulse flex-col gap-2 rounded-lg border border-slate-200 p-4"
      >
        <span className="sr-only">Finding the answer…</span>
        <div className="h-4 w-11/12 rounded bg-slate-200" />
        <div className="h-4 w-4/5 rounded bg-slate-200" />
        <div className="h-4 w-2/3 rounded bg-slate-200" />
      </div>
    )
  }
  if (error) {
    return (
      <p role="alert" className="rounded-lg border border-red-200 bg-red-50 p-4 text-sm text-red-800">
        {error}
      </p>
    )
  }
  if (!result) return null

  const found = result.sources.length > 0
  return (
    <article
      data-testid="answer-card"
      className="flex flex-col gap-3 rounded-lg border border-slate-200 p-4"
    >
      <p className={found ? 'text-slate-900' : 'text-slate-600 italic'}>{result.answer}</p>
      {found && (
        <details open className="group">
          <summary className="cursor-pointer text-sm font-medium text-slate-700">
            Sources ({result.sources.length})
          </summary>
          <ul className="mt-2 flex flex-col gap-2">
            {result.sources.map((source, index) => (
              <SourceItem key={`${source.page}-${index}`} source={source} />
            ))}
          </ul>
        </details>
      )}
      <p className="text-xs text-slate-400">
        Answered in {formatLatency(result.latency_ms)} · Not legal advice
      </p>
    </article>
  )
}

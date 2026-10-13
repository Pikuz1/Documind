import { useEffect, useState } from 'react'
import type { AnswerCardProps, CitedTextProps, SourceItemProps } from '../types/components'
import { formatLatency } from '../utils/format'
import { AlertIcon, ChevronIcon, InfoIcon, SparklesIcon, Spinner } from './Icons'

export const SLOW_AFTER_MS = 10_000
const LONG_PASSAGE = 280 // characters; longer passages start collapsed
const CITATION = /\(p\.\s?(\d+)\)/g

function sourceAnchor(page: number): string {
  return `source-page-${page}`
}

function relevanceColor(percent: number): string {
  if (percent >= 50) return 'bg-emerald-500'
  if (percent >= 35) return 'bg-amber-400'
  return 'bg-slate-300'
}

/** Renders "(p. 6)" citations as badges that link to the page's source passage. */
function CitedText({ text, linkedPages }: CitedTextProps) {
  // split() with a capture group alternates: text, page number, text, page number, …
  const parts = text.split(CITATION)
  return (
    <p className="leading-relaxed text-slate-800">
      {parts.map((part, index) => {
        if (index % 2 === 0) return part
        const page = Number(part)
        const badge = 'mx-0.5 inline-flex rounded-md px-1.5 py-0.5 align-baseline text-xs font-semibold'
        return linkedPages.has(page) ? (
          <a
            key={index}
            href={`#${sourceAnchor(page)}`}
            className={`${badge} bg-indigo-100 text-indigo-700 hover:bg-indigo-200`}
          >
            p. {page}
          </a>
        ) : (
          <span key={index} className={`${badge} bg-slate-100 text-slate-600`}>
            p. {page}
          </span>
        )
      })}
    </p>
  )
}

function SourceItem({ source, anchorId }: SourceItemProps) {
  const [expanded, setExpanded] = useState(false)
  const percent = Math.round(source.score * 100)
  const long = source.text.length > LONG_PASSAGE
  return (
    <li
      id={anchorId}
      data-testid="source-item"
      className="scroll-mt-24 rounded-xl border border-slate-200 bg-slate-50/70 p-4"
    >
      <div className="flex flex-wrap items-center gap-3 text-sm">
        <span className="rounded-md bg-white px-2 py-0.5 font-semibold text-slate-800 shadow-sm ring-1 ring-slate-200">
          Page {source.page}
        </span>
        <div
          role="meter"
          aria-label={`Relevance of page ${source.page}`}
          aria-valuemin={0}
          aria-valuemax={100}
          aria-valuenow={percent}
          aria-valuetext={`${percent}%`}
          className="h-1.5 w-24 overflow-hidden rounded-full bg-slate-200"
        >
          <div className={`h-full rounded-full ${relevanceColor(percent)}`} style={{ width: `${percent}%` }} />
        </div>
        <span className="text-xs font-medium text-slate-500">{percent}% relevant</span>
      </div>
      <p
        className={`mt-2 whitespace-pre-line text-sm leading-relaxed text-slate-600 ${
          long && !expanded ? 'line-clamp-4' : ''
        }`}
      >
        {source.text}
      </p>
      {long && (
        <button
          type="button"
          onClick={() => setExpanded((value) => !value)}
          aria-expanded={expanded}
          className="mt-1 min-h-11 text-xs font-semibold text-indigo-600 hover:text-indigo-500 sm:min-h-0"
        >
          {expanded ? 'Show less' : 'Show full passage'}
        </button>
      )}
    </li>
  )
}

function LoadingState() {
  const [slow, setSlow] = useState(false)
  useEffect(() => {
    const timer = setTimeout(() => setSlow(true), SLOW_AFTER_MS)
    return () => clearTimeout(timer)
  }, [])

  return (
    <div
      data-testid="answer-skeleton"
      aria-busy="true"
      className="flex flex-col gap-3 rounded-2xl border border-slate-200 bg-white p-5"
    >
      <p role="status" className="flex items-center gap-2 text-sm font-medium text-indigo-700">
        <Spinner />
        {slow
          ? 'The AI service is responding slowly — still waiting…'
          : 'Searching the contract and writing an answer…'}
      </p>
      <div className="flex animate-pulse flex-col gap-2">
        <div className="h-3.5 w-11/12 rounded bg-slate-200" />
        <div className="h-3.5 w-4/5 rounded bg-slate-200" />
        <div className="h-3.5 w-2/3 rounded bg-slate-200" />
      </div>
    </div>
  )
}

export function AnswerCard({ result, loading, error }: AnswerCardProps) {
  if (loading) return <LoadingState />
  if (error) {
    return (
      <div
        role="alert"
        className="flex items-start gap-3 rounded-2xl border border-red-200 bg-red-50 p-4 text-sm text-red-800"
      >
        <AlertIcon className="mt-0.5 size-5 shrink-0" />
        <p>{error}</p>
      </div>
    )
  }
  if (!result) return null

  const footer = (
    <p className="text-xs text-slate-400">
      Answered in {formatLatency(result.latency_ms)} · Not legal advice
    </p>
  )

  if (result.sources.length === 0) {
    return (
      <article
        data-testid="answer-card"
        className="flex flex-col gap-2 rounded-2xl border border-amber-200 bg-amber-50 p-5"
      >
        <p className="flex items-center gap-2 text-sm font-semibold text-amber-900">
          <InfoIcon className="size-5" />
          Not in this document
        </p>
        <p className="text-sm text-amber-900/90">{result.answer}</p>
        <p className="text-xs text-amber-800/80">
          Try rephrasing, or ask about a specific clause (e.g. notice period, salary, vacation).
        </p>
        {footer}
      </article>
    )
  }

  const firstIndexOfPage = new Map<number, number>()
  result.sources.forEach((source, index) => {
    if (!firstIndexOfPage.has(source.page)) firstIndexOfPage.set(source.page, index)
  })

  return (
    <article
      data-testid="answer-card"
      className="flex flex-col gap-4 rounded-2xl border border-slate-200 bg-white p-5 shadow-sm"
    >
      <div className="flex flex-col gap-2">
        <p className="flex items-center gap-2 text-xs font-semibold tracking-wide text-indigo-600 uppercase">
          <SparklesIcon className="size-4" />
          Answer
        </p>
        <CitedText text={result.answer} linkedPages={new Set(firstIndexOfPage.keys())} />
      </div>
      <details open className="group border-t border-slate-100 pt-3">
        <summary className="flex cursor-pointer list-none items-center gap-1.5 text-sm font-semibold text-slate-700 select-none [&::-webkit-details-marker]:hidden">
          <ChevronIcon className="size-4 transition-transform group-open:rotate-90" />
          Sources ({result.sources.length})
        </summary>
        <ul className="mt-3 flex flex-col gap-2.5">
          {result.sources.map((source, index) => (
            <SourceItem
              key={`${source.page}-${index}`}
              source={source}
              anchorId={firstIndexOfPage.get(source.page) === index ? sourceAnchor(source.page) : undefined}
            />
          ))}
        </ul>
      </details>
      {footer}
    </article>
  )
}

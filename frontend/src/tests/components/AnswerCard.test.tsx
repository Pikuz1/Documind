import { act, render, screen, within } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { afterEach, describe, expect, it, vi } from 'vitest'
import { answer, notFound } from '../fixtures'
import { AnswerCard, SLOW_AFTER_MS } from '../../components/AnswerCard'
import type { QueryResult, Source } from '../../types'

describe('AnswerCard', () => {
  it('renders nothing before a question is asked', () => {
    const { container } = render(<AnswerCard result={null} loading={false} error={null} />)

    expect(container).toBeEmptyDOMElement()
  })

  it('shows a skeleton while loading', () => {
    render(<AnswerCard result={answer} loading error={null} />)

    expect(screen.getByTestId('answer-skeleton')).toHaveAttribute('aria-busy', 'true')
    expect(screen.queryByTestId('answer-card')).not.toBeInTheDocument()
  })

  it('shows an error', () => {
    render(<AnswerCard result={null} loading={false} error="Please try again later." />)

    expect(screen.getByRole('alert')).toHaveTextContent('Please try again later.')
  })

  it('shows the answer with its sources open', () => {
    render(<AnswerCard result={answer} loading={false} error={null} />)

    const card = screen.getByTestId('answer-card')
    expect(card).toHaveTextContent('The notice period is three months to the end of the month')
    expect(within(card).getByText('Sources (2)').closest('details')).toHaveAttribute('open')
    expect(screen.getAllByTestId('source-item')).toHaveLength(2)
  })

  it('shows page, relevance and passage for each source', () => {
    render(<AnswerCard result={answer} loading={false} error={null} />)

    const [first] = screen.getAllByTestId('source-item')
    expect(first).toHaveTextContent('Page 6')
    expect(first).toHaveTextContent('61% relevant')
    expect(first).toHaveTextContent('Kündigungsfrist drei Monate')
    const meter = within(first).getByRole('meter', { name: 'Relevance of page 6' })
    expect(meter).toHaveAttribute('aria-valuenow', '61')
    expect(meter.firstElementChild).toHaveStyle({ width: '61%' })
  })

  it('shows a not-found answer without a sources section', () => {
    render(<AnswerCard result={notFound} loading={false} error={null} />)

    expect(screen.getByTestId('answer-card')).toHaveTextContent(notFound.answer)
    expect(screen.queryByText(/Sources/)).not.toBeInTheDocument()
  })

  it.each([
    [35, 'Answered in 35 ms'],
    [840, 'Answered in 840 ms'],
    [2345, 'Answered in 2.3 s'],
  ])('formats a latency of %i ms', (latency_ms, text) => {
    render(<AnswerCard result={{ ...notFound, latency_ms }} loading={false} error={null} />)

    expect(screen.getByText(new RegExp(text))).toBeInTheDocument()
  })
})

function withSources(sources: Source[], text = answer.answer): QueryResult {
  return { ...answer, answer: text, sources, top_score: sources[0].score }
}

const LONG_PASSAGE = 'Die Arbeitnehmerin hat Anspruch auf Urlaub. '.repeat(10)

describe('AnswerCard citations and sources', () => {
  it('turns page citations into links to their source passage', () => {
    render(<AnswerCard result={answer} loading={false} error={null} />)

    const link = screen.getByRole('link', { name: 'p. 6' })
    expect(link).toHaveAttribute('href', '#source-page-6')
    expect(document.getElementById('source-page-6')).toHaveTextContent('Page 6')
  })

  it('shows citations without a source passage as plain badges', () => {
    const result = withSources(answer.sources, 'The salary is EUR 5,200 (p. 3).')
    render(<AnswerCard result={result} loading={false} error={null} />)

    expect(screen.getByText('p. 3')).toBeInTheDocument()
    expect(screen.queryByRole('link')).not.toBeInTheDocument()
  })

  it('anchors only the first passage of each page', () => {
    const page6 = answer.sources[0]
    const result = withSources([page6, { ...page6, text: 'second passage', score: 0.5 }, answer.sources[1]])
    render(<AnswerCard result={result} loading={false} error={null} />)

    const ids = screen.getAllByTestId('source-item').map((item) => item.id)
    expect(ids).toEqual(['source-page-6', '', 'source-page-2'])
  })

  it.each([
    [0.61, 'bg-emerald-500'],
    [0.4, 'bg-amber-400'],
    [0.2, 'bg-slate-300'],
  ])('colours a relevance of %f with %s', (score, colour) => {
    render(<AnswerCard result={withSources([{ page: 1, text: 'x', score }])} loading={false} error={null} />)

    expect(screen.getByRole('meter').firstElementChild).toHaveClass(colour)
  })

  it('collapses long passages until expanded', async () => {
    const result = withSources([{ page: 4, text: LONG_PASSAGE, score: 0.6 }])
    render(<AnswerCard result={result} loading={false} error={null} />)
    const passage = screen.getByText(LONG_PASSAGE.trim(), { normalizer: (t) => t.trim() })
    const toggle = screen.getByRole('button', { name: 'Show full passage' })
    expect(passage).toHaveClass('line-clamp-4')
    expect(toggle).toHaveAttribute('aria-expanded', 'false')

    await userEvent.click(toggle)
    expect(passage).not.toHaveClass('line-clamp-4')
    expect(screen.getByRole('button', { name: 'Show less' })).toHaveAttribute('aria-expanded', 'true')
  })

  it('does not offer to expand short passages', () => {
    render(<AnswerCard result={answer} loading={false} error={null} />)

    expect(screen.queryByRole('button', { name: 'Show full passage' })).not.toBeInTheDocument()
  })

  it('labels an answer that is not in the document', () => {
    render(<AnswerCard result={notFound} loading={false} error={null} />)

    expect(screen.getByText('Not in this document')).toBeInTheDocument()
  })
})

describe('AnswerCard while waiting', () => {
  afterEach(() => {
    vi.useRealTimers()
  })

  it('tells the user when the AI service is slow', () => {
    vi.useFakeTimers()
    render(<AnswerCard result={null} loading error={null} />)
    expect(screen.getByRole('status')).toHaveTextContent('Searching the contract and writing an answer…')

    act(() => vi.advanceTimersByTime(SLOW_AFTER_MS - 1))
    expect(screen.getByRole('status')).not.toHaveTextContent('slowly')

    act(() => vi.advanceTimersByTime(1))
    expect(screen.getByRole('status')).toHaveTextContent(
      'The AI service is responding slowly — still waiting…',
    )
  })

  it('cancels the slow-response timer when the answer arrives', () => {
    vi.useFakeTimers()
    const clearTimeoutSpy = vi.spyOn(globalThis, 'clearTimeout')
    const { rerender } = render(<AnswerCard result={null} loading error={null} />)

    rerender(<AnswerCard result={answer} loading={false} error={null} />)

    // Only our timer is asserted: React may schedule timers of its own.
    expect(clearTimeoutSpy).toHaveBeenCalledOnce()
  })
})

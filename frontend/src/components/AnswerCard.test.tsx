import { render, screen, within } from '@testing-library/react'
import { describe, expect, it } from 'vitest'
import { answer, notFound } from '../test/fixtures'
import { AnswerCard } from './AnswerCard'

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
    expect(card).toHaveTextContent(answer.answer)
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

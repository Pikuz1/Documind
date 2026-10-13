import { render, screen, within } from '@testing-library/react'
import { describe, expect, it } from 'vitest'
import { Welcome } from '../../components/Welcome'

describe('Welcome', () => {
  it('explains the product with a headline and three steps', () => {
    render(<Welcome />)

    expect(
      screen.getByRole('heading', { name: 'Understand your contract in seconds' }),
    ).toBeInTheDocument()
    const steps = within(screen.getByRole('list')).getAllByRole('listitem')
    expect(steps.map((step) => step.querySelector('span:nth-child(2)')?.textContent)).toEqual([
      '1. Upload a contract',
      '2. Ask in your own words',
      '3. Check the source',
    ])
  })
})

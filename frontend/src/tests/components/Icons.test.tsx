import { render } from '@testing-library/react'
import { describe, expect, it } from 'vitest'
import { DocumentIcon, Spinner } from '../../components/Icons'

describe('Icons', () => {
  it('are hidden from screen readers and have a default size', () => {
    const { container } = render(<DocumentIcon />)

    const svg = container.querySelector('svg')
    expect(svg).toHaveAttribute('aria-hidden', 'true')
    expect(svg).toHaveClass('size-5')
  })

  it('accept a custom class', () => {
    const { container } = render(<DocumentIcon className="size-8 text-red-500" />)

    expect(container.querySelector('svg')).toHaveClass('size-8', 'text-red-500')
  })

  it('spin while loading', () => {
    const { container } = render(<Spinner />)

    expect(container.querySelector('svg')).toHaveClass('animate-spin', 'size-4')
  })
})

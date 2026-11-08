import { render, screen } from '@testing-library/react'
import { describe, expect, it } from 'vitest'
import { DemoNotice } from '../../components/DemoNotice'

describe('DemoNotice', () => {
  it('explains the sample document and that uploads are off', () => {
    render(<DemoNotice error={null} />)

    expect(screen.getByText('Public demo')).toBeInTheDocument()
    expect(screen.getByText(/Uploads are turned off here/)).toBeInTheDocument()
    expect(screen.queryByRole('alert')).not.toBeInTheDocument()
  })

  it('shows an error', () => {
    render(<DemoNotice error="Could not reach the server" />)

    expect(screen.getByRole('alert')).toHaveTextContent('Could not reach the server')
  })
})

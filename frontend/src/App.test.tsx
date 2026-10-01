import { render, screen } from '@testing-library/react'
import { describe, expect, it } from 'vitest'
import App from './App'

describe('App', () => {
  it('renders the app title and tagline', () => {
    render(<App />)

    expect(screen.getByRole('heading', { name: 'DocuMind' })).toBeInTheDocument()
    expect(screen.getByText(/cite the exact page/i)).toBeInTheDocument()
  })
})

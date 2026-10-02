import { render, screen, waitFor, within } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { afterEach, describe, expect, it, vi } from 'vitest'
import App from '../App'
import { api } from '../services/api'
import { answer, contract, lease, pdfFile } from './fixtures'
import type { DocumentInfo } from '../types'

afterEach(() => {
  vi.restoreAllMocks()
})

async function renderApp(documents: DocumentInfo[] = [contract, lease]) {
  vi.spyOn(api, 'listDocuments').mockResolvedValue(documents)
  render(<App />)
  await waitFor(() => expect(screen.queryByText('Loading documents…')).not.toBeInTheDocument())
  return userEvent.setup()
}

describe('App', () => {
  it('shows the title and selects the newest document', async () => {
    await renderApp()

    expect(screen.getByRole('heading', { level: 1, name: 'DocuMind' })).toBeInTheDocument()
    expect(screen.getByRole('heading', { level: 2 })).toHaveTextContent(contract.filename)
    expect(screen.getByText('6 pages · 12 indexed passages')).toBeInTheDocument()
  })

  it('prompts for a document when there are none', async () => {
    await renderApp([])

    expect(screen.getByText(/Upload or select a contract/)).toBeInTheDocument()
    expect(screen.queryByTestId('question-input')).not.toBeInTheDocument()
  })

  it('asks a question about the selected document and shows the cited answer', async () => {
    const user = await renderApp()
    vi.spyOn(api, 'ask').mockResolvedValue(answer)

    await user.type(screen.getByTestId('question-input'), 'What is the notice period?{Enter}')

    expect(await screen.findByTestId('answer-card')).toHaveTextContent(answer.answer)
    expect(screen.getAllByTestId('source-item')).toHaveLength(2)
    expect(api.ask).toHaveBeenCalledWith(contract.id, 'What is the notice period?')
  })

  it('hides the answer after switching to another document', async () => {
    const user = await renderApp()
    vi.spyOn(api, 'ask').mockResolvedValue(answer)
    await user.type(screen.getByTestId('question-input'), 'What is the notice period?{Enter}')
    await screen.findByTestId('answer-card')

    await user.click(screen.getByRole('button', { name: /^rental_agreement/ }))

    expect(screen.getByRole('heading', { level: 2 })).toHaveTextContent(lease.filename)
    expect(screen.queryByTestId('answer-card')).not.toBeInTheDocument()
  })

  it('uploads a document and selects it', async () => {
    const user = await renderApp([lease])
    vi.spyOn(api, 'uploadDocument').mockResolvedValue(contract)

    await user.upload(screen.getByTestId('upload-input'), pdfFile(contract.filename))

    await waitFor(() =>
      expect(screen.getByRole('heading', { level: 2 })).toHaveTextContent(contract.filename),
    )
    const items = within(screen.getByRole('list', { name: 'Documents' })).getAllByRole('listitem')
    expect(items[0]).toHaveTextContent(contract.filename)
  })

  it('deletes the selected document', async () => {
    const user = await renderApp([contract])
    vi.spyOn(api, 'deleteDocument').mockResolvedValue(undefined)

    await user.click(screen.getByRole('button', { name: `Delete ${contract.filename}` }))

    expect(await screen.findByText(/No documents yet/)).toBeInTheDocument()
    expect(screen.getByText(/Upload or select a contract/)).toBeInTheDocument()
  })
})

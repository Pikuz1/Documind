import { render, screen, within } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { describe, expect, it, vi } from 'vitest'
import { contract, lease } from '../test/fixtures'
import { DocumentList, type DocumentListProps } from './DocumentList'

function setup(props: Partial<DocumentListProps> = {}) {
  const onSelect = vi.fn()
  const onDelete = vi.fn()
  render(
    <DocumentList
      documents={[contract, lease]}
      selectedId={contract.id}
      onSelect={onSelect}
      onDelete={onDelete}
      loading={false}
      {...props}
    />,
  )
  return { onSelect, onDelete, user: userEvent.setup() }
}

describe('DocumentList', () => {
  it('shows a loading state', () => {
    setup({ loading: true })

    expect(screen.getByRole('status')).toHaveTextContent('Loading documents…')
  })

  it('shows an empty state', () => {
    setup({ documents: [] })

    expect(screen.getByText(/No documents yet/)).toBeInTheDocument()
  })

  it('lists documents with their page count', () => {
    setup({ documents: [contract, { ...lease, page_count: 1 }] })

    const items = within(screen.getByRole('list', { name: 'Documents' })).getAllByRole('listitem')
    expect(items).toHaveLength(2)
    expect(items[0]).toHaveTextContent('employment_contract.pdf6 pages')
    expect(items[1]).toHaveTextContent('rental_agreement.pdf1 page')
  })

  it('marks the selected document', () => {
    setup({ selectedId: lease.id })

    expect(screen.getByRole('button', { name: /^rental_agreement/ })).toHaveAttribute(
      'aria-current',
      'true',
    )
    expect(screen.getByRole('button', { name: /^employment_contract/ })).not.toHaveAttribute(
      'aria-current',
    )
  })

  it('selects a document', async () => {
    const { onSelect, user } = setup()

    await user.click(screen.getByRole('button', { name: /^rental_agreement/ }))

    expect(onSelect).toHaveBeenCalledWith(lease.id)
  })

  it('deletes a document', async () => {
    const { onDelete, onSelect, user } = setup()

    await user.click(screen.getByRole('button', { name: 'Delete rental_agreement.pdf' }))

    expect(onDelete).toHaveBeenCalledWith(lease.id)
    expect(onSelect).not.toHaveBeenCalled()
  })
})

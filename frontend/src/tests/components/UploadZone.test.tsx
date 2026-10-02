import { fireEvent, render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { describe, expect, it, vi } from 'vitest'
import { pdfFile } from '../fixtures'
import { UploadZone } from '../../components/UploadZone'
import type { UploadZoneProps } from '../../types/components'

function setup(props: Partial<UploadZoneProps> = {}) {
  const onUpload = vi.fn()
  render(<UploadZone onUpload={onUpload} uploading={false} error={null} {...props} />)
  const input = screen.getByTestId<HTMLInputElement>('upload-input')
  const dropZone = input.closest('label')!
  // applyAccept: false — drag-and-drop and some OS pickers ignore the accept attribute.
  const user = userEvent.setup({ applyAccept: false })
  return { onUpload, input, dropZone, user }
}

describe('UploadZone', () => {
  it('uploads a picked PDF and resets the input', async () => {
    const { onUpload, input, user } = setup()
    const file = pdfFile()

    await user.upload(input, file)

    expect(onUpload).toHaveBeenCalledWith(file)
    expect(input.value).toBe('')
  })

  it('accepts a .pdf file even without a MIME type', async () => {
    const { onUpload, input, user } = setup()

    await user.upload(input, new File(['%PDF-'], 'Contract.PDF', { type: '' }))

    expect(onUpload).toHaveBeenCalledOnce()
  })

  it('rejects a file that is not a PDF', async () => {
    const { onUpload, input, user } = setup()

    await user.upload(input, new File(['hi'], 'notes.txt', { type: 'text/plain' }))

    expect(onUpload).not.toHaveBeenCalled()
    expect(screen.getByRole('alert')).toHaveTextContent('"notes.txt" is not a PDF.')
  })

  it('clears the rejection once a valid PDF is picked', async () => {
    const { input, user } = setup()

    await user.upload(input, new File(['hi'], 'notes.txt', { type: 'text/plain' }))
    await user.upload(input, pdfFile())

    expect(screen.queryByRole('alert')).not.toBeInTheDocument()
  })

  it('shows the server error', () => {
    setup({ error: "'scan.pdf' has no extractable text (scanned PDF?)" })

    expect(screen.getByRole('alert')).toHaveTextContent('no extractable text')
  })

  it('shows progress and disables the input while uploading', () => {
    const { input, dropZone } = setup({ uploading: true })

    expect(screen.getByText('Uploading and indexing…')).toBeInTheDocument()
    expect(input).toBeDisabled()
    expect(dropZone).toHaveAttribute('aria-busy', 'true')
  })

  it('uploads a dropped PDF', () => {
    const { onUpload, dropZone } = setup()
    const file = pdfFile()

    fireEvent.drop(dropZone, { dataTransfer: { files: [file] } })

    expect(onUpload).toHaveBeenCalledWith(file)
  })

  it('highlights the drop zone while dragging over it', () => {
    const { dropZone } = setup()

    fireEvent.dragOver(dropZone)
    expect(dropZone).toHaveClass('border-slate-700')

    fireEvent.dragLeave(dropZone)
    expect(dropZone).not.toHaveClass('border-slate-700')
  })

  it('ignores drops while uploading and drops without files', () => {
    const { onUpload, dropZone } = setup({ uploading: true })

    fireEvent.drop(dropZone, { dataTransfer: { files: [pdfFile()] } })
    fireEvent.drop(dropZone, { dataTransfer: { files: [] } })

    expect(onUpload).not.toHaveBeenCalled()
  })
})

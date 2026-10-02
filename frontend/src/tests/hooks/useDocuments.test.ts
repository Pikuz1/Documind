import { act, renderHook, waitFor } from '@testing-library/react'
import { afterEach, describe, expect, it, vi } from 'vitest'
import { ApiError, api } from '../../services/api'
import { contract, deferred, lease, pdfFile } from '../fixtures'
import type { DocumentInfo } from '../../types'
import { useDocuments } from '../../hooks/useDocuments'

afterEach(() => {
  vi.restoreAllMocks()
})

async function renderLoaded(docs: DocumentInfo[] = [contract, lease]) {
  vi.spyOn(api, 'listDocuments').mockResolvedValue(docs)
  const hook = renderHook(() => useDocuments())
  await waitFor(() => expect(hook.result.current.loading).toBe(false))
  return hook
}

describe('useDocuments', () => {
  it('loads documents and selects the newest one', async () => {
    const { result } = await renderLoaded()

    expect(result.current.documents).toEqual([contract, lease])
    expect(result.current.selectedId).toBe(contract.id)
    expect(result.current.error).toBeNull()
  })

  it('is loading until the list arrives', () => {
    vi.spyOn(api, 'listDocuments').mockReturnValue(new Promise(() => {}))

    const { result } = renderHook(() => useDocuments())

    expect(result.current.loading).toBe(true)
  })

  it('selects nothing when there are no documents', async () => {
    const { result } = await renderLoaded([])

    expect(result.current.selectedId).toBeNull()
  })

  it('reports a failed load', async () => {
    vi.spyOn(api, 'listDocuments').mockRejectedValue(new ApiError(0, 'Could not reach the server'))

    const { result } = renderHook(() => useDocuments())

    await waitFor(() => expect(result.current.loading).toBe(false))
    expect(result.current.error).toBe('Could not reach the server')
  })

  it.each([
    ['resolves', (d: ReturnType<typeof deferred<DocumentInfo[]>>) => d.resolve([contract])],
    ['rejects', (d: ReturnType<typeof deferred<DocumentInfo[]>>) => d.reject(new Error('late'))],
  ])('ignores a load that %s after unmount', async (_label, settle) => {
    const pending = deferred<DocumentInfo[]>()
    vi.spyOn(api, 'listDocuments').mockReturnValue(pending.promise)
    const { result, unmount } = renderHook(() => useDocuments())

    unmount()
    settle(pending)
    await pending.promise.catch(() => {})

    expect(result.current.documents).toEqual([])
    expect(result.current.error).toBeNull()
  })

  it('selects a document', async () => {
    const { result } = await renderLoaded()

    act(() => result.current.select(lease.id))

    expect(result.current.selectedId).toBe(lease.id)
  })

  it('uploads a document, shows it first and selects it', async () => {
    const { result } = await renderLoaded([lease])
    const pending = deferred<DocumentInfo>()
    vi.spyOn(api, 'uploadDocument').mockReturnValue(pending.promise)

    let upload!: Promise<void>
    act(() => {
      upload = result.current.upload(pdfFile())
    })
    expect(result.current.uploading).toBe(true)

    await act(async () => {
      pending.resolve(contract)
      await upload
    })

    expect(result.current.uploading).toBe(false)
    expect(result.current.documents).toEqual([contract, lease])
    expect(result.current.selectedId).toBe(contract.id)
  })

  it('reports a failed upload', async () => {
    const { result } = await renderLoaded([lease])
    vi.spyOn(api, 'uploadDocument').mockRejectedValue(
      new ApiError(422, "'scan.pdf' has no extractable text (scanned PDF?)"),
    )

    await act(() => result.current.upload(pdfFile('scan.pdf')))

    expect(result.current.error).toBe("'scan.pdf' has no extractable text (scanned PDF?)")
    expect(result.current.uploading).toBe(false)
    expect(result.current.documents).toEqual([lease])
  })

  it('removes the selected document and clears the selection', async () => {
    const { result } = await renderLoaded()
    vi.spyOn(api, 'deleteDocument').mockResolvedValue(undefined)

    await act(() => result.current.remove(contract.id))

    expect(api.deleteDocument).toHaveBeenCalledWith(contract.id)
    expect(result.current.documents).toEqual([lease])
    expect(result.current.selectedId).toBeNull()
  })

  it('keeps the selection when removing another document', async () => {
    const { result } = await renderLoaded()
    vi.spyOn(api, 'deleteDocument').mockResolvedValue(undefined)

    await act(() => result.current.remove(lease.id))

    expect(result.current.selectedId).toBe(contract.id)
  })

  it('reports a failed delete and keeps the document', async () => {
    const { result } = await renderLoaded()
    vi.spyOn(api, 'deleteDocument').mockRejectedValue(new ApiError(404, 'Document not found'))

    await act(() => result.current.remove(contract.id))

    expect(result.current.error).toBe('Document not found')
    expect(result.current.documents).toEqual([contract, lease])
  })
})

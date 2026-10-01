import { act, renderHook } from '@testing-library/react'
import { afterEach, describe, expect, it, vi } from 'vitest'
import { ApiError, api } from '../services/api'
import { answer, deferred, notFound } from '../test/fixtures'
import type { QueryResult } from '../types'
import { useAsk } from './useAsk'

afterEach(() => {
  vi.restoreAllMocks()
})

describe('useAsk', () => {
  it('starts empty', () => {
    const { result } = renderHook(() => useAsk('doc-1'))

    expect(result.current).toMatchObject({ result: null, error: null, loading: false })
  })

  it('asks a question and returns the answer', async () => {
    vi.spyOn(api, 'ask').mockResolvedValue(answer)
    const { result } = renderHook(() => useAsk('doc-1'))

    await act(() => result.current.ask('What is the notice period?'))

    expect(api.ask).toHaveBeenCalledWith('doc-1', 'What is the notice period?')
    expect(result.current.result).toEqual(answer)
    expect(result.current.loading).toBe(false)
  })

  it('is loading while the answer is pending', async () => {
    const pending = deferred<QueryResult>()
    vi.spyOn(api, 'ask').mockReturnValue(pending.promise)
    const { result } = renderHook(() => useAsk('doc-1'))

    let request!: Promise<void>
    act(() => {
      request = result.current.ask('What is the notice period?')
    })
    expect(result.current.loading).toBe(true)

    await act(async () => {
      pending.resolve(answer)
      await request
    })
    expect(result.current.loading).toBe(false)
  })

  it('reports a failed request', async () => {
    vi.spyOn(api, 'ask').mockRejectedValue(
      new ApiError(503, 'The answer service is unavailable right now. Please try again later.'),
    )
    const { result } = renderHook(() => useAsk('doc-1'))

    await act(() => result.current.ask('What is the notice period?'))

    expect(result.current.error).toBe(
      'The answer service is unavailable right now. Please try again later.',
    )
    expect(result.current.result).toBeNull()
  })

  it('replaces a previous error with the next answer', async () => {
    vi.spyOn(api, 'ask').mockRejectedValueOnce(new Error('boom')).mockResolvedValueOnce(notFound)
    const { result } = renderHook(() => useAsk('doc-1'))

    await act(() => result.current.ask('first'))
    await act(() => result.current.ask('second'))

    expect(result.current.error).toBeNull()
    expect(result.current.result).toEqual(notFound)
  })

  it('does nothing without a document', async () => {
    vi.spyOn(api, 'ask')
    const { result } = renderHook(() => useAsk(null))

    await act(() => result.current.ask('What is the notice period?'))

    expect(api.ask).not.toHaveBeenCalled()
    expect(result.current.loading).toBe(false)
  })

  it('hides the answer after switching documents and shows it again when switching back', async () => {
    vi.spyOn(api, 'ask').mockResolvedValue(answer)
    const { result, rerender } = renderHook(({ id }) => useAsk(id), {
      initialProps: { id: 'doc-1' },
    })
    await act(() => result.current.ask('What is the notice period?'))

    rerender({ id: 'doc-2' })
    expect(result.current.result).toBeNull()

    rerender({ id: 'doc-1' })
    expect(result.current.result).toEqual(answer)
  })

  it('never shows a late answer under a different document', async () => {
    const forDoc1 = deferred<QueryResult>()
    const forDoc2 = deferred<QueryResult>()
    vi.spyOn(api, 'ask').mockReturnValueOnce(forDoc1.promise).mockReturnValueOnce(forDoc2.promise)
    const { result, rerender } = renderHook(({ id }) => useAsk(id), {
      initialProps: { id: 'doc-1' },
    })

    let first!: Promise<void>
    act(() => {
      first = result.current.ask('question about doc 1')
    })
    rerender({ id: 'doc-2' })
    let second!: Promise<void>
    act(() => {
      second = result.current.ask('question about doc 2')
    })

    await act(async () => {
      forDoc1.resolve(answer) // doc 1's answer arrives while doc 2 is shown and still pending
      await first
    })
    expect(result.current.result).toBeNull()
    expect(result.current.loading).toBe(true)

    await act(async () => {
      forDoc2.resolve(notFound)
      await second
    })
    expect(result.current.result).toEqual(notFound)
    expect(result.current.loading).toBe(false)
  })
})

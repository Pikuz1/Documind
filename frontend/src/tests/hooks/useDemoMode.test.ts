import { renderHook, waitFor } from '@testing-library/react'
import { afterEach, describe, expect, it, vi } from 'vitest'
import { ApiError, api } from '../../services/api'
import { deferred } from '../fixtures'
import type { HealthInfo } from '../../types'
import { useDemoMode } from '../../hooks/useDemoMode'

afterEach(() => {
  vi.restoreAllMocks()
})

describe('useDemoMode', () => {
  it('is off until the server answers', () => {
    vi.spyOn(api, 'health').mockReturnValue(new Promise(() => {}))

    const { result } = renderHook(() => useDemoMode())

    expect(result.current).toBe(false)
  })

  it.each([true, false])('follows the server (demo: %s)', async (demo) => {
    vi.spyOn(api, 'health').mockResolvedValue({ status: 'ok', demo })

    const { result } = renderHook(() => useDemoMode())

    await waitFor(() => expect(api.health).toHaveBeenCalled())
    await waitFor(() => expect(result.current).toBe(demo))
  })

  it('stays off when the server is unreachable', async () => {
    const failed = Promise.reject(new ApiError(0, 'Could not reach the server'))
    vi.spyOn(api, 'health').mockReturnValue(failed)

    const { result } = renderHook(() => useDemoMode())
    await failed.catch(() => {})

    expect(result.current).toBe(false)
  })

  it('ignores an answer that arrives after unmount', async () => {
    const pending = deferred<HealthInfo>()
    vi.spyOn(api, 'health').mockReturnValue(pending.promise)
    const { result, unmount } = renderHook(() => useDemoMode())

    unmount()
    pending.resolve({ status: 'ok', demo: true })
    await pending.promise

    expect(result.current).toBe(false)
  })
})

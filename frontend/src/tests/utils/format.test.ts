import { describe, expect, it } from 'vitest'
import { formatLatency, formatUploadDate, pluralize } from '../../utils/format'

describe('formatUploadDate', () => {
  it('formats the SQLite UTC timestamp as a readable date', () => {
    expect(formatUploadDate('2026-10-02 09:00:00')).toBe('Oct 2, 2026')
  })

  it('treats the timestamp as UTC, so late-evening uploads keep their date', () => {
    expect(formatUploadDate('2026-10-02 23:59:59')).toBe('Oct 2, 2026')
  })
})

describe('formatLatency', () => {
  it.each([
    [35, '35 ms'],
    [999, '999 ms'],
    [1000, '1.0 s'],
    [2345, '2.3 s'],
  ])('formats %i ms as %s', (ms, text) => {
    expect(formatLatency(ms)).toBe(text)
  })
})

describe('pluralize', () => {
  it.each([
    [1, '1 page'],
    [6, '6 pages'],
    [0, '0 pages'],
  ])('formats %i', (count, text) => {
    expect(pluralize(count, 'page')).toBe(text)
  })
})

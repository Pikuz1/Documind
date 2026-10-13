const dateFormat = new Intl.DateTimeFormat('en', { dateStyle: 'medium', timeZone: 'UTC' })

/** SQLite stores `datetime('now')` as UTC "YYYY-MM-DD HH:MM:SS" without a zone marker. */
export function formatUploadDate(createdAt: string): string {
  return dateFormat.format(new Date(`${createdAt.replace(' ', 'T')}Z`))
}

export function formatLatency(ms: number): string {
  return ms < 1000 ? `${ms} ms` : `${(ms / 1000).toFixed(1)} s`
}

export function pluralize(count: number, word: string): string {
  return `${count} ${count === 1 ? word : `${word}s`}`
}

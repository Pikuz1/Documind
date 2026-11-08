import { useEffect, useState } from 'react'
import { api } from '../services/api'

/** True on the public demo, where the backend refuses uploads and deletes. */
export function useDemoMode(): boolean {
  const [demo, setDemo] = useState(false)

  useEffect(() => {
    let active = true // ignore the response if the component unmounted meanwhile
    api
      .health()
      .then((health) => active && setDemo(health.demo))
      .catch(() => {}) // stay in normal mode: the document list reports an unreachable server
    return () => {
      active = false
    }
  }, [])

  return demo
}

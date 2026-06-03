import { useEffect, useRef, useState } from 'react'
import { getJob } from '../lib/api'
import type { PipelineJob } from '../types'

const TERMINAL = new Set<string>(['completed', 'failed'])
const POLL_MS  = 8_000

export function useJobPoller(jobId: string | null) {
  const [job, setJob]     = useState<PipelineJob | null>(null)
  const [error, setError] = useState<string | null>(null)
  const timerRef          = useRef<ReturnType<typeof setTimeout> | null>(null)

  useEffect(() => {
    if (!jobId) return

    let cancelled = false

    async function poll() {
      try {
        const data = await getJob(jobId)
        if (!cancelled) {
          setJob(data)
          if (!TERMINAL.has(data.status)) {
            timerRef.current = setTimeout(poll, POLL_MS)
          }
        }
      } catch (err: unknown) {
        if (!cancelled) {
          const msg = (err as { response?: { data?: { detail?: string } }; message?: string })
          setError(msg?.response?.data?.detail ?? msg?.message ?? 'Polling failed')
        }
      }
    }

    poll()

    return () => {
      cancelled = true
      if (timerRef.current) clearTimeout(timerRef.current)
    }
  }, [jobId])

  return { job, error }
}

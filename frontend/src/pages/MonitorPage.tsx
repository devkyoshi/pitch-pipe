import { useEffect, useRef, useState } from 'react'
import { motion, AnimatePresence } from 'motion/react'
import { CircleNotch } from '@phosphor-icons/react'
import { useJobPoller } from '../hooks/useJobPoller'
import { PipelineStages } from '../components/PipelineStages'
import { ScriptViewer } from '../components/ScriptViewer'
import { VideoResult } from '../components/VideoResult'
import type { LeadPayload, JobStatus } from '../types'

const STATUS_MESSAGES: Record<JobStatus, string> = {
  queued:     'Waiting for a worker to pick up the job...',
  running:    'Gemini is writing the 4-scene video script...',
  stitching:  'All Veo3 clips rendered. FFmpeg is stitching now...',
  publishing: 'Publishing to your selected channels...',
  completed:  'Pipeline complete.',
  failed:     'The pipeline encountered an error.',
}

function Elapsed({ startTime }: { startTime: number }) {
  const [secs, setSecs] = useState(0)
  useEffect(() => {
    const t = setInterval(() => setSecs(Math.floor((Date.now() - startTime) / 1000)), 1000)
    return () => clearInterval(t)
  }, [startTime])
  const m = Math.floor(secs / 60)
  const s = secs % 60
  return <>{m}:{String(s).padStart(2, '0')}</>
}

interface MonitorPageProps {
  jobId:   string
  lead:    LeadPayload | null
  onReset: () => void
}

export function MonitorPage({ jobId, lead, onReset }: MonitorPageProps) {
  const { job, error } = useJobPoller(jobId)
  const startRef        = useRef(Date.now())
  const status          = (job?.status ?? 'queued') as JobStatus
  const isTerminal      = status === 'completed' || status === 'failed'

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.45, ease: [0.16, 1, 0.3, 1] }}
      style={{ width: '100%', maxWidth: 800, margin: '0 auto', display: 'flex', flexDirection: 'column', gap: '1.5rem', boxSizing: 'border-box' }}
    >
      {/* status card */}
      <div className="card" style={{ padding: '1.5rem' }}>
        {/* top row */}
        <div style={{
          display: 'flex', alignItems: 'flex-start',
          justifyContent: 'space-between', marginBottom: '1.5rem',
          flexWrap: 'wrap', gap: '0.75rem', minWidth: 0,
        }}>
          <div>
            {lead && (
              <div style={{ fontSize: '0.88rem', fontWeight: 700, marginBottom: '0.25rem' }}>
                {lead.name}
                <span style={{ fontWeight: 400, color: 'var(--color-muted)', marginLeft: '0.4rem' }}>
                  at {lead.company}
                </span>
              </div>
            )}
            <div style={{
              fontFamily: 'var(--font-mono)',
              fontSize: '0.68rem',
              color: 'var(--color-dim)',
              letterSpacing: '0.04em',
            }}>
              {jobId}
            </div>
          </div>

          <div style={{ display: 'flex', gap: '0.75rem', alignItems: 'center' }}>
            {!isTerminal && (
              <div style={{
                display: 'flex', alignItems: 'center', gap: '0.4rem',
                fontFamily: 'var(--font-mono)',
                fontSize: '0.72rem',
                color: 'var(--color-muted)',
              }}>
                <CircleNotch size={12} style={{ animation: 'spin-slow 1s linear infinite' }} />
                <Elapsed startTime={startRef.current} />
              </div>
            )}
            <button
              onClick={onReset}
              style={{
                padding: '0.35rem 0.75rem',
                borderRadius: 7,
                background: 'transparent',
                border: '1px solid rgba(240,234,216,0.1)',
                color: 'var(--color-muted)',
                fontSize: '0.75rem',
                cursor: 'pointer',
                fontFamily: 'inherit',
                transition: 'color 130ms ease, border-color 130ms ease',
              }}
              onMouseEnter={e => { e.currentTarget.style.color = 'var(--color-ink)'; e.currentTarget.style.borderColor = 'rgba(240,234,216,0.2)' }}
              onMouseLeave={e => { e.currentTarget.style.color = 'var(--color-muted)'; e.currentTarget.style.borderColor = 'rgba(240,234,216,0.1)' }}
            >
              New pipeline
            </button>
          </div>
        </div>

        <PipelineStages status={status} />

        {/* status message */}
        <AnimatePresence mode="wait">
          <motion.p
            key={status}
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            transition={{ duration: 0.2 }}
            style={{
              marginTop: '1rem',
              fontSize: '0.8rem',
              color: status === 'failed'
                ? 'var(--color-danger)'
                : status === 'completed'
                  ? 'var(--color-success)'
                  : 'var(--color-muted)',
            }}
          >
            {error ?? STATUS_MESSAGES[status]}
          </motion.p>
        </AnimatePresence>

        {job?.error_message && (
          <div style={{
            marginTop: '0.75rem',
            padding: '0.6rem 0.8rem',
            borderRadius: 7,
            background: 'rgba(184,74,56,0.06)',
            border: '1px solid rgba(184,74,56,0.18)',
            fontFamily: 'var(--font-mono)',
            fontSize: '0.72rem',
            color: 'var(--color-danger)',
          }}>
            {job.error_message}
          </div>
        )}
      </div>

      {/* script */}
      <AnimatePresence>
        {job?.script && (
          <div className="card" style={{ padding: '1.5rem' }}>
            <ScriptViewer script={job.script} />
          </div>
        )}
      </AnimatePresence>

      {/* video result */}
      <AnimatePresence>
        {(job?.clips || job?.final_video_url) && job && (
          <VideoResult job={job} />
        )}
      </AnimatePresence>

      {/* skeleton while loading */}
      {!job && !error && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '0.6rem' }}>
          {[160, 90, 50].map((h, i) => (
            <div key={i} className="shimmer-bg" style={{ height: h, borderRadius: 10, opacity: 0.5 - i * 0.12 }} />
          ))}
        </div>
      )}
    </motion.div>
  )
}

import { useEffect, useState } from 'react'
import { motion } from 'motion/react'
import { ArrowClockwise, ArrowSquareOut } from '@phosphor-icons/react'
import { listJobs } from '../lib/api'
import type { JobSummary, JobStatus } from '../types'

const STATUS_COLOR: Record<JobStatus, string> = {
  queued:     'var(--color-muted)',
  running:    'var(--color-accent)',
  stitching:  'var(--color-accent)',
  publishing: 'var(--color-accent)',
  completed:  'var(--color-success)',
  failed:     'var(--color-danger)',
}

function StatusBadge({ status }: { status: JobStatus }) {
  return (
    <span style={{
      display: 'inline-block',
      padding: '0.15rem 0.5rem',
      borderRadius: 5,
      fontSize: '0.68rem',
      fontFamily: 'var(--font-mono)',
      letterSpacing: '0.04em',
      color: STATUS_COLOR[status],
      border: `1px solid ${STATUS_COLOR[status]}33`,
      background: `${STATUS_COLOR[status]}0d`,
    }}>
      {status}
    </span>
  )
}

function formatDate(iso: string | null): string {
  if (!iso) return '—'
  const d = new Date(iso)
  return d.toLocaleString(undefined, { month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' })
}

interface PastJobsPageProps {
  onViewJob: (jobId: string) => void
}

export function PastJobsPage({ onViewJob }: PastJobsPageProps) {
  const [jobs, setJobs]       = useState<JobSummary[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError]     = useState<string | null>(null)

  async function load() {
    setLoading(true)
    setError(null)
    try {
      const data = await listJobs({ limit: 20 })
      setJobs(data)
    } catch {
      setError('Failed to load jobs.')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => { load() }, [])

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.35, ease: [0.16, 1, 0.3, 1] }}
      style={{ width: '100%', maxWidth: 800, margin: '0 auto', display: 'flex', flexDirection: 'column', gap: '1.25rem', boxSizing: 'border-box' }}
    >
      {/* header row */}
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
        <div>
          <div style={{ fontWeight: 600, fontSize: '1rem', letterSpacing: '-0.01em' }}>Past Jobs</div>
          <div style={{ fontSize: '0.75rem', color: 'var(--color-muted)', marginTop: '0.15rem' }}>
            Most recent 20 pipeline runs
          </div>
        </div>
        <button
          onClick={load}
          disabled={loading}
          style={{
            display: 'flex', alignItems: 'center', gap: '0.35rem',
            padding: '0.35rem 0.75rem',
            borderRadius: 7,
            background: 'transparent',
            border: '1px solid rgba(240,234,216,0.1)',
            color: 'var(--color-muted)',
            fontSize: '0.75rem',
            cursor: loading ? 'default' : 'pointer',
            fontFamily: 'inherit',
            transition: 'color 130ms ease, border-color 130ms ease',
          }}
          onMouseEnter={e => { if (!loading) { e.currentTarget.style.color = 'var(--color-ink)'; e.currentTarget.style.borderColor = 'rgba(240,234,216,0.2)' } }}
          onMouseLeave={e => { e.currentTarget.style.color = 'var(--color-muted)'; e.currentTarget.style.borderColor = 'rgba(240,234,216,0.1)' }}
        >
          <ArrowClockwise size={12} style={loading ? { animation: 'spin-slow 1s linear infinite' } : undefined} />
          Refresh
        </button>
      </div>

      {/* error */}
      {error && (
        <div style={{
          padding: '0.6rem 0.8rem', borderRadius: 7,
          background: 'rgba(184,74,56,0.06)', border: '1px solid rgba(184,74,56,0.18)',
          fontSize: '0.78rem', color: 'var(--color-danger)',
        }}>
          {error}
        </div>
      )}

      {/* empty */}
      {!loading && !error && jobs.length === 0 && (
        <div className="card" style={{ padding: '2.5rem', textAlign: 'center', color: 'var(--color-dim)', fontSize: '0.82rem' }}>
          No pipeline runs yet. Submit a lead to get started.
        </div>
      )}

      {/* skeleton */}
      {loading && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
          {[1, 2, 3].map(i => (
            <div key={i} className="shimmer-bg" style={{ height: 64, borderRadius: 10, opacity: 0.5 - i * 0.1 }} />
          ))}
        </div>
      )}

      {/* job rows */}
      {!loading && jobs.map((job, i) => (
        <motion.div
          key={job.job_id}
          className="card"
          initial={{ opacity: 0, y: 8 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.25, delay: i * 0.04, ease: [0.16, 1, 0.3, 1] }}
          style={{ padding: '0.9rem 1.1rem', display: 'flex', alignItems: 'center', gap: '1rem', minWidth: 0 }}
        >
          {/* status */}
          <div style={{ flexShrink: 0 }}>
            <StatusBadge status={job.status} />
          </div>

          {/* lead info */}
          <div style={{ flex: 1, minWidth: 0 }}>
            <div style={{ fontWeight: 600, fontSize: '0.85rem', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
              {job.lead_name}
              {job.lead_company && (
                <span style={{ fontWeight: 400, color: 'var(--color-muted)', marginLeft: '0.4rem' }}>
                  at {job.lead_company}
                </span>
              )}
            </div>
            <div style={{
              fontFamily: 'var(--font-mono)', fontSize: '0.63rem',
              color: 'var(--color-dim)', letterSpacing: '0.04em', marginTop: '0.15rem',
              overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap',
            }}>
              {job.job_id}
            </div>
          </div>

          {/* date */}
          <div style={{ flexShrink: 0, textAlign: 'right' }}>
            <div style={{ fontSize: '0.72rem', color: 'var(--color-muted)' }}>
              {formatDate(job.created_at)}
            </div>
            {job.completed_at && (
              <div style={{ fontSize: '0.65rem', color: 'var(--color-dim)', marginTop: '0.1rem' }}>
                done {formatDate(job.completed_at)}
              </div>
            )}
          </div>

          {/* view button */}
          <button
            onClick={() => onViewJob(job.job_id)}
            style={{
              flexShrink: 0,
              display: 'flex', alignItems: 'center', gap: '0.3rem',
              padding: '0.3rem 0.65rem',
              borderRadius: 6,
              background: 'transparent',
              border: '1px solid rgba(240,234,216,0.1)',
              color: 'var(--color-muted)',
              fontSize: '0.72rem',
              cursor: 'pointer',
              fontFamily: 'inherit',
              transition: 'color 130ms ease, border-color 130ms ease',
            }}
            onMouseEnter={e => { e.currentTarget.style.color = 'var(--color-ink)'; e.currentTarget.style.borderColor = 'rgba(240,234,216,0.22)' }}
            onMouseLeave={e => { e.currentTarget.style.color = 'var(--color-muted)'; e.currentTarget.style.borderColor = 'rgba(240,234,216,0.1)' }}
          >
            <ArrowSquareOut size={11} />
            View
          </button>
        </motion.div>
      ))}
    </motion.div>
  )
}

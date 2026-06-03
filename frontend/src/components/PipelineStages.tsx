import type { JobStatus } from '../types'

const STAGES: { key: JobStatus; label: string }[] = [
  { key: 'queued',     label: 'Queued' },
  { key: 'running',    label: 'Script' },
  { key: 'stitching',  label: 'Stitch' },
  { key: 'publishing', label: 'Publish' },
  { key: 'completed',  label: 'Done' },
]

const ORDER: JobStatus[] = ['queued', 'running', 'stitching', 'publishing', 'completed']

function stageIndex(status: JobStatus): number {
  if (status === 'failed') return -1
  return ORDER.indexOf(status)
}

export function PipelineStages({ status }: { status: JobStatus }) {
  const current = stageIndex(status)
  const failed  = status === 'failed'

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '0.35rem' }}>
      {/* track */}
      <div style={{ display: 'flex', gap: '3px', marginBottom: '0.5rem' }}>
        {STAGES.map((_, i) => {
          const done   = !failed && current > i
          const active = !failed && current === i
          return (
            <div
              key={i}
              style={{
                flex: 1,
                height: 3,
                borderRadius: 99,
                background: done
                  ? 'var(--color-accent)'
                  : active
                    ? 'var(--color-accent)'
                    : 'rgba(240,234,216,0.08)',
                opacity: done ? 1 : active ? 0.9 : 0.4,
                transition: 'background 400ms ease, opacity 400ms ease',
                ...(active && {
                  boxShadow: '0 0 8px rgba(200,127,26,0.5)',
                }),
              }}
            />
          )
        })}
      </div>

      {/* labels */}
      <div style={{ display: 'flex' }}>
        {STAGES.map((stage, i) => {
          const done   = !failed && current > i
          const active = !failed && current === i
          return (
            <div key={stage.key} style={{ flex: 1 }}>
              <span style={{
                fontSize: '0.68rem',
                fontFamily: 'var(--font-mono)',
                letterSpacing: '0.04em',
                color: active
                  ? 'var(--color-amber)'
                  : done
                    ? 'var(--color-muted)'
                    : 'var(--color-dim)',
                fontWeight: active ? 600 : 400,
                transition: 'color 300ms ease',
              }}>
                {failed && i === current ? 'Failed' : stage.label}
              </span>
            </div>
          )
        })}
      </div>
    </div>
  )
}

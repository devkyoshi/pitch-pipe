import { useState } from 'react'
import { motion } from 'motion/react'
import { LeadForm } from '../components/LeadForm'
import type { LeadPayload } from '../types'

interface PipelineConfig {
  useClaude:   boolean
  hasPublish:  boolean
}

function PipelineStepRow({
  num, name, detail, active, dimmed,
}: {
  num: string; name: string; detail: string; active: boolean; dimmed: boolean
}) {
  return (
    <div style={{
      display: 'grid',
      gridTemplateColumns: '2rem 1fr auto',
      gap: '0.75rem',
      padding: '0.6rem 0',
      borderBottom: '1px solid rgba(240,234,216,0.05)',
      alignItems: 'baseline',
      opacity: dimmed ? 0.3 : 1,
      transition: 'opacity 250ms ease',
    }}>
      <span style={{
        fontFamily: 'var(--font-mono)', fontSize: '0.62rem',
        color: active ? 'var(--color-accent)' : 'var(--color-dim)',
        letterSpacing: '0.04em', transition: 'color 250ms ease',
      }}>
        {num}
      </span>
      <div>
        <span style={{ fontSize: '0.85rem', fontWeight: 600, color: active ? 'var(--color-ink)' : 'var(--color-muted)' }}>
          {name}
        </span>
        {detail && (
          <span style={{
            marginLeft: '0.45rem', fontSize: '0.72rem',
            color: active ? 'var(--color-accent)' : 'var(--color-dim)',
            fontFamily: 'var(--font-mono)',
            transition: 'color 250ms ease',
          }}>
            {detail}
          </span>
        )}
      </div>
      <span style={{
        fontSize: '0.7rem', color: dimmed ? 'var(--color-dim)' : 'var(--color-muted)',
        fontStyle: dimmed ? 'italic' : 'normal', transition: 'all 250ms ease',
      }}>
        {dimmed ? 'skipped' : 'active'}
      </span>
    </div>
  )
}

interface SubmitPageProps {
  onJobCreated: (jobId: string, form: LeadPayload) => void
}

export function SubmitPage({ onJobCreated }: SubmitPageProps) {
  const [config, setConfig] = useState<PipelineConfig>({ useClaude: true, hasPublish: true })

  function handleJobCreated(jobId: string, form: LeadPayload) {
    onJobCreated(jobId, form)
  }

  const steps = [
    {
      num: '01', name: 'Script',
      detail: config.useClaude ? 'Gemini' : 'Manual',
      active: true, dimmed: false,
    },
    { num: '02', name: 'Clips',    detail: 'Veo 3',   active: true, dimmed: false },
    { num: '03', name: 'Stitch',   detail: 'FFmpeg',  active: true, dimmed: false },
    {
      num: '04', name: 'Publish',
      detail: config.hasPublish ? '3 channels' : '',
      active: config.hasPublish, dimmed: !config.hasPublish,
    },
  ]

  return (
    <div className="submit-grid">
      {/* ── Left ── */}
      <motion.div
        initial={{ opacity: 0, x: -20 }}
        animate={{ opacity: 1, x: 0 }}
        transition={{ duration: 0.55, ease: [0.16, 1, 0.3, 1] }}
        style={{ display: 'flex', flexDirection: 'column', gap: '2.5rem', paddingTop: '0.5rem' }}
      >
        <div>
          <h1 style={{
            fontSize: 'clamp(2.25rem, 4.5vw, 3.25rem)',
            fontWeight: 800, letterSpacing: '-0.045em', lineHeight: 1.05,
            marginBottom: '1rem', color: 'var(--color-ink)',
          }}>
            A new video<br />
            <span style={{ color: 'var(--color-accent)' }}>every lead.</span>
          </h1>
          <p style={{ fontSize: '0.9rem', color: 'var(--color-muted)', lineHeight: 1.7, maxWidth: '34ch' }}>
            Configure the pipeline on the right. Each step is optional — run only what you need.
          </p>
        </div>

        {/* dynamic pipeline steps */}
        <div>
          <div style={{
            fontSize: '0.62rem', fontFamily: 'var(--font-mono)',
            letterSpacing: '0.1em', color: 'var(--color-dim)',
            marginBottom: '0.5rem', textTransform: 'uppercase',
          }}>
            Pipeline
          </div>
          <div>
            {steps.map(s => (
              <PipelineStepRow key={s.num} {...s} />
            ))}
          </div>
        </div>
      </motion.div>

      {/* ── Right: form ── */}
      <motion.div
        initial={{ opacity: 0, x: 20 }}
        animate={{ opacity: 1, x: 0 }}
        transition={{ duration: 0.55, ease: [0.16, 1, 0.3, 1], delay: 0.08 }}
      >
        <LeadForm
          onJobCreated={handleJobCreated}
          onConfigChange={setConfig}
        />
      </motion.div>
    </div>
  )
}

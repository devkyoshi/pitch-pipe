import { motion } from 'motion/react'
import type { VideoScript } from '../types'

export function ScriptViewer({ script }: { script: VideoScript }) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 16 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.45, ease: [0.16, 1, 0.3, 1] }}
    >
      <div style={{
        display: 'flex', alignItems: 'baseline',
        justifyContent: 'space-between', flexWrap: 'wrap',
        gap: '0.5rem', marginBottom: '1.25rem',
      }}>
        <div>
          <div style={{ fontSize: '0.65rem', fontFamily: 'var(--font-mono)', letterSpacing: '0.08em', color: 'var(--color-muted)', marginBottom: '0.3rem', textTransform: 'uppercase' }}>
            Generated script
          </div>
          <h3 style={{ fontSize: '1rem', fontWeight: 700, letterSpacing: '-0.02em' }}>
            {script.video_title}
          </h3>
        </div>
        {script.cta && (
          <span style={{
            padding: '0.3rem 0.7rem',
            borderRadius: 5,
            background: 'rgba(200,127,26,0.1)',
            border: '1px solid rgba(200,127,26,0.25)',
            fontSize: '0.72rem',
            color: 'var(--color-accent)',
            fontFamily: 'var(--font-mono)',
            letterSpacing: '0.03em',
          }}>
            CTA: {script.cta}
          </span>
        )}
      </div>

      <div style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))',
        gap: '0.75rem',
      }}>
        {script.scenes?.map((scene, i) => (
          <motion.div
            key={scene.order}
            initial={{ opacity: 0, y: 12 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.35, delay: i * 0.07, ease: [0.16, 1, 0.3, 1] }}
            style={{
              background: 'var(--color-canvas)',
              border: '1px solid rgba(240,234,216,0.07)',
              borderRadius: 10,
              padding: '1rem',
              display: 'flex',
              flexDirection: 'column',
              gap: '0.7rem',
            }}
          >
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <span style={{
                fontFamily: 'var(--font-mono)',
                fontSize: '0.65rem',
                letterSpacing: '0.08em',
                color: 'var(--color-accent)',
              }}>
                SCENE {String(scene.order).padStart(2, '0')}
              </span>
              <span style={{ fontFamily: 'var(--font-mono)', fontSize: '0.62rem', color: 'var(--color-dim)' }}>
                {scene.duration_seconds}s
              </span>
            </div>

            <p style={{ fontSize: '0.83rem', lineHeight: 1.55, color: 'var(--color-ink)' }}>
              {scene.narration}
            </p>

            <div style={{
              padding: '0.55rem 0.7rem',
              background: 'rgba(240,234,216,0.03)',
              border: '1px solid rgba(240,234,216,0.06)',
              borderRadius: 6,
            }}>
              <div style={{ fontSize: '0.6rem', fontFamily: 'var(--font-mono)', letterSpacing: '0.08em', color: 'var(--color-dim)', marginBottom: '0.3rem', textTransform: 'uppercase' }}>
                Veo prompt
              </div>
              <p style={{ fontSize: '0.74rem', lineHeight: 1.5, color: 'var(--color-muted)' }}>
                {scene.veo_prompt}
              </p>
            </div>
          </motion.div>
        ))}
      </div>
    </motion.div>
  )
}

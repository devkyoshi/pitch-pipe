import { motion } from 'motion/react'
import { CheckCircle } from '@phosphor-icons/react'
import type { PipelineJob, Channel } from '../types'

const CHANNEL_LABEL: Record<Channel, string> = {
  linkedin:  'LinkedIn',
  instagram: 'Instagram',
  meta_ads:  'Meta Ads',
}

export function VideoResult({ job }: { job: PipelineJob }) {
  const { final_video_url: url, clips, target_channels: channels, status } = job

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5, ease: [0.16, 1, 0.3, 1] }}
      style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}
    >
      {/* video player */}
      {url && (
        <div style={{
          background: 'var(--color-surface)',
          border: '1px solid rgba(240,234,216,0.07)',
          borderRadius: 12,
          overflow: 'hidden',
        }}>
          <div style={{
            padding: '0.7rem 1rem',
            borderBottom: '1px solid rgba(240,234,216,0.06)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
          }}>
            <span style={{ fontSize: '0.78rem', fontWeight: 600 }}>Final video</span>
            <div style={{ display: 'flex', gap: '0.5rem' }}>
              <a
                href={url}
                target="_blank"
                rel="noopener noreferrer"
                style={{
                  padding: '0.3rem 0.7rem', borderRadius: 6,
                  background: 'rgba(200,127,26,0.1)',
                  border: '1px solid rgba(200,127,26,0.25)',
                  color: 'var(--color-accent)', fontSize: '0.72rem', fontWeight: 600,
                  textDecoration: 'none', transition: 'background 140ms ease',
                }}
                onMouseEnter={e => (e.currentTarget.style.background = 'rgba(200,127,26,0.18)')}
                onMouseLeave={e => (e.currentTarget.style.background = 'rgba(200,127,26,0.1)')}
              >
                Open
              </a>
              <a
                href={url}
                download
                style={{
                  padding: '0.3rem 0.7rem', borderRadius: 6,
                  background: 'transparent',
                  border: '1px solid rgba(240,234,216,0.1)',
                  color: 'var(--color-muted)', fontSize: '0.72rem', textDecoration: 'none',
                }}
              >
                Download
              </a>
            </div>
          </div>
          <div style={{ background: '#080706', aspectRatio: '16/9', maxHeight: 320 }}>
            <video src={url} controls style={{ width: '100%', height: '100%', objectFit: 'contain' }} />
          </div>
        </div>
      )}

      {/* clips */}
      {clips && clips.length > 0 && (
        <div className="card" style={{ padding: '1rem' }}>
          <div style={{ fontSize: '0.65rem', fontFamily: 'var(--font-mono)', letterSpacing: '0.08em', color: 'var(--color-muted)', marginBottom: '0.75rem', textTransform: 'uppercase' }}>
            Rendered clips
          </div>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.35rem' }}>
            {clips.map((uri, i) => (
              <div key={i} style={{
                display: 'flex', alignItems: 'center', gap: '0.6rem',
                padding: '0.45rem 0.7rem',
                background: 'var(--color-canvas)',
                borderRadius: 7,
                border: '1px solid rgba(240,234,216,0.05)',
              }}>
                <span style={{
                  fontFamily: 'var(--font-mono)', fontSize: '0.62rem',
                  color: 'var(--color-accent)', minWidth: '1.5rem',
                }}>
                  {String(i + 1).padStart(2, '0')}
                </span>
                <span style={{
                  fontFamily: 'var(--font-mono)', fontSize: '0.7rem',
                  color: 'var(--color-muted)',
                  overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap', flex: 1,
                }}>
                  {uri}
                </span>
                <CheckCircle size={13} color="var(--color-success)" weight="fill" />
              </div>
            ))}
          </div>
        </div>
      )}

      {/* channels */}
      {channels && channels.length > 0 && (
        <div className="card" style={{ padding: '1rem' }}>
          <div style={{ fontSize: '0.65rem', fontFamily: 'var(--font-mono)', letterSpacing: '0.08em', color: 'var(--color-muted)', marginBottom: '0.75rem', textTransform: 'uppercase' }}>
            Published to
          </div>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.35rem' }}>
            {(channels as Channel[]).map(ch => (
              <div key={ch} style={{
                display: 'flex', alignItems: 'center', justifyContent: 'space-between',
                padding: '0.55rem 0.7rem',
                background: 'var(--color-canvas)',
                borderRadius: 7,
                border: '1px solid rgba(240,234,216,0.05)',
              }}>
                <span style={{ fontSize: '0.83rem', fontWeight: 500 }}>
                  {CHANNEL_LABEL[ch] ?? ch}
                </span>
                {status === 'completed'
                  ? <CheckCircle size={14} color="var(--color-success)" weight="fill" />
                  : <div className="shimmer-bg" style={{ width: 50, height: 8, borderRadius: 99 }} />
                }
              </div>
            ))}
          </div>
        </div>
      )}
    </motion.div>
  )
}

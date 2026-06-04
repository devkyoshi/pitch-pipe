interface NavProps { onReset: () => void; onHistory: () => void }

export function Nav({ onReset, onHistory }: NavProps) {
  return (
    <header style={{
      position: 'fixed', top: 0, left: 0, right: 0, zIndex: 100,
      height: 56,
      background: 'var(--color-canvas)',
      borderBottom: '1px solid rgba(240,234,216,0.07)',
    }}>
      <div style={{
        maxWidth: 1200, margin: '0 auto', height: '100%',
        display: 'flex', alignItems: 'center', justifyContent: 'space-between',
        padding: '0 2rem',
      }}>
        <button
          onClick={onReset}
          style={{
            background: 'none', border: 'none', cursor: 'pointer',
            color: 'var(--color-ink)', padding: 0,
            display: 'flex', alignItems: 'center', gap: '0.6rem',
          }}
        >
          <svg width="18" height="18" viewBox="0 0 18 18" fill="none">
            <rect width="7" height="7" rx="1.5" fill="var(--color-accent)" />
            <rect x="9" width="7" height="7" rx="1.5" fill="rgba(200,127,26,0.45)" />
            <rect y="9" width="7" height="7" rx="1.5" fill="rgba(200,127,26,0.25)" />
            <rect x="9" y="9" width="7" height="7" rx="1.5" fill="rgba(200,127,26,0.12)" />
          </svg>
          <span style={{ fontWeight: 600, fontSize: '0.9rem', letterSpacing: '-0.01em' }}>
            Veo Pipeline
          </span>
        </button>

        <div style={{ display: 'flex', gap: '1.75rem', alignItems: 'center' }}>
          <button
            onClick={onHistory}
            style={{
              background: 'none', border: 'none', cursor: 'pointer', padding: 0,
              fontSize: '0.78rem', color: 'var(--color-muted)',
              fontFamily: 'inherit',
              transition: 'color 140ms ease',
            }}
            onMouseEnter={e => (e.currentTarget.style.color = 'var(--color-ink)')}
            onMouseLeave={e => (e.currentTarget.style.color = 'var(--color-muted)')}
          >
            History
          </button>
          <a
            href="http://localhost:8000/docs"
            target="_blank"
            rel="noopener noreferrer"
            style={{
              fontSize: '0.78rem', color: 'var(--color-muted)',
              textDecoration: 'none',
              transition: 'color 140ms ease',
            }}
            onMouseEnter={e => (e.currentTarget.style.color = 'var(--color-ink)')}
            onMouseLeave={e => (e.currentTarget.style.color = 'var(--color-muted)')}
          >
            API docs
          </a>
          <a
            href="http://localhost:8000/redoc"
            target="_blank"
            rel="noopener noreferrer"
            style={{
              fontSize: '0.78rem', color: 'var(--color-muted)',
              textDecoration: 'none',
              transition: 'color 140ms ease',
            }}
            onMouseEnter={e => (e.currentTarget.style.color = 'var(--color-ink)')}
            onMouseLeave={e => (e.currentTarget.style.color = 'var(--color-muted)')}
          >
            ReDoc
          </a>
        </div>
      </div>
    </header>
  )
}

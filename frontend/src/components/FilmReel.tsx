const SCENES = [
  { label: 'SCENE 01', gradient: 'linear-gradient(135deg, rgba(34,211,238,0.12) 0%, rgba(99,102,241,0.08) 100%)', delay: '0s' },
  { label: 'SCENE 02', gradient: 'linear-gradient(135deg, rgba(99,102,241,0.12) 0%, rgba(34,211,238,0.06) 100%)', delay: '1.2s' },
  { label: 'SCENE 03', gradient: 'linear-gradient(135deg, rgba(34,211,238,0.08) 0%, rgba(52,211,153,0.08) 100%)', delay: '2.5s' },
  { label: 'SCENE 04', gradient: 'linear-gradient(135deg, rgba(52,211,153,0.1) 0%, rgba(34,211,238,0.06) 100%)', delay: '3.8s' },
] as const

export function FilmReel() {
  return (
    <div style={{ position: 'relative', width: '100%', maxWidth: 380 }}>
      {SCENES.map((scene, i) => (
        <div
          key={i}
          style={{
            position: 'relative',
            marginBottom: i < 3 ? '-2.5rem' : 0,
            marginLeft: `${i * 1.2}rem`,
            zIndex: SCENES.length - i,
            animationName: 'drift',
            animationDuration: `${7 + i}s`,
            animationTimingFunction: 'ease-in-out',
            animationIterationCount: 'infinite',
            animationDelay: scene.delay,
          }}
        >
          <div
            style={{
              height: 90,
              background: scene.gradient,
              border: '1px solid rgba(255,255,255,0.08)',
              borderRadius: 12,
              display: 'flex',
              alignItems: 'flex-end',
              padding: '0.75rem 1rem',
              backdropFilter: 'blur(8px)',
              boxShadow: '0 8px 32px rgba(0,0,0,0.4)',
              position: 'relative',
              overflow: 'hidden',
            }}
          >
            <div style={{
              position: 'absolute', top: 0, left: 0, right: 0,
              height: '30%',
              background: 'linear-gradient(180deg, rgba(255,255,255,0.04) 0%, transparent 100%)',
              pointerEvents: 'none',
            }} />
            {/* film perforations */}
            {(['left', 'right'] as const).map(side => (
              <div
                key={side}
                style={{
                  position: 'absolute', top: 0, bottom: 0,
                  [side]: 0, width: 16,
                  display: 'flex', flexDirection: 'column',
                  justifyContent: 'space-around', padding: '6px 0',
                }}
              >
                {[0, 1, 2, 3].map(p => (
                  <div
                    key={p}
                    style={{
                      width: 8, height: 8, borderRadius: 2,
                      background: 'rgba(255,255,255,0.08)',
                      [side === 'left' ? 'marginLeft' : 'marginRight']: 4,
                    }}
                  />
                ))}
              </div>
            ))}
            <span style={{
              fontFamily: 'var(--font-mono)',
              fontSize: '0.65rem',
              letterSpacing: '0.12em',
              color: 'rgba(255,255,255,0.35)',
              marginLeft: 16,
            }}>
              {scene.label}
            </span>
          </div>
        </div>
      ))}
    </div>
  )
}

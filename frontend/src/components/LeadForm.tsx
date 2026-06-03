import { useState } from 'react'
import { motion, AnimatePresence } from 'motion/react'
import { ArrowRight, ArrowLeft, CircleNotch, Check, User, Buildings, Brain, PencilSimple, LinkedinLogo, InstagramLogo, MetaLogo } from '@phosphor-icons/react'
import { submitLead } from '../lib/api'
import type { FunnelStage, Channel, LeadPayload, ManualScene } from '../types'

// ─── Constants ────────────────────────────────────────────────────────────────

const FUNNEL_STAGES: { id: FunnelStage; label: string; hint: string }[] = [
  { id: 'awareness',     label: 'Awareness',     hint: 'Just discovered the problem' },
  { id: 'consideration', label: 'Consideration', hint: 'Evaluating solutions' },
  { id: 'decision',      label: 'Decision',      hint: 'Ready to buy' },
]

const CHANNELS: { id: Channel; label: string; hint: string; Icon: typeof LinkedinLogo }[] = [
  { id: 'linkedin',  label: 'LinkedIn',  hint: 'Posted as a ugcPost video',   Icon: LinkedinLogo },
  { id: 'instagram', label: 'Instagram', hint: 'Published as an Instagram Reel', Icon: InstagramLogo },
  { id: 'meta_ads',  label: 'Meta Ads',  hint: 'Uploaded to your ad account', Icon: MetaLogo },
]

const EMPTY_SCENES: ManualScene[] = [1, 2, 3, 4].map(order => ({
  order, narration: '', veo_prompt: '', duration_seconds: 8,
}))

// ─── Sub-components ───────────────────────────────────────────────────────────

function StepDots({ current }: { current: number }) {
  const steps = [
    { n: 1, label: 'Lead' },
    { n: 2, label: 'Script' },
    { n: 3, label: 'Publish' },
  ]
  return (
    <div style={{ display: 'flex', alignItems: 'center', gap: 0, marginBottom: '1.75rem' }}>
      {steps.map((s, i) => {
        const done   = current > s.n
        const active = current === s.n
        return (
          <div key={s.n} style={{ display: 'flex', alignItems: 'center', flex: i < steps.length - 1 ? 1 : 'none' }}>
            <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '0.3rem' }}>
              <div style={{
                width: 28, height: 28, borderRadius: '50%',
                background: done ? 'var(--color-accent)' : active ? 'rgba(200,127,26,0.15)' : 'transparent',
                border: `1.5px solid ${done || active ? 'var(--color-accent)' : 'rgba(240,234,216,0.12)'}`,
                display: 'flex', alignItems: 'center', justifyContent: 'center',
                transition: 'all 250ms ease',
                flexShrink: 0,
              }}>
                {done
                  ? <Check size={12} weight="bold" color="#0d0c09" />
                  : <span style={{ fontSize: '0.68rem', fontWeight: 600, color: active ? 'var(--color-amber)' : 'var(--color-dim)', fontFamily: 'var(--font-mono)' }}>{s.n}</span>
                }
              </div>
              <span style={{
                fontSize: '0.62rem', fontFamily: 'var(--font-mono)', letterSpacing: '0.06em',
                color: active ? 'var(--color-amber)' : done ? 'var(--color-muted)' : 'var(--color-dim)',
                textTransform: 'uppercase', transition: 'color 250ms ease',
              }}>
                {s.label}
              </span>
            </div>
            {i < steps.length - 1 && (
              <div style={{
                flex: 1, height: 1, marginBottom: '1.2rem',
                background: done ? 'var(--color-accent)' : 'rgba(240,234,216,0.08)',
                transition: 'background 400ms ease',
              }} />
            )}
          </div>
        )
      })}
    </div>
  )
}

function StepHeader({ title, subtitle }: { title: string; subtitle: string }) {
  return (
    <div style={{ marginBottom: '1.25rem' }}>
      <h2 style={{ fontSize: '1rem', fontWeight: 700, letterSpacing: '-0.02em', marginBottom: '0.2rem' }}>
        {title}
      </h2>
      <p style={{ fontSize: '0.78rem', color: 'var(--color-muted)', lineHeight: 1.55 }}>
        {subtitle}
      </p>
    </div>
  )
}

function InfoBox({ text }: { text: string }) {
  return (
    <div style={{
      padding: '0.6rem 0.75rem', borderRadius: 7,
      background: 'rgba(200,127,26,0.06)',
      border: '1px solid rgba(200,127,26,0.15)',
      fontSize: '0.75rem', color: 'var(--color-muted)', lineHeight: 1.55,
      marginBottom: '0.85rem',
    }}>
      {text}
    </div>
  )
}

function NavRow({
  onBack, onNext, nextLabel = 'Continue', loading = false, isFirst = false,
}: {
  onBack?: () => void
  onNext?: () => void
  nextLabel?: string
  loading?: boolean
  isFirst?: boolean
}) {
  return (
    <div style={{ display: 'flex', gap: '0.5rem', marginTop: '1.25rem' }}>
      {!isFirst && (
        <button
          type="button"
          onClick={onBack}
          style={{
            display: 'flex', alignItems: 'center', gap: '0.35rem',
            padding: '0.65rem 1rem', borderRadius: 8,
            background: 'transparent', border: '1px solid rgba(240,234,216,0.1)',
            color: 'var(--color-muted)', fontSize: '0.82rem', cursor: 'pointer', fontFamily: 'inherit',
            transition: 'color 130ms ease, border-color 130ms ease',
          }}
          onMouseEnter={e => { e.currentTarget.style.color = 'var(--color-ink)'; e.currentTarget.style.borderColor = 'rgba(240,234,216,0.2)' }}
          onMouseLeave={e => { e.currentTarget.style.color = 'var(--color-muted)'; e.currentTarget.style.borderColor = 'rgba(240,234,216,0.1)' }}
        >
          <ArrowLeft size={13} /> Back
        </button>
      )}
      <button
        type={onNext ? 'button' : 'submit'}
        onClick={onNext}
        disabled={loading}
        style={{
          flex: 1, display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '0.4rem',
          padding: '0.65rem 1rem', borderRadius: 8, border: 'none',
          background: loading ? 'rgba(200,127,26,0.4)' : 'var(--color-accent)',
          color: '#0d0c09', fontSize: '0.85rem', fontWeight: 700,
          cursor: loading ? 'not-allowed' : 'pointer', fontFamily: 'inherit',
          transition: 'transform 100ms ease-out, background 150ms ease-out',
        }}
        onMouseEnter={e => { if (!loading) e.currentTarget.style.background = 'var(--color-amber)' }}
        onMouseLeave={e => { e.currentTarget.style.background = loading ? 'rgba(200,127,26,0.4)' : 'var(--color-accent)' }}
        onMouseDown={e => { if (!loading) e.currentTarget.style.transform = 'scale(0.97)' }}
        onMouseUp={e => { e.currentTarget.style.transform = 'scale(1)' }}
      >
        {loading
          ? <><CircleNotch size={14} style={{ animation: 'spin-slow 0.75s linear infinite' }} /> Launching...</>
          : <>{nextLabel} <ArrowRight size={13} weight="bold" /></>
        }
      </button>
    </div>
  )
}

// ─── Main form ────────────────────────────────────────────────────────────────

interface PipelineConfig { useClaude: boolean; hasPublish: boolean }

interface LeadFormProps {
  onJobCreated:    (jobId: string, form: LeadPayload) => void
  onConfigChange?: (config: PipelineConfig) => void
}

export function LeadForm({ onJobCreated, onConfigChange }: LeadFormProps) {
  // Navigation
  const [step, setStep]           = useState(1)
  const [direction, setDirection] = useState(1)

  // Step 1 — Lead
  const [name, setName]       = useState('')
  const [company, setCompany] = useState('')

  // Step 2 — Script
  const [useClaude, setUseClaude]     = useState(true)
  const [industry, setIndustry]       = useState('')
  const [painPoint, setPainPoint]     = useState('')
  const [funnelStage, setFunnelStage] = useState<FunnelStage>('awareness')
  const [scenes, setScenes]           = useState<ManualScene[]>(EMPTY_SCENES)
  const [videoTitle, setVideoTitle]   = useState('')
  const [cta, setCta]                 = useState('')

  // Step 3 — Publish
  const [channels, setChannels] = useState<Channel[]>(['linkedin'])

  // UI
  const [stepError, setStepError] = useState<string | null>(null)
  const [loading, setLoading]     = useState(false)

  function go(next: number) {
    setDirection(next > step ? 1 : -1)
    setStepError(null)
    setStep(next)
  }

  function setScriptMode(claude: boolean) {
    setUseClaude(claude)
    onConfigChange?.({ useClaude: claude, hasPublish: channels.length > 0 })
  }

  function toggleChannel(ch: Channel) {
    setChannels(prev => {
      const next = prev.includes(ch) ? prev.filter(c => c !== ch) : [...prev, ch]
      onConfigChange?.({ useClaude, hasPublish: next.length > 0 })
      return next
    })
  }

  function updateScene(i: number, field: keyof ManualScene, val: string | number) {
    setScenes(prev => prev.map((s, idx) => idx === i ? { ...s, [field]: val } : s))
  }

  function validateStep1() {
    if (!name.trim())    { setStepError('Name is required.'); return false }
    if (!company.trim()) { setStepError('Company is required.'); return false }
    return true
  }

  function validateStep2() {
    if (useClaude) {
      if (!industry.trim())  { setStepError('Industry is required for Gemini auto-generation.'); return false }
      if (!painPoint.trim()) { setStepError('Pain point is required for Gemini auto-generation.'); return false }
    } else {
      const empty = scenes.find(s => !s.veo_prompt.trim())
      if (empty) { setStepError(`Scene ${empty.order}: Veo prompt is required.`); return false }
    }
    return true
  }

  async function handleLaunch() {
    setStepError(null)
    setLoading(true)

    const payload: LeadPayload = {
      name, company, funnel_stage: funnelStage,
      use_claude: useClaude,
      target_channel: channels,
      ...(useClaude
        ? { industry, pain_point: painPoint }
        : { manual_script: { video_title: videoTitle || 'Custom Video', scenes, cta } }
      ),
    }

    try {
      const data = await submitLead(payload)
      onJobCreated(data.job_id, payload)
    } catch (err: unknown) {
      const e = err as { response?: { data?: { detail?: Array<{ msg: string }> | string } }; message?: string }
      const detail = e?.response?.data?.detail
      const msg = Array.isArray(detail) ? detail[0]?.msg : (detail ?? e?.message ?? 'Something went wrong.')
      setStepError(msg ?? 'Unknown error')
      setLoading(false)
    }
  }

  // ── Shared styles ──────────────────────────────────────────────────────────

  const segBtn = (active: boolean): React.CSSProperties => ({
    flex: 1, padding: '0.5rem 0', borderRadius: 7,
    border: `1px solid ${active ? 'rgba(200,127,26,0.5)' : 'rgba(240,234,216,0.08)'}`,
    background: active ? 'rgba(200,127,26,0.12)' : 'transparent',
    color: active ? 'var(--color-amber)' : 'var(--color-muted)',
    fontSize: '0.78rem', fontWeight: active ? 600 : 400,
    cursor: 'pointer', fontFamily: 'inherit',
    transition: 'all 130ms ease-out',
  })

  const slideVariants = {
    enter:  (d: number) => ({ x: d * 32, opacity: 0 }),
    center: { x: 0, opacity: 1 },
    exit:   (d: number) => ({ x: d * -32, opacity: 0 }),
  }

  // ── Review summary (used in step 3) ───────────────────────────────────────

  function ReviewRow({ label, value }: { label: string; value: string }) {
    return (
      <div style={{
        display: 'flex', justifyContent: 'space-between', alignItems: 'baseline',
        padding: '0.5rem 0',
        borderBottom: '1px solid rgba(240,234,216,0.05)',
      }}>
        <span style={{ fontSize: '0.72rem', color: 'var(--color-muted)', minWidth: 80 }}>{label}</span>
        <span style={{ fontSize: '0.78rem', fontWeight: 500, color: 'var(--color-ink)', textAlign: 'right' }}>{value}</span>
      </div>
    )
  }

  return (
    <motion.form
      onSubmit={e => { e.preventDefault(); if (step === 3) handleLaunch() }}
      className="card"
      style={{ padding: '1.75rem', overflow: 'hidden' }}
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5, ease: [0.16, 1, 0.3, 1] }}
    >
      <StepDots current={step} />

      <AnimatePresence mode="wait" custom={direction}>
        {/* ── Step 1: Lead ── */}
        {step === 1 && (
          <motion.div
            key="step1"
            custom={direction}
            variants={slideVariants}
            initial="enter"
            animate="center"
            exit="exit"
            transition={{ duration: 0.22, ease: [0.16, 1, 0.3, 1] }}
          >
            <StepHeader
              title="Who is this lead?"
              subtitle="Basic info about the person this video is being generated for."
            />

            <div className="form-2col">
              <div>
                <label className="input-label">
                  <User size={10} style={{ marginRight: '0.3rem', verticalAlign: 'middle' }} />
                  Full name
                </label>
                <input
                  className="input-field"
                  placeholder="Jane Smith"
                  value={name}
                  onChange={e => setName(e.target.value)}
                  autoFocus
                />
              </div>
              <div>
                <label className="input-label">
                  <Buildings size={10} style={{ marginRight: '0.3rem', verticalAlign: 'middle' }} />
                  Company
                </label>
                <input
                  className="input-field"
                  placeholder="Acme Corp"
                  value={company}
                  onChange={e => setCompany(e.target.value)}
                />
              </div>
            </div>

            {stepError && <ErrorBanner msg={stepError} />}

            <NavRow
              isFirst
              nextLabel="Continue"
              onNext={() => { if (validateStep1()) go(2) }}
            />
          </motion.div>
        )}

        {/* ── Step 2: Script ── */}
        {step === 2 && (
          <motion.div
            key="step2"
            custom={direction}
            variants={slideVariants}
            initial="enter"
            animate="center"
            exit="exit"
            transition={{ duration: 0.22, ease: [0.16, 1, 0.3, 1] }}
          >
            <StepHeader
              title="How should the script be created?"
              subtitle="Gemini can write a tailored 4-scene script, or you can provide your own Veo prompts."
            />

            {/* Mode toggle */}
            <div style={{ display: 'flex', gap: '0.4rem', marginBottom: '1rem' }}>
              <button type="button" onClick={() => setScriptMode(true)} style={{
                ...segBtn(useClaude),
                display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '0.35rem',
              }}>
                <Brain size={13} /> Gemini auto-gen
              </button>
              <button type="button" onClick={() => setScriptMode(false)} style={{
                ...segBtn(!useClaude),
                display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '0.35rem',
              }}>
                <PencilSimple size={13} /> Manual prompts
              </button>
            </div>

            <AnimatePresence mode="wait">
              {useClaude ? (
                <motion.div key="gemini"
                  initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, y: -8 }}
                  transition={{ duration: 0.18 }}
                >
                  <InfoBox text="Gemini will write a 4-scene, 30-second script personalised to this lead's industry and pain point. Each scene includes a Veo 3 visual prompt." />
                  <div style={{ display: 'flex', flexDirection: 'column', gap: '0.7rem' }}>
                    <div>
                      <label className="input-label">Industry</label>
                      <input className="input-field" placeholder="SaaS, E-commerce, FinTech..." value={industry} onChange={e => setIndustry(e.target.value)} />
                    </div>
                    <div>
                      <label className="input-label">Pain point</label>
                      <textarea className="input-field" rows={2} placeholder="What problem are they trying to solve?" value={painPoint} onChange={e => setPainPoint(e.target.value)} style={{ resize: 'none', lineHeight: 1.5 }} />
                    </div>
                    <div>
                      <label className="input-label">Funnel stage</label>
                      <div style={{ display: 'flex', flexDirection: 'column', gap: '0.35rem' }}>
                        {FUNNEL_STAGES.map(s => (
                          <button key={s.id} type="button" onClick={() => setFunnelStage(s.id)}
                            style={{
                              display: 'flex', justifyContent: 'space-between', alignItems: 'center',
                              padding: '0.55rem 0.75rem', borderRadius: 8, cursor: 'pointer',
                              fontFamily: 'inherit', textAlign: 'left',
                              border: `1px solid ${funnelStage === s.id ? 'rgba(200,127,26,0.5)' : 'rgba(240,234,216,0.08)'}`,
                              background: funnelStage === s.id ? 'rgba(200,127,26,0.1)' : 'transparent',
                              transition: 'all 130ms ease',
                            }}
                          >
                            <span style={{ fontSize: '0.82rem', fontWeight: funnelStage === s.id ? 600 : 400, color: funnelStage === s.id ? 'var(--color-amber)' : 'var(--color-ink)' }}>
                              {s.label}
                            </span>
                            <span style={{ fontSize: '0.72rem', color: 'var(--color-muted)' }}>
                              {s.hint}
                            </span>
                          </button>
                        ))}
                      </div>
                    </div>
                  </div>
                </motion.div>
              ) : (
                <motion.div key="manual"
                  initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, y: -8 }}
                  transition={{ duration: 0.18 }}
                >
                  <InfoBox text="Write your own Veo 3 prompts for each scene. Include lighting, mood, and camera angle for best results. Narration is optional." />
                  <div className="scene-2col">
                    <div>
                      <label className="input-label">Video title</label>
                      <input className="input-field" placeholder="My Campaign" value={videoTitle} onChange={e => setVideoTitle(e.target.value)} />
                    </div>
                    <div>
                      <label className="input-label">CTA text</label>
                      <input className="input-field" placeholder="Get started free" value={cta} onChange={e => setCta(e.target.value)} />
                    </div>
                  </div>
                  <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
                    {scenes.map((scene, i) => (
                      <div key={scene.order} style={{
                        background: 'var(--color-canvas)', borderRadius: 9,
                        border: '1px solid rgba(240,234,216,0.07)', padding: '0.75rem',
                      }}>
                        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.5rem' }}>
                          <span style={{ fontFamily: 'var(--font-mono)', fontSize: '0.6rem', color: 'var(--color-accent)', letterSpacing: '0.1em' }}>
                            SCENE {String(scene.order).padStart(2, '0')}
                          </span>
                          <div style={{ display: 'flex', alignItems: 'center', gap: '0.35rem' }}>
                            <span style={{ fontSize: '0.6rem', color: 'var(--color-dim)', fontFamily: 'var(--font-mono)' }}>duration</span>
                            <input type="number" min={1} max={30} value={scene.duration_seconds}
                              onChange={e => updateScene(i, 'duration_seconds', Number(e.target.value))}
                              style={{
                                width: 38, padding: '0.15rem 0.35rem', borderRadius: 5,
                                background: 'var(--color-raised)', border: '1px solid rgba(240,234,216,0.08)',
                                color: 'var(--color-muted)', fontSize: '0.7rem', fontFamily: 'var(--font-mono)',
                                textAlign: 'center', outline: 'none',
                              }}
                            />
                            <span style={{ fontSize: '0.6rem', color: 'var(--color-dim)', fontFamily: 'var(--font-mono)' }}>s</span>
                          </div>
                        </div>
                        <textarea className="input-field" rows={2} placeholder="Describe the visual — lighting, mood, camera angle, subject..." value={scene.veo_prompt} onChange={e => updateScene(i, 'veo_prompt', e.target.value)} style={{ resize: 'none', lineHeight: 1.5, marginBottom: '0.4rem', fontSize: '0.8rem' }} />
                        <input className="input-field" placeholder="Narration / voiceover (optional)" value={scene.narration ?? ''} onChange={e => updateScene(i, 'narration', e.target.value)} style={{ fontSize: '0.76rem' }} />
                      </div>
                    ))}
                  </div>
                </motion.div>
              )}
            </AnimatePresence>

            {stepError && <ErrorBanner msg={stepError} />}

            <NavRow
              onBack={() => go(1)}
              nextLabel="Continue"
              onNext={() => { if (validateStep2()) go(3) }}
            />
          </motion.div>
        )}

        {/* ── Step 3: Publish + launch ── */}
        {step === 3 && (
          <motion.div
            key="step3"
            custom={direction}
            variants={slideVariants}
            initial="enter"
            animate="center"
            exit="exit"
            transition={{ duration: 0.22, ease: [0.16, 1, 0.3, 1] }}
          >
            <StepHeader
              title="Where should it be published?"
              subtitle="Select one or more channels. Leave all unchecked to generate the video without publishing."
            />

            <div style={{ display: 'flex', flexDirection: 'column', gap: '0.4rem', marginBottom: '1.1rem' }}>
              {CHANNELS.map(ch => {
                const active = channels.includes(ch.id)
                return (
                  <button key={ch.id} type="button" onClick={() => toggleChannel(ch.id)} style={{
                    display: 'flex', alignItems: 'center', gap: '0.75rem',
                    padding: '0.65rem 0.85rem', borderRadius: 9, cursor: 'pointer',
                    fontFamily: 'inherit', textAlign: 'left',
                    border: `1px solid ${active ? 'rgba(200,127,26,0.45)' : 'rgba(240,234,216,0.08)'}`,
                    background: active ? 'rgba(200,127,26,0.08)' : 'transparent',
                    transition: 'all 140ms ease',
                  }}>
                    <ch.Icon size={16} color={active ? 'var(--color-accent)' : 'var(--color-dim)'} style={{ flexShrink: 0 }} />
                    <div style={{ flex: 1 }}>
                      <div style={{ fontSize: '0.82rem', fontWeight: active ? 600 : 400, color: active ? 'var(--color-ink)' : 'var(--color-muted)' }}>
                        {ch.label}
                      </div>
                      <div style={{ fontSize: '0.7rem', color: 'var(--color-dim)' }}>{ch.hint}</div>
                    </div>
                    <div style={{
                      width: 18, height: 18, borderRadius: '50%', flexShrink: 0,
                      border: `1.5px solid ${active ? 'var(--color-accent)' : 'rgba(240,234,216,0.15)'}`,
                      background: active ? 'var(--color-accent)' : 'transparent',
                      display: 'flex', alignItems: 'center', justifyContent: 'center',
                      transition: 'all 140ms ease',
                    }}>
                      {active && <Check size={10} weight="bold" color="#0d0c09" />}
                    </div>
                  </button>
                )
              })}
            </div>

            {channels.length === 0 && (
              <div style={{
                padding: '0.5rem 0.75rem', borderRadius: 7, marginBottom: '1rem',
                background: 'rgba(240,234,216,0.04)', border: '1px solid rgba(240,234,216,0.07)',
                fontSize: '0.73rem', color: 'var(--color-muted)',
              }}>
                No channels selected — the video will be generated and stitched but not published.
              </div>
            )}

            {/* Review summary */}
            <div style={{
              background: 'var(--color-canvas)', borderRadius: 9,
              border: '1px solid rgba(240,234,216,0.07)',
              padding: '0.9rem 1rem', marginBottom: '0.25rem',
            }}>
              <div style={{ fontSize: '0.6rem', fontFamily: 'var(--font-mono)', letterSpacing: '0.1em', color: 'var(--color-dim)', textTransform: 'uppercase', marginBottom: '0.4rem' }}>
                Pipeline summary
              </div>
              <ReviewRow label="Lead" value={`${name} @ ${company}`} />
              <ReviewRow
                label="Script"
                value={useClaude
                  ? `Gemini auto-gen (${funnelStage})`
                  : `Manual — ${scenes.filter(s => s.veo_prompt).length} scenes`
                }
              />
              {useClaude && industry && <ReviewRow label="Industry" value={industry} />}
              <ReviewRow
                label="Publish"
                value={channels.length ? channels.map(c => CHANNELS.find(ch => ch.id === c)?.label).join(', ') : 'Skipped'}
              />
              <div style={{ display: 'flex', justifyContent: 'space-between', paddingTop: '0.5rem' }}>
                <span style={{ fontSize: '0.72rem', color: 'var(--color-dim)' }}>Estimated time</span>
                <span style={{ fontSize: '0.72rem', color: 'var(--color-muted)' }}>8-15 minutes</span>
              </div>
            </div>

            {stepError && <ErrorBanner msg={stepError} />}

            <NavRow
              onBack={() => go(2)}
              nextLabel="Launch pipeline"
              loading={loading}
            />
          </motion.div>
        )}
      </AnimatePresence>
    </motion.form>
  )
}

function ReviewRow({ label, value }: { label: string; value: string }) {
  return (
    <div style={{
      display: 'flex', justifyContent: 'space-between', alignItems: 'baseline',
      padding: '0.4rem 0', borderBottom: '1px solid rgba(240,234,216,0.05)',
    }}>
      <span style={{ fontSize: '0.72rem', color: 'var(--color-muted)', minWidth: 72 }}>{label}</span>
      <span style={{ fontSize: '0.78rem', fontWeight: 500, color: 'var(--color-ink)', textAlign: 'right' }}>{value}</span>
    </div>
  )
}

function ErrorBanner({ msg }: { msg: string }) {
  return (
    <div style={{
      marginTop: '0.85rem', padding: '0.6rem 0.8rem', borderRadius: 7,
      background: 'rgba(184,74,56,0.08)', border: '1px solid rgba(184,74,56,0.22)',
      color: 'var(--color-danger)', fontSize: '0.78rem',
    }}>
      {msg}
    </div>
  )
}

import { useState } from 'react'
import { AnimatePresence, motion } from 'motion/react'
import { Noise }       from './components/Noise'
import { Nav }         from './components/Nav'
import { SubmitPage }  from './pages/SubmitPage'
import { MonitorPage } from './pages/MonitorPage'
import type { LeadPayload } from './types'

type View = 'submit' | 'monitor'

export default function App() {
  const [view, setView]   = useState<View>('submit')
  const [jobId, setJobId] = useState<string | null>(null)
  const [lead, setLead]   = useState<LeadPayload | null>(null)

  function handleJobCreated(id: string, form: LeadPayload) {
    setJobId(id)
    setLead(form)
    setView('monitor')
  }

  function handleReset() {
    setJobId(null)
    setLead(null)
    setView('submit')
  }

  return (
    <>
      <Noise />
      <Nav onReset={handleReset} />

      <AnimatePresence mode="wait">
        {view === 'submit' ? (
          <motion.div
            key="submit"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0, y: -12 }}
            transition={{ duration: 0.3, ease: [0.16, 1, 0.3, 1] }}
          >
            <SubmitPage onJobCreated={handleJobCreated} />
          </motion.div>
        ) : (
          <motion.main
            key="monitor"
            className="monitor-wrap"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -12 }}
            transition={{ duration: 0.35, ease: [0.16, 1, 0.3, 1] }}
          >
            <MonitorPage jobId={jobId!} lead={lead} onReset={handleReset} />
          </motion.main>
        )}
      </AnimatePresence>
    </>
  )
}

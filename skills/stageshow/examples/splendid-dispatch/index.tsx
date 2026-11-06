import { Avatar, Badge, Stage, Text, Window, type Act } from '../../kit'
import './dispatch.css'

// Splendid Moving — Ops Agent Dispatch Showcase
// Demonstrates the automated booking workflow from an incoming customer enquiry
// to instant multi-system dispatch across GoHighLevel, Google Calendar, AppSheet,
// SMS deposit links, and customer confirmation.

type S = {
  status: 'idle' | 'hovering' | 'dispatching' | 'booked'
  stepsCompleted: number
  confirmed: boolean
}

const initial: S = {
  status: 'idle',
  stepsCompleted: 0,
  confirmed: false,
}

const POSTER: S = {
  status: 'booked',
  stepsCompleted: 5,
  confirmed: true,
}

const STEPS = [
  { label: 'GoHighLevel', detail: 'Contact created' },
  { label: 'Google Calendar', detail: 'Truck #2 reserved' },
  { label: 'Crew AppSheet', detail: 'Marco R. (Lead)' },
  { label: 'SMS Invoice', detail: '$50 deposit link sent' },
  { label: 'Customer Email', detail: 'Confirmation delivered' },
]

async function script(a: Act<S>) {
  await a.wait(900)
  a.mark('enter')
  
  // Smoothly move pointer to the Approve button
  await a.move({ at: 'approve-btn', x: 0.5, y: 0.5 }, { duration: 600 })
  a.put({ status: 'hovering' })
  await a.wait(250)

  // Click down
  a.mark('click')
  await a.click({ at: 'approve-btn', x: 0.5, y: 0.5 })
  a.put({ status: 'dispatching', stepsCompleted: 1 })
  
  // Move pointer slightly aside to let viewer watch the pipeline light up
  await a.move({ at: 'approve-btn', x: 1.1, y: 0.5 }, { duration: 400 })
  
  // Sequential API checkoffs
  await a.wait(300)
  a.put({ stepsCompleted: 2 })
  await a.wait(260)
  a.put({ stepsCompleted: 3 })
  await a.wait(260)
  a.put({ stepsCompleted: 4 })
  await a.wait(280)
  a.mark('completed')
  a.put({ stepsCompleted: 5, status: 'booked', confirmed: true })

  // Hold payoff so the viewer can comfortably read the success state
  await a.wait(3500)
}

export default function SplendidDispatch() {
  return (
    <Stage<S>
      width={780}
      height={440}
      compact={{ below: 780, width: 358, height: 560 }}
      initial={initial}
      poster={POSTER}
      script={script}
      play="loop"
      cursor={{ at: { x: 740, y: 390 } }}
      className="sd-stage"
    >
      {(s, _rectFor, layout) => {
        const isCompact = layout === 'compact'
        return (
          <Window url="ops.splendidmoving.com/dispatch" className="sd-window">
            <div className={`sd-layout ${isCompact ? 'sd-layout--compact' : ''}`}>
              {/* Left Column: Chat Feed & Action Card */}
              <div className="sd-chat-col">
                <div className="sd-feed-header">
                  <div className="sd-bot-badge">
                    <span className="sd-pulse-dot" />
                    <span className="sd-feed-title">#ops-dispatch · Google Chat</span>
                  </div>
                  <Badge tone="neutral">Splendid Bot</Badge>
                </div>

                <div className="sd-message-box">
                  <div className="sd-msg-sender">
                    <Avatar name="Sarah Jenkins" size={20} tone="accent" />
                    <span className="sd-sender-name">Sarah Jenkins (Yelp Lead)</span>
                    <span className="sd-time">09:14 AM</span>
                  </div>
                  <div className="sd-lead-bubble">
                    <div className="sd-lead-title">2-Bed Apt Move · Manhattan → Brooklyn</div>
                    <div className="sd-lead-sub">1420 5th Ave (Elevator) to 880 Broadway · Nov 14, 9am</div>
                  </div>
                </div>

                {/* Bot Proposal & Approval Action */}
                <div className="sd-action-card">
                  <div className="sd-action-head">
                    <span className="sd-action-tag">READY TO BOOK</span>
                    <span className="sd-quote-price">$420 · 2 Movers + Truck</span>
                  </div>

                  <div className="sd-specs-row">
                    <span className="sd-spec-pill">Nov 14 · 9:00 AM</span>
                    <span className="sd-spec-pill">$50 Deposit</span>
                    <span className="sd-spec-pill">Truck #2</span>
                  </div>

                  <div className="sd-btn-row">
                    <button
                      type="button"
                      className="sd-approve-btn"
                      data-target="approve-btn"
                      data-status={s.status}
                      disabled={s.status === 'dispatching' || s.status === 'booked'}
                    >
                      {s.status === 'booked' ? (
                        <>
                          <span className="sd-btn-check">✓</span> Dispatched to Crew
                        </>
                      ) : s.status === 'dispatching' ? (
                        <>
                          <span className="sd-spinner" /> Booking systems...
                        </>
                      ) : (
                        <>
                          <span className="sd-btn-spark">⚡</span> Approve & Dispatch
                        </>
                      )}
                    </button>
                  </div>

                  {s.confirmed && (
                    <div className="sd-confirmed-note">
                      <span className="sd-confirmed-text">✓ 5/5 systems confirmed. Calendar locked.</span>
                    </div>
                  )}
                </div>
              </div>

              {/* Right Column: Satellite Pipeline & Calendar Slot */}
              <div className="sd-satellite-col" data-target="pipeline-card">
                <div className="sd-panel-head">
                  <span className="sd-panel-title">Automated Ops Pipeline</span>
                  <Badge tone={s.confirmed ? 'success' : s.stepsCompleted > 0 ? 'accent' : 'neutral'}>
                    {s.confirmed ? 'COMPLETED' : s.stepsCompleted > 0 ? 'RUNNING' : 'QUEUED'}
                  </Badge>
                </div>

                <div className="sd-steps-list">
                  {STEPS.map((step, idx) => {
                    const done = s.stepsCompleted > idx
                    const current = s.stepsCompleted === idx + 1 && !s.confirmed
                    return (
                      <div key={step.label} className="sd-step-item" data-done={done} data-active={current}>
                        <div className="sd-step-indicator">
                          {done ? <span className="sd-step-check">✓</span> : <span className="sd-step-num">{idx + 1}</span>}
                        </div>
                        <div className="sd-step-info">
                          <span className="sd-step-label">{step.label}</span>
                          <span className="sd-step-detail">{step.detail}</span>
                        </div>
                      </div>
                    )
                  })}
                </div>

                {/* Truck Booking Schedule Ticket */}
                <div className="sd-ticket-card" data-booked={s.confirmed}>
                  <div className="sd-ticket-top">
                    <div className="sd-ticket-truck">
                      <span className="sd-truck-icon">🚚</span>
                      <div>
                        <div className="sd-truck-name">Truck #2 (16ft)</div>
                        <div className="sd-truck-meta">Lead: Marco R. · 2 Movers</div>
                      </div>
                    </div>
                    <span className={`sd-status-chip ${s.confirmed ? 'sd-chip-booked' : 'sd-chip-pending'}`}>
                      {s.confirmed ? 'BOOKED' : 'PENDING'}
                    </span>
                  </div>
                  <div className="sd-ticket-route">
                    <span className="sd-route-dot start" />
                    <span className="sd-route-line" />
                    <span className="sd-route-dot end" />
                    <span className="sd-route-text">1420 5th Ave → 880 Broadway</span>
                  </div>
                </div>
              </div>
            </div>
          </Window>
        )
      }}
    </Stage>
  )
}

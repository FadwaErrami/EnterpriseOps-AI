import { useCallback, useEffect, useMemo, useState } from 'react'
import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'
import {
  Activity, Check, Clock, FileText,
  RefreshCw, Server, ShieldCheck, Sparkles, X,
} from 'lucide-react'
import { StackedTimeline, Sparkline, SegmentBar, BarList } from './components/Charts'
import {
  SEVERITIES, severityColor, severityOf, formatDate, formatWhen, buildTimeline, countBy,
} from './lib/incidents'
import './App.css'

const API = '/api'

export default function App() {
  const [incidents, setIncidents] = useState([])
  const [selectedId, setSelectedId] = useState(null)
  const [audits, setAudits] = useState([])
  const [health, setHealth] = useState('checking')
  const [loading, setLoading] = useState(true)
  const [notice, setNotice] = useState(null) // { type: 'info' | 'success' | 'error', text }
  const [diagnoses, setDiagnoses] = useState({}) // une analyse par incident, conservée au changement de sélection
  const [analyzingId, setAnalyzingId] = useState(null)
  const [pendingAction, setPendingAction] = useState(null) // 'approve' | 'reject' | null
  const [filter, setFilter] = useState('ALL')
  const [query, setQuery] = useState('')
  const [autoRefresh, setAutoRefresh] = useState(false)
  const [updatedAt, setUpdatedAt] = useState(null)

  const loadIncidents = useCallback(async ({ silent = false } = {}) => {
    try {
      if (!silent) setLoading(true)
      const [healthRes, incidentRes] = await Promise.all([
        fetch(`${API}/health`),
        fetch(`${API}/incidents`),
      ])
      if (!healthRes.ok || !incidentRes.ok) throw new Error('API request failed')

      const healthData = await healthRes.json()
      const incidentData = await incidentRes.json()
      const items = incidentData.incidents || []

      setHealth(healthData.status)
      setIncidents(items)
      setSelectedId((prev) => (items.some((i) => i.id === prev) ? prev : items[0]?.id ?? null))
      setUpdatedAt(new Date())
    } catch {
      setHealth('unavailable')
      setNotice({
        type: 'error',
        text: 'Cannot reach the FastAPI backend. Check that it is running and that the /api proxy is configured.',
      })
    } finally {
      setLoading(false)
    }
  }, [])

  const loadAudit = useCallback(async (id) => {
    if (!id) {
      setAudits([])
      return
    }
    try {
      const response = await fetch(`${API}/incidents/${id}/audit`)
      if (!response.ok) throw new Error('Audit unavailable')
      const data = await response.json()
      setAudits(data.audits || [])
    } catch {
      setAudits([])
    }
  }, [])

  useEffect(() => {
    loadIncidents()
  }, [loadIncidents])

  useEffect(() => {
    if (!autoRefresh) return undefined
    const timer = setInterval(() => loadIncidents({ silent: true }), 15000)
    return () => clearInterval(timer)
  }, [autoRefresh, loadIncidents])

  useEffect(() => {
    setPendingAction(null)
    loadAudit(selectedId)
  }, [selectedId, loadAudit])

  async function decide(action) {
    if (!selectedId) return
    try {
      const response = await fetch(`${API}/incidents/${selectedId}/${action}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          comment:
            action === 'approve'
              ? 'Approved from EnterpriseOps AI dashboard'
              : 'Rejected from EnterpriseOps AI dashboard',
        }),
      })
      const data = await response.json()
      if (!response.ok) throw new Error(data.detail || 'Action failed')

      setNotice({ type: 'success', text: action === 'approve' ? 'Incident approved.' : 'Incident rejected.' })
      await loadAudit(selectedId)
    } catch (error) {
      setNotice({ type: 'error', text: error.message })
    } finally {
      setPendingAction(null)
    }
  }

  async function analyze() {
    if (!selectedId) return
    const id = selectedId
    setAnalyzingId(id)
    setNotice(null)
    try {
      const response = await fetch(`${API}/incidents/${id}/analyze`, { method: 'POST' })
      const data = await response.json()
      if (!response.ok || data.error) throw new Error(data.error || 'Analysis failed')

      setDiagnoses((prev) => ({ ...prev, [id]: data.diagnosis }))
      setNotice({ type: 'success', text: 'AI diagnosis generated.' })
    } catch (error) {
      setNotice({ type: 'error', text: error.message })
    } finally {
      setAnalyzingId(null)
    }
  }

  // ---- Valeurs dérivées (toutes calculées depuis les incidents réels) ----
  const selected = useMemo(
    () => incidents.find((i) => i.id === selectedId) || null,
    [incidents, selectedId],
  )
  const diagnosis = selectedId ? diagnoses[selectedId] : null

  const severityCounts = useMemo(() => {
    const counts = {}
    incidents.forEach((i) => {
      const key = severityOf(i)
      counts[key] = (counts[key] || 0) + 1
    })
    return counts
  }, [incidents])

  const timeline = useMemo(() => buildTimeline(incidents), [incidents])
  const services = useMemo(
    () => countBy(incidents, (i) => i.service || 'Unknown service'),
    [incidents],
  )

  const total = incidents.length
  const criticalHigh = (severityCounts.CRITICAL || 0) + (severityCounts.HIGH || 0)
  const criticalShare = total ? Math.round((criticalHigh / total) * 100) : 0

  const visible = useMemo(() => {
    const q = query.trim().toLowerCase()
    return incidents.filter((i) => {
      if (filter !== 'ALL' && severityOf(i) !== filter) return false
      if (!q) return true
      return [i.title, i.service, i.id].some((v) => String(v || '').toLowerCase().includes(q))
    })
  }, [incidents, filter, query])

  // Cycle de vie de l'incident sélectionné : détecté → analysé → décidé
  const decision = audits.some((a) => /approve/i.test(a.action || ''))
    ? 'approved'
    : audits.some((a) => /reject/i.test(a.action || ''))
      ? 'rejected'
      : null
  const steps = [
    { label: 'Detected', state: 'done' },
    { label: 'Analysed', state: diagnosis ? 'done' : 'current' },
    {
      label: decision === 'approved' ? 'Approved' : decision === 'rejected' ? 'Rejected' : 'Decision',
      state: decision ? 'done' : diagnosis ? 'current' : 'todo',
    },
  ]

  const healthy = health === 'healthy'
  const filterLabel = SEVERITIES.find((s) => s.key === filter)?.label

  return (
    <div className="shell">
      <aside className="rail">
        <div className="wordmark">
          <span className="mark"><Activity size={16} /></span>
          EnterpriseOps
        </div>

        <nav className="nav" aria-label="Main">
          <button className="nav-item active" aria-current="page"><Server size={16} /> Incidents</button>
          <button className="nav-item" disabled title="Coming soon">
            <Activity size={16} /> Monitoring <span className="soon">Soon</span>
          </button>
          <button className="nav-item" disabled title="Coming soon">
            <ShieldCheck size={16} /> Governance <span className="soon">Soon</span>
          </button>
          <button className="nav-item" disabled title="Coming soon">
            <FileText size={16} /> Audit logs <span className="soon">Soon</span>
          </button>
        </nav>

        <div className="rail-status" data-testid="backend-status">
          <span className={`dot ${healthy ? 'ok' : 'down'}`} />
          Backend {health}
        </div>
      </aside>

      <main className="main">
        <header className="topbar">
          <div>
            <h1>Incidents</h1>
            <p>Anomalies detected in logs, analysed by the AI agent, approved by a human.</p>
          </div>
          <div className="topbar-actions">
            {updatedAt && (
              <span className="updated">
                Updated {updatedAt.toLocaleTimeString('en-GB')}
              </span>
            )}
            <label className="toggle">
              <input
                type="checkbox"
                checked={autoRefresh}
                onChange={(e) => setAutoRefresh(e.target.checked)}
              />
              <span className="toggle-track" aria-hidden="true" />
              Auto-refresh
              {autoRefresh && <span className="dot ok pulse" />}
            </label>
            <button className="btn" onClick={() => loadIncidents()} data-testid="refresh-button">
              <RefreshCw size={15} className={loading ? 'spin' : ''} /> Refresh
            </button>
          </div>
        </header>

        {notice && (
          <div className={`notice ${notice.type}`} role="status" data-testid="notice">
            <span>{notice.text}</span>
            <button onClick={() => setNotice(null)} aria-label="Dismiss message"><X size={15} /></button>
          </div>
        )}

        <section className="kpis" aria-label="Key figures">
          <div className="kpi" data-testid="kpi-total">
            <span className="kpi-label">Incidents</span>
            <strong className="kpi-value">{total}</strong>
            <div className="kpi-foot">
              {timeline ? <Sparkline values={timeline.buckets.map((b) => b.total)} /> : <small>No timeline yet</small>}
            </div>
          </div>
          <div className="kpi" data-testid="kpi-critical">
            <span className="kpi-label">Critical and high</span>
            <strong className="kpi-value tone-critical">{criticalHigh}</strong>
            <div className="kpi-foot"><small>{total ? `${criticalShare}% of all incidents` : 'Nothing to rank'}</small></div>
          </div>
          <div className="kpi" data-testid="kpi-services">
            <span className="kpi-label">Services affected</span>
            <strong className="kpi-value">{services.length}</strong>
            <div className="kpi-foot"><small>{services[0] ? `Most hit: ${services[0].label}` : 'No service data'}</small></div>
          </div>
          <div className="kpi" data-testid="kpi-health">
            <span className="kpi-label">Backend</span>
            <strong className={`kpi-value kpi-text ${healthy ? 'tone-ok' : 'tone-critical'}`}>{health}</strong>
            <div className="kpi-foot"><small>{updatedAt ? `Checked ${updatedAt.toLocaleTimeString('en-GB')}` : 'Waiting for first check'}</small></div>
          </div>
        </section>

        <section className="overview">
          <div className="panel timeline-panel">
            <div className="panel-head">
              <div>
                <h2>Incident volume</h2>
                <p>
                  {timeline
                    ? `${formatDate(timeline.start)} to ${formatDate(timeline.end)}, stacked by severity`
                    : 'Incidents over time'}
                </p>
              </div>
              {timeline && (
                <ul className="key">
                  {SEVERITIES.filter((s) => severityCounts[s.key]).map((s) => (
                    <li key={s.key}><i style={{ background: severityColor(s.key) }} />{s.label}</li>
                  ))}
                </ul>
              )}
            </div>
            {timeline ? (
              <StackedTimeline timeline={timeline} />
            ) : (
              <p className="empty">
                A timeline needs at least two incidents with different <code>created_at</code> or{' '}
                <code>timestamp</code> values.
              </p>
            )}
          </div>

          <div className="panel mix-panel">
            <div className="panel-head">
              <div><h2>Severity mix</h2><p>Select a severity to filter the queue</p></div>
            </div>
            {total ? (
              <SegmentBar counts={severityCounts} active={filter} onSelect={setFilter} />
            ) : (
              <p className="empty">No incidents to classify.</p>
            )}

            <div className="subhead">Most affected services</div>
            {services.length ? <BarList items={services.slice(0, 5)} /> : <p className="empty">No service data.</p>}
          </div>
        </section>

        <section className="workspace">
          <div className="panel queue">
            <div className="panel-head">
              <div><h2>Incident queue</h2><p>{visible.length} of {total} shown</p></div>
              {filter !== 'ALL' && (
                <button className="chip" onClick={() => setFilter('ALL')}>
                  {filterLabel} <X size={12} />
                </button>
              )}
            </div>

            <input
              className="search"
              type="search"
              placeholder="Search by title, service or ID"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              aria-label="Search incidents"
            />

            {loading ? (
              <p className="empty">Loading incidents…</p>
            ) : visible.length === 0 ? (
              <p className="empty">
                {total === 0
                  ? 'No incidents yet. Start the log simulator to generate some.'
                  : 'No incident matches these filters.'}
              </p>
            ) : (
              <ul className="incident-list">
                {visible.map((item) => {
                  const sev = severityOf(item)
                  return (
                    <li key={item.id}>
                      <button
                        className={`incident ${selectedId === item.id ? 'selected' : ''}`}
                        data-sev={sev}
                        data-testid="incident-item"
                        aria-current={selectedId === item.id}
                        onClick={() => setSelectedId(item.id)}
                      >
                        <span className="incident-top">
                          <strong>{item.title || 'Untitled incident'}</strong>
                          <span className="sev-tag">{SEVERITIES.find((s) => s.key === sev).label}</span>
                        </span>
                        <span className="incident-meta">
                          <span>{item.service || 'Unknown service'}</span>
                          <span><Clock size={11} /> {formatWhen(item)}</span>
                        </span>
                      </button>
                    </li>
                  )
                })}
              </ul>
            )}
          </div>

          <div className="investigation">
            {!selected ? (
              <div className="panel">
                <p className="empty">Select an incident from the queue to investigate it.</p>
              </div>
            ) : (
              <>
                <div className="panel" data-sev={severityOf(selected)}>
                  <div className="detail-head">
                    <span className="sev-tag big">{SEVERITIES.find((s) => s.key === severityOf(selected)).label}</span>
                    <h2 className="detail-title" data-testid="detail-title">{selected.title || 'Untitled incident'}</h2>
                    <div className="detail-meta">
                      <span>{selected.service || 'Unknown service'}</span>
                      <span><Clock size={12} /> {formatWhen(selected)}</span>
                      <code>{selected.id}</code>
                    </div>
                  </div>

                  <ol className="steps" aria-label="Incident lifecycle">
                    {steps.map((s) => (
                      <li key={s.label} className={s.state}>
                        <span className="step-dot">{s.state === 'done' ? <Check size={11} /> : null}</span>
                        {s.label}
                      </li>
                    ))}
                  </ol>

                  <p className="description">{selected.description || 'No description available.'}</p>
                </div>

                <div className="panel">
                  <div className="panel-head">
                    <div><h2>AI diagnosis</h2><p>Retrieves matching runbooks and proposes a probable cause. Nothing is executed.</p></div>
                    <button
                      className="btn primary"
                      onClick={analyze}
                      disabled={analyzingId === selectedId}
                      data-testid="analyze-button"
                    >
                      <Sparkles size={15} />
                      {analyzingId === selectedId ? 'Analysing…' : diagnosis ? 'Analyse again' : 'Analyse with AI'}
                    </button>
                  </div>

                  {diagnosis ? (
                    <div className="diagnosis" data-testid="diagnosis-result">
                      <dl className="facts">
                        <div>
                          <dt>Severity</dt>
                          <dd>
                            <span className="sev-tag" data-sev={severityOf({ severity: diagnosis.severity })}>
                              {diagnosis.severity}
                            </span>
                          </dd>
                        </div>
                        <div><dt>Probable cause or runbook</dt><dd>{diagnosis.probable_cause}</dd></div>
                        <div><dt>Approval required</dt><dd>{diagnosis.approval_required ? 'Yes' : 'No'}</dd></div>
                      </dl>

                      {diagnosis.evidence?.length > 0 && (
                        <div className="evidence">
                          <h3>Evidence retrieved from runbooks</h3>
                          <ol>
                            {diagnosis.evidence.map((item, index) => (
                              <li key={index}>{item}</li>
                            ))}
                          </ol>
                        </div>
                      )}

                      <div className="analysis-text">
                        <ReactMarkdown remarkPlugins={[remarkGfm]}>
                          {diagnosis.ai_analysis || diagnosis.summary || ''}
                        </ReactMarkdown>
                      </div>
                    </div>
                  ) : (
                    <p className="empty">No diagnosis yet. Run the analysis to see the agent's findings.</p>
                  )}
                </div>

                <div className="panel decision">
                  <div className="panel-head">
                    <div><h2>Human decision</h2><p>Human approval is required. Remediation is currently simulated.</p></div>
                  </div>

                  {pendingAction ? (
                    <div className="confirm" role="alertdialog" aria-label="Confirm decision">
                      <span>
                        {pendingAction === 'approve'
                          ? 'Approve the remediation for this incident?'
                          : 'Reject the remediation for this incident?'}
                      </span>
                      <div className="confirm-actions">
                        <button
                          className={`btn ${pendingAction === 'approve' ? 'approve' : 'reject'}`}
                          onClick={() => decide(pendingAction)}
                          data-testid="confirm-button"
                        >
                          {pendingAction === 'approve' ? 'Confirm approval' : 'Confirm rejection'}
                        </button>
                        <button className="btn" onClick={() => setPendingAction(null)}>Cancel</button>
                      </div>
                    </div>
                  ) : (
                    <div className="actions">
                      <button className="btn approve" onClick={() => setPendingAction('approve')} data-testid="approve-button">
                        <Check size={15} /> Approve
                      </button>
                      <button className="btn reject" onClick={() => setPendingAction('reject')} data-testid="reject-button">
                        <X size={15} /> Reject
                      </button>
                    </div>
                  )}
                </div>

                <div className="panel">
                  <div className="panel-head">
                    <div><h2>Remediation audit</h2><p>Actions recorded for this incident</p></div>
                  </div>
                  {audits.length === 0 ? (
                    <p className="empty">No audit records yet. Decisions you make above are recorded here.</p>
                  ) : (
                    <ol className="audit" data-testid="audit-list">
                      {audits.map((audit) => (
                        <li key={audit.id}>
                          <span className="audit-dot" />
                          <div>
                            <div className="audit-line">
                              <strong>{audit.action}</strong>
                              <span className="audit-status">{audit.status}</span>
                            </div>
                            <p>{audit.message}</p>
                            <small>{audit.created_at}</small>
                          </div>
                        </li>
                      ))}
                    </ol>
                  )}
                </div>
              </>
            )}
          </div>
        </section>
      </main>
    </div>
  )
}


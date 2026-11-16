// Rapport d'analyse IA : verdict, sources, puis analyse découpée en sections repliables.
// Le markdown renvoyé par le LLM est découpé par titres (#, ##, ###) : chaque titre devient une section.
import { useState } from 'react'
import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'
import { Sparkles } from 'lucide-react'
import { SEVERITIES, severityOf } from '../lib/incidents'

// Une section dont le titre parle de remédiation est présentée comme une liste d'étapes numérotées.
const ACTION_RE = /action|remediat|step|recommend|fix|solution|mitigat|resolution|next/i

export function parseSections(markdown = '') {
  const sections = []
  let current = { title: null, lines: [] }
  let inFence = false

  const flush = () => {
    const body = current.lines.join('\n').trim()
    if (body) sections.push({ title: current.title, body })
  }

  for (const line of markdown.split('\n')) {
    if (line.trim().startsWith('```')) inFence = !inFence
    const match = !inFence && line.match(/^#{1,4}\s+(.*)$/)
    if (match) {
      flush()
      current = { title: match[1].replace(/[*_`]/g, '').trim(), lines: [] }
    } else {
      current.lines.push(line)
    }
  }
  flush()
  return sections
}

function AnalyseButton({ analyzing, label, onAnalyze, primary }) {
  return (
    <button
      className={`btn ${primary ? 'primary' : ''}`}
      onClick={onAnalyze}
      disabled={analyzing}
      data-testid="analyze-button"
    >
      <Sparkles size={15} />
      {analyzing ? 'Analysing…' : label}
    </button>
  )
}

export default function AiReport({ diagnosis, analyzing, onAnalyze }) {
  const [expanded, setExpanded] = useState(() => new Set())

  if (!diagnosis) {
    return (
      <div className="report-empty">
        <p className="empty">
          The AI agent has not analysed this incident yet. When you run it, the agent works in three
          stages. Nothing is executed on your systems.
        </p>
        <ol className="pipeline">
          <li><b>Retrieve</b><span>Finds the runbooks that match this incident.</span></li>
          <li><b>Diagnose</b><span>Proposes a probable cause backed by those sources.</span></li>
          <li><b>Hand over</b><span>Sends the proposal to a human for approval.</span></li>
        </ol>
        <AnalyseButton primary analyzing={analyzing} label="Analyse with AI" onAnalyze={onAnalyze} />
        {analyzing && <div className="progress" role="progressbar" aria-label="Analysis in progress" />}
      </div>
    )
  }

  const sev = severityOf({ severity: diagnosis.severity })
  const sevLabel = SEVERITIES.find((s) => s.key === sev).label
  const sources = diagnosis.evidence || []
  const sections = parseSections(diagnosis.ai_analysis || diagnosis.summary || '')

  const toggle = (index) =>
    setExpanded((prev) => {
      const next = new Set(prev)
      if (next.has(index)) next.delete(index)
      else next.add(index)
      return next
    })

  return (
    <div className="report" data-testid="diagnosis-result">
      <header className="verdict" data-sev={sev}>
        <div>
          <span className="verdict-label">Probable cause or runbook</span>
          <h3>{diagnosis.probable_cause || 'No probable cause returned'}</h3>
        </div>
        <div className="verdict-side">
          <span className="sev-tag">{sevLabel} severity</span>
          <span className={`gate ${diagnosis.approval_required ? 'required' : 'none'}`}>
            {diagnosis.approval_required ? 'Human approval required' : 'No approval required'}
          </span>
          <AnalyseButton analyzing={analyzing} label="Run again" onAnalyze={onAnalyze} />
        </div>
      </header>

      {analyzing && <div className="progress" role="progressbar" aria-label="Analysis in progress" />}

      {sources.length > 0 && (
        <section aria-label="Sources">
          <h3 className="report-title">Sources retrieved from runbooks <span>{sources.length}</span></h3>
          <ul className="sources">
            {sources.map((text, index) => {
              const long = String(text).length > 150
              const open = expanded.has(index)
              return (
                <li key={index}>
                  <button
                    className={`source ${open ? 'expanded' : ''}`}
                    onClick={() => long && toggle(index)}
                    aria-expanded={long ? open : undefined}
                    disabled={!long}
                  >
                    <span className="source-n">Source {index + 1}</span>
                    <span className="source-text">{text}</span>
                    {long && <span className="source-more">{open ? 'Show less' : 'Show more'}</span>}
                  </button>
                </li>
              )
            })}
          </ul>
        </section>
      )}

      {sections.length > 0 && (
        <section aria-label="Analysis">
          <h3 className="report-title">Analysis <span>{sections.length}</span></h3>
          {sections.map((section, index) => {
            const isActions = section.title && ACTION_RE.test(section.title)
            return (
              <details key={index} className={`section ${isActions ? 'actions' : ''}`} open>
                <summary>
                  {section.title || 'Summary'}
                  {isActions && <em className="tag-sim">Simulated, nothing is executed</em>}
                </summary>
                <div className="section-body">
                  <ReactMarkdown remarkPlugins={[remarkGfm]}>{section.body}</ReactMarkdown>
                </div>
              </details>
            )
          })}
        </section>
      )}
    </div>
  )
}

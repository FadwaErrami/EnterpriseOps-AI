// Graphiques en SVG/HTML pur : zéro dépendance supplémentaire (pas de Recharts, pas de Chart.js).
import { SEVERITIES, severityColor, formatDate } from '../lib/incidents'

// Volume d'incidents dans le temps, empilé par sévérité.
export function StackedTimeline({ timeline }) {
  const W = 600
  const H = 150
  const GAP = 5
  const n = timeline.buckets.length
  const barWidth = (W - GAP * (n - 1)) / n
  const max = Math.max(...timeline.buckets.map((b) => b.total), 1)
  const stackOrder = [...SEVERITIES].reverse() // les plus graves au sommet

  return (
    <svg
      className="timeline-svg"
      viewBox={`0 0 ${W} ${H}`}
      preserveAspectRatio="none"
      role="img"
      aria-label="Incident volume over time, stacked by severity"
    >
      {[0, 0.5, 1].map((t) => (
        <line
          key={t}
          className="grid-line"
          x1="0"
          x2={W}
          y1={H - t * (H - 6)}
          y2={H - t * (H - 6)}
          vectorEffect="non-scaling-stroke"
        />
      ))}

      {timeline.buckets.map((bucket, i) => {
        const x = i * (barWidth + GAP)
        let y = H
        const breakdown = SEVERITIES.filter((s) => bucket.counts[s.key])
          .map((s) => `${bucket.counts[s.key]} ${s.label.toLowerCase()}`)
          .join(', ')
        const tip = `${formatDate(bucket.from)} to ${formatDate(bucket.to)}: ${bucket.total} incident${
          bucket.total === 1 ? '' : 's'
        }${breakdown ? ` (${breakdown})` : ''}`

        return (
          <g key={i}>
            {stackOrder.map((s) => {
              const count = bucket.counts[s.key] || 0
              if (!count) return null
              const h = (count / max) * (H - 6)
              y -= h
              return (
                <rect
                  key={s.key}
                  className="bar"
                  x={x}
                  y={y}
                  width={barWidth}
                  height={Math.max(h - 1, 1)}
                  style={{ fill: severityColor(s.key), animationDelay: `${i * 30}ms` }}
                />
              )
            })}
            <rect x={x} y={0} width={barWidth} height={H} fill="transparent">
              <title>{tip}</title>
            </rect>
          </g>
        )
      })}
    </svg>
  )
}

export function Sparkline({ values, color = 'var(--accent)' }) {
  if (!values || values.length < 2) return null
  const W = 100
  const H = 28
  const max = Math.max(...values, 1)
  const points = values
    .map((v, i) => `${(i / (values.length - 1)) * W},${H - 2 - (v / max) * (H - 4)}`)
    .join(' ')

  return (
    <svg className="spark" viewBox={`0 0 ${W} ${H}`} preserveAspectRatio="none" aria-hidden="true">
      <polyline
        points={points}
        fill="none"
        strokeWidth="1.5"
        vectorEffect="non-scaling-stroke"
        style={{ stroke: color }}
      />
    </svg>
  )
}

// Barre segmentée de la répartition par sévérité. La légende sert de filtre.
export function SegmentBar({ counts, active, onSelect }) {
  const present = SEVERITIES.filter((s) => counts[s.key] > 0)

  return (
    <div>
      <div className="segbar" role="img" aria-label="Severity distribution">
        {present.map((s) => (
          <span key={s.key} style={{ flexGrow: counts[s.key], background: severityColor(s.key) }} />
        ))}
      </div>
      <ul className="seglegend">
        {present.map((s) => (
          <li key={s.key}>
            <button
              type="button"
              className={`legend-btn ${active === s.key ? 'active' : ''}`}
              aria-pressed={active === s.key}
              onClick={() => onSelect(active === s.key ? 'ALL' : s.key)}
            >
              <i style={{ background: severityColor(s.key) }} />
              <span>{s.label}</span>
              <b>{counts[s.key]}</b>
            </button>
          </li>
        ))}
      </ul>
    </div>
  )
}

export function BarList({ items }) {
  const max = Math.max(...items.map((it) => it.value), 1)
  return (
    <ul className="barlist">
      {items.map((it) => (
        <li key={it.label}>
          <div className="barlist-row">
            <span title={it.label}>{it.label}</span>
            <b>{it.value}</b>
          </div>
          <div className="barlist-track">
            <i style={{ width: `${(it.value / max) * 100}%` }} />
          </div>
        </li>
      ))}
    </ul>
  )
}

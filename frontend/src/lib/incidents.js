// Fonctions pures de calcul pour le dashboard : aucune dépendance, aucune donnée inventée.
// Tout ce qui est affiché dans les graphiques est dérivé de la liste d'incidents renvoyée par l'API.

// Ordre = du plus grave au moins grave (sert aussi à l'empilement des barres).
export const SEVERITIES = [
  { key: 'CRITICAL', label: 'Critical' },
  { key: 'HIGH', label: 'High' },
  { key: 'MEDIUM', label: 'Medium' },
  { key: 'LOW', label: 'Low' },
  { key: 'UNKNOWN', label: 'Unclassified' },
]

export const severityColor = (key) => `var(--sev-${key.toLowerCase()})`

export function severityOf(incident) {
  const raw = String(incident?.severity || incident?.priority || '').toUpperCase()
  return SEVERITIES.some((s) => s.key === raw) ? raw : 'UNKNOWN'
}

export function dateOf(incident) {
  const raw = incident?.created_at || incident?.timestamp
  if (!raw) return null
  const d = new Date(raw)
  return Number.isNaN(d.getTime()) ? null : d
}

export function formatDate(d) {
  return d.toLocaleString('en-GB', {
    day: '2-digit',
    month: 'short',
    hour: '2-digit',
    minute: '2-digit',
  })
}

export function formatWhen(incident) {
  const d = dateOf(incident)
  if (d) return formatDate(d)
  return incident?.created_at || incident?.timestamp || 'No timestamp'
}

export function countBy(items, getKey) {
  const map = new Map()
  items.forEach((item) => {
    const key = getKey(item)
    map.set(key, (map.get(key) || 0) + 1)
  })
  return [...map.entries()]
    .map(([label, value]) => ({ label, value }))
    .sort((a, b) => b.value - a.value)
}

// Répartit les incidents datés en tranches de temps égales entre le plus ancien et le plus récent.
// Retourne null s'il n'y a pas assez de dates pour dessiner une courbe honnête.
export function buildTimeline(incidents, bucketCount = 14) {
  const dated = incidents
    .map((incident) => ({ date: dateOf(incident), severity: severityOf(incident) }))
    .filter((x) => x.date)

  if (dated.length < 2) return null

  const times = dated.map((x) => x.date.getTime())
  const min = Math.min(...times)
  const max = Math.max(...times)
  if (max === min) return null

  const step = (max - min) / bucketCount
  const buckets = Array.from({ length: bucketCount }, (_, i) => ({
    from: new Date(min + i * step),
    to: new Date(min + (i + 1) * step),
    total: 0,
    counts: {},
  }))

  dated.forEach(({ date, severity }) => {
    const index = Math.min(bucketCount - 1, Math.floor((date.getTime() - min) / step))
    const bucket = buckets[index]
    bucket.total += 1
    bucket.counts[severity] = (bucket.counts[severity] || 0) + 1
  })

  return { buckets, start: new Date(min), end: new Date(max), dated: dated.length }
}

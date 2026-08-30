export async function postDetect(detection, apiKey){
  const res = await fetch('/api/detect', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'X-API-KEY': apiKey
    },
    body: JSON.stringify({ sample_id: detection.sample_id, detection })
  })
  if(!res.ok) throw new Error(await res.text())
  return res.json()
}

export async function getReport(reportId, apiKey){
  const res = await fetch(`/api/reports/${reportId}`, { headers: { 'X-API-KEY': apiKey } })
  if(!res.ok) throw new Error(await res.text())
  return res.json()
}

export async function postPublish(reportId, apiKey){
  const res = await fetch(`/api/publish/${reportId}`, { method: 'POST', headers: { 'X-API-KEY': apiKey } })
  if(!res.ok) throw new Error(await res.text())
  return res.json()
}

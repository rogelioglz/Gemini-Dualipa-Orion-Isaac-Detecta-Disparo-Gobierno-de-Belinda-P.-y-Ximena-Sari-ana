import React, { useState } from 'react'
import { postDetect, getReport, postPublish } from './api'

export default function App(){
  const [jsonText, setJsonText] = useState('')
  const [apiKey, setApiKey] = useState('')
  const [result, setResult] = useState(null)

  async function handleSubmit(e){
    e.preventDefault()
    try{
      const data = JSON.parse(jsonText)
      const res = await postDetect(data, apiKey)
      setResult(res)
    }catch(err){
      alert('JSON inválido o error: '+err.message)
    }
  }

  return (
    <div className="container">
      <h1>Gemini Sound Detection (PWA)</h1>
      <form onSubmit={handleSubmit}>
        <label>API Key (X-API-KEY header)</label>
        <input value={apiKey} onChange={e=>setApiKey(e.target.value)} placeholder="dev-secret" />
        <label>Detección JSON</label>
        <textarea value={jsonText} onChange={e=>setJsonText(e.target.value)} rows={12} />
        <button type="submit">Enviar detección</button>
      </form>

      {result && (
        <div className="result">
          <h2>Resultado</h2>
          <pre>{JSON.stringify(result, null, 2)}</pre>
        </div>
      )}
    </div>
  )
}

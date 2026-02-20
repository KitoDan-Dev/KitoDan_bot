import { useEffect, useMemo, useRef, useState } from 'react'

const API_BASE = import.meta.env.VITE_API_BASE || '/api'
const MODES = ['auto', 'friend', 'sales', 'creative', 'automation']

export default function App() {
  const [sessions, setSessions] = useState([])
  const [messages, setMessages] = useState([])
  const [input, setInput] = useState('')
  const [mode, setMode] = useState(localStorage.getItem('mode') || 'auto')
  const [sessionId, setSessionId] = useState(localStorage.getItem('session_id') || '')
  const [status, setStatus] = useState({ ollama: 'checking...', model: '-', latency: '-', serverVersion: '-' })
  const [sending, setSending] = useState(false)
  const [responseTime, setResponseTime] = useState('-')
  const inputRef = useRef(null)

  const currentSession = useMemo(() => sessions.find((s) => s.id === sessionId), [sessions, sessionId])

  const loadHealth = async () => {
    const started = performance.now()
    try {
      const res = await fetch(`${API_BASE}/health`)
      const data = await res.json()
      setStatus({
        ollama: data.ollama_online ? 'online' : 'offline',
        model: data.model,
        latency: `${Math.round(performance.now() - started)} ms`,
        serverVersion: data.server_version || '-',
      })
    } catch {
      setStatus({ ollama: 'offline', model: '-', latency: '-', serverVersion: '-' })
    }
  }

  const loadSessions = async () => {
    const res = await fetch(`${API_BASE}/history?sessions=1`)
    const data = await res.json()
    setSessions(data.sessions || [])
  }

  const loadMessages = async (sid) => {
    if (!sid) return
    const res = await fetch(`${API_BASE}/history/${sid}`)
    const data = await res.json()
    setMessages(data.messages || [])
  }

  useEffect(() => {
    loadHealth()
    loadSessions()
    if (sessionId) loadMessages(sessionId)

    const timer = setInterval(loadHealth, 10000)
    return () => clearInterval(timer)
  }, [])

  useEffect(() => {
    localStorage.setItem('mode', mode)
  }, [mode])

  useEffect(() => {
    const onHotkey = (event) => {
      if (event.ctrlKey && event.shiftKey && event.key.toLowerCase() === 'k') {
        event.preventDefault()
        inputRef.current?.focus()
        if (!input.trim()) {
          sendMessage('Activate KitoDan')
        }
      }
    }

    window.addEventListener('keydown', onHotkey)
    return () => window.removeEventListener('keydown', onHotkey)
  }, [input])

  const sendMessage = async (text, { reset = false } = {}) => {
    if (!text.trim() || sending) return
    setSending(true)

    const userMessage = { role: 'user', content: text, created_at: new Date().toISOString() }
    setMessages((prev) => [...prev, userMessage])

    const started = performance.now()
    try {
      const res = await fetch(`${API_BASE}/chat`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          ...(sessionId ? { 'X-Session-Id': sessionId } : {}),
        },
        body: JSON.stringify({ message: text, mode, reset }),
      })

      const data = await res.json()
      if (!res.ok) throw new Error(data.detail || 'Request failed')

      const sid = res.headers.get('x-session-id') || data.session_id
      if (sid && sid !== sessionId) {
        setSessionId(sid)
        localStorage.setItem('session_id', sid)
      }

      setResponseTime(`${Math.round(performance.now() - started)} ms`)
      setMessages((prev) => [...prev, { role: 'assistant', content: data.reply, created_at: new Date().toISOString() }])
      setInput('')
      await loadSessions()
    } catch (error) {
      setMessages((prev) => [...prev, { role: 'assistant', content: `Error: ${error.message}`, created_at: new Date().toISOString() }])
    } finally {
      setSending(false)
    }
  }

  const handleReset = async () => {
    if (!sessionId) return
    await fetch(`${API_BASE}/reset`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ session_id: sessionId }),
    })
    setMessages([])
    await loadSessions()
  }

  const handleNewChat = () => {
    setMessages([])
    setSessionId('')
    localStorage.removeItem('session_id')
    inputRef.current?.focus()
  }

  const onInputKeyDown = (event) => {
    if (event.key === 'Enter' && !event.shiftKey) {
      event.preventDefault()
      sendMessage(input)
    }
  }

  return (
    <div className="layout">
      <aside className="sidebar">
        <button className="secondary" onClick={handleNewChat}>New Chat</button>
        <h3>Sessions</h3>
        <div className="session-list">
          {sessions.map((s) => (
            <button
              key={s.id}
              className={`session-item ${sessionId === s.id ? 'active' : ''}`}
              onClick={() => {
                setSessionId(s.id)
                localStorage.setItem('session_id', s.id)
                loadMessages(s.id)
              }}
            >
              <div>{s.title || `Session ${s.id.slice(0, 8)}`}</div>
              <small>{s.message_count} msgs</small>
            </button>
          ))}
        </div>
      </aside>

      <main className="app">
        <header>
          <h1>KitoDan (Local)</h1>
          <button className="activate" onClick={() => sendMessage('Activate KitoDan')}>Activate KitoDan</button>
        </header>

        <section className="controls">
          <label>
            Mode
            <select value={mode} onChange={(e) => setMode(e.target.value)}>
              {MODES.map((m) => <option key={m} value={m}>{m[0].toUpperCase() + m.slice(1)}</option>)}
            </select>
          </label>
          <button className="secondary" onClick={handleReset}>Reset chat</button>
          <span>{sending ? 'sending...' : `last response: ${responseTime}`}</span>
        </section>

        <section className="status">
          <strong>Ollama:</strong> {status.ollama}
          <strong>Model:</strong> {status.model}
          <strong>Latency:</strong> {status.latency}
          <strong>Server:</strong> {status.serverVersion}
          <strong>Session:</strong> {currentSession?.id?.slice(0, 8) || 'new'}
        </section>

        <section className="chat">
          {messages.map((m, idx) => (
            <div key={idx} className={`msg ${m.role}`}>
              <span>{m.role === 'user' ? 'You' : 'KitoDan'}:</span> {m.content}
            </div>
          ))}
        </section>

        <footer>
          <textarea
            ref={inputRef}
            value={input}
            placeholder="Type message (Enter to send, Shift+Enter for line break)..."
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={onInputKeyDown}
          />
          <button onClick={() => sendMessage(input)} disabled={sending}>Send</button>
        </footer>
      </main>
    </div>
  )
}

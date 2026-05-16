import { useState } from 'react'

const roles = ['Team Member', 'Team Captain', 'Faculty Advisor', 'Finance Manager', 'Department Manager']

function Chat() {
  const [role, setRole] = useState('Team Member')
  const [messages, setMessages] = useState([
    { from: 'bot', text: 'Hello! I am BAJA RuleBot. Select your role and ask me anything about the rulebook!' }
  ])
  const [input, setInput] = useState('')

  const sendMessage = () => {
    if (!input.trim()) return

    const userMsg = { from: 'user', text: input }
    const botMsg = { from: 'bot', text: `As a ${role}, here is what the rulebook says about "${input}": [Backend AI response will appear here once Renish connects the API]` }

    setMessages([...messages, userMsg, botMsg])
    setInput('')
  }

  const handleKey = (e) => {
    if (e.key === 'Enter') sendMessage()
  }

  return (
    <div className="min-h-screen bg-gray-950 text-white flex flex-col">
      {/* Role Selector */}
      <div className="bg-gray-800 px-6 py-3 flex items-center gap-4">
        <span className="text-gray-400 text-sm">Your Role:</span>
        <select
          value={role}
          onChange={(e) => setRole(e.target.value)}
          className="bg-gray-700 text-white px-4 py-2 rounded-lg text-sm focus:outline-none"
        >
          {roles.map(r => <option key={r}>{r}</option>)}
        </select>
        <span className="text-orange-500 text-sm font-bold ml-auto">📘 Rulebook Loaded</span>
      </div>

      {/* Chat Messages */}
      <div className="flex-1 overflow-y-auto px-6 py-6 flex flex-col gap-4">
        {messages.map((msg, i) => (
          <div key={i} className={`flex ${msg.from === 'user' ? 'justify-end' : 'justify-start'}`}>
            <div className={`max-w-xl px-5 py-3 rounded-2xl text-sm ${
              msg.from === 'user'
                ? 'bg-orange-500 text-white'
                : 'bg-gray-800 text-gray-200'
            }`}>
              {msg.text}
            </div>
          </div>
        ))}
      </div>

      {/* Input Box */}
      <div className="bg-gray-800 px-6 py-4 flex gap-3">
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={handleKey}
          placeholder="Ask about rulebook... e.g. What are roll cage requirements?"
          className="flex-1 bg-gray-700 text-white px-5 py-3 rounded-xl focus:outline-none text-sm"
        />
        <button
          onClick={sendMessage}
          className="bg-orange-500 hover:bg-orange-600 text-white font-bold px-6 py-3 rounded-xl transition"
        >
          Send
        </button>
      </div>
    </div>
  )
}

export default Chat
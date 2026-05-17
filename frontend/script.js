const BACKEND_URL = "http://127.0.0.1:8000"

function sendMessage() {
  const input = document.getElementById('chatInput')
  const messages = document.getElementById('chatMessages')
  const role = document.getElementById('roleSelect').value
  const text = input.value.trim()

  if (!text) return

  // Add user message
  const userMsg = document.createElement('div')
  userMsg.classList.add('message', 'user')
  userMsg.textContent = text
  messages.appendChild(userMsg)

  input.value = ''
  messages.scrollTop = messages.scrollHeight

  // Show loading
  const loadingMsg = document.createElement('div')
  loadingMsg.classList.add('message', 'bot')
  loadingMsg.textContent = 'Thinking...'
  loadingMsg.id = 'loading'
  messages.appendChild(loadingMsg)

  // Call backend
  fetch(`${BACKEND_URL}/chat`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ question: text, role: role })
  })
  .then(res => res.json())
  .then(data => {
    document.getElementById('loading').remove()
    const botMsg = document.createElement('div')
    botMsg.classList.add('message', 'bot')
    botMsg.textContent = data.answer || data.error
    messages.appendChild(botMsg)
    messages.scrollTop = messages.scrollHeight
  })
  .catch(err => {
    document.getElementById('loading').remove()
    const botMsg = document.createElement('div')
    botMsg.classList.add('message', 'bot')
    botMsg.textContent = 'Error connecting to server. Please try again!'
    messages.appendChild(botMsg)
    messages.scrollTop = messages.scrollHeight
  })
}

function handleKey(event) {
  if (event.key === 'Enter') sendMessage()
}
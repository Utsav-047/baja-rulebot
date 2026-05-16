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

  // Clear input
  input.value = ''

  // Scroll to bottom
  messages.scrollTop = messages.scrollHeight

  // Add bot reply
  setTimeout(() => {
    const botMsg = document.createElement('div')
    botMsg.classList.add('message', 'bot')
    botMsg.textContent = `As a ${role}, here is what the rulebook says about "${text}": [AI response will appear here once backend is connected by Renish]`
    messages.appendChild(botMsg)
    messages.scrollTop = messages.scrollHeight
  }, 1000)
}

function handleKey(event) {
  if (event.key === 'Enter') {
    sendMessage()
  }
}

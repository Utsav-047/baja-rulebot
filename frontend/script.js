// const BACKEND_URL = "http://127.0.0.1:8000"


// function formatResponse(text) {
//   // Convert **bold** to <strong>
//   text = text.replace(/\*\*(.*?)\*\*/g, '<strong style="color:white;">$1</strong>')
  
//   // Convert numbered list items
//   text = text.replace(/(\d+)\.\s+/g, '<br><br><span style="color:#f97316; font-weight:bold;">$1.</span> ')
  
//   // Convert bullet points
//   text = text.replace(/\*\s+/g, '<br>• ')
  
//   // Convert line breaks
//   text = text.replace(/\n/g, '<br>')
  
//   // Clean up extra breaks at start
//   text = text.replace(/^(<br>)+/, '')
  
//   return text
// }

// function sendMessage() {
//   const input = document.getElementById('chatInput')
//   const messages = document.getElementById('chatMessages')
//   const role = document.getElementById('roleSelect').value
//   const text = input.value.trim()

//   if (!text) return

//   // Add user message
//   const userMsg = document.createElement('div')
//   userMsg.classList.add('message', 'user')
//   userMsg.textContent = text
//   messages.appendChild(userMsg)

//   input.value = ''
//   messages.scrollTop = messages.scrollHeight

//   // Show loading
//   const loadingMsg = document.createElement('div')
//   loadingMsg.classList.add('message', 'bot')
//   loadingMsg.textContent = 'Thinking...'
//   loadingMsg.id = 'loading'
//   messages.appendChild(loadingMsg)

//   // Call backend
//   fetch(`${BACKEND_URL}/chat`, {
//     method: 'POST',
//     headers: { 'Content-Type': 'application/json' },
//     body: JSON.stringify({ question: text, role: role })
//   })
//   .then(res => res.json())
//   .then(data => {
//     document.getElementById('loading').remove()
//     const botMsg = document.createElement('div')
//     botMsg.classList.add('message', 'bot')
//     botMsg.innerHTML = formatResponse(data.answer || data.error)
//     messages.appendChild(botMsg)
//     messages.scrollTop = messages.scrollHeight
//   })
//   .catch(err => {
//     document.getElementById('loading').remove()
//     const botMsg = document.createElement('div')
//     botMsg.classList.add('message', 'bot')
//     botMsg.textContent = 'Error connecting to server. Please try again!'
//     messages.appendChild(botMsg)
//     messages.scrollTop = messages.scrollHeight
//   })
// }

// function handleKey(event) {
//   if (event.key === 'Enter') sendMessage()
// }

const BACKEND_URL = "http://127.0.0.1:8000"
let currentUserId = 0

window.onload = function() {
  currentUserId = parseInt(localStorage.getItem('user_id')) || 0
}

function formatResponse(text) {
  // Convert **bold** to <strong>
  text = text.replace(/\*\*(.*?)\*\*/g, '<strong style="color:#f97316;">$1</strong>')
  
  // Convert numbered list - each point on new line
  text = text.replace(/(\d+)\.\s+/g, '<br><br><span style="color:#f97316; font-weight:700;">$1.</span> ')
  
  // Convert bullet points
  text = text.replace(/[-•]\s+/g, '<br><span style="color:#f97316;">•</span> ')
  
  // Convert line breaks
  text = text.replace(/\n/g, '<br>')
  
  // Clean up extra breaks at start
  text = text.replace(/^(<br>)+/, '')
  
  return `<div style="line-height:1.8;">${text}</div>`
}

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
  loadingMsg.innerHTML = '⏳ <em style="color:#6b7280;">Searching rulebook...</em>'
  loadingMsg.id = 'loading'
  messages.appendChild(loadingMsg)
  messages.scrollTop = messages.scrollHeight

  // Call backend
  fetch(`${BACKEND_URL}/chat`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      question: text,
      role: role,
      user_id: currentUserId
    })
  })
  .then(res => res.json())
  .then(data => {
    document.getElementById('loading').remove()

    // Bot wrapper
    const botWrapper = document.createElement('div')
    botWrapper.style.cssText = `
      display: flex;
      flex-direction: column;
      align-items: flex-start;
      gap: 8px;
    `

    // Bot message
    const botMsg = document.createElement('div')
    botMsg.classList.add('message', 'bot')
    botMsg.innerHTML = formatResponse(data.answer || data.error)
    botWrapper.appendChild(botMsg)

    // Feedback buttons
    if (data.chat_id > 0) {
      const feedbackDiv = document.createElement('div')
      feedbackDiv.style.cssText = `
        display: flex;
        gap: 8px;
        padding-left: 4px;
      `
      feedbackDiv.innerHTML = `
        <button onclick="sendFeedback(${data.chat_id}, 'up', this)"
          style="background:rgba(52,211,153,0.1); border:1px solid rgba(52,211,153,0.3);
                 color:#34d399; padding:6px 14px; border-radius:8px;
                 cursor:pointer; font-size:13px; transition:all 0.2s;">
          👍 Helpful
        </button>
        <button onclick="sendFeedback(${data.chat_id}, 'down', this)"
          style="background:rgba(248,113,113,0.1); border:1px solid rgba(248,113,113,0.3);
                 color:#f87171; padding:6px 14px; border-radius:8px;
                 cursor:pointer; font-size:13px; transition:all 0.2s;">
          👎 Not Helpful
        </button>`
      botWrapper.appendChild(feedbackDiv)
    }

    messages.appendChild(botWrapper)
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

function sendFeedback(chatId, feedback, btn) {
  fetch(`${BACKEND_URL}/feedback`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ chat_id: chatId, feedback: feedback })
  })
  .then(() => {
    btn.parentElement.innerHTML = feedback === 'up'
      ? '<span style="color:#34d399; font-size:13px;">✅ Thanks for your feedback!</span>'
      : '<span style="color:#f87171; font-size:13px;">Thanks for your feedback!</span>'
  })
}

function handleKey(event) {
  if (event.key === 'Enter') sendMessage()
}
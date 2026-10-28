/**
 * BAJA RuleBot - Interactive Compliance Chat Client
 * Handles real-time messaging, role-based querying, JWT authentication, and structured rule formatting.
 */

const BACKEND_URL = window.BACKEND_URL || "http://127.0.0.1:8000";
let currentUserId = 0;
let currentRole = "Team Member";
let messageCount = 0;

window.addEventListener("DOMContentLoaded", () => {
  const userId = localStorage.getItem("user_id");
  const name = localStorage.getItem("userName") || "User";
  const role = localStorage.getItem("userRole") || "Team Member";
  const team = localStorage.getItem("teamName") || "BAJA Team";

  currentUserId = parseInt(userId) || 0;
  currentRole = role;

  const roleTag = document.getElementById("userRoleTag");
  const teamTag = document.getElementById("userTeamTag");
  const roleDisp = document.getElementById("roleDisplay");
  const ruleStatus = document.getElementById("rulebookStatus");

  if (roleTag) roleTag.textContent = `Role: ${role}`;
  if (teamTag) teamTag.textContent = `Team: ${team}`;
  if (roleDisp) roleDisp.textContent = role;
  if (ruleStatus) ruleStatus.textContent = "BAJA 2026 Rulebook — Ready";

  // Check for resumed conversation from history page
  const resumeQ = localStorage.getItem("resumeQuestion");
  const resumeA = localStorage.getItem("resumeAnswer");

  if (resumeQ && resumeA) {
    const chatHistory = document.getElementById("chatHistory");
    if (chatHistory) {
      const banner = document.createElement("div");
      banner.className = "flex justify-center mb-2";
      banner.innerHTML = `<span class="text-[10px] font-label-caps text-primary bg-engineering-blue-light px-4 py-1 rounded-full border border-primary/10">📂 Resumed from history</span>`;
      chatHistory.appendChild(banner);

      addUserMessage(resumeQ);
      addBotMessage(resumeA, 0);
    }

    localStorage.removeItem("resumeQuestion");
    localStorage.removeItem("resumeAnswer");
  }

  // Auto-grow textarea
  const tx = document.getElementById("chatInput");
  if (tx) {
    tx.addEventListener("input", function () {
      this.style.height = "40px";
      this.style.height = this.scrollHeight + "px";
    });
  }
});

function sendMessage() {
  const input = document.getElementById("chatInput");
  if (!input) return;
  const text = input.value.trim();
  if (!text) return;

  input.value = "";
  input.style.height = "40px";

  addUserMessage(text);
  showTyping();
  callBackend(text);
}

function quickAsk(question) {
  const input = document.getElementById("chatInput");
  if (input) {
    input.value = question;
    sendMessage();
  }
}

function addUserMessage(text) {
  messageCount++;
  const history = document.getElementById("chatHistory");
  if (!history) return;

  const now = new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });
  const div = document.createElement("div");
  div.className = "flex flex-col items-end gap-1 max-w-[80%] self-end msg-anim";
  div.innerHTML = `
    <div class="bg-primary text-white px-5 py-3 rounded-2xl rounded-tr-none shadow-sm">
      <p class="font-body-md">${escapeHtml(text)}</p>
    </div>
    <span class="text-[10px] font-label-caps text-on-surface-variant px-2">${now}</span>`;
  history.appendChild(div);
  scrollToBottom();
}

function showTyping() {
  const history = document.getElementById("chatHistory");
  if (!history) return;

  const div = document.createElement("div");
  div.id = "typingIndicator";
  div.className = "flex flex-col items-start gap-1 max-w-[85%] self-start msg-anim";
  div.innerHTML = `
    <div class="flex gap-3">
      <div class="w-8 h-8 rounded-lg bg-cad-gray flex items-center justify-center flex-shrink-0 border border-metallic-slate/10">
        <span class="material-symbols-outlined text-primary scale-75">smart_toy</span>
      </div>
      <div class="bg-white px-5 py-4 rounded-2xl rounded-tl-none border border-metallic-slate/10 shadow-sm flex items-center gap-1.5">
        <span class="typing-dot w-2 h-2 bg-primary/40 rounded-full inline-block"></span>
        <span class="typing-dot w-2 h-2 bg-primary/40 rounded-full inline-block"></span>
        <span class="typing-dot w-2 h-2 bg-primary/40 rounded-full inline-block"></span>
      </div>
    </div>`;
  history.appendChild(div);
  scrollToBottom();
}

function addBotMessage(text, chatId) {
  const typing = document.getElementById("typingIndicator");
  if (typing) typing.remove();

  const history = document.getElementById("chatHistory");
  if (!history) return;

  const now = new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });
  const div = document.createElement("div");
  div.className = "flex flex-col items-start gap-1 max-w-[85%] self-start msg-anim";

  const feedbackHtml =
    chatId > 0
      ? `
    <div class="flex items-center border-l border-metallic-slate/10 pl-2 ml-1 gap-1" id="fb-${chatId}">
      <button onclick="sendFeedback(${chatId},'up',this)" class="p-1 hover:text-primary transition-colors" title="Helpful">
        <span class="material-symbols-outlined text-sm text-on-surface-variant">thumb_up</span>
      </button>
      <button onclick="sendFeedback(${chatId},'down',this)" class="p-1 hover:text-error transition-colors" title="Not Helpful">
        <span class="material-symbols-outlined text-sm text-on-surface-variant">thumb_down</span>
      </button>
    </div>`
      : "";

  div.innerHTML = `
    <div class="flex gap-3">
      <div class="w-8 h-8 rounded-lg bg-cad-gray flex items-center justify-center flex-shrink-0 border border-metallic-slate/10">
        <span class="material-symbols-outlined text-primary scale-75">smart_toy</span>
      </div>
      <div class="flex flex-col gap-3">
        <div class="bg-white text-on-background px-5 py-4 rounded-2xl rounded-tl-none border border-metallic-slate/10 shadow-sm">
          <div class="font-body-md leading-relaxed">${formatAnswer(text)}</div>
        </div>
        <div class="flex gap-2 flex-wrap">
          ${feedbackHtml}
        </div>
      </div>
    </div>
    <span class="text-[10px] font-label-caps text-on-surface-variant px-12">${now}</span>`;
  history.appendChild(div);
  scrollToBottom();
}

function callBackend(question) {
  const headers = window.getAuthHeaders
    ? window.getAuthHeaders({ "Content-Type": "application/json" })
    : { "Content-Type": "application/json" };

  fetch(`${BACKEND_URL}/chat`, {
    method: "POST",
    headers: headers,
    body: JSON.stringify({ question, role: currentRole, user_id: currentUserId }),
  })
    .then((r) => r.json())
    .then((data) => {
      addBotMessage(data.answer || data.error, data.chat_id || 0);
    })
    .catch(() => {
      addBotMessage("⚠️ Error connecting to server. Please check if backend is running.", 0);
    });
}

function sendFeedback(chatId, feedback, btn) {
  const headers = window.getAuthHeaders
    ? window.getAuthHeaders({ "Content-Type": "application/json" })
    : { "Content-Type": "application/json" };

  fetch(`${BACKEND_URL}/feedback`, {
    method: "POST",
    headers: headers,
    body: JSON.stringify({ chat_id: chatId, feedback }),
  }).then(() => {
    const fbDiv = document.getElementById(`fb-${chatId}`);
    if (fbDiv) {
      fbDiv.innerHTML =
        feedback === "up"
          ? '<span class="text-[11px] font-label-caps text-green-600 px-2 font-bold">👍 Helpful</span>'
          : '<span class="text-[11px] font-label-caps text-red-500 px-2 font-bold">Thanks for feedback</span>';
    }
  });
}

function formatAnswer(text) {
  if (!text) return "";

  // Fix rule section spacing e.g. B.10. 3 -> B.10.3
  text = text.replace(/([A-Z]\.\d+)\.\s+(\d)/g, "$1.$2");
  text = text.replace(/\n(\d+)\.\n/g, "\n");

  const lines = text.split("\n");
  let html = "";
  let inList = false;

  lines.forEach((line) => {
    line = line.trim();
    if (!line) {
      if (inList) {
        html += "</div>";
        inList = false;
      }
      return;
    }

    // ## Heading (Topic Title)
    if (line.startsWith("## ")) {
      const title = line.replace("## ", "");
      html += `<div style="font-size:18px; font-weight:800; color:#004183; margin-bottom:16px; padding-bottom:8px; border-bottom:2px solid #e5eeff;">${title}</div>`;
      return;
    }

    // ### Sub Heading
    if (line.startsWith("### ")) {
      const title = line.replace("### ", "");
      html += `<div style="font-size:14px; font-weight:700; color:#004183; margin:16px 0 8px 0; text-transform:uppercase; letter-spacing:0.05em;">${title}</div>`;
      return;
    }

    // Numbered points with **Title** `Rule`
    const pointMatch = line.match(/^\*\*(\d+)\.\s+(.*?)\*\*\s*`?(Rule\s+[\w.]+)?`?(.*)/);
    if (pointMatch) {
      if (inList) {
        html += "</div>";
        inList = false;
      }
      const num = pointMatch[1];
      const title = pointMatch[2];
      const rule = pointMatch[3] || "";
      const rest = pointMatch[4] || "";
      html += `
        <div style="background:#f8fafc; border:1px solid #e2e8f0; border-left:4px solid #004183; border-radius:0 10px 10px 0; padding:14px 16px; margin-bottom:12px;">
          <div style="display:flex; align-items:center; gap:10px; margin-bottom:6px;">
            <span style="background:#004183; color:white; width:24px; height:24px; border-radius:50%; display:flex; align-items:center; justify-content:center; font-size:12px; font-weight:700; flex-shrink:0;">${num}</span>
            <span style="font-weight:700; color:#0f172a; font-size:14px;">${title}</span>
            ${rule ? `<span style="background:#eff4ff; color:#004183; font-size:11px; font-weight:600; padding:2px 8px; border-radius:4px; border:1px solid #c7d7fe; font-family:monospace;">${rule}</span>` : ""}
          </div>
          ${rest ? `<p style="color:#475569; font-size:14px; line-height:1.7; margin:0; padding-left:34px;">${rest}</p>` : ""}
        </div>`;
      return;
    }

    // Bullet points (- or *)
    if (line.startsWith("- ") || line.startsWith("* ")) {
      const content = line.replace(/^[-*]\s+/, "");
      const formatted = content.replace(/\*\*(.*?)\*\*/g, '<strong style="color:#004183;">$1</strong>');
      html += `
        <div style="display:flex; gap:8px; margin-bottom:6px; padding-left:8px; align-items:flex-start;">
          <span style="color:#004183; margin-top:2px; flex-shrink:0;">•</span>
          <span style="color:#475569; font-size:14px; line-height:1.7;">${formatted}</span>
        </div>`;
      return;
    }

    // Reference citation line
    if (line.includes("📌") || line.startsWith("Reference:")) {
      const formatted = line.replace(/\*\*(.*?)\*\*/g, "<strong>$1</strong>");
      html += `<div style="margin-top:16px; padding:10px 16px; background:#eff4ff; border:1px solid #c7d7fe; border-radius:8px; color:#004183; font-size:13px; font-weight:600; display:flex; align-items:center; gap:8px;">${formatted}</div>`;
      return;
    }

    // Horizontal rule
    if (line === "---") {
      html += `<hr style="border:none; border-top:1px solid #e2e8f0; margin:16px 0;">`;
      return;
    }

    // Regular paragraph
    if (line.length > 0) {
      const formatted = line
        .replace(/\*\*(.*?)\*\*/g, '<strong style="color:#004183;">$1</strong>')
        .replace(/`(.*?)`/g, '<code style="background:#f1f5f9; color:#004183; padding:1px 6px; border-radius:4px; font-family:monospace; font-size:13px;">$1</code>');
      html += `<p style="color:#374151; font-size:14px; line-height:1.8; margin-bottom:10px;">${formatted}</p>`;
    }
  });

  return `<div style="font-family:'Inter',sans-serif; padding:4px 0;">${html}</div>`;
}

function escapeHtml(text) {
  return String(text).replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
}

function scrollToBottom() {
  const chat = document.getElementById("chatHistory");
  if (chat) chat.scrollTop = chat.scrollHeight;
}

function handleKey(e) {
  if (e.key === "Enter" && !e.shiftKey) {
    e.preventDefault();
    sendMessage();
  }
}

function clearChat() {
  const chat = document.getElementById("chatHistory");
  if (!chat) return;
  chat.innerHTML = `
    <div class="flex justify-center mb-4">
      <span class="text-[10px] font-label-caps text-on-surface-variant bg-cad-gray px-4 py-1 rounded-full border border-metallic-slate/5">New session started</span>
    </div>
    <div class="flex flex-col items-start gap-1 max-w-[85%] self-start msg-anim">
      <div class="flex gap-3">
        <div class="w-8 h-8 rounded-lg bg-cad-gray flex items-center justify-center flex-shrink-0 border border-metallic-slate/10">
          <span class="material-symbols-outlined text-primary scale-75">smart_toy</span>
        </div>
        <div class="bg-white text-on-background px-5 py-4 rounded-2xl rounded-tl-none border border-metallic-slate/10 shadow-sm">
          <p class="font-body-md leading-relaxed">New session started! Ask me anything about the BAJA rulebook.</p>
        </div>
      </div>
    </div>`;
}

function exportChat() {
  const chat = document.getElementById("chatHistory");
  if (!chat) return;
  const messages = chat.innerText;
  const blob = new Blob([messages], { type: "text/plain" });
  const a = document.createElement("a");
  a.href = URL.createObjectURL(blob);
  a.download = "baja-chat-log.txt";
  a.click();
}

function logout() {
  localStorage.clear();
  window.location.href = "login.html";
}

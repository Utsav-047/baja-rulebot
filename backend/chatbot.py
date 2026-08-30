import os
import requests
from dotenv import load_dotenv
from database import search_chunks

load_dotenv()

API_KEY = os.getenv("API_KEY")


def get_answer(question: str, rulebook_text: str, role: str) -> str:
    """
    Generate an AI compliance answer tailored to the user's role using RAG context.
    """
    question_clean = question.lower().strip()

    # ----------------------------
    # Greeting / small talk filter
    # ----------------------------
    greetings = {
        "hi", "hii", "hello", "hey",
        "good morning", "good evening", "good afternoon"
    }

    small_talk = {
        "thanks": "You're welcome! Ask me anything about BAJA rules 🚗",
        "thank you": "You're welcome! Ask me anything about BAJA rules 🚗",
        "bye": "Goodbye! Best of luck with BAJA 🚗"
    }

    if question_clean in greetings:
        return (
            "Hi! I'm BAJA RuleBot 👋\n"
            "Ask me anything about BAJA SAEINDIA rules, vehicle design, "
            "compliance, or technical requirements."
        )

    if question_clean in small_talk:
        return small_talk[question_clean]

    # ----------------------------
    # Retrieve relevant chunks via Vector / Keyword Search
    # ----------------------------
    relevant_chunks = search_chunks(question)

    if relevant_chunks:
        context = "\n\n".join(relevant_chunks)
    elif rulebook_text:
        context = rulebook_text[:10000]
    else:
        return (
            "I couldn't find relevant information in the uploaded rulebook.\n"
            "Please ask a more specific BAJA-related question or upload the rulebook PDF."
        )

    snippets = "\n\n---\n📄 **Referenced Rulebook Sections:**\n" + "\n\n".join(
        f"[{i+1}] {chunk[:250].strip()}..." for i, chunk in enumerate(relevant_chunks)
    ) if relevant_chunks else ""

    # ----------------------------
    # Role-based instructions
    # ----------------------------
    role_instructions = {
        "Team Captain": """
- Focus on overall compliance, team coordination and competition readiness
- Highlight deadlines, submission requirements and team responsibilities
- Mention penalties for non-compliance
- Give leadership-oriented actionable points
""",
        "Faculty Advisor": """
- Focus on academic compliance, student eligibility and institutional requirements
- Highlight documentation, approval processes and faculty responsibilities
- Mention college-level submissions and verifications required
- Give guidance-oriented professional points
""",
        "Finance Manager": """
- Focus on billing requirements, invoice documentation and cost report
- Highlight original tax invoices, GST requirements and financial submissions
- Mention approved vendor lists and purchase documentation
- Give finance-oriented professional points
""",
        "Department Manager": """
- Focus on department-level approvals, resource allocation and oversight
- Highlight interdepartmental coordination and management responsibilities
- Give management-oriented professional points
""",
        "Team Member": """
- Focus on technical requirements, safety rules and vehicle specifications
- Highlight measurements, materials and construction standards
- Mention inspection checklist items
- Give practical technical guidance
"""
    }

    role_guide = role_instructions.get(role, role_instructions["Team Member"])

    # ----------------------------
    # Prompt Construction
    # ----------------------------
    prompt = f"""
You are BAJA RuleBot, a strict technical AI assistant for BAJA SAEINDIA.

IMPORTANT RULES:
1. Answer ONLY using retrieved rulebook context.
2. Never use outside knowledge or hallucinate rules.
3. Never invent rule numbers.
4. Only cite rule numbers explicitly present in context.
5. If context is insufficient, say: "This requirement was not found in the uploaded rulebook."
6. Only include requirements relevant to the question.
7. Do NOT include unrelated vehicle systems.

The user role is: {role}

Role-specific guidance:
{role_guide}

Context:
{context}

Question:
{question}

Output Format:

## [Topic Title]

### Overview
[2-3 sentences providing high level summary for {role}]

### Detailed Requirements
1. **[Requirement Title]** `(Rule X.X.X)`
[Explanation]

2. **[Requirement Title]** `(Rule X.X.X)`
[Explanation]

### Key Notes for {role}
- Point 1
- Point 2
- Point 3

Reference:
BAJA SAEINDIA Rulebook 2026
"""

    api_key = os.getenv("API_KEY") or API_KEY
    if not api_key:
        return (
            "⚠️ **API Key Missing**: The Groq API key is not configured. "
            "Please add `API_KEY=gsk_...` to your `.env` file to enable AI answers."
        )

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    data = {
        "model": "llama-3.3-70b-versatile",
        "messages": [
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.2
    }

    try:
        response = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers=headers,
            json=data,
            timeout=30
        )

        result = response.json()
        if "choices" in result:
            return result["choices"][0]["message"]["content"] + snippets
        else:
            print("Groq API error response:", result)
            error_msg = result.get("error", {}).get("message", "AI service error.")
            return f"⚠️ **AI Service Error:** {error_msg}. Please verify your API key and quota."

    except Exception as e:
        print("Chatbot query exception:", str(e))
        return f"⚠️ **Error connecting to AI service:** {str(e)}"


def get_checklist_items(category: str, rulebook_text: str, role: str) -> str:
    """
    Generate numbered checklist items for technical inspection or event readiness.
    """
    relevant_chunks = search_chunks(category)

    if relevant_chunks:
        context = "\n\n".join(relevant_chunks)
    elif rulebook_text:
        context = rulebook_text[:10000]
    else:
        return "1. No specific requirements found in uploaded rulebook."

    prompt = f"""
You are BAJA RuleBot.

Generate a technical compliance checklist for category: "{category}".
User Role: {role}

Context:
{context}

STRICT RULES:
- Output ONLY a numbered list (1. 2. 3. ...)
- 8 to 15 concise actionable points
- One item per line
- No markdown headings or conversational intros/outros
- Include rule references where available
"""

    api_key = os.getenv("API_KEY") or API_KEY
    if not api_key:
        return "1. API_KEY is missing in backend configuration."

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    data = {
        "model": "llama-3.3-70b-versatile",
        "messages": [
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.2
    }

    try:
        response = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers=headers,
            json=data,
            timeout=30
        )

        result = response.json()
        if "choices" in result:
            return result["choices"][0]["message"]["content"]
        else:
            return "1. AI service error generating checklist. Please try again."

    except Exception as e:
        return f"1. Error generating checklist: {str(e)}"

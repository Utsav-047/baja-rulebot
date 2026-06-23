

# import requests
# import os
# from dotenv import load_dotenv
# from database import search_chunks

# load_dotenv()

# API_KEY = os.getenv("API_KEY")

# def get_answer(question, rulebook_text, role):

#     question_clean = question.lower().strip()

# greetings = {
#     "hi", "hii", "hello", "hey",
#     "good morning", "good evening", "good afternoon"
# }

# small_talk = {
#     "thanks": "You're welcome! Ask me anything about BAJA rules 🚗",
#     "thank you": "You're welcome! Ask me anything about BAJA rules 🚗",
#     "bye": "Goodbye! Best of luck with BAJA 🚗"
# }

# if question_clean in greetings:
#     return "Hi! I'm BAJA RuleBot 👋 Ask me anything about BAJA SAEINDIA rules, vehicle design, compliance, or technical requirements."

# if question_clean in small_talk:
#     return small_talk[question_clean]

#     # Get relevant chunks from MySQL
#     relevant_chunks = search_chunks(question)

#     if relevant_chunks:
#         context = '\n\n'.join(relevant_chunks)
#     else:
#         context = rulebook_text[:10000]

#     role_instructions = {
#         "Team Captain": """
# - Focus on overall compliance, team coordination and competition readiness
# - Highlight deadlines, submission requirements and team responsibilities
# - Mention penalties for non-compliance
# - Give leadership-oriented actionable points
# """,
#         "Faculty Advisor": """
# - Focus on academic compliance, student eligibility and institutional requirements
# - Highlight documentation, approval processes and faculty responsibilities
# - Mention college-level submissions and verifications required
# - Give guidance-oriented professional points
# """,
#         "Finance Manager": """
# - Focus on billing requirements, invoice documentation and cost report
# - Highlight original tax invoices, GST requirements and financial submissions
# - Mention approved vendor lists and purchase documentation
# - Give finance and documentation oriented points
# """,
#         "Department Manager": """
# - Focus on department-level approvals, resource allocation and oversight
# - Highlight interdepartmental coordination and management requirements
# - Mention approval workflows and departmental responsibilities
# - Give management and coordination oriented points
# """,
#         "Team Member": """
# - Focus on technical requirements, safety rules and vehicle specifications
# - Highlight specific measurements, materials and construction standards
# - Mention inspection checklist items and technical compliance points
# - Give clear technical and practical points
# """
#     }

#     # Get role instruction or default to Team Member
#     role_guide = role_instructions.get(role, role_instructions["Team Member"])

#     prompt = f"""
# You are BAJA RuleBot, a professional AI technical assistant specialized in
# BAJA SAEINDIA vehicle competition rules and regulations.

# The user is a {role}. Tailor your answer specifically for their role:
# {role_guide}

# RELEVANT RULEBOOK SECTIONS:
# {context}

# QUESTION: {question}

# Provide a comprehensive professional answer in this EXACT format:

# ## [Answer Topic Title]

# ### Overview
# [Write 2-3 sentences giving a clear overview relevant to {role}]

# ### Detailed Requirements

# **1. [Requirement Title]** `Rule [X.X.X]`
# [Write 2-3 sentences explaining this requirement specifically for {role}]

# **2. [Requirement Title]** `Rule [X.X.X]`
# [Write 2-3 sentences explaining this requirement specifically for {role}]

# **3. [Requirement Title]** `Rule [X.X.X]`
# [Write 2-3 sentences explaining this requirement specifically for {role}]

# [Continue maximum 8 points]

# ### Key Notes for {role}
# - [Important note specific to {role}]
# - [Important note specific to {role}]
# - [Important note specific to {role}]

# ---
# 📌 **Reference:** BAJA SAEINDIA Rulebook 2026 | Section [X]

# STRICT RULES:
# - Write rule sections WITHOUT spaces e.g. B.9.1 not B.9. 1
# - Give detailed explanations tailored to {role}
# - Include measurements and specifications when available
# - If not found say: "This requirement was not found in the uploaded rulebook."
# - Be professional and precise
# """

#     headers = {
#         "Authorization": f"Bearer {API_KEY}",
#         "Content-Type": "application/json"
#     }

#     data = {
#         "model": "llama-3.3-70b-versatile",
#         "messages": [
#             {"role": "user", "content": prompt}
#         ]
#     }

#     try:
#         response = requests.post(
#             "https://api.groq.com/openai/v1/chat/completions",
#             headers=headers,
#             json=data,
#             timeout=30
#         )
#         result = response.json()
#         print("Groq response received")
#         if "choices" in result:
#             return result["choices"][0]["message"]["content"]
#         else:
#             print("Full error:", result)
#             return "Sorry! AI service error. Please try again."
#     except Exception as e:
#         print("Error:", str(e))
#         return f"Error getting answer: {str(e)}"


# def get_checklist_items(category, rulebook_text, role):
#     """
#     Generates a clean, flat list of checklist items for the given category.
#     Unlike get_answer(), this returns ONLY a numbered list with no markdown
#     headers, overview sections, or notes — suitable for rendering as
#     individual checkbox items.
#     """

#     relevant_chunks = search_chunks(category)
#     if relevant_chunks:
#         context = '\n\n'.join(relevant_chunks)
#     else:
#         context = rulebook_text[:10000]

#     prompt = f"""
# You are BAJA RuleBot, generating a compliance checklist for BAJA SAEINDIA
# vehicle competition rules.

# The user is a {role}.

# RELEVANT RULEBOOK SECTIONS:
# {context}

# Generate a checklist of specific, actionable items for the category: "{category}".

# STRICT OUTPUT RULES — FOLLOW EXACTLY:
# - Output ONLY a numbered list (1. 2. 3. ...), one item per line.
# - Each item must be ONE short, specific, actionable checklist point (max 1-2 sentences).
# - Include the rulebook section number in parentheses where available, e.g. (Rule B.9.1).
# - Generate between 8 and 15 items.
# - DO NOT include any markdown symbols such as ##, ###, **, ---, or 📌.
# - DO NOT include any headings, titles, introductions, overview paragraphs, or notes/reference sections.
# - DO NOT write anything before item 1 or after the last item.
# - If no relevant information is found, output exactly one line: "1. No specific requirements found in the uploaded rulebook for this category."
# """

#     headers = {
#         "Authorization": f"Bearer {API_KEY}",
#         "Content-Type": "application/json"
#     }

#     data = {
#         "model": "llama-3.3-70b-versatile",
#         "messages": [
#             {"role": "user", "content": prompt}
#         ]
#     }

#     try:
#         response = requests.post(
#             "https://api.groq.com/openai/v1/chat/completions",
#             headers=headers,
#             json=data,
#             timeout=30
#         )
#         result = response.json()
#         print("Groq checklist response received")
#         if "choices" in result:
#             return result["choices"][0]["message"]["content"]
#         else:
#             print("Full error:", result)
#             return "1. AI service error. Please try again."
#     except Exception as e:
#         print("Error:", str(e))
#         return f"1. Error generating checklist: {str(e)}"





import requests
import os
from dotenv import load_dotenv
from database import search_chunks

load_dotenv()

API_KEY = os.getenv("API_KEY")


def get_answer(question, rulebook_text, role):
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
    # Retrieve relevant chunks
    # ----------------------------
    relevant_chunks = search_chunks(question)

    if relevant_chunks:
        context = "\n\n".join(relevant_chunks)
    else:
        return (
            "I couldn't find relevant information in the uploaded rulebook.\n"
            "Please ask a more specific BAJA-related question."
        )

    snippets = "\n\n---\n📄 Referenced Rulebook Sections:\n" + "\n\n".join(
        f"[{i+1}] {chunk[:300].strip()}..." for i, chunk in enumerate(relevant_chunks)
    )

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
    # Prompt
    # ----------------------------
    prompt = f"""
You are BAJA RuleBot, a strict technical AI assistant for BAJA SAEINDIA.

IMPORTANT RULES:
1. Answer ONLY using retrieved rulebook context.
2. Never use outside knowledge.
3. Never invent rule numbers.
4. Only cite rule numbers explicitly present in context.
5. If context is insufficient, say:
   "This requirement was not found in the uploaded rulebook."
6. Only include requirements relevant to the question.
7. Do NOT include unrelated vehicle systems.
IMPORTANT:
- NEVER create a requirement unless the exact requirement exists in context.
- NEVER infer rule numbers.
- If rule number is missing, write: Rule reference unavailable.
- Do not guess.


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
2-3 sentences.

### Detailed Requirements
1. Requirement Title (Rule X.X.X)
Explanation

2. Requirement Title (Rule X.X.X)
Explanation

### Key Notes for {role}
- Point 1
- Point 2
- Point 3

Reference:
BAJA SAEINDIA Rulebook 2026
"""

    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }

    data = {
        "model": "llama-3.3-70b-versatile",
        "messages": [
            {"role": "user", "content": prompt}
        ]
    }

    try:
        response = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers=headers,
            json=data,
            timeout=30
        )

        result = response.json()
        print("Groq response received")

        if "choices" in result:
            return result["choices"][0]["message"]["content"] + snippets
        else:
            print(result)
            return "Sorry! AI service error. Please try again."

    except Exception as e:
        print("Error:", str(e))
        return f"Error getting answer: {str(e)}"


def get_checklist_items(category, rulebook_text, role):
    relevant_chunks = search_chunks(category)

    if relevant_chunks:
        context = "\n\n".join(relevant_chunks)
    else:
        return "1. No specific requirements found in uploaded rulebook."

    prompt = f"""
You are BAJA RuleBot.

Generate checklist for category: {category}

Context:
{context}

STRICT RULES:
- Output ONLY numbered list
- 8 to 15 points
- One item per line
- No headings
- Include rule references where available
"""

    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }

    data = {
        "model": "llama-3.3-70b-versatile",
        "messages": [
            {"role": "user", "content": prompt}
        ]
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
            return "1. AI service error."

    except Exception as e:
        return f"1. Error generating checklist: {str(e)}"


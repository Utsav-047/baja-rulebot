import requests
import os
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("API_KEY")

def find_relevant_text(question, full_text):
    # Split text into chunks
    chunks = full_text.split('\n')
    
    # Find chunks that contain keywords from question
    question_words = question.lower().split()
    relevant = []
    
    for chunk in chunks:
        chunk_lower = chunk.lower()
        score = sum(1 for word in question_words if word in chunk_lower)
        if score > 0:
            relevant.append((score, chunk))
    
    # Sort by relevance score
    relevant.sort(reverse=True)
    
    # Return top relevant chunks
    top_chunks = [chunk for score, chunk in relevant[:50]]
    return '\n'.join(top_chunks)

def get_answer(question, rulebook_text, role):

    # Get relevant sections only
    relevant_text = find_relevant_text(question, rulebook_text)
    
    if not relevant_text:
        relevant_text = rulebook_text[:10000]

    prompt = f"""
You are BAJA RuleBot, an AI assistant for BAJA SAEINDIA competition rules.
The user is a {role}.

Here are the relevant rulebook sections:
{relevant_text[:12000]}

Answer this question clearly and specifically:
{question}

Give specific answer with rule section number if possible.
If not found say "This information is not found in the uploaded rulebook."
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
        print("Groq response:", result)
        return result["choices"][0]["message"]["content"]
    except Exception as e:
        print("Error:", str(e))
        return f"Error getting answer: {str(e)}"
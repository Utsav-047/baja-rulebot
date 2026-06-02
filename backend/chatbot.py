# import requests
# import os
# from dotenv import load_dotenv
# from database import search_chunks

# load_dotenv()

# API_KEY = os.getenv("API_KEY")

# def get_answer(question, rulebook_text, role):

#     # Get relevant chunks from MySQL
#     relevant_chunks = search_chunks(question)
    
#     if relevant_chunks:
#         context = '\n\n'.join(relevant_chunks)
#     else:
#         context = rulebook_text[:10000]

#     prompt = f"""
# You are BAJA RuleBot, an AI assistant for BAJA SAEINDIA competition rules.
# The user is a {role}.

# Here are the most relevant rulebook sections for this question:
# {context}

# Answer this question clearly and specifically:
# {question}

# Give specific answer with rule section number if possible.
# If not found say "This information is not found in the uploaded rulebook."
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
#         print("Groq response:", result)
#         return result["choices"][0]["message"]["content"]
#     except Exception as e:
#         print("Error:", str(e))
#         return f"Error getting answer: {str(e)}"



import requests
import os
from dotenv import load_dotenv
from database import search_chunks

load_dotenv()

API_KEY = os.getenv("API_KEY")

def get_answer(question, rulebook_text, role):

    # Get relevant chunks from MySQL
    relevant_chunks = search_chunks(question)
    
    if relevant_chunks:
        context = '\n\n'.join(relevant_chunks)
    else:
        context = rulebook_text[:10000]

    prompt = f"""
You are BAJA RuleBot, an AI assistant for BAJA SAEINDIA competition rules.
The user is a {role}.

Here are the most relevant rulebook sections for this question:
{context}

Answer this question in the following format STRICTLY:

1. **Point Title**: Explanation with rule section (e.g. B.3.4)
2. **Point Title**: Explanation with rule section
3. **Point Title**: Explanation with rule section

Rules for answering:
- ALWAYS use numbered points
- ALWAYS bold the point title using **title**
- ALWAYS mention rule section number if available
- Maximum 8 points per answer
- Keep each point clear and concise
- If not found say "This information is not found in the uploaded rulebook."

Question: {question}
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
        if "choices" in result:
            return result["choices"][0]["message"]["content"]
        else:
            print("Full error:", result)
            return "Sorry! AI service error. Please try again."
    except Exception as e:
        print("Error:", str(e))
        return f"Error getting answer: {str(e)}"
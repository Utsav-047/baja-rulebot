from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from pdf_reader import extract_text_from_pdf
from chatbot import get_answer
from database import (save_feedback, get_chat_history,
                      register_user, login_user, get_all_users, get_all_chats,
                      save_rulebook_record, get_global_rulebook, get_user_rulebook,
                      save_chunks)
from pydantic import BaseModel
import os
import shutil

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

os.makedirs("uploads", exist_ok=True)
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

rulebook_text = ""
rulebook_filename = ""

class ChatRequest(BaseModel):
    question: str
    role: str
    user_id: int = 0

class FeedbackRequest(BaseModel):
    chat_id: int
    feedback: str

class RegisterRequest(BaseModel):
    name: str
    email: str
    password: str
    role: str
    team: str

class LoginRequest(BaseModel):
    email: str
    password: str

@app.on_event("startup")
async def auto_load_rulebook():
    global rulebook_text, rulebook_filename
    print("Checking for saved rulebook on startup...")
    try:
        result = get_global_rulebook()
        if result:
            filename, filepath = result
            if os.path.exists(filepath):
                with open(filepath, "rb") as f:
                    rulebook_text = extract_text_from_pdf(f)
                # Save chunks to MySQL
                words = rulebook_text.split()
                chunks = []
                for i in range(0, len(words), 500):
                    chunk = ' '.join(words[i:i+500])
                    chunks.append(chunk)
                save_chunks(chunks)
                rulebook_filename = filename
                print(f"✅ Auto-loaded: {filename} | Words: {len(rulebook_text.split())}")
            else:
                print("⚠️ File not found on disk")
        else:
            print("ℹ️ No global rulebook in database yet")
    except Exception as e:
        print(f"Startup error: {e}")

@app.get("/health")
def health():
    return {
        "status": "BAJA RuleBot Backend Running!",
        "rulebook_loaded": bool(rulebook_text),
        "rulebook_name": rulebook_filename
    }

@app.post("/register")
def register(request: RegisterRequest):
    user_id = register_user(
        request.name, request.email,
        request.password, request.role, request.team
    )
    if user_id:
        return {"message": "Registration successful!", "user_id": user_id}
    return JSONResponse(status_code=400, content={"error": "Email already exists!"})

@app.post("/login")
def login(request: LoginRequest):
    user = login_user(request.email, request.password)
    if user:
        return {
            "message": "Login successful!",
            "user_id": user[0], "name": user[1],
            "role": user[2], "team": user[3], "is_admin": user[4]
        }
    return JSONResponse(status_code=401, content={"error": "Invalid email or password!"})

@app.get("/rulebook/status")
def rulebook_status():
    global rulebook_text, rulebook_filename
    try:
        result = get_global_rulebook()
        if result:
            filename, filepath = result
            if not rulebook_text and os.path.exists(filepath):
                with open(filepath, "rb") as f:
                    rulebook_text = extract_text_from_pdf(f)
                rulebook_filename = filename
            return {
                "filename": filename,
                "is_global": True,
                "loaded": True
            }
    except Exception as e:
        print(f"Status error: {e}")

    if rulebook_text:
        return {"filename": rulebook_filename, "is_global": False, "loaded": True}

    return {"filename": None, "loaded": False}

@app.post("/upload")
async def upload_rulebook(
    file: UploadFile = File(...),
    user_id: int = Form(0),
    is_global: int = Form(0)
):
    global rulebook_text, rulebook_filename

    content = await file.read()

    # Clean filename
    safe_filename = file.filename.replace(" ", "_").replace("(", "").replace(")", "")
    if is_global:
        safe_filename = "global_" + safe_filename
    filepath = os.path.join("uploads", safe_filename)

    # Save to disk
    with open(filepath, "wb") as f:
        f.write(content)
    print(f"✅ Saved: {filepath}")

    # Extract text
    import io
    from pdfplumber import open as pdf_open
    text = ""
    with pdf_open(io.BytesIO(content)) as pdf:
        for page in pdf.pages:
            extracted = page.extract_text()
            if extracted and extracted.strip():
                text += extracted + "\n"

    rulebook_text = text
    rulebook_filename = safe_filename
    word_count = len(text.split())
    print(f"✅ Extracted {word_count} words")

    # Save chunks to MySQL
    words = text.split()
    chunks = []
    for i in range(0, len(words), 500):
        chunk = ' '.join(words[i:i+500])
        chunks.append(chunk)
    save_chunks(chunks)
    print(f"✅ Saved {len(chunks)} chunks to MySQL")

    # Save record
    save_rulebook_record(user_id, safe_filename, filepath, is_global)

    return {
        "message": "Rulebook uploaded successfully!",
        "words_extracted": word_count,
        "chunks_created": len(chunks),
        "filename": safe_filename,
        "is_global": is_global
    }

@app.post("/chat")
async def chat(request: ChatRequest):
    global rulebook_text

    if not rulebook_text:
        try:
            result = get_global_rulebook()
            if result:
                filename, filepath = result
                if os.path.exists(filepath):
                    with open(filepath, "rb") as f:
                        rulebook_text = extract_text_from_pdf(f)
        except Exception as e:
            print(f"Auto-load error: {e}")

    if not rulebook_text:
        return JSONResponse(
            status_code=400,
            content={"error": "Please upload a rulebook first!"}
        )

    answer = get_answer(request.question, rulebook_text, request.role)

    chat_id = 0
    if request.user_id > 0:
        from database import get_connection
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO chat_history (user_id, question, answer) VALUES (%s, %s, %s)",
            (request.user_id, request.question, answer)
        )
        conn.commit()
        chat_id = cursor.lastrowid
        cursor.close()
        conn.close()

    return {"answer": answer, "chat_id": chat_id}

@app.post("/feedback")
def feedback(request: FeedbackRequest):
    save_feedback(request.chat_id, request.feedback)
    return {"message": "Feedback saved!"}

@app.get("/history/{user_id}")
def history(user_id: int):
    chats = get_chat_history(user_id)
    return [
        {"id": c[0], "question": c[1], "answer": c[2],
         "feedback": c[3], "created_at": str(c[4])}
        for c in chats
    ]

@app.get("/admin/users")
def admin_users():
    users = get_all_users()
    return [
        {"id": u[0], "name": u[1], "email": u[2],
         "role": u[3], "team": u[4], "created_at": str(u[5])}
        for u in users
    ]

@app.get("/admin/chats")
def admin_chats():
    chats = get_all_chats()
    return [
        {"id": c[0], "user_name": c[1], "question": c[2],
         "answer": c[3], "feedback": c[4], "created_at": str(c[5])}
        for c in chats
    ]

@app.get("/global-rulebook")
def get_global():
    result = get_global_rulebook()
    if result:
        return {"filename": result[0], "filepath": result[1], "available": True}
    return {"available": False}

@app.get("/my-rulebook/{user_id}")
def get_my_rulebook(user_id: int):
    result = get_user_rulebook(user_id)
    if result:
        return {"filename": result[0], "filepath": result[1], "available": True}
    return {"available": False}
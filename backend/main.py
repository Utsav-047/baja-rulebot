 
from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pdf_reader import extract_text_from_pdf
from chatbot import get_answer
from pydantic import BaseModel

app = FastAPI()

# Allow frontend to talk to backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Store rulebook text in memory
rulebook_text = ""

class ChatRequest(BaseModel):
    question: str
    role: str

@app.get("/health")
def health():
    return {"status": "BAJA RuleBot Backend Running!"}

@app.post("/upload")
async def upload_rulebook(file: UploadFile = File(...)):
    global rulebook_text
    rulebook_text = extract_text_from_pdf(file.file)
    word_count = len(rulebook_text.split())
    return {"message": "Rulebook uploaded successfully!", "words_extracted": word_count}

@app.post("/chat")
async def chat(request: ChatRequest):
    global rulebook_text
    if not rulebook_text:
        return JSONResponse(
            status_code=400,
            content={"error": "Please upload rulebook first!"}
        )
    answer = get_answer(request.question, rulebook_text, request.role)
    return {"answer": answer}
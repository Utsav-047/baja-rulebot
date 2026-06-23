# # import smtplib
# # import random
# # import string
# # from email.mime.text import MIMEText
# # from email.mime.multipart import MIMEMultipart
# # from database import save_otp, verify_otp, reset_password, email_exists
# # from fastapi import FastAPI, UploadFile, File, Form
# # from fastapi.middleware.cors import CORSMiddleware
# # from fastapi.responses import JSONResponse, FileResponse
# # from fastapi.staticfiles import StaticFiles
# # from pdf_reader import extract_text_from_pdf
# # from chatbot import get_answer
# # from database import (save_feedback, get_chat_history,
# #                       register_user, login_user, get_all_users, get_all_chats,
# #                       save_rulebook_record, get_global_rulebook, get_user_rulebook,
# #                       save_chunks)
# # from pydantic import BaseModel
# # import os
# # import shutil

# # app = FastAPI()

# # app.add_middleware(
# #     CORSMiddleware,
# #     allow_origins=["*"],
# #     allow_credentials=True,
# #     allow_methods=["*"],
# #     allow_headers=["*"],
# # )

# # os.makedirs("uploads", exist_ok=True)
# # app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

# # rulebook_text = ""
# # rulebook_filename = ""

# # class ChatRequest(BaseModel):
# #     question: str
# #     role: str
# #     user_id: int = 0

# # class FeedbackRequest(BaseModel):
# #     chat_id: int
# #     feedback: str

# # class RegisterRequest(BaseModel):
# #     name: str
# #     email: str
# #     password: str
# #     role: str
# #     team: str

# # class LoginRequest(BaseModel):
# #     email: str
# #     password: str

# # class SendOTPRequest(BaseModel):
# #     email: str

# # class VerifyOTPRequest(BaseModel):
# #     email: str
# #     otp: str

# # class ResetPasswordRequest(BaseModel):
# #     email: str
# #     otp: str
# #     new_password: str


# # @app.on_event("startup")
# # async def auto_load_rulebook():
# #     global rulebook_text, rulebook_filename
# #     print("Checking for saved rulebook on startup...")
# #     try:
# #         result = get_global_rulebook()
# #         if result:
# #             filename, filepath = result
# #             if os.path.exists(filepath):
# #                 with open(filepath, "rb") as f:
# #                     rulebook_text = extract_text_from_pdf(f)
# #                 # Save chunks to MySQL
# #                 words = rulebook_text.split()
# #                 chunks = []
# #                 for i in range(0, len(words), 500):
# #                     chunk = ' '.join(words[i:i+500])
# #                     chunks.append(chunk)
# #                 save_chunks(chunks)
# #                 rulebook_filename = filename
# #                 print(f"✅ Auto-loaded: {filename} | Words: {len(rulebook_text.split())}")
# #             else:
# #                 print("⚠️ File not found on disk")
# #         else:
# #             print("ℹ️ No global rulebook in database yet")
# #     except Exception as e:
# #         print(f"Startup error: {e}")

# # @app.get("/health")
# # def health():
# #     return {
# #         "status": "BAJA RuleBot Backend Running!",
# #         "rulebook_loaded": bool(rulebook_text),
# #         "rulebook_name": rulebook_filename
# #     }

# # @app.post("/register")
# # def register(request: RegisterRequest):
# #     user_id = register_user(
# #         request.name, request.email,
# #         request.password, request.role, request.team
# #     )
# #     if user_id:
# #         return {"message": "Registration successful!", "user_id": user_id}
# #     return JSONResponse(status_code=400, content={"error": "Email already exists!"})

# # @app.post("/login")
# # def login(request: LoginRequest):
# #     user = login_user(request.email, request.password)
# #     if user:
# #         return {
# #             "message": "Login successful!",
# #             "user_id": user[0], "name": user[1],
# #             "role": user[2], "team": user[3], "is_admin": user[4]
# #         }
# #     return JSONResponse(status_code=401, content={"error": "Invalid email or password!"})

# # @app.get("/rulebook/status")
# # def rulebook_status():
# #     global rulebook_text, rulebook_filename
# #     try:
# #         result = get_global_rulebook()
# #         if result:
# #             filename, filepath = result
# #             if not rulebook_text and os.path.exists(filepath):
# #                 with open(filepath, "rb") as f:
# #                     rulebook_text = extract_text_from_pdf(f)
# #                 rulebook_filename = filename
# #             return {
# #                 "filename": filename,
# #                 "is_global": True,
# #                 "loaded": True
# #             }
# #     except Exception as e:
# #         print(f"Status error: {e}")

# #     if rulebook_text:
# #         return {"filename": rulebook_filename, "is_global": False, "loaded": True}

# #     return {"filename": None, "loaded": False}

# # @app.post("/upload")
# # async def upload_rulebook(
# #     file: UploadFile = File(...),
# #     user_id: int = Form(0),
# #     is_global: int = Form(0)
# # ):
# #     global rulebook_text, rulebook_filename

# #     content = await file.read()

# #     # Clean filename
# #     safe_filename = file.filename.replace(" ", "_").replace("(", "").replace(")", "")
# #     if is_global:
# #         safe_filename = "global_" + safe_filename
# #     filepath = os.path.join("uploads", safe_filename)

# #     # Save to disk
# #     with open(filepath, "wb") as f:
# #         f.write(content)
# #     print(f"✅ Saved: {filepath}")

# #     # Extract text
# #     import io
# #     from pdfplumber import open as pdf_open
# #     text = ""
# #     with pdf_open(io.BytesIO(content)) as pdf:
# #         for page in pdf.pages:
# #             extracted = page.extract_text()
# #             if extracted and extracted.strip():
# #                 text += extracted + "\n"

# #     rulebook_text = text
# #     rulebook_filename = safe_filename
# #     word_count = len(text.split())
# #     print(f"✅ Extracted {word_count} words")

# #     # Save chunks to MySQL
# #     words = text.split()
# #     chunks = []
# #     for i in range(0, len(words), 500):
# #         chunk = ' '.join(words[i:i+500])
# #         chunks.append(chunk)
# #     save_chunks(chunks)
# #     print(f"✅ Saved {len(chunks)} chunks to MySQL")

# #     # Save record
# #     save_rulebook_record(user_id, safe_filename, filepath, is_global)

# #     return {
# #         "message": "Rulebook uploaded successfully!",
# #         "words_extracted": word_count,
# #         "chunks_created": len(chunks),
# #         "filename": safe_filename,
# #         "is_global": is_global
# #     }

# # @app.post("/chat")
# # async def chat(request: ChatRequest):
# #     global rulebook_text

# #     if not rulebook_text:
# #         try:
# #             result = get_global_rulebook()
# #             if result:
# #                 filename, filepath = result
# #                 if os.path.exists(filepath):
# #                     with open(filepath, "rb") as f:
# #                         rulebook_text = extract_text_from_pdf(f)
# #         except Exception as e:
# #             print(f"Auto-load error: {e}")

# #     if not rulebook_text:
# #         return JSONResponse(
# #             status_code=400,
# #             content={"error": "Please upload a rulebook first!"}
# #         )

# #     answer = get_answer(request.question, rulebook_text, request.role)

# #     chat_id = 0
# #     if request.user_id > 0:
# #         from database import get_connection
# #         conn = get_connection()
# #         cursor = conn.cursor()
# #         cursor.execute(
# #             "INSERT INTO chat_history (user_id, question, answer) VALUES (%s, %s, %s)",
# #             (request.user_id, request.question, answer)
# #         )
# #         conn.commit()
# #         chat_id = cursor.lastrowid
# #         cursor.close()
# #         conn.close()

# #     return {"answer": answer, "chat_id": chat_id}

# # @app.post("/feedback")
# # def feedback(request: FeedbackRequest):
# #     save_feedback(request.chat_id, request.feedback)
# #     return {"message": "Feedback saved!"}

# # @app.get("/history/{user_id}")
# # def history(user_id: int):
# #     chats = get_chat_history(user_id)
# #     return [
# #         {"id": c[0], "question": c[1], "answer": c[2],
# #          "feedback": c[3], "created_at": str(c[4])}
# #         for c in chats
# #     ]

# # @app.get("/admin/users")
# # def admin_users():
# #     users = get_all_users()
# #     return [
# #         {"id": u[0], "name": u[1], "email": u[2],
# #          "role": u[3], "team": u[4], "created_at": str(u[5])}
# #         for u in users
# #     ]

# # @app.get("/admin/chats")
# # def admin_chats():
# #     chats = get_all_chats()
# #     return [
# #         {"id": c[0], "user_name": c[1], "question": c[2],
# #          "answer": c[3], "feedback": c[4], "created_at": str(c[5])}
# #         for c in chats
# #     ]

# # @app.get("/global-rulebook")
# # def get_global():
# #     result = get_global_rulebook()
# #     if result:
# #         return {"filename": result[0], "filepath": result[1], "available": True}
# #     return {"available": False}

# # @app.get("/my-rulebook/{user_id}")
# # def get_my_rulebook(user_id: int):
# #     result = get_user_rulebook(user_id)
# #     if result:
# #         return {"filename": result[0], "filepath": result[1], "available": True}
# #     return {"available": False}

# # # ─────────────────────────────────────────
# # # MISSING ENDPOINTS FIX
# # # ─────────────────────────────────────────

# # @app.post("/admin/upload-global")
# # async def admin_upload_global(
# #     file: UploadFile = File(...),
# #     user_id: int = Form(0)
# # ):
# #     # Same as /upload but always global
# #     global rulebook_text, rulebook_filename

# #     content = await file.read()
# #     safe_filename = "global_" + file.filename.replace(" ", "_").replace("(", "").replace(")", "")
# #     filepath = os.path.join("uploads", safe_filename)

# #     with open(filepath, "wb") as f:
# #         f.write(content)
# #     print(f"✅ Global saved: {filepath}")

# #     import io
# #     from pdfplumber import open as pdf_open
# #     text = ""
# #     with pdf_open(io.BytesIO(content)) as pdf:
# #         for page in pdf.pages:
# #             extracted = page.extract_text()
# #             if extracted and extracted.strip():
# #                 text += extracted + "\n"

# #     rulebook_text = text
# #     rulebook_filename = safe_filename
# #     word_count = len(text.split())
# #     print(f"✅ Extracted {word_count} words")

# #     words = text.split()
# #     chunks = [' '.join(words[i:i+500]) for i in range(0, len(words), 500)]
# #     save_chunks(chunks)
# #     print(f"✅ Saved {len(chunks)} chunks")

# #     save_rulebook_record(user_id, safe_filename, filepath, is_global=1)

# #     return {
# #         "message": "Global rulebook uploaded!",
# #         "words_extracted": word_count,
# #         "chunks_created": len(chunks),
# #         "filename": safe_filename
# #     }

# # @app.post("/load-rulebook")
# # async def load_rulebook():
# #     global rulebook_text, rulebook_filename
# #     try:
# #         result = get_global_rulebook()
# #         if result:
# #             filename, filepath = result
# #             if os.path.exists(filepath):
# #                 with open(filepath, "rb") as f:
# #                     rulebook_text = extract_text_from_pdf(f)
# #                 rulebook_filename = filename
# #                 words = rulebook_text.split()
# #                 chunks = [' '.join(words[i:i+500]) for i in range(0, len(words), 500)]
# #                 save_chunks(chunks)
# #                 print(f"Loaded rulebook: {filename}")
# #                 return {"message": "Rulebook loaded!", "filename": filename, "loaded": True}
# #         return {"message": "No global rulebook found", "loaded": False}
# #     except Exception as e:
# #         print(f"Load error: {e}")
# #         return {"message": str(e), "loaded": False}

# # def send_otp_email(email, otp):
# #     sender = os.getenv("EMAIL")
# #     password = os.getenv("EMAIL_PASSWORD")

# #     msg = MIMEMultipart("alternative")
# #     msg["Subject"] = "BAJA RuleBot - Password Reset OTP"
# #     msg["From"] = sender
# #     msg["To"] = email

# #     html = f"""
# #     <html>
# #     <body style="font-family:Inter,sans-serif; background:#f8fafc; padding:40px;">
# #       <div style="max-width:480px; margin:0 auto; background:white; 
# #                   border-radius:16px; padding:40px; box-shadow:0 4px 24px rgba(0,0,0,0.08);">
# #         <div style="text-align:center; margin-bottom:32px;">
# #           <div style="background:#f97316; color:white; font-weight:800; 
# #                       padding:8px 16px; border-radius:8px; display:inline-block; 
# #                       font-size:18px;">BAJA</div>
# #           <span style="font-size:20px; font-weight:700; color:#0f172a; margin-left:8px;">
# #             RuleBot</span>
# #         </div>
# #         <h2 style="color:#0f172a; font-size:24px; margin-bottom:8px;">
# #           Password Reset Request</h2>
# #         <p style="color:#64748b; margin-bottom:32px;">
# #           Use the OTP below to reset your password. Valid for 10 minutes.</p>
# #         <div style="background:#eff4ff; border:2px dashed #004183; border-radius:12px; 
# #                     padding:24px; text-align:center; margin-bottom:32px;">
# #           <p style="color:#64748b; font-size:13px; margin-bottom:8px;">Your OTP Code</p>
# #           <div style="font-size:40px; font-weight:900; color:#004183; 
# #                       letter-spacing:8px;">{otp}</div>
# #         </div>
# #         <p style="color:#94a3b8; font-size:13px; text-align:center;">
# #           If you did not request this, please ignore this email.</p>
# #       </div>
# #     </body>
# #     </html>
# #     """

# #     msg.attach(MIMEText(html, "html"))

# #     with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
# #         server.login(sender, password)
# #         server.sendmail(sender, email, msg.as_string())

# # # @app.post("/forgot-password/send-otp")
# # # def send_otp(request: SendOTPRequest):
# # #     if not email_exists(request.email):
# # #         return JSONResponse(
# # #             status_code=404,
# # #             content={"error": "No account found with this email!"}
# # #         )
# # #     otp = ''.join(random.choices(string.digits, k=6))
# # #     save_otp(request.email, otp)
# # #     try:
# # #         send_otp_email(request.email, otp)
# # #         return {"message": "OTP sent successfully! Check your email."}
# # #     except Exception as e:
# # #         print(f"Email error: {e}")
# # #         return JSONResponse(
# # #             status_code=500,
# # #             content={"error": f"Failed to send email: {str(e)}"}
# # #         )
# # # Store last OTP request time
# # otp_cooldown = {}

# # @app.post("/forgot-password/send-otp")
# # def send_otp(request: SendOTPRequest):
# #     import time

# #     # Check cooldown - 60 seconds between requests
# #     current_time = time.time()
# #     if request.email in otp_cooldown:
# #         time_passed = current_time - otp_cooldown[request.email]
# #         if time_passed < 60:
# #             remaining = int(60 - time_passed)
# #             return JSONResponse(
# #                 status_code=429,
# #                 content={"error": f"Please wait {remaining} seconds before requesting another OTP!"}
# #             )

# #     if not email_exists(request.email):
# #         return JSONResponse(
# #             status_code=404,
# #             content={"error": "No account found with this email!"}
# #         )

# #     otp = ''.join(random.choices(string.digits, k=6))
# #     save_otp(request.email, otp)

# #     try:
# #         send_otp_email(request.email, otp)
# #         # Save cooldown time
# #         otp_cooldown[request.email] = current_time
# #         return {"message": "OTP sent successfully! Check your email."}
# #     except Exception as e:
# #         print(f"Email error: {e}")
# #         return JSONResponse(
# #             status_code=500,
# #             content={"error": f"Failed to send email: {str(e)}"}
# #         )


# # @app.post("/forgot-password/verify-otp")
# # def verify(request: VerifyOTPRequest):
# #     if verify_otp(request.email, request.otp):
# #         return {"message": "OTP verified!", "verified": True}
# #     return JSONResponse(
# #         status_code=400,
# #         content={"error": "Invalid or expired OTP!"}
# #     )

# # @app.post("/forgot-password/reset")
# # def reset(request: ResetPasswordRequest):
# #     if not verify_otp(request.email, request.otp):
# #         return JSONResponse(
# #             status_code=400,
# #             content={"error": "Invalid OTP!"}
# #         )
# #     success = reset_password(request.email, request.new_password)
# #     if success:
# #         return {"message": "Password reset successfully!"}
# #     return JSONResponse(
# #         status_code=400,
# #         content={"error": "Failed to reset password!"}
# #     )
















# import smtplib
# import random
# import string
# from email.mime.text import MIMEText
# from email.mime.multipart import MIMEMultipart
# from database import save_otp, verify_otp, reset_password, email_exists
# from fastapi import FastAPI, UploadFile, File, Form
# from fastapi.middleware.cors import CORSMiddleware
# from fastapi.responses import JSONResponse, FileResponse
# from fastapi.staticfiles import StaticFiles
# from pdf_reader import extract_text_from_pdf
# from chatbot import get_answer
# from database import (save_feedback, get_chat_history,
#                       register_user, login_user, get_all_users, get_all_chats,
#                       save_rulebook_record, get_global_rulebook, get_user_rulebook,
#                       save_chunks, save_checklist, get_checklist, delete_checklist)
# from pydantic import BaseModel
# import os
# import shutil

# app = FastAPI()

# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# os.makedirs("uploads", exist_ok=True)
# app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

# rulebook_text = ""
# rulebook_filename = ""

# class ChatRequest(BaseModel):
#     question: str
#     role: str
#     user_id: int = 0

# class FeedbackRequest(BaseModel):
#     chat_id: int
#     feedback: str

# class RegisterRequest(BaseModel):
#     name: str
#     email: str
#     password: str
#     role: str
#     team: str

# class LoginRequest(BaseModel):
#     email: str
#     password: str

# class SendOTPRequest(BaseModel):
#     email: str

# class VerifyOTPRequest(BaseModel):
#     email: str
#     otp: str

# class ResetPasswordRequest(BaseModel):
#     email: str
#     otp: str
#     new_password: str

# class ChecklistSaveRequest(BaseModel):
#     user_id: int
#     category: str
#     items: list


# @app.on_event("startup")
# async def auto_load_rulebook():
#     global rulebook_text, rulebook_filename
#     print("Checking for saved rulebook on startup...")
#     try:
#         result = get_global_rulebook()
#         if result:
#             filename, filepath = result
#             if os.path.exists(filepath):
#                 with open(filepath, "rb") as f:
#                     rulebook_text = extract_text_from_pdf(f)
#                 # Save chunks to MySQL
#                 words = rulebook_text.split()
#                 chunks = []
#                 for i in range(0, len(words), 500):
#                     chunk = ' '.join(words[i:i+500])
#                     chunks.append(chunk)
#                 save_chunks(chunks)
#                 rulebook_filename = filename
#                 print(f"✅ Auto-loaded: {filename} | Words: {len(rulebook_text.split())}")
#             else:
#                 print("⚠️ File not found on disk")
#         else:
#             print("ℹ️ No global rulebook in database yet")
#     except Exception as e:
#         print(f"Startup error: {e}")

# @app.get("/health")
# def health():
#     return {
#         "status": "BAJA RuleBot Backend Running!",
#         "rulebook_loaded": bool(rulebook_text),
#         "rulebook_name": rulebook_filename
#     }

# @app.post("/register")
# def register(request: RegisterRequest):
#     user_id = register_user(
#         request.name, request.email,
#         request.password, request.role, request.team
#     )
#     if user_id:
#         return {"message": "Registration successful!", "user_id": user_id}
#     return JSONResponse(status_code=400, content={"error": "Email already exists!"})

# @app.post("/login")
# def login(request: LoginRequest):
#     user = login_user(request.email, request.password)
#     if user:
#         return {
#             "message": "Login successful!",
#             "user_id": user[0], "name": user[1],
#             "role": user[2], "team": user[3], "is_admin": user[4]
#         }
#     return JSONResponse(status_code=401, content={"error": "Invalid email or password!"})

# @app.get("/rulebook/status")
# def rulebook_status():
#     global rulebook_text, rulebook_filename
#     try:
#         result = get_global_rulebook()
#         if result:
#             filename, filepath = result
#             if not rulebook_text and os.path.exists(filepath):
#                 with open(filepath, "rb") as f:
#                     rulebook_text = extract_text_from_pdf(f)
#                 rulebook_filename = filename
#             return {
#                 "filename": filename,
#                 "is_global": True,
#                 "loaded": True
#             }
#     except Exception as e:
#         print(f"Status error: {e}")

#     if rulebook_text:
#         return {"filename": rulebook_filename, "is_global": False, "loaded": True}

#     return {"filename": None, "loaded": False}

# @app.post("/upload")
# async def upload_rulebook(
#     file: UploadFile = File(...),
#     user_id: int = Form(0),
#     is_global: int = Form(0)
# ):
#     global rulebook_text, rulebook_filename

#     content = await file.read()

#     # Clean filename
#     safe_filename = file.filename.replace(" ", "_").replace("(", "").replace(")", "")
#     if is_global:
#         safe_filename = "global_" + safe_filename
#     filepath = os.path.join("uploads", safe_filename)

#     # Save to disk
#     with open(filepath, "wb") as f:
#         f.write(content)
#     print(f"✅ Saved: {filepath}")

#     # Extract text
#     import io
#     from pdfplumber import open as pdf_open
#     text = ""
#     with pdf_open(io.BytesIO(content)) as pdf:
#         for page in pdf.pages:
#             extracted = page.extract_text()
#             if extracted and extracted.strip():
#                 text += extracted + "\n"

#     rulebook_text = text
#     rulebook_filename = safe_filename
#     word_count = len(text.split())
#     print(f"✅ Extracted {word_count} words")

#     # Save chunks to MySQL
#     words = text.split()
#     chunks = []
#     for i in range(0, len(words), 500):
#         chunk = ' '.join(words[i:i+500])
#         chunks.append(chunk)
#     save_chunks(chunks)
#     print(f"✅ Saved {len(chunks)} chunks to MySQL")

#     # Save record
#     save_rulebook_record(user_id, safe_filename, filepath, is_global)

#     return {
#         "message": "Rulebook uploaded successfully!",
#         "words_extracted": word_count,
#         "chunks_created": len(chunks),
#         "filename": safe_filename,
#         "is_global": is_global
#     }

# @app.post("/chat")
# async def chat(request: ChatRequest):
#     global rulebook_text

#     if not rulebook_text:
#         try:
#             result = get_global_rulebook()
#             if result:
#                 filename, filepath = result
#                 if os.path.exists(filepath):
#                     with open(filepath, "rb") as f:
#                         rulebook_text = extract_text_from_pdf(f)
#         except Exception as e:
#             print(f"Auto-load error: {e}")

#     if not rulebook_text:
#         return JSONResponse(
#             status_code=400,
#             content={"error": "Please upload a rulebook first!"}
#         )

#     answer = get_answer(request.question, rulebook_text, request.role)

#     chat_id = 0
#     if request.user_id > 0:
#         from database import get_connection
#         conn = get_connection()
#         cursor = conn.cursor()
#         cursor.execute(
#             "INSERT INTO chat_history (user_id, question, answer) VALUES (%s, %s, %s)",
#             (request.user_id, request.question, answer)
#         )
#         conn.commit()
#         chat_id = cursor.lastrowid
#         cursor.close()
#         conn.close()

#     return {"answer": answer, "chat_id": chat_id}

# @app.post("/feedback")
# def feedback(request: FeedbackRequest):
#     save_feedback(request.chat_id, request.feedback)
#     return {"message": "Feedback saved!"}

# @app.get("/history/{user_id}")
# def history(user_id: int):
#     chats = get_chat_history(user_id)
#     return [
#         {"id": c[0], "question": c[1], "answer": c[2],
#          "feedback": c[3], "created_at": str(c[4])}
#         for c in chats
#     ]

# @app.post("/checklist/save")
# def checklist_save(request: ChecklistSaveRequest):
#     save_checklist(request.user_id, request.category, request.items)
#     return {"message": "Checklist saved!"}

# @app.get("/checklist/{user_id}/{category}")
# def checklist_get(user_id: int, category: str):
#     items, updated_at = get_checklist(user_id, category)
#     if items is not None:
#         return {"found": True, "items": items, "updated_at": str(updated_at)}
#     return {"found": False, "items": []}

# @app.delete("/checklist/{user_id}/{category}")
# def checklist_delete(user_id: int, category: str):
#     deleted = delete_checklist(user_id, category)
#     return {"deleted": deleted}

# @app.get("/admin/users")
# def admin_users():
#     users = get_all_users()
#     return [
#         {"id": u[0], "name": u[1], "email": u[2],
#          "role": u[3], "team": u[4], "created_at": str(u[5])}
#         for u in users
#     ]

# @app.get("/admin/chats")
# def admin_chats():
#     chats = get_all_chats()
#     return [
#         {"id": c[0], "user_id": c[1], "user_name": c[2], "user_email": c[3],
#          "user_role": c[4], "user_team": c[5], "question": c[6],
#          "answer": c[7], "feedback": c[8], "created_at": str(c[9])}
#         for c in chats
#     ]

# @app.get("/global-rulebook")
# def get_global():
#     result = get_global_rulebook()
#     if result:
#         return {"filename": result[0], "filepath": result[1], "available": True}
#     return {"available": False}

# @app.get("/my-rulebook/{user_id}")
# def get_my_rulebook(user_id: int):
#     result = get_user_rulebook(user_id)
#     if result:
#         return {"filename": result[0], "filepath": result[1], "available": True}
#     return {"available": False}

# # ─────────────────────────────────────────
# # MISSING ENDPOINTS FIX
# # ─────────────────────────────────────────

# @app.post("/admin/upload-global")
# async def admin_upload_global(
#     file: UploadFile = File(...),
#     user_id: int = Form(0)
# ):
#     # Same as /upload but always global
#     global rulebook_text, rulebook_filename

#     content = await file.read()
#     safe_filename = "global_" + file.filename.replace(" ", "_").replace("(", "").replace(")", "")
#     filepath = os.path.join("uploads", safe_filename)

#     with open(filepath, "wb") as f:
#         f.write(content)
#     print(f"✅ Global saved: {filepath}")

#     import io
#     from pdfplumber import open as pdf_open
#     text = ""
#     with pdf_open(io.BytesIO(content)) as pdf:
#         for page in pdf.pages:
#             extracted = page.extract_text()
#             if extracted and extracted.strip():
#                 text += extracted + "\n"

#     rulebook_text = text
#     rulebook_filename = safe_filename
#     word_count = len(text.split())
#     print(f"✅ Extracted {word_count} words")

#     words = text.split()
#     chunks = [' '.join(words[i:i+500]) for i in range(0, len(words), 500)]
#     save_chunks(chunks)
#     print(f"✅ Saved {len(chunks)} chunks")

#     save_rulebook_record(user_id, safe_filename, filepath, is_global=1)

#     return {
#         "message": "Global rulebook uploaded!",
#         "words_extracted": word_count,
#         "chunks_created": len(chunks),
#         "filename": safe_filename
#     }

# @app.post("/load-rulebook")
# async def load_rulebook():
#     global rulebook_text, rulebook_filename
#     try:
#         result = get_global_rulebook()
#         if result:
#             filename, filepath = result
#             if os.path.exists(filepath):
#                 with open(filepath, "rb") as f:
#                     rulebook_text = extract_text_from_pdf(f)
#                 rulebook_filename = filename
#                 words = rulebook_text.split()
#                 chunks = [' '.join(words[i:i+500]) for i in range(0, len(words), 500)]
#                 save_chunks(chunks)
#                 print(f"Loaded rulebook: {filename}")
#                 return {"message": "Rulebook loaded!", "filename": filename, "loaded": True}
#         return {"message": "No global rulebook found", "loaded": False}
#     except Exception as e:
#         print(f"Load error: {e}")
#         return {"message": str(e), "loaded": False}

# def send_otp_email(email, otp):
#     sender = os.getenv("EMAIL")
#     password = os.getenv("EMAIL_PASSWORD")

#     msg = MIMEMultipart("alternative")
#     msg["Subject"] = "BAJA RuleBot - Password Reset OTP"
#     msg["From"] = sender
#     msg["To"] = email

#     html = f"""
#     <html>
#     <body style="font-family:Inter,sans-serif; background:#f8fafc; padding:40px;">
#       <div style="max-width:480px; margin:0 auto; background:white; 
#                   border-radius:16px; padding:40px; box-shadow:0 4px 24px rgba(0,0,0,0.08);">
#         <div style="text-align:center; margin-bottom:32px;">
#           <div style="background:#f97316; color:white; font-weight:800; 
#                       padding:8px 16px; border-radius:8px; display:inline-block; 
#                       font-size:18px;">BAJA</div>
#           <span style="font-size:20px; font-weight:700; color:#0f172a; margin-left:8px;">
#             RuleBot</span>
#         </div>
#         <h2 style="color:#0f172a; font-size:24px; margin-bottom:8px;">
#           Password Reset Request</h2>
#         <p style="color:#64748b; margin-bottom:32px;">
#           Use the OTP below to reset your password. Valid for 10 minutes.</p>
#         <div style="background:#eff4ff; border:2px dashed #004183; border-radius:12px; 
#                     padding:24px; text-align:center; margin-bottom:32px;">
#           <p style="color:#64748b; font-size:13px; margin-bottom:8px;">Your OTP Code</p>
#           <div style="font-size:40px; font-weight:900; color:#004183; 
#                       letter-spacing:8px;">{otp}</div>
#         </div>
#         <p style="color:#94a3b8; font-size:13px; text-align:center;">
#           If you did not request this, please ignore this email.</p>
#       </div>
#     </body>
#     </html>
#     """

#     msg.attach(MIMEText(html, "html"))

#     with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
#         server.login(sender, password)
#         server.sendmail(sender, email, msg.as_string())

# # @app.post("/forgot-password/send-otp")
# # def send_otp(request: SendOTPRequest):
# #     if not email_exists(request.email):
# #         return JSONResponse(
# #             status_code=404,
# #             content={"error": "No account found with this email!"}
# #         )
# #     otp = ''.join(random.choices(string.digits, k=6))
# #     save_otp(request.email, otp)
# #     try:
# #         send_otp_email(request.email, otp)
# #         return {"message": "OTP sent successfully! Check your email."}
# #     except Exception as e:
# #         print(f"Email error: {e}")
# #         return JSONResponse(
# #             status_code=500,
# #             content={"error": f"Failed to send email: {str(e)}"}
# #         )
# # Store last OTP request time
# otp_cooldown = {}

# @app.post("/forgot-password/send-otp")
# def send_otp(request: SendOTPRequest):
#     import time

#     # Check cooldown - 60 seconds between requests
#     current_time = time.time()
#     if request.email in otp_cooldown:
#         time_passed = current_time - otp_cooldown[request.email]
#         if time_passed < 60:
#             remaining = int(60 - time_passed)
#             return JSONResponse(
#                 status_code=429,
#                 content={"error": f"Please wait {remaining} seconds before requesting another OTP!"}
#             )

#     if not email_exists(request.email):
#         return JSONResponse(
#             status_code=404,
#             content={"error": "No account found with this email!"}
#         )

#     otp = ''.join(random.choices(string.digits, k=6))
#     save_otp(request.email, otp)

#     try:
#         send_otp_email(request.email, otp)
#         # Save cooldown time
#         otp_cooldown[request.email] = current_time
#         return {"message": "OTP sent successfully! Check your email."}
#     except Exception as e:
#         print(f"Email error: {e}")
#         return JSONResponse(
#             status_code=500,
#             content={"error": f"Failed to send email: {str(e)}"}
#         )


# @app.post("/forgot-password/verify-otp")
# def verify(request: VerifyOTPRequest):
#     if verify_otp(request.email, request.otp):
#         return {"message": "OTP verified!", "verified": True}
#     return JSONResponse(
#         status_code=400,
#         content={"error": "Invalid or expired OTP!"}
#     )

# @app.post("/forgot-password/reset")
# def reset(request: ResetPasswordRequest):
#     if not verify_otp(request.email, request.otp):
#         return JSONResponse(
#             status_code=400,
#             content={"error": "Invalid OTP!"}
#         )
#     success = reset_password(request.email, request.new_password)
#     if success:
#         return {"message": "Password reset successfully!"}
#     return JSONResponse(
#         status_code=400,
#         content={"error": "Failed to reset password!"}
#     )



import smtplib
import random
import string
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from database import save_otp, verify_otp, reset_password, email_exists
from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from pdf_reader import extract_text_from_pdf
from chatbot import get_answer, get_checklist_items
from database import (save_feedback, get_chat_history,
                      register_user, login_user, get_all_users, get_all_chats,
                      save_rulebook_record, get_global_rulebook, get_user_rulebook,
                      save_chunks, save_chunks_to_chroma, save_checklist, get_checklist, delete_checklist)
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

class SendOTPRequest(BaseModel):
    email: str

class VerifyOTPRequest(BaseModel):
    email: str
    otp: str

class ResetPasswordRequest(BaseModel):
    email: str
    otp: str
    new_password: str

class ChecklistSaveRequest(BaseModel):
    user_id: int
    category: str
    items: list

class ChecklistGenerateRequest(BaseModel):
    category: str
    role: str = "Team Member"


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
                save_chunks_to_chroma(chunks)
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
    save_chunks_to_chroma(chunks)
    print(f"✅ Saved {len(chunks)} chunks to MySQL + ChromaDB")

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

@app.post("/checklist/generate")
def checklist_generate(request: ChecklistGenerateRequest):
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

    items_text = get_checklist_items(request.category, rulebook_text, request.role)
    return {"items": items_text}

@app.post("/checklist/save")
def checklist_save(request: ChecklistSaveRequest):
    save_checklist(request.user_id, request.category, request.items)
    return {"message": "Checklist saved!"}

@app.get("/checklist/{user_id}/{category}")
def checklist_get(user_id: int, category: str):
    items, updated_at = get_checklist(user_id, category)
    if items is not None:
        return {"found": True, "items": items, "updated_at": str(updated_at)}
    return {"found": False, "items": []}

@app.delete("/checklist/{user_id}/{category}")
def checklist_delete(user_id: int, category: str):
    deleted = delete_checklist(user_id, category)
    return {"deleted": deleted}

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
        {"id": c[0], "user_id": c[1], "user_name": c[2], "user_email": c[3],
         "user_role": c[4], "user_team": c[5], "question": c[6],
         "answer": c[7], "feedback": c[8], "created_at": str(c[9])}
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

# ─────────────────────────────────────────
# MISSING ENDPOINTS FIX
# ─────────────────────────────────────────

@app.post("/admin/upload-global")
async def admin_upload_global(
    file: UploadFile = File(...),
    user_id: int = Form(0)
):
    # Same as /upload but always global
    global rulebook_text, rulebook_filename

    content = await file.read()
    safe_filename = "global_" + file.filename.replace(" ", "_").replace("(", "").replace(")", "")
    filepath = os.path.join("uploads", safe_filename)

    with open(filepath, "wb") as f:
        f.write(content)
    print(f"✅ Global saved: {filepath}")

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

    words = text.split()
    chunks = [' '.join(words[i:i+500]) for i in range(0, len(words), 500)]
    save_chunks(chunks)
    save_chunks_to_chroma(chunks)
    print(f"✅ Saved {len(chunks)} chunks")

    save_rulebook_record(None, safe_filename, filepath, is_global=1)

    return {
        "message": "Global rulebook uploaded!",
        "words_extracted": word_count,
        "chunks_created": len(chunks),
        "filename": safe_filename
    }

@app.post("/load-rulebook")
async def load_rulebook():
    global rulebook_text, rulebook_filename
    try:
        result = get_global_rulebook()
        if result:
            filename, filepath = result
            if os.path.exists(filepath):
                with open(filepath, "rb") as f:
                    rulebook_text = extract_text_from_pdf(f)
                rulebook_filename = filename
                words = rulebook_text.split()
                chunks = [' '.join(words[i:i+500]) for i in range(0, len(words), 500)]
                save_chunks(chunks)
                save_chunks_to_chroma(chunks)
                print(f"Loaded rulebook: {filename}")
                return {"message": "Rulebook loaded!", "filename": filename, "loaded": True}
        return {"message": "No global rulebook found", "loaded": False}
    except Exception as e:
        print(f"Load error: {e}")
        return {"message": str(e), "loaded": False}

def send_otp_email(email, otp):
    sender = os.getenv("EMAIL")
    password = os.getenv("EMAIL_PASSWORD")

    msg = MIMEMultipart("alternative")
    msg["Subject"] = "BAJA RuleBot - Password Reset OTP"
    msg["From"] = sender
    msg["To"] = email

    html = f"""
    <html>
    <body style="font-family:Inter,sans-serif; background:#f8fafc; padding:40px;">
      <div style="max-width:480px; margin:0 auto; background:white; 
                  border-radius:16px; padding:40px; box-shadow:0 4px 24px rgba(0,0,0,0.08);">
        <div style="text-align:center; margin-bottom:32px;">
          <div style="background:#f97316; color:white; font-weight:800; 
                      padding:8px 16px; border-radius:8px; display:inline-block; 
                      font-size:18px;">BAJA</div>
          <span style="font-size:20px; font-weight:700; color:#0f172a; margin-left:8px;">
            RuleBot</span>
        </div>
        <h2 style="color:#0f172a; font-size:24px; margin-bottom:8px;">
          Password Reset Request</h2>
        <p style="color:#64748b; margin-bottom:32px;">
          Use the OTP below to reset your password. Valid for 10 minutes.</p>
        <div style="background:#eff4ff; border:2px dashed #004183; border-radius:12px; 
                    padding:24px; text-align:center; margin-bottom:32px;">
          <p style="color:#64748b; font-size:13px; margin-bottom:8px;">Your OTP Code</p>
          <div style="font-size:40px; font-weight:900; color:#004183; 
                      letter-spacing:8px;">{otp}</div>
        </div>
        <p style="color:#94a3b8; font-size:13px; text-align:center;">
          If you did not request this, please ignore this email.</p>
      </div>
    </body>
    </html>
    """

    msg.attach(MIMEText(html, "html"))

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(sender, password)
        server.sendmail(sender, email, msg.as_string())

# @app.post("/forgot-password/send-otp")
# def send_otp(request: SendOTPRequest):
#     if not email_exists(request.email):
#         return JSONResponse(
#             status_code=404,
#             content={"error": "No account found with this email!"}
#         )
#     otp = ''.join(random.choices(string.digits, k=6))
#     save_otp(request.email, otp)
#     try:
#         send_otp_email(request.email, otp)
#         return {"message": "OTP sent successfully! Check your email."}
#     except Exception as e:
#         print(f"Email error: {e}")
#         return JSONResponse(
#             status_code=500,
#             content={"error": f"Failed to send email: {str(e)}"}
#         )
# Store last OTP request time
otp_cooldown = {}

@app.post("/forgot-password/send-otp")
def send_otp(request: SendOTPRequest):
    import time

    # Check cooldown - 60 seconds between requests
    current_time = time.time()
    if request.email in otp_cooldown:
        time_passed = current_time - otp_cooldown[request.email]
        if time_passed < 60:
            remaining = int(60 - time_passed)
            return JSONResponse(
                status_code=429,
                content={"error": f"Please wait {remaining} seconds before requesting another OTP!"}
            )

    if not email_exists(request.email):
        return JSONResponse(
            status_code=404,
            content={"error": "No account found with this email!"}
        )

    otp = ''.join(random.choices(string.digits, k=6))
    save_otp(request.email, otp)

    try:
        send_otp_email(request.email, otp)
        # Save cooldown time
        otp_cooldown[request.email] = current_time
        return {"message": "OTP sent successfully! Check your email."}
    except Exception as e:
        print(f"Email error: {e}")
        return JSONResponse(
            status_code=500,
            content={"error": f"Failed to send email: {str(e)}"}
        )


@app.post("/forgot-password/verify-otp")
def verify(request: VerifyOTPRequest):
    if verify_otp(request.email, request.otp):
        return {"message": "OTP verified!", "verified": True}
    return JSONResponse(
        status_code=400,
        content={"error": "Invalid or expired OTP!"}
    )

@app.post("/forgot-password/reset")
def reset(request: ResetPasswordRequest):
    if not verify_otp(request.email, request.otp):
        return JSONResponse(
            status_code=400,
            content={"error": "Invalid OTP!"}
        )
    success = reset_password(request.email, request.new_password)
    if success:
        return {"message": "Password reset successfully!"}
    return JSONResponse(
        status_code=400,
        content={"error": "Failed to reset password!"}
    )
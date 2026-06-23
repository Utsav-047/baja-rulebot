


import mysql.connector
import json

import os

def get_connection():
    return mysql.connector.connect(
        host=os.getenv("MYSQLHOST", "localhost"),
        port=int(os.getenv("MYSQLPORT", 3307)),
        user=os.getenv("MYSQLUSER", "root"),
        password=os.getenv("MYSQLPASSWORD", ""),
        database=os.getenv("MYSQL_DATABASE", "baja_rulebot")
    )

def save_chat_history(user_id, question, answer):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO chat_history (user_id, question, answer) VALUES (%s, %s, %s)",
        (user_id, question, answer)
    )
    conn.commit()
    cursor.close()
    conn.close()

def save_feedback(chat_id, feedback):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE chat_history SET feedback = %s WHERE id = %s",
        (feedback, chat_id)
    )
    conn.commit()
    cursor.close()
    conn.close()

def get_chat_history(user_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id, question, answer, feedback, created_at FROM chat_history WHERE user_id = %s ORDER BY created_at DESC",
        (user_id,)
    )
    results = cursor.fetchall()
    cursor.close()
    conn.close()
    return results

def register_user(name, email, password, role, team):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO users (name, email, password, role, team) VALUES (%s, %s, %s, %s, %s)",
            (name, email, password, role, team)
        )
        conn.commit()
        user_id = cursor.lastrowid
        cursor.close()
        conn.close()
        return user_id
    except Exception as e:
        cursor.close()
        conn.close()
        return None

def login_user(email, password):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id, name, role, team, is_admin FROM users WHERE email = %s AND password = %s",
        (email, password)
    )
    user = cursor.fetchone()
    cursor.close()
    conn.close()
    return user

def get_all_users():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, email, role, team, created_at FROM users")
    users = cursor.fetchall()
    cursor.close()
    conn.close()
    return users

def get_all_chats():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT c.id, u.id, u.name, u.email, u.role, u.team, "
        "c.question, c.answer, c.feedback, c.created_at "
        "FROM chat_history c JOIN users u ON c.user_id = u.id "
        "ORDER BY c.created_at DESC"
    )
    chats = cursor.fetchall()
    cursor.close()
    conn.close()
    return chats

def save_chunks(chunks):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM rulebook_chunks")
    for i, chunk in enumerate(chunks):
        cursor.execute(
            "INSERT INTO rulebook_chunks (chunk_text, chunk_index) VALUES (%s, %s)",
            (chunk, i)
        )
    conn.commit()
    cursor.close()
    conn.close()

# def search_chunks(question, top_n=5):
#     conn = get_connection()
#     cursor = conn.cursor()
#     question_words = [w for w in question.lower().split() if len(w) > 3]

#     if not question_words:
#         cursor.execute("SELECT chunk_text FROM rulebook_chunks LIMIT 5")
#         results = cursor.fetchall()
#         cursor.close()
#         conn.close()
#         return [r[0] for r in results]

#     scored_chunks = []
#     cursor.execute("SELECT chunk_text FROM rulebook_chunks")
#     all_chunks = cursor.fetchall()
#     cursor.close()
#     conn.close()

#     for chunk_row in all_chunks:
#         chunk = chunk_row[0]
#         chunk_lower = chunk.lower()
#         score = sum(1 for word in question_words if word in chunk_lower)
#         if score > 0:
#             scored_chunks.append((score, chunk))

#     scored_chunks.sort(reverse=True)
#     return [chunk for score, chunk in scored_chunks[:top_n]]
import chromadb
from sentence_transformers import SentenceTransformer

_embedding_model = SentenceTransformer("all-MiniLM-L6-v2")
_chroma_client = chromadb.PersistentClient(path="./chroma_db")
_collection = _chroma_client.get_or_create_collection("rulebook_chunks")


def save_chunks_to_chroma(chunks):
    _collection.delete(where={"source": "rulebook"})
    embeddings = _embedding_model.encode(chunks).tolist()
    _collection.add(
        documents=chunks,
        embeddings=embeddings,
        ids=[f"chunk_{i}" for i in range(len(chunks))],
        metadatas=[{"source": "rulebook"} for _ in chunks]
    )
    print(f"✅ Saved {len(chunks)} chunks to ChromaDB")


def search_chunks(question, top_n=5):
    query_embedding = _embedding_model.encode([question]).tolist()
    results = _collection.query(
        query_embeddings=query_embedding,
        n_results=top_n
    )
    docs = results.get("documents", [[]])[0]
    return docs if docs else []

def save_rulebook_record(user_id, filename, filepath, is_global=0):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO rulebooks (user_id, filename, filepath, is_global) VALUES (%s, %s, %s, %s)",
        (user_id, filename, filepath, is_global)
    )
    conn.commit()
    cursor.close()
    conn.close()

def get_global_rulebook():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT filename, filepath FROM rulebooks WHERE is_global = 1 ORDER BY id DESC LIMIT 1"
    )
    result = cursor.fetchone()
    cursor.close()
    conn.close()
    return result

def get_user_rulebook(user_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT filename, filepath FROM rulebooks WHERE user_id = %s AND is_global = 0 ORDER BY id DESC LIMIT 1",
        (user_id,)
    )
    result = cursor.fetchone()
    cursor.close()
    conn.close()
    return result

def save_otp(email, otp):
    conn = get_connection()
    cursor = conn.cursor()
    # Delete old OTP first
    cursor.execute("DELETE FROM password_otp WHERE email = %s", (email,))
    cursor.execute(
        "INSERT INTO password_otp (email, otp) VALUES (%s, %s)",
        (email, otp)
    )
    conn.commit()
    cursor.close()
    conn.close()

def verify_otp(email, otp):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT otp FROM password_otp WHERE email = %s ORDER BY created_at DESC LIMIT 1",
        (email,)
    )
    result = cursor.fetchone()
    cursor.close()
    conn.close()
    if result and result[0] == otp:
        return True
    return False

def reset_password(email, new_password):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE users SET password = %s WHERE email = %s",
        (new_password, email)
    )
    conn.commit()
    rows = cursor.rowcount
    cursor.close()
    conn.close()
    return rows > 0

def email_exists(email):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM users WHERE email = %s", (email,))
    result = cursor.fetchone()
    cursor.close()
    conn.close()
    return result is not None


# ── CHECKLIST PERSISTENCE ──

def save_checklist(user_id, category, items):
    """items: list of {"text": str, "checked": bool}"""
    conn = get_connection()
    cursor = conn.cursor()
    items_json = json.dumps(items)
    cursor.execute(
        "SELECT id FROM checklists WHERE user_id = %s AND category = %s",
        (user_id, category)
    )
    existing = cursor.fetchone()
    if existing:
        cursor.execute(
            "UPDATE checklists SET items = %s, updated_at = NOW() WHERE id = %s",
            (items_json, existing[0])
        )
    else:
        cursor.execute(
            "INSERT INTO checklists (user_id, category, items) VALUES (%s, %s, %s)",
            (user_id, category, items_json)
        )
    conn.commit()
    cursor.close()
    conn.close()


def get_checklist(user_id, category):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT items, updated_at FROM checklists WHERE user_id = %s AND category = %s",
        (user_id, category)
    )
    result = cursor.fetchone()
    cursor.close()
    conn.close()
    if result:
        return json.loads(result[0]), result[1]
    return None, None


def delete_checklist(user_id, category):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "DELETE FROM checklists WHERE user_id = %s AND category = %s",
        (user_id, category)
    )
    conn.commit()
    rows = cursor.rowcount
    cursor.close()
    conn.close()
    return rows > 0

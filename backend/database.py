import mysql.connector

def get_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="baja_rulebot"
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
        "SELECT c.id, u.name, c.question, c.answer, c.feedback, c.created_at FROM chat_history c JOIN users u ON c.user_id = u.id ORDER BY c.created_at DESC"
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

def search_chunks(question, top_n=5):
    conn = get_connection()
    cursor = conn.cursor()
    question_words = [w for w in question.lower().split() if len(w) > 3]

    if not question_words:
        cursor.execute("SELECT chunk_text FROM rulebook_chunks LIMIT 5")
        results = cursor.fetchall()
        cursor.close()
        conn.close()
        return [r[0] for r in results]

    scored_chunks = []
    cursor.execute("SELECT chunk_text FROM rulebook_chunks")
    all_chunks = cursor.fetchall()
    cursor.close()
    conn.close()

    for chunk_row in all_chunks:
        chunk = chunk_row[0]
        chunk_lower = chunk.lower()
        score = sum(1 for word in question_words if word in chunk_lower)
        if score > 0:
            scored_chunks.append((score, chunk))

    scored_chunks.sort(reverse=True)
    return [chunk for score, chunk in scored_chunks[:top_n]]

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
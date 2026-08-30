import os
import json
import hashlib
import secrets
from urllib.parse import urlparse
import mysql.connector


# ==============================================================================
# Database Connection Helper
# ==============================================================================

def get_connection():
    """
    Establish connection to MySQL using individual env vars or DATABASE_URL/MYSQL_URL.
    Defaults to localhost:3306 for local development.
    """
    database_url = os.getenv("DATABASE_URL") or os.getenv("MYSQL_URL")
    if database_url:
        parsed = urlparse(database_url)
        return mysql.connector.connect(
            host=parsed.hostname or "localhost",
            port=parsed.port or 3306,
            user=parsed.username or "root",
            password=parsed.password or "",
            database=parsed.path.lstrip("/") or "baja_rulebot"
        )

    return mysql.connector.connect(
        host=os.getenv("MYSQLHOST") or os.getenv("MYSQL_HOST") or "localhost",
        port=int(os.getenv("MYSQLPORT") or os.getenv("MYSQL_PORT") or 3306),
        user=os.getenv("MYSQLUSER") or os.getenv("MYSQL_USER") or "root",
        password=os.getenv("MYSQLPASSWORD") or os.getenv("MYSQL_PASSWORD") or "",
        database=os.getenv("MYSQLDATABASE") or os.getenv("MYSQL_DATABASE") or "baja_rulebot"
    )


# ==============================================================================
# Database Schema Initialization
# ==============================================================================

def init_db():
    """
    Ensure all necessary tables exist in the database upon application startup.
    """
    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(255) NOT NULL,
                email VARCHAR(255) NOT NULL UNIQUE,
                password VARCHAR(255) NOT NULL,
                role VARCHAR(100) NOT NULL,
                team VARCHAR(255) NOT NULL,
                is_admin TINYINT(1) DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS chat_history (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT NOT NULL,
                question TEXT NOT NULL,
                answer LONGTEXT NOT NULL,
                feedback VARCHAR(50) DEFAULT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS rulebooks (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT DEFAULT NULL,
                filename VARCHAR(255) NOT NULL,
                filepath VARCHAR(500) NOT NULL,
                is_global TINYINT(1) DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS rulebook_chunks (
                id INT AUTO_INCREMENT PRIMARY KEY,
                chunk_text LONGTEXT NOT NULL,
                chunk_index INT NOT NULL
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS password_otp (
                id INT AUTO_INCREMENT PRIMARY KEY,
                email VARCHAR(255) NOT NULL,
                otp VARCHAR(10) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS checklists (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT NOT NULL,
                category VARCHAR(255) NOT NULL,
                items JSON NOT NULL,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
        """)

        conn.commit()
        cursor.close()
        conn.close()
        print("✅ Database tables verified and initialized successfully.")
    except Exception as e:
        print(f"⚠️ Database initialization notice: {e}")


# ==============================================================================
# Cryptographic Password Hashing & Verification
# ==============================================================================

def hash_password(plain_password: str) -> str:
    """
    Hash a password using PBKDF2-HMAC-SHA256 with 100,000 iterations and a unique salt.
    Format: pbkdf2:sha256:100000$salt$hash
    """
    salt = secrets.token_hex(16)
    iterations = 100_000
    key = hashlib.pbkdf2_hmac(
        'sha256',
        plain_password.encode('utf-8'),
        salt.encode('utf-8'),
        iterations
    )
    return f"pbkdf2:sha256:{iterations}${salt}${key.hex()}"


def verify_password(plain_password: str, stored_password: str) -> bool:
    """
    Verify a plaintext password against a stored hash string.
    Supports backward compatibility for legacy plaintext records.
    """
    if not stored_password:
        return False

    if stored_password.startswith("pbkdf2:sha256:"):
        try:
            parts = stored_password.split("$")
            iterations = int(parts[0].split(":")[-1])
            salt = parts[1]
            original_hash = parts[2]
            key = hashlib.pbkdf2_hmac(
                'sha256',
                plain_password.encode('utf-8'),
                salt.encode('utf-8'),
                iterations
            )
            return secrets.compare_digest(key.hex(), original_hash)
        except Exception:
            return False

    # Fallback to direct comparison for legacy unhashed entries
    return stored_password == plain_password


# ==============================================================================
# User Management & Authentication
# ==============================================================================

def register_user(name, email, password, role, team):
    """
    Register a new user with secure password hashing.
    """
    conn = get_connection()
    cursor = conn.cursor()
    try:
        hashed_pwd = hash_password(password)
        cursor.execute(
            "INSERT INTO users (name, email, password, role, team) VALUES (%s, %s, %s, %s, %s)",
            (name, email, hashed_pwd, role, team)
        )
        conn.commit()
        user_id = cursor.lastrowid
        cursor.close()
        conn.close()
        return user_id
    except Exception as e:
        print(f"Registration error: {e}")
        cursor.close()
        conn.close()
        return None


def login_user(email, password):
    """
    Authenticate user by verifying credentials against stored hash.
    Automatically upgrades legacy plaintext passwords to hashed format upon login.
    """
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "SELECT id, name, role, team, is_admin, password FROM users WHERE email = %s",
            (email,)
        )
        user = cursor.fetchone()
        if user:
            user_id, name, role, team, is_admin, stored_password = user
            if verify_password(password, stored_password):
                # Upgrade legacy unhashed password if needed
                if not str(stored_password).startswith("pbkdf2:sha256:"):
                    try:
                        new_hashed = hash_password(password)
                        cursor.execute("UPDATE users SET password = %s WHERE id = %s", (new_hashed, user_id))
                        conn.commit()
                    except Exception as upgrade_err:
                        print(f"Password auto-upgrade error: {upgrade_err}")

                cursor.close()
                conn.close()
                return (user_id, name, role, team, is_admin)

        cursor.close()
        conn.close()
        return None
    except Exception as e:
        print(f"Login error: {e}")
        cursor.close()
        conn.close()
        return None


def get_all_users():
    """
    Retrieve all registered users (for admin panel).
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, email, role, team, created_at FROM users ORDER BY created_at DESC")
    users = cursor.fetchall()
    cursor.close()
    conn.close()
    return users


# ==============================================================================
# Chat History & Feedback
# ==============================================================================

def save_chat_history(user_id, question, answer):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO chat_history (user_id, question, answer) VALUES (%s, %s, %s)",
        (user_id, question, answer)
    )
    conn.commit()
    chat_id = cursor.lastrowid
    cursor.close()
    conn.close()
    return chat_id


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


# ==============================================================================
# ChromaDB Vector Store & Embeddings (Lazy Loaded)
# ==============================================================================

_embedding_model = None
_chroma_client = None
_collection = None


def get_vector_store():
    """Lazy-load ChromaDB and embedding model to ensure resilient startup."""
    global _embedding_model, _chroma_client, _collection
    if _collection is None:
        try:
            import chromadb
            from sentence_transformers import SentenceTransformer
            _embedding_model = SentenceTransformer("all-MiniLM-L6-v2")
            _chroma_client = chromadb.PersistentClient(path="./chroma_db")
            _collection = _chroma_client.get_or_create_collection("rulebook_chunks")
        except Exception as e:
            print(f"⚠️ Vector engine lazy-load notice: {e}")
            return None, None
    return _embedding_model, _collection


def save_chunks(chunks):
    """Save chunks into MySQL as persistent relational backup."""
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


def save_chunks_to_chroma(chunks):
    """Embed and index chunks into ChromaDB."""
    model, collection = get_vector_store()
    if collection is None or model is None:
        print("ℹ️ ChromaDB unavailable; indexed into MySQL.")
        return

    try:
        collection.delete(where={"source": "rulebook"})
    except Exception:
        pass

    if chunks:
        embeddings = model.encode(chunks).tolist()
        collection.add(
            documents=chunks,
            embeddings=embeddings,
            ids=[f"chunk_{i}" for i in range(len(chunks))],
            metadatas=[{"source": "rulebook"} for _ in chunks]
        )
        print(f"✅ Saved {len(chunks)} chunks to ChromaDB")


def search_chunks(question, top_n=5):
    """Search for relevant chunks using cosine similarity embeddings in ChromaDB with MySQL fallback."""
    model, collection = get_vector_store()
    if collection is not None and model is not None:
        try:
            query_embedding = model.encode([question]).tolist()
            results = collection.query(
                query_embeddings=query_embedding,
                n_results=top_n
            )
            docs = results.get("documents", [[]])[0]
            if docs:
                return docs
        except Exception as e:
            print(f"ChromaDB search notice: {e}")

    # Fallback to MySQL keyword matching
    return search_chunks_mysql(question, top_n)


def search_chunks_mysql(question, top_n=5):
    """Fallback text search in MySQL rulebook_chunks table."""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        question_words = [w for w in question.lower().split() if len(w) > 3]

        if not question_words:
            cursor.execute("SELECT chunk_text FROM rulebook_chunks LIMIT %s", (top_n,))
            results = cursor.fetchall()
            cursor.close()
            conn.close()
            return [r[0] for r in results]

        cursor.execute("SELECT chunk_text FROM rulebook_chunks")
        all_chunks = cursor.fetchall()
        cursor.close()
        conn.close()

        scored = []
        for row in all_chunks:
            chunk = row[0]
            chunk_lower = chunk.lower()
            score = sum(1 for word in question_words if word in chunk_lower)
            if score > 0:
                scored.append((score, chunk))

        scored.sort(reverse=True, key=lambda x: x[0])
        return [chunk for score, chunk in scored[:top_n]]
    except Exception as e:
        print(f"MySQL search fallback error: {e}")
        return []


# ==============================================================================
# Rulebook Metadata
# ==============================================================================

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


# ==============================================================================
# Password Reset OTP Flow
# ==============================================================================

def save_otp(email, otp):
    conn = get_connection()
    cursor = conn.cursor()
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
    if result and str(result[0]).strip() == str(otp).strip():
        return True
    return False


def reset_password(email, new_password):
    conn = get_connection()
    cursor = conn.cursor()
    hashed_pwd = hash_password(new_password)
    cursor.execute(
        "UPDATE users SET password = %s WHERE email = %s",
        (hashed_pwd, email)
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


# ==============================================================================
# Checklist Persistence
# ==============================================================================

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

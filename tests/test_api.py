import os
import sys
from unittest.mock import patch
import pytest
from fastapi.testclient import TestClient

# Ensure backend directory is in python path
BACKEND_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend"))
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

from main import app, chunk_text, create_access_token, decode_access_token
from database import hash_password, verify_password
from chatbot import get_answer

client = TestClient(app)


# ==============================================================================
# 1. Health & Root Endpoints
# ==============================================================================

def test_root_endpoint():
    """Verify the root health endpoint returns online status and metadata."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "BAJA RuleBot API"
    assert data["status"] == "online"
    assert "version" in data
    assert "rulebook_loaded" in data


def test_health_endpoint():
    """Verify /health returns healthy status."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"


# ==============================================================================
# 2. Chunking with Overlap (RAG Engine)
# ==============================================================================

def test_chunking_empty_text():
    """Verify chunk_text handles empty string gracefully."""
    chunks = chunk_text("")
    assert chunks == []


def test_chunking_short_text():
    """Verify text shorter than chunk size returns a single chunk."""
    text = "BAJA SAEINDIA roll cage tubing specifications and inspection criteria."
    chunks = chunk_text(text, chunk_size=500, overlap=75)
    assert len(chunks) == 1
    assert chunks[0] == text


def test_chunking_overlap_properties():
    """Verify that chunks have the expected word length and sliding overlap."""
    words = [f"word_{i}" for i in range(1200)]
    text = " ".join(words)
    chunks = chunk_text(text, chunk_size=500, overlap=75)

    assert len(chunks) == 3
    # First chunk has 500 words
    assert len(chunks[0].split()) == 500
    # Second chunk starts at index (500 - 75) = 425
    chunk_0_words = chunks[0].split()
    chunk_1_words = chunks[1].split()
    # Check that the 75 overlapping words exist in both chunk 0 and chunk 1
    assert chunk_0_words[-75:] == chunk_1_words[:75]


# ==============================================================================
# 3. Cryptographic Password Hashing & Verification
# ==============================================================================

def test_password_hashing():
    """Verify PBKDF2-HMAC-SHA256 password hashing and verification."""
    password = "SuperSecretBajaPassword!2026"
    hashed = hash_password(password)

    # Format check: pbkdf2:sha256:100000$salt$hash
    assert hashed.startswith("pbkdf2:sha256:100000$")
    assert verify_password(password, hashed) is True
    assert verify_password("WrongPassword", hashed) is False
    assert verify_password("", hashed) is False


# ==============================================================================
# 4. JWT Authentication & Role Authorization
# ==============================================================================

def test_jwt_token_creation_and_decoding():
    """Verify generating and decoding a signed JWT token."""
    token = create_access_token(
        user_id=42,
        name="Team Captain",
        email="captain@bajaracing.org",
        role="Team Captain",
        is_admin=0
    )
    assert isinstance(token, str)

    payload = decode_access_token(token)
    assert payload["user_id"] == 42
    assert payload["name"] == "Team Captain"
    assert payload["email"] == "captain@bajaracing.org"
    assert payload["role"] == "Team Captain"
    assert payload["is_admin"] == 0


def test_admin_route_unauthenticated():
    """Verify that /admin/users rejects requests without an Authorization token (401)."""
    response = client.get("/admin/users")
    assert response.status_code == 401


def test_admin_route_forbidden_for_regular_user():
    """Verify that /admin/users rejects authenticated non-admin users (403 Forbidden)."""
    user_token = create_access_token(
        user_id=101,
        name="Member",
        email="member@baja.org",
        role="Team Member",
        is_admin=0
    )
    headers = {"Authorization": f"Bearer {user_token}"}
    response = client.get("/admin/users", headers=headers)
    assert response.status_code == 403
    assert "Forbidden" in response.json().get("detail", "")


def test_admin_route_authorized():
    """Verify that /admin/users accepts valid admin bearer tokens and returns structured user data."""
    admin_token = create_access_token(
        user_id=1,
        name="System Admin",
        email="admin@bajarulebot.com",
        role="Faculty Advisor",
        is_admin=1
    )
    headers = {"Authorization": f"Bearer {admin_token}"}
    fake_users = [
        (1, "Alice Admin", "admin@baja.org", "Faculty Advisor", "BAJA Team", "2026-01-01 12:00:00"),
        (2, "Bob Captain", "bob@baja.org", "Team Captain", "BAJA Team", "2026-01-01 12:05:00"),
    ]
    with patch("main.get_all_users", return_value=fake_users):
        response = client.get("/admin/users", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        assert data[0]["name"] == "Alice Admin"
        assert data[1]["role"] == "Team Captain"


def test_idor_protection_on_history():
    """Verify that user A cannot access user B's history unless admin."""
    user_a_token = create_access_token(user_id=10, name="User A", email="a@baja.org", role="Member", is_admin=0)
    headers = {"Authorization": f"Bearer {user_a_token}"}

    # User A attempting to access User B (user_id=20) history
    response = client.get("/history/20", headers=headers)
    assert response.status_code == 403
    assert "Forbidden" in response.json().get("detail", "")


# ==============================================================================
# 5. Greetings & Small Talk (Fast-Path NLP)
# ==============================================================================

def test_chatbot_greetings():
    """Verify greeting fast-path avoids unnecessary LLM consumption."""
    ans = get_answer("hello", rulebook_text="", role="Team Member")
    assert "Hi! I'm BAJA RuleBot" in ans

    ans_thanks = get_answer("thank you", rulebook_text="", role="Team Member")
    assert "You're welcome" in ans_thanks

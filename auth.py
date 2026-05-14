"""
Authentication helpers for the admin backend.
"""
import bcrypt
import hashlib
import secrets
from datetime import datetime, timedelta
from db import get_user_by_username, create_user, create_session, get_session, delete_session

SESSION_DURATION_HOURS = 24

def hash_password(password):
    """Hash a password using bcrypt."""
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def verify_password(password, password_hash):
    """Verify a password against its bcrypt hash."""
    return bcrypt.checkpw(password.encode('utf-8'), password_hash.encode('utf-8'))

def authenticate(username, password):
    """Authenticate a user and return a session token, or None."""
    user = get_user_by_username(username)
    if not user:
        return None
    if not verify_password(password, user['password_hash']):
        return None
    # Create session
    token = secrets.token_urlsafe(48)
    expires_at = (datetime.utcnow() + timedelta(hours=SESSION_DURATION_HOURS)).isoformat()
    create_session(user['id'], token, expires_at)
    return token

def check_session(token):
    """Check if a session token is valid. Returns user dict or None."""
    if not token:
        return None
    session = get_session(token)
    if not session:
        return None
    from db import get_db
    conn = get_db()
    user = conn.execute('SELECT id, username FROM users WHERE id = ?',
                        (session['user_id'],)).fetchone()
    conn.close()
    return dict(user) if user else None

def logout(token):
    """Delete a session."""
    if token:
        delete_session(token)

def ensure_admin(username, password):
    """Create an admin user if one doesn't exist."""
    existing = get_user_by_username(username)
    if not existing:
        create_user(username, hash_password(password))
        print(f"Admin user '{username}' created.")
    else:
        print(f"Admin user '{username}' already exists.")

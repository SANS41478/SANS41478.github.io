"""
Database module for Laodang's Genesis Block.
Uses Python's built-in sqlite3.
"""
import sqlite3
import os
import json

DB_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data')
DB_PATH = os.path.join(DB_DIR, 'laodang.db')

def get_db():
    """Get a database connection with row factory enabled."""
    os.makedirs(DB_DIR, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    return conn

def init_db():
    """Create all tables if they don't exist."""
    conn = get_db()
    cursor = conn.cursor()

    cursor.executescript('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            password_hash TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT DEFAULT '',
            email TEXT DEFAULT '',
            body TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS articles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            slug TEXT NOT NULL UNIQUE,
            title_zh TEXT NOT NULL,
            title_en TEXT NOT NULL,
            content TEXT NOT NULL DEFAULT '',
            excerpt_zh TEXT DEFAULT '',
            excerpt_en TEXT DEFAULT '',
            cover_image TEXT DEFAULT '',
            published INTEGER DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS projects (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            slug TEXT NOT NULL UNIQUE,
            name_zh TEXT NOT NULL,
            name_en TEXT NOT NULL,
            desc_zh TEXT DEFAULT '',
            desc_en TEXT DEFAULT '',
            intro_content TEXT DEFAULT '',
            tags TEXT DEFAULT '[]',
            github_url TEXT DEFAULT '',
            external_url TEXT DEFAULT '',
            icon TEXT DEFAULT '📦',
            cover_image TEXT DEFAULT '',
            published INTEGER DEFAULT 1,
            sort_order INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS media (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            filename TEXT NOT NULL,
            original_name TEXT NOT NULL,
            mime_type TEXT NOT NULL,
            file_size INTEGER DEFAULT 0,
            article_id INTEGER,
            project_id INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (article_id) REFERENCES articles(id) ON DELETE SET NULL,
            FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE SET NULL
        );

        CREATE TABLE IF NOT EXISTS sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            token TEXT NOT NULL UNIQUE,
            user_id INTEGER NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            expires_at TIMESTAMP NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        );

        CREATE INDEX IF NOT EXISTS idx_messages_created ON messages(created_at DESC);
        CREATE INDEX IF NOT EXISTS idx_articles_slug ON articles(slug);
        CREATE INDEX IF NOT EXISTS idx_projects_slug ON projects(slug);
        CREATE INDEX IF NOT EXISTS idx_sessions_token ON sessions(token);
    ''')

    conn.commit()
    conn.close()

# ── Messages ──────────────────────────────────────────

def save_message(name, email, body):
    conn = get_db()
    conn.execute(
        'INSERT INTO messages (name, email, body) VALUES (?, ?, ?)',
        (name, email, body)
    )
    conn.commit()
    conn.close()

def get_messages(limit=100, offset=0):
    conn = get_db()
    rows = conn.execute(
        'SELECT * FROM messages ORDER BY created_at DESC LIMIT ? OFFSET ?',
        (limit, offset)
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]

def delete_message(msg_id):
    conn = get_db()
    conn.execute('DELETE FROM messages WHERE id = ?', (msg_id,))
    conn.commit()
    conn.close()

def count_messages():
    conn = get_db()
    row = conn.execute('SELECT COUNT(*) as cnt FROM messages').fetchone()
    conn.close()
    return row['cnt']

# ── Articles ──────────────────────────────────────────

def get_articles(published_only=True):
    conn = get_db()
    if published_only:
        rows = conn.execute(
            'SELECT * FROM articles WHERE published = 1 ORDER BY created_at DESC'
        ).fetchall()
    else:
        rows = conn.execute(
            'SELECT * FROM articles ORDER BY created_at DESC'
        ).fetchall()
    conn.close()
    return [dict(r) for r in rows]

def get_article_by_slug(slug):
    conn = get_db()
    row = conn.execute('SELECT * FROM articles WHERE slug = ?', (slug,)).fetchone()
    conn.close()
    return dict(row) if row else None

def get_article_by_id(article_id):
    conn = get_db()
    row = conn.execute('SELECT * FROM articles WHERE id = ?', (article_id,)).fetchone()
    conn.close()
    return dict(row) if row else None

def create_article(slug, title_zh, title_en, content='', excerpt_zh='', excerpt_en='',
                   cover_image='', published=1):
    conn = get_db()
    conn.execute('''
        INSERT INTO articles (slug, title_zh, title_en, content, excerpt_zh, excerpt_en,
                              cover_image, published, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
    ''', (slug, title_zh, title_en, content, excerpt_zh, excerpt_en, cover_image, published))
    conn.commit()
    article_id = conn.execute('SELECT last_insert_rowid()').fetchone()[0]
    conn.close()
    return article_id

def update_article(article_id, **kwargs):
    allowed = ['slug', 'title_zh', 'title_en', 'content', 'excerpt_zh', 'excerpt_en',
               'cover_image', 'published']
    updates = {k: v for k, v in kwargs.items() if k in allowed}
    if not updates:
        return
    updates['updated_at'] = 'CURRENT_TIMESTAMP'
    set_clause = ', '.join(f'{k} = ?' for k in updates)
    # Handle CURRENT_TIMESTAMP specially
    set_parts = []
    values = []
    for k, v in updates.items():
        if v == 'CURRENT_TIMESTAMP':
            set_parts.append(f'{k} = CURRENT_TIMESTAMP')
        else:
            set_parts.append(f'{k} = ?')
            values.append(v)
    values.append(article_id)
    conn = get_db()
    conn.execute(f'UPDATE articles SET {", ".join(set_parts)} WHERE id = ?', values)
    conn.commit()
    conn.close()

def delete_article(article_id):
    conn = get_db()
    conn.execute('DELETE FROM articles WHERE id = ?', (article_id,))
    conn.commit()
    conn.close()

# ── Projects ──────────────────────────────────────────

def get_projects(published_only=True):
    conn = get_db()
    if published_only:
        rows = conn.execute(
            'SELECT * FROM projects WHERE published = 1 ORDER BY sort_order, created_at DESC'
        ).fetchall()
    else:
        rows = conn.execute(
            'SELECT * FROM projects ORDER BY sort_order, created_at DESC'
        ).fetchall()
    conn.close()
    results = []
    for r in rows:
        d = dict(r)
        d['tags'] = json.loads(d.get('tags', '[]'))
        results.append(d)
    return results

def get_project_by_slug(slug):
    conn = get_db()
    row = conn.execute('SELECT * FROM projects WHERE slug = ?', (slug,)).fetchone()
    conn.close()
    if row:
        d = dict(row)
        d['tags'] = json.loads(d.get('tags', '[]'))
        return d
    return None

def get_project_by_id(project_id):
    conn = get_db()
    row = conn.execute('SELECT * FROM projects WHERE id = ?', (project_id,)).fetchone()
    conn.close()
    if row:
        d = dict(row)
        d['tags'] = json.loads(d.get('tags', '[]'))
        return d
    return None

def create_project(slug, name_zh, name_en, desc_zh='', desc_en='', intro_content='',
                   tags=None, github_url='', external_url='', icon='📦',
                   cover_image='', published=1, sort_order=0):
    conn = get_db()
    conn.execute('''
        INSERT INTO projects (slug, name_zh, name_en, desc_zh, desc_en, intro_content,
                              tags, github_url, external_url, icon, cover_image,
                              published, sort_order, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
    ''', (slug, name_zh, name_en, desc_zh, desc_en, intro_content,
          json.dumps(tags or []), github_url, external_url, icon,
          cover_image, published, sort_order))
    conn.commit()
    project_id = conn.execute('SELECT last_insert_rowid()').fetchone()[0]
    conn.close()
    return project_id

def update_project(project_id, **kwargs):
    allowed = ['slug', 'name_zh', 'name_en', 'desc_zh', 'desc_en', 'intro_content',
               'tags', 'github_url', 'external_url', 'icon', 'cover_image',
               'published', 'sort_order']
    updates = {k: v for k, v in kwargs.items() if k in allowed}
    if not updates:
        return
    if 'tags' in updates:
        updates['tags'] = json.dumps(updates['tags'])
    set_clause = ', '.join(f'{k} = ?' for k in updates)
    values = list(updates.values()) + [project_id]
    conn = get_db()
    conn.execute(f'UPDATE projects SET {set_clause}, updated_at = CURRENT_TIMESTAMP WHERE id = ?', values)
    conn.commit()
    conn.close()

def delete_project(project_id):
    conn = get_db()
    conn.execute('DELETE FROM projects WHERE id = ?', (project_id,))
    conn.commit()
    conn.close()

# ── Media ─────────────────────────────────────────────

def save_media(filename, original_name, mime_type, file_size, article_id=None, project_id=None):
    conn = get_db()
    conn.execute('''
        INSERT INTO media (filename, original_name, mime_type, file_size, article_id, project_id)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (filename, original_name, mime_type, file_size, article_id, project_id))
    conn.commit()
    media_id = conn.execute('SELECT last_insert_rowid()').fetchone()[0]
    conn.close()
    return media_id

def get_media_for_article(article_id):
    conn = get_db()
    rows = conn.execute(
        'SELECT * FROM media WHERE article_id = ? ORDER BY created_at DESC', (article_id,)
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]

def get_media_for_project(project_id):
    conn = get_db()
    rows = conn.execute(
        'SELECT * FROM media WHERE project_id = ? ORDER BY created_at DESC', (project_id,)
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]

# ── Users / Auth ──────────────────────────────────────

def get_user_by_username(username):
    conn = get_db()
    row = conn.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
    conn.close()
    return dict(row) if row else None

def create_user(username, password_hash):
    conn = get_db()
    conn.execute('INSERT INTO users (username, password_hash) VALUES (?, ?)',
                 (username, password_hash))
    conn.commit()
    conn.close()

def create_session(user_id, token, expires_at):
    conn = get_db()
    conn.execute(
        'INSERT INTO sessions (user_id, token, expires_at) VALUES (?, ?, ?)',
        (user_id, token, expires_at)
    )
    conn.commit()
    conn.close()

def get_session(token):
    conn = get_db()
    row = conn.execute(
        "SELECT * FROM sessions WHERE token = ? AND expires_at > datetime('now')",
        (token,)
    ).fetchone()
    conn.close()
    return dict(row) if row else None

def delete_session(token):
    conn = get_db()
    conn.execute('DELETE FROM sessions WHERE token = ?', (token,))
    conn.commit()
    conn.close()

def cleanup_expired_sessions():
    conn = get_db()
    conn.execute("DELETE FROM sessions WHERE expires_at <= datetime('now')")
    conn.commit()
    conn.close()

# ── Stats ─────────────────────────────────────────────

def get_stats():
    conn = get_db()
    msg_count = conn.execute('SELECT COUNT(*) FROM messages').fetchone()[0]
    art_count = conn.execute('SELECT COUNT(*) FROM articles WHERE published = 1').fetchone()[0]
    proj_count = conn.execute('SELECT COUNT(*) FROM projects WHERE published = 1').fetchone()[0]
    conn.close()
    return {
        'messages': msg_count,
        'articles': art_count,
        'projects': proj_count
    }


if __name__ == '__main__':
    init_db()
    print("Database initialized at", DB_PATH)

#!/usr/bin/env python3
"""
Laodang's Genesis Block — Main Server
A personal website with password-protected admin backend.
Built with Python stdlib + Jinja2 + Markdown + bcrypt.
"""
import http.server
import json
import os
import re
import sys
import mimetypes
import urllib.parse
import traceback
import io
import uuid as uuid_lib
from datetime import datetime, timedelta
from pathlib import Path

# Local imports
from db import (init_db, save_message, get_messages, delete_message, count_messages,
                get_articles, get_article_by_slug, get_article_by_id,
                create_article, update_article, delete_article,
                get_projects, get_project_by_slug, get_project_by_id,
                create_project, update_project, delete_project,
                save_media, get_media_for_article, get_media_for_project,
                get_stats)
from auth import authenticate, check_session, logout, ensure_admin, hash_password

# Jinja2 setup
from jinja2 import Environment, FileSystemLoader, select_autoescape

# Markdown setup
import markdown as md_lib

# ── Configuration ─────────────────────────────────────
HOST = '0.0.0.0'
PORT = int(os.environ.get('PORT', 8080))
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TEMPLATE_DIR = os.path.join(BASE_DIR, 'templates')
UPLOADS_DIR = os.path.join(BASE_DIR, 'uploads')
DATA_DIR = os.path.join(BASE_DIR, 'data')
COOKIE_NAME = 'lb_session'
SESSION_EXPIRY_HOURS = 24
MAX_UPLOAD_SIZE = 100 * 1024 * 1024  # 100MB

os.makedirs(UPLOADS_DIR, exist_ok=True)
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(TEMPLATE_DIR, exist_ok=True)

# ── Jinja2 Environment ─────────────────────────────────
jinja_env = Environment(
    loader=FileSystemLoader(TEMPLATE_DIR),
    autoescape=select_autoescape(['html', 'xml'])
)

def render_template(template_name, **context):
    """Render a Jinja2 template with context."""
    template = jinja_env.get_template(template_name)
    return template.render(**context)

# ── Helpers ────────────────────────────────────────────

def json_response(handler, data, status=200):
    """Send a JSON response."""
    body = json.dumps(data, ensure_ascii=False, default=str).encode('utf-8')
    handler.send_response(status)
    handler.send_header('Content-Type', 'application/json; charset=utf-8')
    handler.send_header('Content-Length', len(body))
    handler.send_header('Access-Control-Allow-Origin', '*')
    handler.end_headers()
    handler.wfile.write(body)

def html_response(handler, html_str, status=200):
    """Send an HTML response."""
    body = html_str.encode('utf-8')
    handler.send_response(status)
    handler.send_header('Content-Type', 'text/html; charset=utf-8')
    handler.send_header('Content-Length', len(body))
    handler.end_headers()
    handler.wfile.write(body)

def redirect(handler, location, status=302):
    """Send a redirect response."""
    handler.send_response(status)
    handler.send_header('Location', location)
    handler.end_headers()

def parse_cookies(handler):
    """Parse cookies from request headers."""
    cookie_header = handler.headers.get('Cookie', '')
    cookies = {}
    for part in cookie_header.split(';'):
        part = part.strip()
        if '=' in part:
            key, value = part.split('=', 1)
            cookies[key.strip()] = value.strip()
    return cookies

def set_cookie(handler, name, value, max_age=None, path='/', httponly=True):
    """Set a cookie in the response."""
    cookie = f'{name}={value}; Path={path}'
    if max_age:
        cookie += f'; Max-Age={max_age}'
    if httponly:
        cookie += '; HttpOnly'
    cookie += '; SameSite=Lax'
    handler.send_header('Set-Cookie', cookie)

def delete_cookie(handler, name, path='/'):
    """Delete a cookie."""
    cookie = f'{name}=; Path={path}; Max-Age=0; HttpOnly; SameSite=Lax'
    handler.send_header('Set-Cookie', cookie)

def get_current_user(handler):
    """Get the currently logged-in user from session cookie."""
    cookies = parse_cookies(handler)
    token = cookies.get(COOKIE_NAME)
    if token:
        return check_session(token)
    return None

def require_admin(handler):
    """Check if user is logged in. If not, redirect or return 401."""
    user = get_current_user(handler)
    if not user:
        # Check if this is an API request
        path = handler.path.split('?')[0]
        if path.startswith('/api/'):
            json_response(handler, {'error': 'Unauthorized'}, 401)
        else:
            redirect(handler, '/admin/login')
        return None
    return user

def parse_multipart(handler):
    """Parse multipart/form-data request body.
    Returns (fields_dict, files_list) where files = [{name, filename, data, content_type}]
    """
    content_type = handler.headers.get('Content-Type', '')
    if 'multipart/form-data' not in content_type:
        return None, None

    # Extract boundary
    match = re.search(r'boundary=([^;]+)', content_type)
    if not match:
        return None, None
    boundary = match.group(1).encode('utf-8')

    # Read body
    content_length = int(handler.headers.get('Content-Length', 0))
    if content_length > MAX_UPLOAD_SIZE:
        return None, None
    body = handler.rfile.read(content_length)

    # Parse multipart
    fields = {}
    files = []
    parts = body.split(b'--' + boundary)

    for part in parts:
        if part in (b'', b'--', b'--\r\n'):
            continue
        # Split headers and body
        if b'\r\n\r\n' in part:
            headers_section, part_body = part.split(b'\r\n\r\n', 1)
        else:
            continue

        # Remove trailing boundary
        if part_body.endswith(b'\r\n'):
            part_body = part_body[:-2]
        # Remove trailing \r\n--boundary
        end_marker = b'\r\n--' + boundary
        if end_marker in part_body:
            part_body = part_body[:part_body.index(end_marker)]

        headers_text = headers_section.decode('utf-8', errors='replace')
        # Parse Content-Disposition
        cd_match = re.search(r'Content-Disposition:\s*form-data;\s*name="([^"]*)"(?:\s*;\s*filename="([^"]*)")?',
                             headers_text, re.IGNORECASE)
        if not cd_match:
            continue

        field_name = cd_match.group(1)
        filename = cd_match.group(2)

        # Parse Content-Type
        ct_match = re.search(r'Content-Type:\s*([^\r\n]+)', headers_text, re.IGNORECASE)
        field_content_type = ct_match.group(1).strip() if ct_match else 'text/plain'

        if filename:
            files.append({
                'name': field_name,
                'filename': filename,
                'data': part_body,
                'content_type': field_content_type
            })
        else:
            fields[field_name] = part_body.decode('utf-8', errors='replace')

    return fields, files

def serve_static_file(handler, filepath):
    """Serve a static file with proper MIME type."""
    full_path = os.path.join(BASE_DIR, filepath.lstrip('/'))
    # Security: prevent directory traversal
    full_path = os.path.normpath(full_path)
    if not full_path.startswith(os.path.normpath(BASE_DIR)):
        handler.send_error(403)
        return

    if not os.path.isfile(full_path):
        handler.send_error(404)
        return

    mime_type, _ = mimetypes.guess_type(full_path)
    if mime_type is None:
        mime_type = 'application/octet-stream'

    file_size = os.path.getsize(full_path)
    handler.send_response(200)
    handler.send_header('Content-Type', mime_type)
    handler.send_header('Content-Length', file_size)
    # Cache static assets
    if mime_type.startswith(('image/', 'font/', 'text/css', 'application/javascript')):
        handler.send_header('Cache-Control', 'public, max-age=86400')
    handler.end_headers()

    with open(full_path, 'rb') as f:
        while True:
            chunk = f.read(65536)
            if not chunk:
                break
            handler.wfile.write(chunk)

# ── API Handlers ───────────────────────────────────────

def handle_api_messages_get(handler, user):
    """GET /api/messages — Admin only."""
    if not user:
        return json_response(handler, {'error': 'Unauthorized'}, 401)
    messages = get_messages()
    return json_response(handler, {'messages': messages, 'total': len(messages)})

def handle_api_messages_post(handler, user):
    """POST /api/messages — Public, submit a message."""
    content_length = int(handler.headers.get('Content-Length', 0))
    body = handler.rfile.read(content_length)
    try:
        data = json.loads(body.decode('utf-8'))
    except (json.JSONDecodeError, UnicodeDecodeError):
        return json_response(handler, {'error': 'Invalid JSON'}, 400)

    name = (data.get('name') or '').strip()
    email = (data.get('email') or '').strip()
    body_text = (data.get('body') or '').strip()

    if not body_text:
        return json_response(handler, {'error': 'Message body required'}, 400)

    save_message(name, email, body_text)
    return json_response(handler, {'ok': True, 'message': 'Message sent'})

def handle_api_messages_delete(handler, user, msg_id):
    """DELETE /api/messages/:id — Admin only."""
    if not user:
        return json_response(handler, {'error': 'Unauthorized'}, 401)
    delete_message(msg_id)
    return json_response(handler, {'ok': True})

def handle_api_articles_get(handler, user):
    """GET /api/articles — Public, returns article list."""
    articles = get_articles(published_only=not user)
    # Strip content for list view (too heavy)
    for a in articles:
        a.pop('content', None)
    return json_response(handler, {'articles': articles})

def handle_api_articles_post(handler, user):
    """POST /api/articles — Admin only, create article."""
    if not user:
        return json_response(handler, {'error': 'Unauthorized'}, 401)

    content_length = int(handler.headers.get('Content-Length', 0))
    body = handler.rfile.read(content_length)
    try:
        data = json.loads(body.decode('utf-8'))
    except (json.JSONDecodeError, UnicodeDecodeError):
        return json_response(handler, {'error': 'Invalid JSON'}, 400)

    slug = (data.get('slug') or '').strip()
    title_zh = (data.get('title_zh') or '').strip()
    title_en = (data.get('title_en') or '').strip()

    if not slug or not title_zh:
        return json_response(handler, {'error': 'slug and title_zh required'}, 400)

    # Check slug uniqueness
    existing = get_article_by_slug(slug)
    if existing:
        return json_response(handler, {'error': 'Slug already exists'}, 409)

    article_id = create_article(
        slug=slug,
        title_zh=title_zh,
        title_en=title_en,
        content=data.get('content', ''),
        excerpt_zh=data.get('excerpt_zh', ''),
        excerpt_en=data.get('excerpt_en', ''),
        cover_image=data.get('cover_image', ''),
        published=data.get('published', 1)
    )
    return json_response(handler, {'ok': True, 'id': article_id}, 201)

def handle_api_article_detail(handler, user, article_id_or_slug):
    """GET /api/articles/:id_or_slug — Public, with content."""
    # Try numeric ID first
    if article_id_or_slug.isdigit():
        article = get_article_by_id(int(article_id_or_slug))
    else:
        article = get_article_by_slug(article_id_or_slug)

    if not article:
        return json_response(handler, {'error': 'Not found'}, 404)
    if not article.get('published') and not user:
        return json_response(handler, {'error': 'Not found'}, 404)

    return json_response(handler, {'article': article})

def handle_api_article_update(handler, user, article_id):
    """PUT /api/articles/:id — Admin only."""
    if not user:
        return json_response(handler, {'error': 'Unauthorized'}, 401)

    content_length = int(handler.headers.get('Content-Length', 0))
    body = handler.rfile.read(content_length)
    try:
        data = json.loads(body.decode('utf-8'))
    except (json.JSONDecodeError, UnicodeDecodeError):
        return json_response(handler, {'error': 'Invalid JSON'}, 400)

    update_article(int(article_id), **data)
    return json_response(handler, {'ok': True})

def handle_api_article_delete(handler, user, article_id):
    """DELETE /api/articles/:id — Admin only."""
    if not user:
        return json_response(handler, {'error': 'Unauthorized'}, 401)
    delete_article(int(article_id))
    return json_response(handler, {'ok': True})

def handle_api_projects_get(handler, user):
    """GET /api/projects — Public."""
    projects = get_projects(published_only=not user)
    return json_response(handler, {'projects': projects})

def handle_api_projects_post(handler, user):
    """POST /api/projects — Admin only."""
    if not user:
        return json_response(handler, {'error': 'Unauthorized'}, 401)

    content_length = int(handler.headers.get('Content-Length', 0))
    body = handler.rfile.read(content_length)
    try:
        data = json.loads(body.decode('utf-8'))
    except (json.JSONDecodeError, UnicodeDecodeError):
        return json_response(handler, {'error': 'Invalid JSON'}, 400)

    slug = (data.get('slug') or '').strip()
    name_zh = (data.get('name_zh') or '').strip()
    name_en = (data.get('name_en') or '').strip()

    if not slug or not name_zh:
        return json_response(handler, {'error': 'slug and name_zh required'}, 400)

    existing = get_project_by_slug(slug)
    if existing:
        return json_response(handler, {'error': 'Slug already exists'}, 409)

    project_id = create_project(
        slug=slug,
        name_zh=name_zh,
        name_en=name_en,
        desc_zh=data.get('desc_zh', ''),
        desc_en=data.get('desc_en', ''),
        intro_content=data.get('intro_content', ''),
        tags=data.get('tags', []),
        github_url=data.get('github_url', ''),
        external_url=data.get('external_url', ''),
        icon=data.get('icon', '📦'),
        cover_image=data.get('cover_image', ''),
        published=data.get('published', 1),
        sort_order=data.get('sort_order', 0)
    )
    return json_response(handler, {'ok': True, 'id': project_id}, 201)

def handle_api_project_detail(handler, user, project_id_or_slug):
    """GET /api/projects/:id_or_slug — Public."""
    if project_id_or_slug.isdigit():
        project = get_project_by_id(int(project_id_or_slug))
    else:
        project = get_project_by_slug(project_id_or_slug)

    if not project:
        return json_response(handler, {'error': 'Not found'}, 404)
    if not project.get('published') and not user:
        return json_response(handler, {'error': 'Not found'}, 404)

    return json_response(handler, {'project': project})

def handle_api_project_update(handler, user, project_id):
    """PUT /api/projects/:id — Admin only."""
    if not user:
        return json_response(handler, {'error': 'Unauthorized'}, 401)

    content_length = int(handler.headers.get('Content-Length', 0))
    body = handler.rfile.read(content_length)
    try:
        data = json.loads(body.decode('utf-8'))
    except (json.JSONDecodeError, UnicodeDecodeError):
        return json_response(handler, {'error': 'Invalid JSON'}, 400)

    update_project(int(project_id), **data)
    return json_response(handler, {'ok': True})

def handle_api_project_delete(handler, user, project_id):
    """DELETE /api/projects/:id — Admin only."""
    if not user:
        return json_response(handler, {'error': 'Unauthorized'}, 401)
    delete_project(int(project_id))
    return json_response(handler, {'ok': True})

def handle_api_upload(handler, user):
    """POST /api/upload — Admin only, multipart file upload."""
    if not user:
        return json_response(handler, {'error': 'Unauthorized'}, 401)

    fields, files = parse_multipart(handler)
    if files is None:
        return json_response(handler, {'error': 'Invalid multipart data'}, 400)

    if not files:
        return json_response(handler, {'error': 'No files uploaded'}, 400)

    uploaded = []
    for f in files:
        # Generate unique filename
        ext = os.path.splitext(f['filename'])[1] or ''
        unique_name = f"{uuid_lib.uuid4().hex}{ext}"
        filepath = os.path.join(UPLOADS_DIR, unique_name)

        with open(filepath, 'wb') as fout:
            fout.write(f['data'])

        # Determine type
        mime_type = f['content_type']
        if mime_type.startswith('image/'):
            media_type = 'image'
        elif mime_type.startswith('video/'):
            media_type = 'video'
        else:
            media_type = 'file'

        media_id = save_media(
            filename=unique_name,
            original_name=f['filename'],
            mime_type=mime_type,
            file_size=len(f['data'])
        )

        uploaded.append({
            'id': media_id,
            'filename': unique_name,
            'original_name': f['filename'],
            'url': f'/uploads/{unique_name}',
            'type': media_type,
            'mime_type': mime_type,
            'size': len(f['data'])
        })

    return json_response(handler, {'ok': True, 'files': uploaded})

def handle_api_stats(handler, user):
    """GET /api/stats — Admin only."""
    if not user:
        return json_response(handler, {'error': 'Unauthorized'}, 401)
    return json_response(handler, get_stats())

# ── Auth Handlers ──────────────────────────────────────

def handle_admin_login_get(handler):
    """GET /admin/login — Login page."""
    user = get_current_user(handler)
    if user:
        return redirect(handler, '/admin')
    html = render_template('admin/login.html', error=None)
    html_response(handler, html)

def handle_admin_login_post(handler):
    """POST /admin/login — Process login."""
    content_length = int(handler.headers.get('Content-Length', 0))
    body = handler.rfile.read(content_length)
    try:
        data = json.loads(body.decode('utf-8'))
    except (json.JSONDecodeError, UnicodeDecodeError):
        # Try form-encoded
        data = {}
        for pair in body.decode('utf-8', errors='replace').split('&'):
            if '=' in pair:
                k, v = pair.split('=', 1)
                data[urllib.parse.unquote(k)] = urllib.parse.unquote(v)

    username = data.get('username', '').strip()
    password = data.get('password', '').strip()

    token = authenticate(username, password)
    if token:
        # Check if it's an API request
        if handler.path.startswith('/api/'):
            set_cookie(handler, COOKIE_NAME, token, max_age=SESSION_EXPIRY_HOURS * 3600)
            return json_response(handler, {'ok': True, 'redirect': '/admin'})
        else:
            handler.send_response(302)
            set_cookie(handler, COOKIE_NAME, token, max_age=SESSION_EXPIRY_HOURS * 3600)
            handler.send_header('Location', '/admin')
            handler.end_headers()
            return
    else:
        if handler.path.startswith('/api/'):
            return json_response(handler, {'error': 'Invalid credentials'}, 401)
        html = render_template('admin/login.html', error='用户名或密码错误')
        html_response(handler, html)

def handle_admin_logout(handler):
    """GET /admin/logout"""
    cookies = parse_cookies(handler)
    token = cookies.get(COOKIE_NAME)
    if token:
        logout(token)
    handler.send_response(302)
    delete_cookie(handler, COOKIE_NAME)
    handler.send_header('Location', '/admin/login')
    handler.end_headers()

def handle_admin_dashboard(handler, user):
    """GET /admin — Admin dashboard."""
    if not user:
        return redirect(handler, '/admin/login')
    stats = get_stats()
    html = render_template('admin/dashboard.html', user=user, stats=stats)
    html_response(handler, html)

def handle_admin_messages(handler, user):
    """GET /admin/messages — View messages page."""
    if not user:
        return redirect(handler, '/admin/login')
    messages = get_messages()
    html = render_template('admin/messages.html', user=user, messages=messages)
    html_response(handler, html)

def handle_admin_articles_page(handler, user):
    """GET /admin/articles — Manage articles page."""
    if not user:
        return redirect(handler, '/admin/login')
    articles = get_articles(published_only=False)
    html = render_template('admin/articles.html', user=user, articles=articles)
    html_response(handler, html)

def handle_admin_projects_page(handler, user):
    """GET /admin/projects — Manage projects page."""
    if not user:
        return redirect(handler, '/admin/login')
    projects = get_projects(published_only=False)
    html = render_template('admin/projects.html', user=user, projects=projects)
    html_response(handler, html)

def handle_admin_editor(handler, user):
    """GET /admin/editor — Article/project editor."""
    if not user:
        return redirect(handler, '/admin/login')
    html = render_template('admin/editor.html', user=user)
    html_response(handler, html)

# ── Public Page Handlers ───────────────────────────────

def handle_article_page(handler, slug):
    """GET /articles/:slug — Public article detail page."""
    article = get_article_by_slug(slug)
    if not article or not article.get('published'):
        handler.send_error(404)
        return

    # Render markdown to HTML
    content_html = md_lib.markdown(
        article['content'],
        extensions=['extra', 'codehilite', 'tables', 'fenced_code']
    )

    html = render_template('article.html', article=article, content_html=content_html)
    html_response(handler, html)

def handle_project_page(handler, slug):
    """GET /projects/:slug — Public project intro page."""
    project = get_project_by_slug(slug)
    if not project or not project.get('published'):
        handler.send_error(404)
        return

    # Render intro content markdown to HTML
    intro_html = md_lib.markdown(
        project['intro_content'] or '',
        extensions=['extra', 'codehilite', 'tables', 'fenced_code']
    ) if project['intro_content'] else ''

    html = render_template('project.html', project=project, intro_html=intro_html)
    html_response(handler, html)

# ── Main Request Handler ───────────────────────────────

class RequestHandler(http.server.BaseHTTPRequestHandler):

    def log_message(self, format, *args):
        """Suppress default logging; use our own."""
        pass

    def do_OPTIONS(self):
        """Handle CORS preflight."""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        self.end_headers()

    def do_GET(self):
        path = self.path.split('?')[0]
        user = get_current_user(self)

        # API Routes
        if path == '/api/messages':
            return handle_api_messages_get(self, user)
        if path == '/api/articles':
            return handle_api_articles_get(self, user)
        if path == '/api/projects':
            return handle_api_projects_get(self, user)
        if path == '/api/stats':
            return handle_api_stats(self, user)

        # API detail routes
        m = re.match(r'^/api/articles/(.+)$', path)
        if m:
            return handle_api_article_detail(self, user, m.group(1))
        m = re.match(r'^/api/projects/(.+)$', path)
        if m:
            return handle_api_project_detail(self, user, m.group(1))

        # Admin pages
        if path == '/admin/login':
            return handle_admin_login_get(self)
        if path == '/admin/logout':
            return handle_admin_logout(self)
        if path == '/admin' or path == '/admin/':
            return handle_admin_dashboard(self, user)
        if path == '/admin/messages':
            return handle_admin_messages(self, user)
        if path == '/admin/articles':
            return handle_admin_articles_page(self, user)
        if path == '/admin/projects':
            return handle_admin_projects_page(self, user)
        if path == '/admin/editor':
            return handle_admin_editor(self, user)

        # Public article detail pages
        m = re.match(r'^/articles/([a-z0-9\-]+)$', path)
        if m:
            return handle_article_page(self, m.group(1))

        # Public project detail pages
        m = re.match(r'^/projects/([a-z0-9\-]+)$', path)
        if m:
            return handle_project_page(self, m.group(1))

        # Static files and uploads
        if path.startswith('/uploads/'):
            return serve_static_file(self, path)

        # Default: serve static file or SPA fallback
        if path == '/' or path == '':
            path = '/index.html'

        filepath = path.lstrip('/')
        full_path = os.path.join(BASE_DIR, filepath)
        full_path = os.path.normpath(full_path)

        if not full_path.startswith(os.path.normpath(BASE_DIR)):
            self.send_error(403)
            return

        if os.path.isfile(full_path):
            return serve_static_file(self, path)
        elif os.path.isdir(full_path):
            # Try index.html in directory
            index_path = os.path.join(full_path, 'index.html')
            if os.path.isfile(index_path):
                return serve_static_file(self, path.rstrip('/') + '/index.html')

        # 404
        self.send_error(404)

    def do_POST(self):
        path = self.path.split('?')[0]
        user = get_current_user(self)

        # Auth
        if path == '/admin/login' or path == '/api/login':
            return handle_admin_login_post(self)

        # API
        if path == '/api/messages':
            return handle_api_messages_post(self, user)
        if path == '/api/articles':
            return handle_api_articles_post(self, user)
        if path == '/api/projects':
            return handle_api_projects_post(self, user)
        if path == '/api/upload':
            return handle_api_upload(self, user)

        self.send_error(404)

    def do_PUT(self):
        path = self.path.split('?')[0]
        user = get_current_user(self)

        m = re.match(r'^/api/articles/(\d+)$', path)
        if m:
            return handle_api_article_update(self, user, m.group(1))
        m = re.match(r'^/api/projects/(\d+)$', path)
        if m:
            return handle_api_project_update(self, user, m.group(1))

        self.send_error(404)

    def do_DELETE(self):
        path = self.path.split('?')[0]
        user = get_current_user(self)

        m = re.match(r'^/api/messages/(\d+)$', path)
        if m:
            return handle_api_messages_delete(self, user, m.group(1))
        m = re.match(r'^/api/articles/(\d+)$', path)
        if m:
            return handle_api_article_delete(self, user, m.group(1))
        m = re.match(r'^/api/projects/(\d+)$', path)
        if m:
            return handle_api_project_delete(self, user, m.group(1))

        self.send_error(404)


# ── Entry Point ────────────────────────────────────────

def main():
    # Migration: init DB and seed if needed
    init_db()
    from db import get_db
    conn = get_db()
    user_count = conn.execute('SELECT COUNT(*) FROM users').fetchone()[0]
    conn.close()
    if user_count == 0:
        print("No admin user found. Running seed...")
        import subprocess
        subprocess.run([sys.executable, os.path.join(BASE_DIR, 'seed.py')])

    print(f"\n{'='*60}")
    print(f"  老铛的创世区块 — Server")
    print(f"  http://localhost:{PORT}")
    print(f"  Admin: http://localhost:{PORT}/admin")
    print(f"{'='*60}\n")

    server = http.server.HTTPServer((HOST, PORT), RequestHandler)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down...")
        server.shutdown()

if __name__ == '__main__':
    main()

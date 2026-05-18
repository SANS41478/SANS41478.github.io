#!/usr/bin/env python3
"""
MCP Server for Laodang's Genesis Block admin management.
Provides tools to manage messages, articles, projects, media, and stats.
"""

import json
import os
import asyncio
import httpx
from pathlib import Path

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

# ── Configuration ─────────────────────────────────────
SITE_URL = os.environ.get("LAODANG_SITE_URL", "https://laodang.asia")
ADMIN_USER = os.environ.get("LAODANG_ADMIN_USER", "laodang")
ADMIN_PASS = os.environ.get("LAODANG_ADMIN_PASS", "")

# ── Session state ─────────────────────────────────────
_session_cookie: str | None = None
_client: httpx.AsyncClient | None = None


def get_client() -> httpx.AsyncClient:
    global _client
    if _client is None:
        _client = httpx.AsyncClient(
            timeout=httpx.Timeout(30.0),
            trust_env=False,  # 忽略 HTTP_PROXY/HTTPS_PROXY 等代理环境变量
        )
    return _client


async def ensure_auth() -> bool:
    """Ensure we have a valid admin session. Returns True if authenticated."""
    global _session_cookie

    client = get_client()

    # Check if current session is still valid
    if _session_cookie:
        try:
            resp = await client.get(
                f"{SITE_URL}/api/stats",
                cookies={"lb_session": _session_cookie},
            )
            if resp.status_code == 200:
                return True
        except Exception:
            pass

    # Need to login
    if not ADMIN_PASS:
        return False

    try:
        resp = await client.post(
            f"{SITE_URL}/api/login",
            json={"username": ADMIN_USER, "password": ADMIN_PASS},
        )
        if resp.status_code == 200:
            # Extract cookie from response
            for cookie in resp.headers.get_list("set-cookie"):
                if cookie.startswith("lb_session="):
                    _session_cookie = cookie.split(";")[0].split("=", 1)[1]
                    return True

        # Try form-encoded as fallback
        resp2 = await client.post(
            f"{SITE_URL}/admin/login",
            data={"username": ADMIN_USER, "password": ADMIN_PASS},
        )
        if resp2.status_code in (200, 302):
            for cookie in resp2.headers.get_list("set-cookie"):
                if cookie.startswith("lb_session="):
                    _session_cookie = cookie.split(";")[0].split("=", 1)[1]
                    return True
    except Exception as e:
        pass

    return False


async def api_get(path: str) -> dict:
    """Make an authenticated GET request."""
    client = get_client()
    cookies = {"lb_session": _session_cookie} if _session_cookie else {}
    resp = await client.get(f"{SITE_URL}{path}", cookies=cookies)
    if resp.status_code == 401:
        if await ensure_auth():
            cookies = {"lb_session": _session_cookie}
            resp = await client.get(f"{SITE_URL}{path}", cookies=cookies)
    return resp.json() if resp.status_code == 200 else {"error": resp.text, "status": resp.status_code}


async def api_post(path: str, data: dict) -> dict:
    """Make an authenticated POST request."""
    client = get_client()
    cookies = {"lb_session": _session_cookie} if _session_cookie else {}
    resp = await client.post(f"{SITE_URL}{path}", json=data, cookies=cookies)
    if resp.status_code == 401:
        if await ensure_auth():
            cookies = {"lb_session": _session_cookie}
            resp = await client.post(f"{SITE_URL}{path}", json=data, cookies=cookies)
    if resp.status_code == 200:
        try:
            return resp.json()
        except Exception:
            return {"ok": True}
    return {"error": resp.text, "status": resp.status_code}


async def api_put(path: str, data: dict) -> dict:
    """Make an authenticated PUT request."""
    client = get_client()
    cookies = {"lb_session": _session_cookie} if _session_cookie else {}
    resp = await client.put(f"{SITE_URL}{path}", json=data, cookies=cookies)
    if resp.status_code == 401:
        if await ensure_auth():
            cookies = {"lb_session": _session_cookie}
            resp = await client.put(f"{SITE_URL}{path}", json=data, cookies=cookies)
    if resp.status_code == 200:
        try:
            return resp.json()
        except Exception:
            return {"ok": True}
    return {"error": resp.text, "status": resp.status_code}


async def api_delete(path: str) -> dict:
    """Make an authenticated DELETE request."""
    client = get_client()
    cookies = {"lb_session": _session_cookie} if _session_cookie else {}
    resp = await client.delete(f"{SITE_URL}{path}", cookies=cookies)
    if resp.status_code == 401:
        if await ensure_auth():
            cookies = {"lb_session": _session_cookie}
            resp = await client.delete(f"{SITE_URL}{path}", cookies=cookies)
    if resp.status_code == 200:
        try:
            return resp.json()
        except Exception:
            return {"ok": True}
    return {"error": resp.text, "status": resp.status_code}


# ── MCP Server ─────────────────────────────────────────

server = Server("laodang-admin")


@server.list_tools()
async def list_tools() -> list[Tool]:
    return [
        # ── Messages ──
        Tool(
            name="messages_list",
            description="列出所有留言（需要管理员权限）",
            inputSchema={"type": "object", "properties": {}, "required": []},
        ),
        Tool(
            name="messages_delete",
            description="删除指定留言（需要管理员权限）",
            inputSchema={
                "type": "object",
                "properties": {
                    "message_id": {
                        "type": "integer",
                        "description": "要删除的留言ID",
                    }
                },
                "required": ["message_id"],
            },
        ),
        # ── Articles ──
        Tool(
            name="articles_list",
            description="列出所有文章，管理员可以看到未发布的草稿",
            inputSchema={"type": "object", "properties": {}, "required": []},
        ),
        Tool(
            name="articles_get",
            description="根据ID或slug获取文章详情（含完整内容）",
            inputSchema={
                "type": "object",
                "properties": {
                    "id_or_slug": {
                        "type": "string",
                        "description": "文章的数字ID或slug",
                    }
                },
                "required": ["id_or_slug"],
            },
        ),
        Tool(
            name="articles_create",
            description="创建新文章（需要管理员权限）",
            inputSchema={
                "type": "object",
                "properties": {
                    "slug": {"type": "string", "description": "URL slug，如 hello-world"},
                    "title_zh": {"type": "string", "description": "中文标题"},
                    "title_en": {"type": "string", "description": "英文标题", "default": ""},
                    "content": {"type": "string", "description": "Markdown正文内容", "default": ""},
                    "excerpt_zh": {"type": "string", "description": "中文摘要", "default": ""},
                    "excerpt_en": {"type": "string", "description": "英文摘要", "default": ""},
                    "cover_image": {"type": "string", "description": "封面图URL", "default": ""},
                    "published": {"type": "integer", "description": "1=发布, 0=草稿", "default": 1},
                },
                "required": ["slug", "title_zh", "title_en"],
            },
        ),
        Tool(
            name="articles_update",
            description="更新文章（需要管理员权限）",
            inputSchema={
                "type": "object",
                "properties": {
                    "article_id": {"type": "integer", "description": "文章ID"},
                    "slug": {"type": "string", "description": "新的URL slug"},
                    "title_zh": {"type": "string", "description": "中文标题"},
                    "title_en": {"type": "string", "description": "英文标题"},
                    "content": {"type": "string", "description": "Markdown正文"},
                    "excerpt_zh": {"type": "string", "description": "中文摘要"},
                    "excerpt_en": {"type": "string", "description": "英文摘要"},
                    "cover_image": {"type": "string", "description": "封面图URL"},
                    "published": {"type": "integer", "description": "1=发布, 0=草稿"},
                },
                "required": ["article_id"],
            },
        ),
        Tool(
            name="articles_delete",
            description="删除文章及关联的媒体文件（需要管理员权限）",
            inputSchema={
                "type": "object",
                "properties": {
                    "article_id": {"type": "integer", "description": "要删除的文章ID"}
                },
                "required": ["article_id"],
            },
        ),
        # ── Projects ──
        Tool(
            name="projects_list",
            description="列出所有项目，管理员可以看到未发布的草稿",
            inputSchema={"type": "object", "properties": {}, "required": []},
        ),
        Tool(
            name="projects_get",
            description="根据ID或slug获取项目详情（含完整内容）",
            inputSchema={
                "type": "object",
                "properties": {
                    "id_or_slug": {
                        "type": "string",
                        "description": "项目的数字ID或slug",
                    }
                },
                "required": ["id_or_slug"],
            },
        ),
        Tool(
            name="projects_create",
            description="创建新项目（需要管理员权限）",
            inputSchema={
                "type": "object",
                "properties": {
                    "slug": {"type": "string", "description": "URL slug"},
                    "name_zh": {"type": "string", "description": "中文名称"},
                    "name_en": {"type": "string", "description": "英文名称", "default": ""},
                    "desc_zh": {"type": "string", "description": "中文描述", "default": ""},
                    "desc_en": {"type": "string", "description": "英文描述", "default": ""},
                    "intro_content": {"type": "string", "description": "Markdown介绍内容", "default": ""},
                    "tags": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "标签列表",
                        "default": [],
                    },
                    "github_url": {"type": "string", "description": "GitHub仓库地址", "default": ""},
                    "external_url": {"type": "string", "description": "外部链接", "default": ""},
                    "icon": {"type": "string", "description": "项目图标emoji", "default": "📦"},
                    "cover_image": {"type": "string", "description": "封面图URL", "default": ""},
                    "published": {"type": "integer", "description": "1=发布, 0=草稿", "default": 1},
                    "sort_order": {"type": "integer", "description": "排序权重", "default": 0},
                },
                "required": ["slug", "name_zh", "name_en"],
            },
        ),
        Tool(
            name="projects_update",
            description="更新项目（需要管理员权限）",
            inputSchema={
                "type": "object",
                "properties": {
                    "project_id": {"type": "integer", "description": "项目ID"},
                    "slug": {"type": "string", "description": "新的URL slug"},
                    "name_zh": {"type": "string", "description": "中文名称"},
                    "name_en": {"type": "string", "description": "英文名称"},
                    "desc_zh": {"type": "string", "description": "中文描述"},
                    "desc_en": {"type": "string", "description": "英文描述"},
                    "intro_content": {"type": "string", "description": "Markdown介绍"},
                    "tags": {"type": "array", "items": {"type": "string"}, "description": "标签列表"},
                    "github_url": {"type": "string", "description": "GitHub仓库"},
                    "external_url": {"type": "string", "description": "外部链接"},
                    "icon": {"type": "string", "description": "emoji图标"},
                    "cover_image": {"type": "string", "description": "封面图URL"},
                    "published": {"type": "integer", "description": "1=发布, 0=草稿"},
                    "sort_order": {"type": "integer", "description": "排序权重"},
                },
                "required": ["project_id"],
            },
        ),
        Tool(
            name="projects_delete",
            description="删除项目及关联的媒体文件（需要管理员权限）",
            inputSchema={
                "type": "object",
                "properties": {
                    "project_id": {"type": "integer", "description": "要删除的项目ID"}
                },
                "required": ["project_id"],
            },
        ),
        # ── Stats ──
        Tool(
            name="stats_get",
            description="获取网站统计数据：留言数、文章数、项目数（需要管理员权限）",
            inputSchema={"type": "object", "properties": {}, "required": []},
        ),
    ]


@server.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    # Ensure we're authenticated for admin operations
    # All tools require admin auth (so we can see unpublished drafts)
    if True:
        authed = await ensure_auth()
        if not authed:
            return [TextContent(
                type="text",
                text=json.dumps({
                    "error": "认证失败。请设置 LAODANG_ADMIN_USER 和 LAODANG_ADMIN_PASS 环境变量。"
                }, ensure_ascii=False, indent=2),
            )]

    result = {}

    try:
        # ── Messages ──
        if name == "messages_list":
            result = await api_get("/api/messages")
        elif name == "messages_delete":
            result = await api_delete(f"/api/messages/{arguments['message_id']}")

        # ── Articles ──
        elif name == "articles_list":
            result = await api_get("/api/articles")
        elif name == "articles_get":
            result = await api_get(f"/api/articles/{arguments['id_or_slug']}")
        elif name == "articles_create":
            result = await api_post("/api/articles", arguments)
        elif name == "articles_update":
            aid = arguments.pop("article_id")
            result = await api_put(f"/api/articles/{aid}", arguments)
        elif name == "articles_delete":
            result = await api_delete(f"/api/articles/{arguments['article_id']}")

        # ── Projects ──
        elif name == "projects_list":
            result = await api_get("/api/projects")
        elif name == "projects_get":
            result = await api_get(f"/api/projects/{arguments['id_or_slug']}")
        elif name == "projects_create":
            result = await api_post("/api/projects", arguments)
        elif name == "projects_update":
            pid = arguments.pop("project_id")
            result = await api_put(f"/api/projects/{pid}", arguments)
        elif name == "projects_delete":
            result = await api_delete(f"/api/projects/{arguments['project_id']}")

        # ── Stats ──
        elif name == "stats_get":
            result = await api_get("/api/stats")

        else:
            result = {"error": f"Unknown tool: {name}"}

    except Exception as e:
        result = {"error": str(e)}

    return [TextContent(
        type="text",
        text=json.dumps(result, ensure_ascii=False, indent=2),
    )]


async def main():
    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream, server.create_initialization_options())


if __name__ == "__main__":
    asyncio.run(main())

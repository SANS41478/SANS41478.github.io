"""
Seed script: Initialize database with admin user and migrate existing content.
Run with: python3 seed.py
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from db import init_db, create_article, create_project
from auth import ensure_admin

# ── Configuration ──
ADMIN_USERNAME = os.environ.get('ADMIN_USER', 'laodang')
ADMIN_PASSWORD = os.environ.get('ADMIN_PASS')
if not ADMIN_PASSWORD:
    import secrets
    ADMIN_PASSWORD = secrets.token_urlsafe(16)
    print(f"[seed] ADMIN_PASS not set — generated random password: {ADMIN_PASSWORD}")
    print("[seed] Set ADMIN_PASS environment variable to persist across restarts.")

def seed_articles():
    """Import existing articles from markdown files."""
    articles_dir = os.path.join(os.path.dirname(__file__), 'articles')
    if not os.path.isdir(articles_dir):
        print("No articles directory found, skipping.")
        return

    for fname in sorted(os.listdir(articles_dir)):
        if not fname.endswith('.md'):
            continue
        slug = fname.replace('.md', '')
        path = os.path.join(articles_dir, fname)
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Parse first line as title, second as date quote
        lines = content.strip().split('\n')
        title_zh = lines[0].replace('# ', '').strip() if lines[0].startswith('#') else slug
        title_en = title_zh  # Default; can be updated in admin

        # Extract excerpt (first paragraph after the header block)
        excerpt = ''
        in_header = True
        for line in lines[1:]:
            stripped = line.strip()
            if in_header:
                if stripped.startswith('>') or stripped == '' or stripped.startswith('#'):
                    continue
                in_header = False
            if stripped and not stripped.startswith('#') and not stripped.startswith('>'):
                excerpt = stripped[:200]
                break

        try:
            create_article(
                slug=slug,
                title_zh=title_zh,
                title_en=title_en,
                content=content,
                excerpt_zh=excerpt,
                excerpt_en=excerpt,
                published=1
            )
            print(f"  Imported article: {slug}")
        except Exception as e:
            print(f"  Skipped article {slug}: {e}")

def seed_projects():
    """Import sample project data."""
    sample_projects = [
        {
            'slug': 'demo-project-alpha',
            'name_zh': '示例项目 Alpha',
            'name_en': 'Demo Project Alpha',
            'desc_zh': '一个高性能的 Web 工具，用于自动化工作流处理。',
            'desc_en': 'A high-performance web tool for automated workflow processing.',
            'tags': ['TypeScript', 'React', 'Node.js'],
            'github_url': 'https://github.com',
            'icon': '🛠️',
            'intro_content': '''# 示例项目 Alpha

## 项目简介

这是一个高性能的 Web 工具，用于自动化工作流处理。基于 TypeScript + React + Node.js 构建。

## 核心功能

- 自动化工作流引擎
- 可视化流程编辑器
- 实时日志监控

## 技术栈

| 层级 | 技术 |
|------|------|
| 前端 | React + TypeScript |
| 后端 | Node.js + Express |
| 数据库 | PostgreSQL |

## 快速开始

```bash
git clone https://github.com/example/alpha
cd alpha
npm install
npm run dev
```

[前往 GitHub 仓库](https://github.com)
'''
        },
        {
            'slug': 'data-viz-dashboard',
            'name_zh': '数据可视化面板',
            'name_en': 'Data Viz Dashboard',
            'desc_zh': '实时数据监控与可视化仪表盘，支持多种图表类型。',
            'desc_en': 'Real-time data monitoring and visualization dashboard.',
            'tags': ['D3.js', 'WebSocket', 'Python'],
            'github_url': 'https://github.com',
            'icon': '📊',
        },
        {
            'slug': 'cli-toolkit',
            'name_zh': 'CLI 效率工具集',
            'name_en': 'CLI Toolkit',
            'desc_zh': '一组命令行效率工具，提升日常开发体验。',
            'desc_en': 'A collection of CLI productivity tools.',
            'tags': ['Rust', 'Shell', 'Linux'],
            'github_url': 'https://github.com',
            'icon': '🔧',
        },
    ]

    for proj in sample_projects:
        try:
            create_project(**proj)
            print(f"  Imported project: {proj['slug']}")
        except Exception as e:
            print(f"  Skipped project {proj['slug']}: {e}")


if __name__ == '__main__':
    print("Initializing database...")
    init_db()

    print(f"\nSetting up admin user '{ADMIN_USERNAME}'...")
    ensure_admin(ADMIN_USERNAME, ADMIN_PASSWORD)

    print("\nImporting articles...")
    seed_articles()

    print("\nImporting projects...")
    seed_projects()

    print("\nSeed complete! You can now start the server with: python3 server.py")

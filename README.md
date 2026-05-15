<h1 align="center">老铛的创世区块</h1>
<p align="center">Laodang's Genesis Block — 个人网站 · 博客 · 作品集</p>

---

一个自带后台的个人网站系统。公开侧展示文章、项目和联系方式，后台提供密码保护的文章编辑、项目管理、留言查看和媒体上传。

在线访问：[laodang.asia](https://laodang.asia)

## 功能

- **公开页面** — 首页、文章列表、文章详情、项目作品、联系方式、留言表单
- **后台管理** — 密码登录，仪表盘、留言查看、文章和项目的增删改
- **文章系统** — Markdown 编辑器 + 实时预览，图片/视频上传，服务端渲染详情页
- **项目展示** — 每个项目拥有独立介绍页，可链接到 GitHub、线上地址等
- **留言系统** — 访客提交后仅后台可见，服务端存储
- **中英双语** — 前端全量支持中英文切换
- **HTTPS** — 支持 Let's Encrypt 免费证书

## 技术栈

- **后端** — Python 3 + 标准库 HTTP Server
- **数据库** — SQLite（零配置，数据存为单文件）
- **模板** — Jinja2（后台及文章/项目详情页服务端渲染）
- **前端** — 原生 HTML / CSS / JS，shadcn/ui 风格暗色主题
- **认证** — bcrypt 密码哈希 + Cookie-based 会话
- **部署** — systemd 守护 + Nginx 反向代理
- **Markdown** — 服务端 Python-Markdown 渲染，编辑器端 marked.js 预览

## 文件结构

```
.
├── server.py           # HTTP 服务主入口（路由、API、会话）
├── db.py               # 数据库层（SQLite CRUD）
├── auth.py             # 认证模块（密码哈希、会话管理）
├── seed.py             # 初始化脚本（管理员账号、示例数据）
├── requirements.txt    # Python 依赖
├── laodang.service     # systemd 服务文件
├── deploy.sh           # 一键部署脚本
├── Procfile            # 平台部署声明
├── index.html          # 首页
├── projects.html       # 项目列表页
├── articles.html       # 文章列表页
├── css/style.css       # 全局样式
├── js/
│   ├── i18n.js         # 中英文词典 + 语言切换
│   └── common.js       # 前端逻辑（API 调用、留言表单、导航）
├── templates/
│   ├── admin/          # 后台模板（登录、仪表盘、编辑器等）
│   ├── article.html    # 文章详情页模板
│   └── project.html    # 项目介绍页模板
├── articles/           # Markdown 源文件（导入用）
├── uploads/            # 上传的媒体文件
└── data/               # SQLite 数据库
```

## 本地运行

```bash
# 安装依赖
pip install -r requirements.txt

# 初始化数据库 + 管理员账号
python seed.py

# 启动
python server.py
# → http://localhost:8080
# → 后台 http://localhost:8080/admin
```

管理员密码通过环境变量 `ADMIN_PASS` 设置，默认 `changeme`。首次运行 `seed.py` 会自动创建。

## 部署

项目包含一个 `deploy.sh` 脚本，适用于 CentOS / Alibaba Cloud Linux / RHEL 系列：

```bash
bash deploy.sh
```

会完成 Python 依赖安装、数据库初始化、systemd 服务注册和防火墙配置。部署后访问 `http://服务器IP:8080`。

配合 Nginx 反向代理可实现 80 端口访问和 HTTPS：

```bash
dnf install -y nginx
# 配置 /etc/nginx/conf.d/laodang.conf 反向代理到 127.0.0.1:8080
systemctl enable --now nginx
certbot --nginx -d your-domain.com     # HTTPS
```

## 自定义

- **联系信息** — 编辑 `js/common.js` 中的 `CONFIG.contact`
- **项目数据** — 通过后台 `/admin` 添加编辑，或调用 `/api/projects`
- **主题** — 修改 `css/style.css` 中的 CSS 变量
- **翻译** — 编辑 `js/i18n.js` 中的 `I18N` 词典

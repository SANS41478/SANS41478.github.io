# 老铛的创世区块 (Laodang's Genesis Block)

个人网站 + 博客 + 作品集。Python 后端 + SQLite + 原生前端。

## 架构

- **后端**: `server.py` — Python stdlib HTTP Server，Jinja2 模板，Markdown 渲染
- **数据库**: SQLite (`data/laodang.db`)，通过 `db.py` 访问
- **认证**: bcrypt 密码哈希，Cookie session (`lb_session`)，`auth.py`
- **前端**: 原生 HTML/CSS/JS，shadcn/ui 暗色主题，`js/i18n.js` 中英双语

## 常用操作

### 部署到服务器
```bash
# 推送到 main 后，同步文件到阿里云服务器并重启服务
scp -i "D:\xxxxx\fuwuqi.pem" <files> root@8.136.58.133:/opt/laodang/
ssh -i "D:\xxxxx\fuwuqi.pem" root@8.136.58.133 "systemctl restart laodang"
```

### 后台管理
- 管理后台: `http://8.136.58.133:8080/admin`
- MCP 工具: 通过 `mcp__laodang-admin__*` 系列工具直接操作后台
- 管理员密码存储在服务器 `/etc/systemd/system/laodang.service` 的 `ADMIN_PASS` 环境变量中

### 本地开发
```bash
pip install -r requirements.txt
python seed.py    # 初始化数据库
python server.py  # 启动 http://localhost:8080
```

## 文件要点

| 文件 | 作用 |
|------|------|
| `server.py` | 路由、API、认证、模板渲染 |
| `db.py` | SQLite CRUD（articles/projects/messages/users/sessions/media） |
| `auth.py` | bcrypt 密码哈希、session 管理 |
| `seed.py` | 初始化数据库和管理员账号 |
| `index.html` | 首页（Hero、关于、联系、留言） |
| `js/common.js` | `CONFIG.contact` 联系信息、API 调用、留言表单 |
| `js/i18n.js` | 中英文翻译词典 |
| `mcp/server.py` | Claude Code MCP Server（后台管理工具） |
| `css/style.css` | 全局样式（暗色主题、CSS 变量） |

## 注意事项

- 推送代码到 `main` 后需要手动同步到服务器（SCP + systemctl restart）
- `.env` 和 `.mcp.json` 已加入 `.gitignore`，密钥不会提交
- `ADMIN_PASS` 未设置时 `seed.py` 会生成随机密码
- 静态资源缓存 1 小时 (`max-age=3600`)，如需立即生效清除浏览器缓存
- 文章/项目 slug 路由支持大小写字母

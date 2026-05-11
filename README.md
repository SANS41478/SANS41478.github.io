# 老铛的创世区块 — 个人网站

多页面个人网站，shadcn/ui 风格设计，华文新魏字体，支持中英文切换、项目展示、Markdown 文章、加密留言。

## 文件结构

```
.
├── index.html          # 首页（Hero + 关于 + 联系 / 留言）
├── projects.html       # 项目页面（独立展示所有项目）
├── articles.html       # 文章页面（独立展示所有文章）
├── css/
│   └── style.css       # 全局样式（shadcn 风格设计系统）
├── js/
│   ├── i18n.js         # 中英文翻译 + 语言切换
│   └── common.js       # 共享逻辑（导航、留言、加密、渲染）
└── articles/
    ├── hello-world.md
    └── building-with-vanilla.md
```

## 快速开始

双击 `index.html` 即可在浏览器中打开，或部署到任意静态托管服务。

## 自定义

### 修改个人信息

打开 `js/common.js`，编辑 `CONFIG` 对象：

```javascript
const CONFIG = {
  contact: {
    email: 'hello@example.com',     // 你的邮箱
    github: 'https://github.com/...', // 你的 GitHub
    twitter: '',
    wechat: '',
    blog: '',
  },
  // 留言加密密钥 — 改成你自己的
  encryptionKey: 'laodang-genesis-block-secret-key-2026',
};
```

### 添加 / 修改项目

编辑 `js/common.js` 中的 `PROJECTS` 数组。

### 发布文章

1. 在 `articles/` 下创建 `.md` 文件
2. 在 `js/common.js` 的 `ARTICLES_INDEX` 中注册

### 开启 EmailJS 邮件通知

1. 注册 [EmailJS](https://www.emailjs.com/)（免费 200 封 / 月）
2. 添加 Email Service + 创建 Template（变量：`from_name`, `from_email`, `message`, `date`）
3. 将密钥填入 `CONFIG.emailjs`，设置 `enabled: true`

### 查看留言

- 点击底部「管理留言」
- 或按 `Ctrl + Shift + M`

### 字体说明

网站首选字体为「华文新魏」(STXinwei)。Windows 用户通常已预装；macOS 用户需手动安装。未安装时将自动降级为宋体 / 微软雅黑。

## 技术栈

纯原生 HTML / CSS / JS，零框架，零构建。唯一 CDN 依赖：marked.js（Markdown 渲染）和 EmailJS（可选）。

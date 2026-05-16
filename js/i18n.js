/* ============================================
   i18n — Chinese / English Dictionary
   Shared across all pages
   ============================================ */

const I18N = {
  zh: {
    // Navigation
    'nav.brandName': '老铛的创世区块',
    'nav.home': '首页',
    'nav.projects': '项目',
    'nav.articles': '文章',
    'nav.contact': '联系',
    'nav.messages': '留言管理',

    // Hero
    'hero.badge': '个人网站 · 2026',
    'hero.subtitle': 'Laodang\'s Genesis Block — 构建、记录、连接',
    'hero.ctaProjects': '查看项目',
    'hero.ctaContact': '联系我',

    // About
    'about.label': '关于',
    'about.title': '老铛的创世区块',
    'about.p1': '你好，我是老铛。一名全栈开发者与技术创作者，专注于构建优雅、高性能的 Web 应用与工具。我相信代码不仅是功能的实现，更是思想的表达。',
    'about.p2': '这里是我的数字花园——记录项目、分享思考、连接同路人。无论是开源工具、技术文章，还是实验性的 Side Project，每一行代码都承载着对技术的热爱。',
    'about.stat1': '开源项目',
    'about.stat2': '技术文章',
    'about.stat3': '探索精神',
    'about.stat4': '持续构建',

    // Projects
    'projects.label': '项目作品',
    'projects.title': '精选项目',
    'projects.viewProject': '查看项目',
    'projects.empty': '暂无项目，敬请期待。',
    'projects.back': '← 返回首页',

    // Articles
    'articles.label': '文章',
    'articles.title': '全部文章',
    'articles.readMore': '展开阅读',
    'articles.collapse': '收起',
    'articles.loading': '加载中...',
    'articles.loadError': '文章加载失败',
    'articles.empty': '还没有文章，敬请期待。',
    'articles.back': '← 返回首页',

    // Contact
    'contact.label': '联系',
    'contact.title': '与我连接',
    'contact.infoTitle': '联系方式',
    'contact.email': '邮箱',
    'contact.github': 'GitHub',
    'contact.twitter': 'Twitter',
    'contact.wechat': '微信',
    'contact.blog': '博客',

    // Message Form
    'message.title': '给我留言',
    'message.hint': '你的留言将被加密存储，仅我可见。',
    'message.name': '你的名字',
    'message.namePlaceholder': '你的名字（选填）',
    'message.email': '你的邮箱',
    'message.emailPlaceholder': 'your@email.com（选填，方便我回复）',
    'message.body': '留言内容',
    'message.bodyPlaceholder': '写下你想说的话...',
    'message.submit': '发送留言',
    'message.sending': '发送中...',

    // Admin
    'admin.title': '留言管理',
    'admin.hint': '所有留言仅在你本地可见。点击右上角关闭或按 Esc。',
    'admin.empty': '暂无留言',
    'admin.anonymous': '匿名',
    'admin.noEmail': '未留邮箱',

    // Footer
    'footer.text': '© 2026 老铛的创世区块',
    'footer.admin': '管理留言',
    'footer.builtWith': '精心构建 · Python 后端驱动',

    // Toast
    'toast.sent': '留言已发送，感谢！',
    'toast.error': '发送失败，请稍后重试',
    'toast.empty': '请输入留言内容',
    'toast.copied': '已复制到剪贴板',
  },

  en: {
    // Navigation
    'nav.brandName': 'Laodang\'s Genesis Block',
    'nav.home': 'Home',
    'nav.projects': 'Projects',
    'nav.articles': 'Articles',
    'nav.contact': 'Contact',
    'nav.messages': 'Messages',

    // Hero
    'hero.badge': 'Personal Site · 2026',
    'hero.subtitle': 'Laodang\'s Genesis Block — Build, Record, Connect',
    'hero.ctaProjects': 'View Projects',
    'hero.ctaContact': 'Get in Touch',

    // About
    'about.label': 'About',
    'about.title': "Laodang's Genesis Block",
    'about.p1': 'Hi, I\'m Laodang. A full-stack developer and tech creator focused on building elegant, high-performance web applications and tools. I believe code is not just implementation — it\'s the expression of ideas.',
    'about.p2': 'This is my digital garden — documenting projects, sharing thoughts, connecting with fellow builders. Whether open-source tools, technical articles, or experimental side projects, every line of code carries a passion for technology.',
    'about.stat1': 'Open Source Projects',
    'about.stat2': 'Tech Articles',
    'about.stat3': 'Curiosity',
    'about.stat4': 'Building Since',

    // Projects
    'projects.label': 'Projects',
    'projects.title': 'Featured Work',
    'projects.viewProject': 'View Project',
    'projects.empty': 'No projects yet. Stay tuned.',
    'projects.back': '← Back to Home',

    // Articles
    'articles.label': 'Articles',
    'articles.title': 'All Articles',
    'articles.readMore': 'Read More',
    'articles.collapse': 'Collapse',
    'articles.loading': 'Loading...',
    'articles.loadError': 'Failed to load article',
    'articles.empty': 'No articles yet. Stay tuned.',
    'articles.back': '← Back to Home',

    // Contact
    'contact.label': 'Contact',
    'contact.title': 'Get in Touch',
    'contact.infoTitle': 'Contact Info',
    'contact.email': 'Email',
    'contact.github': 'GitHub',
    'contact.twitter': 'Twitter',
    'contact.wechat': 'WeChat',
    'contact.blog': 'Blog',

    // Message Form
    'message.title': 'Leave a Message',
    'message.hint': 'Your message is encrypted and visible only to me.',
    'message.name': 'Your Name',
    'message.namePlaceholder': 'Your name (optional)',
    'message.email': 'Your Email',
    'message.emailPlaceholder': 'your@email.com (optional, for replies)',
    'message.body': 'Message',
    'message.bodyPlaceholder': 'Write your message...',
    'message.submit': 'Send Message',
    'message.sending': 'Sending...',

    // Admin
    'admin.title': 'Message Inbox',
    'admin.hint': 'All messages are visible only locally on your device. Click the close button or press Esc.',
    'admin.empty': 'No messages yet.',
    'admin.anonymous': 'Anonymous',
    'admin.noEmail': 'No email provided',

    // Footer
    'footer.text': '© 2026 Laodang\'s Genesis Block',
    'footer.admin': 'Manage Messages',
    'footer.builtWith': 'Crafted with care · Python-powered backend',

    // Toast
    'toast.sent': 'Message sent. Thank you!',
    'toast.error': 'Failed to send. Please try again.',
    'toast.empty': 'Please enter a message.',
    'toast.copied': 'Copied to clipboard',
  }
};

let currentLang = localStorage.getItem('lang') || 'zh';

function t(key) {
  return I18N[currentLang]?.[key] || I18N['zh'][key] || key;
}

function toggleLang() {
  currentLang = currentLang === 'zh' ? 'en' : 'zh';
  localStorage.setItem('lang', currentLang);
  applyI18n();
}

function applyI18n() {
  document.documentElement.lang = currentLang === 'zh' ? 'zh-CN' : 'en';

  // Text content
  document.querySelectorAll('[data-i18n]').forEach(el => {
    el.textContent = t(el.getAttribute('data-i18n'));
  });

  // Placeholders
  document.querySelectorAll('[data-i18n-placeholder]').forEach(el => {
    el.placeholder = t(el.getAttribute('data-i18n-placeholder'));
  });

  // Lang toggle button
  const toggleBtn = document.getElementById('langToggle');
  if (toggleBtn) {
    toggleBtn.textContent = currentLang === 'zh' ? 'EN' : '中文';
  }

  // Page title
  document.title = currentLang === 'zh'
    ? '老铛的创世区块 | Laodang\'s Genesis Block'
    : 'Laodang\'s Genesis Block | 老铛的创世区块';

  // Highlight active nav link
  highlightActiveNav();

  // Let each page re-render dynamic content
  if (typeof onLangChange === 'function') {
    onLangChange();
  }
}

function highlightActiveNav() {
  const path = window.location.pathname;
  const page = path.split('/').pop() || 'index.html';

  document.querySelectorAll('.nav-link').forEach(link => {
    const href = link.getAttribute('href');
    link.classList.toggle('active', href === page || (page === 'index.html' && href === 'index.html'));
  });
}

// Initialize on DOM ready
document.addEventListener('DOMContentLoaded', () => {
  applyI18n();
});

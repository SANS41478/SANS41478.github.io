/* ============================================
   Common JS — Shared across all pages
   Config, Messages, Admin, Animations, Navigation
   ============================================ */

/* ---- Configuration ---- */
const CONFIG = {
  contact: {
    email: 'hello@example.com',
    github: 'https://github.com/yourusername',
    twitter: '',
    wechat: '',
    blog: '',
  },
  emailjs: {
    enabled: false,
    publicKey: 'YOUR_PUBLIC_KEY',
    serviceId: 'YOUR_SERVICE_ID',
    templateId: 'YOUR_TEMPLATE_ID',
  },
  encryptionKey: 'laodang-genesis-block-secret-key-2026',
};

/* ---- Project Data ---- */
const PROJECTS = [
  {
    icon: '🛠️',
    nameZh: '示例项目 Alpha',
    nameEn: 'Demo Project Alpha',
    descZh: '一个高性能的 Web 工具，用于自动化工作流处理。',
    descEn: 'A high-performance web tool for automated workflow processing.',
    tags: ['TypeScript', 'React', 'Node.js'],
    url: 'https://github.com',
  },
  {
    icon: '📊',
    nameZh: '数据可视化面板',
    nameEn: 'Data Viz Dashboard',
    descZh: '实时数据监控与可视化仪表盘，支持多种图表类型。',
    descEn: 'Real-time data monitoring and visualization dashboard with multiple chart types.',
    tags: ['D3.js', 'WebSocket', 'Python'],
    url: 'https://github.com',
  },
  {
    icon: '🔧',
    nameZh: 'CLI 效率工具集',
    nameEn: 'CLI Toolkit',
    descZh: '一组命令行效率工具，提升日常开发体验。',
    descEn: 'A collection of CLI productivity tools for daily development.',
    tags: ['Rust', 'Shell', 'Linux'],
    url: 'https://github.com',
  },
];

/* ---- Article Index ---- */
const ARTICLES_INDEX = [
  { slug: 'hello-world', date: '2026-05-01', titleZh: '你好，世界——我的第一篇博客', titleEn: 'Hello, World — My First Blog Post' },
  { slug: 'building-with-vanilla', date: '2026-04-15', titleZh: '为什么我选择原生 JS 构建个人网站', titleEn: 'Why I Chose Vanilla JS for My Personal Site' },
];

/* ---- Navigation ---- */
function initNav() {
  const mobileBtn = document.getElementById('mobileMenuBtn');
  const mobileNav = document.getElementById('mobileNav');

  if (mobileBtn && mobileNav) {
    mobileBtn.addEventListener('click', () => {
      mobileNav.classList.toggle('open');
    });

    mobileNav.querySelectorAll('a').forEach(link => {
      link.addEventListener('click', () => mobileNav.classList.remove('open'));
    });
  }

  // Lang toggle
  const langBtn = document.getElementById('langToggle');
  if (langBtn) {
    langBtn.addEventListener('click', toggleLang);
  }
}

/* ---- Back to Top ---- */
function initBackToTop() {
  const btn = document.getElementById('backToTop');
  if (!btn) return;

  let ticking = false;
  window.addEventListener('scroll', () => {
    if (!ticking) {
      requestAnimationFrame(() => {
        btn.classList.toggle('visible', window.scrollY > 400);
        ticking = false;
      });
      ticking = true;
    }
  });

  btn.addEventListener('click', () => {
    window.scrollTo({ top: 0, behavior: 'smooth' });
  });
}

/* ---- Scroll Reveal ---- */
function initScrollReveal() {
  if (!('IntersectionObserver' in window)) return;

  const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        entry.target.classList.add('visible');
      }
    });
  }, { threshold: 0.1, rootMargin: '0px 0px -40px 0px' });

  document.querySelectorAll('.reveal').forEach(el => observer.observe(el));

  // Return observer so it can be reused for dynamically added elements
  return observer;
}

/* ---- Toast ---- */
let toastTimer;
function showToast(msg) {
  const toast = document.getElementById('toast');
  if (!toast) return;
  toast.textContent = msg;
  toast.classList.add('show');
  clearTimeout(toastTimer);
  toastTimer = setTimeout(() => toast.classList.remove('show'), 2500);
}

/* ---- Message Encryption (AES-GCM) ---- */
async function deriveKey(password) {
  const enc = new TextEncoder();
  const keyMaterial = await crypto.subtle.importKey(
    'raw', enc.encode(password), 'PBKDF2', false, ['deriveKey']
  );
  const salt = enc.encode('laodang-genesis-salt');
  return crypto.subtle.deriveKey(
    { name: 'PBKDF2', salt, iterations: 100000, hash: 'SHA-256' },
    keyMaterial,
    { name: 'AES-GCM', length: 256 },
    false,
    ['encrypt', 'decrypt']
  );
}

async function encryptMessage(plaintext) {
  const key = await deriveKey(CONFIG.encryptionKey);
  const iv = crypto.getRandomValues(new Uint8Array(12));
  const enc = new TextEncoder();
  const ciphertext = await crypto.subtle.encrypt(
    { name: 'AES-GCM', iv }, key, enc.encode(plaintext)
  );
  const combined = new Uint8Array(iv.length + ciphertext.byteLength);
  combined.set(iv);
  combined.set(new Uint8Array(ciphertext), iv.length);
  return btoa(String.fromCharCode(...combined));
}

async function decryptMessage(encrypted) {
  try {
    const key = await deriveKey(CONFIG.encryptionKey);
    const data = Uint8Array.from(atob(encrypted), c => c.charCodeAt(0));
    const iv = data.slice(0, 12);
    const ciphertext = data.slice(12);
    const decrypted = await crypto.subtle.decrypt(
      { name: 'AES-GCM', iv }, key, ciphertext
    );
    return new TextDecoder().decode(decrypted);
  } catch {
    return '[Decryption failed]';
  }
}

/* ---- Message Storage ---- */
function getMessages() {
  try { return JSON.parse(localStorage.getItem('lb_messages') || '[]'); }
  catch { return []; }
}

async function saveMessage(msg) {
  const messages = getMessages();
  const payload = JSON.stringify({
    name: msg.name,
    email: msg.email,
    body: msg.body,
    date: new Date().toISOString(),
  });
  const encrypted = await encryptMessage(payload);
  messages.push(encrypted);
  localStorage.setItem('lb_messages', JSON.stringify(messages));
}

/* ---- EmailJS ---- */
function sendEmailNotification(msg) {
  if (!CONFIG.emailjs.enabled) return Promise.resolve();

  return new Promise((resolve, reject) => {
    if (window.emailjs) {
      window.emailjs.init(CONFIG.emailjs.publicKey);
      window.emailjs.send(CONFIG.emailjs.serviceId, CONFIG.emailjs.templateId, {
        from_name: msg.name || 'Anonymous',
        from_email: msg.email || 'N/A',
        message: msg.body,
        date: new Date().toLocaleString(),
      }).then(resolve).catch(reject);
      return;
    }

    const script = document.createElement('script');
    script.src = 'https://cdn.jsdelivr.net/npm/@emailjs/browser@4/dist/email.min.js';
    script.onload = () => {
      window.emailjs.init(CONFIG.emailjs.publicKey);
      window.emailjs.send(CONFIG.emailjs.serviceId, CONFIG.emailjs.templateId, {
        from_name: msg.name || 'Anonymous',
        from_email: msg.email || 'N/A',
        message: msg.body,
        date: new Date().toLocaleString(),
      }).then(resolve).catch(reject);
    };
    script.onerror = reject;
    document.head.appendChild(script);
  });
}

/* ---- Message Form Handler ---- */
function initMessageForm() {
  const form = document.getElementById('messageFormCard');
  if (!form) return;

  const submitBtn = document.getElementById('submitBtn');
  const statusEl = document.getElementById('formStatus');

  if (!submitBtn) return;

  submitBtn.addEventListener('click', async () => {
    const name = (document.getElementById('msgName')?.value || '').trim();
    const email = (document.getElementById('msgEmail')?.value || '').trim();
    const body = (document.getElementById('msgBody')?.value || '').trim();

    if (!body) {
      statusEl.textContent = t('toast.empty');
      statusEl.className = 'form-status error';
      return;
    }

    submitBtn.disabled = true;
    submitBtn.textContent = t('message.sending');
    statusEl.textContent = '';
    statusEl.className = 'form-status';

    const msg = { name, email, body };

    try {
      await saveMessage(msg);
      await sendEmailNotification(msg);

      statusEl.textContent = t('toast.sent');
      statusEl.className = 'form-status success';
      if (document.getElementById('msgName')) document.getElementById('msgName').value = '';
      if (document.getElementById('msgEmail')) document.getElementById('msgEmail').value = '';
      if (document.getElementById('msgBody')) document.getElementById('msgBody').value = '';
    } catch {
      // Local save succeeded even if email fails
      statusEl.textContent = t('toast.sent');
      statusEl.className = 'form-status success';
    }

    submitBtn.disabled = false;
    submitBtn.textContent = t('message.submit');

    setTimeout(() => {
      statusEl.textContent = '';
      statusEl.className = 'form-status';
    }, 4000);
  });
}

/* ---- Admin Panel ---- */
function initAdminPanel() {
  const overlay = document.getElementById('adminOverlay');
  const messagesContainer = document.getElementById('adminMessages');
  const closeBtn = document.getElementById('adminCloseBtn');
  const adminLink = document.getElementById('adminLink');

  if (!overlay) return;

  async function renderMessages() {
    const messages = getMessages();
    if (messages.length === 0) {
      messagesContainer.innerHTML = `<div class="admin-empty">${t('admin.empty')}</div>`;
      return;
    }

    const decrypted = await Promise.all(messages.map(async (enc) => {
      const plain = await decryptMessage(enc);
      try { return JSON.parse(plain); }
      catch { return { name: '', email: '', body: plain, date: '' }; }
    }));

    decrypted.reverse();

    messagesContainer.innerHTML = decrypted.map(m => `
      <div class="admin-message">
        <div class="admin-message-meta">
          <span><strong>${m.name || t('admin.anonymous')}</strong> &mdash; ${m.email || t('admin.noEmail')}</span>
          <span>${m.date ? new Date(m.date).toLocaleString() : ''}</span>
        </div>
        <div class="admin-message-body">${escapeHtml(m.body)}</div>
      </div>
    `).join('');
  }

  function escapeHtml(text) {
    const d = document.createElement('div');
    d.textContent = text;
    return d.innerHTML;
  }

  function open() {
    overlay.classList.add('open');
    renderMessages();
    document.body.style.overflow = 'hidden';
  }

  function close() {
    overlay.classList.remove('open');
    document.body.style.overflow = '';
  }

  if (closeBtn) closeBtn.addEventListener('click', close);

  overlay.addEventListener('click', (e) => {
    if (e.target === overlay) close();
  });

  if (adminLink) {
    adminLink.addEventListener('click', (e) => {
      e.preventDefault();
      open();
    });
  }

  document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape' && overlay.classList.contains('open')) close();
    if (e.ctrlKey && e.shiftKey && e.key === 'M') { e.preventDefault(); open(); }
  });
}

/* ---- Contact Info Rendering ---- */
function renderContactInfo(containerId) {
  const container = document.getElementById(containerId);
  if (!container) return;

  const items = [
    { icon: '✉️', key: 'contact.email', value: CONFIG.contact.email, href: `mailto:${CONFIG.contact.email}` },
    { icon: '🐙', key: 'contact.github', value: CONFIG.contact.github.replace('https://github.com/', '@'), href: CONFIG.contact.github },
  ];
  if (CONFIG.contact.twitter) items.push({ icon: '🐦', key: 'contact.twitter', value: CONFIG.contact.twitter, href: CONFIG.contact.twitter });
  if (CONFIG.contact.wechat) items.push({ icon: '💬', key: 'contact.wechat', value: CONFIG.contact.wechat, href: '#' });
  if (CONFIG.contact.blog) items.push({ icon: '📝', key: 'contact.blog', value: CONFIG.contact.blog, href: CONFIG.contact.blog });

  container.innerHTML = items.map(item => `
    <div class="contact-info-item">
      <div class="contact-info-icon">${item.icon}</div>
      <div class="contact-info-text">
        ${t(item.key)}：<a href="${item.href}" target="_blank" rel="noopener">${item.value}</a>
      </div>
    </div>
  `).join('');
}

/* ---- Projects Rendering ---- */
function renderProjects(containerId) {
  const container = document.getElementById(containerId);
  if (!container) return;

  if (PROJECTS.length === 0) {
    container.innerHTML = `<div class="empty-state"><div class="empty-state-icon">📦</div><div class="empty-state-text">${t('projects.empty')}</div></div>`;
    return;
  }

  container.innerHTML = PROJECTS.map((p, i) => `
    <div class="project-card reveal reveal-delay-${i + 1}" onclick="window.open('${p.url}', '_blank', 'noopener')">
      <div class="project-card-header">
        <div class="project-card-icon">${p.icon}</div>
      </div>
      <div class="project-card-title">${currentLang === 'zh' ? p.nameZh : p.nameEn}</div>
      <div class="project-card-desc">${currentLang === 'zh' ? p.descZh : p.descEn}</div>
      <div class="project-card-tags">
        ${p.tags.map(t => `<span class="badge">${t}</span>`).join('')}
      </div>
      <span class="project-card-link">
        ${t('projects.viewProject')}
        <span class="project-card-link-arrow">→</span>
      </span>
    </div>
  `).join('');

  // Re-observe new reveal elements
  if (window._revealObserver) {
    container.querySelectorAll('.reveal').forEach(el => window._revealObserver.observe(el));
  }
}

/* ---- Articles Rendering ---- */
function renderArticles(containerId) {
  const container = document.getElementById(containerId);
  if (!container) return;

  if (ARTICLES_INDEX.length === 0) {
    container.innerHTML = `<div class="empty-state"><div class="empty-state-icon">📝</div><div class="empty-state-text">${t('articles.empty')}</div></div>`;
    return;
  }

  container.innerHTML = ARTICLES_INDEX.map((a, i) => `
    <div class="reveal reveal-delay-${i + 1}">
      <div class="article-item" data-slug="${a.slug}">
        <span class="article-item-title">${currentLang === 'zh' ? a.titleZh : a.titleEn}</span>
        <div class="article-item-meta">
          <span class="article-item-date">${a.date}</span>
          <span class="article-item-arrow">→</span>
        </div>
      </div>
      <div class="article-detail" id="article-${a.slug}">
        <div class="article-body">${t('articles.loading')}</div>
        <button class="btn btn-ghost btn-sm mt-3 article-collapse-btn">${t('articles.collapse')}</button>
      </div>
    </div>
  `).join('');

  // Re-observe reveal elements
  if (window._revealObserver) {
    container.querySelectorAll('.reveal').forEach(el => window._revealObserver.observe(el));
  }

  // Expand/collapse
  container.querySelectorAll('.article-item').forEach(item => {
    item.addEventListener('click', async () => {
      const slug = item.dataset.slug;
      const detail = document.getElementById(`article-${slug}`);
      const body = detail.querySelector('.article-body');

      if (detail.classList.contains('open')) {
        detail.classList.remove('open');
        return;
      }

      // Close others
      container.querySelectorAll('.article-detail.open').forEach(d => d.classList.remove('open'));
      detail.classList.add('open');

      if (body.textContent === t('articles.loading')) {
        try {
          const resp = await fetch(`articles/${slug}.md`);
          if (!resp.ok) throw new Error('Not found');
          const md = await resp.text();
          body.innerHTML = marked.parse(md);
        } catch {
          body.innerHTML = `<p class="text-muted">${t('articles.loadError')}</p>`;
        }
      }
    });
  });

  // Collapse buttons
  container.querySelectorAll('.article-collapse-btn').forEach(btn => {
    btn.addEventListener('click', (e) => {
      e.stopPropagation();
      btn.parentElement.classList.remove('open');
    });
  });
}

/* ---- Init everything common ---- */
document.addEventListener('DOMContentLoaded', () => {
  initNav();
  initBackToTop();
  window._revealObserver = initScrollReveal();
  initMessageForm();
  initAdminPanel();
});

/* ============================================
   Common JS — Shared across all pages
   API-driven data, Messages, Navigation, Admin link
   ============================================ */

const API_BASE = '';

/* ---- Configuration ---- */
const CONFIG = {
  contact: {
    email: 'sans41478@gmail.com',
    github: 'https://github.com/SANS41478',
    twitter: '',
    wechat: '',
    blog: '',
  },
};

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

/* ---- Message Form (API-driven) ---- */
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

    try {
      const resp = await fetch(API_BASE + '/api/messages', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ name, email, body })
      });

      if (resp.ok) {
        statusEl.textContent = t('toast.sent');
        statusEl.className = 'form-status success';
        document.getElementById('msgName').value = '';
        document.getElementById('msgEmail').value = '';
        document.getElementById('msgBody').value = '';
      } else {
        const err = await resp.json();
        statusEl.textContent = err.error || t('toast.error');
        statusEl.className = 'form-status error';
      }
    } catch {
      statusEl.textContent = t('toast.error');
      statusEl.className = 'form-status error';
    }

    submitBtn.disabled = false;
    submitBtn.textContent = t('message.submit');

    setTimeout(() => {
      statusEl.textContent = '';
      statusEl.className = 'form-status';
    }, 4000);
  });
}

/* ---- Admin Link (now points to /admin) ---- */
function initAdminLink() {
  const adminLink = document.getElementById('adminLink');
  if (adminLink) {
    adminLink.href = '/admin';
    adminLink.textContent = '后台管理';
  }
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

/* ---- Projects Rendering (API-driven) ---- */
async function renderProjects(containerId) {
  const container = document.getElementById(containerId);
  if (!container) return;

  container.innerHTML = `<div class="empty-state"><div class="empty-state-text">加载中...</div></div>`;

  try {
    const resp = await fetch(API_BASE + '/api/projects');
    const data = await resp.json();
    const projects = data.projects || [];

    if (projects.length === 0) {
      container.innerHTML = `<div class="empty-state"><div class="empty-state-icon">📦</div><div class="empty-state-text">${t('projects.empty')}</div></div>`;
      return;
    }

    container.innerHTML = projects.map((p, i) => `
      <a href="/projects/${p.slug}" class="project-card reveal reveal-delay-${i + 1}" style="text-decoration:none;color:inherit;">
        <div class="project-card-header">
          <div class="project-card-icon">${p.icon || '📦'}</div>
        </div>
        <div class="project-card-title">${currentLang === 'zh' ? p.name_zh : p.name_en}</div>
        <div class="project-card-desc">${currentLang === 'zh' ? p.desc_zh : p.desc_en}</div>
        <div class="project-card-tags">
          ${(p.tags || []).map(t => `<span class="badge">${t}</span>`).join('')}
        </div>
        <span class="project-card-link">
          ${t('projects.viewProject')}
          <span class="project-card-link-arrow">→</span>
        </span>
      </a>
    `).join('');

    // Re-observe new reveal elements
    if (window._revealObserver) {
      container.querySelectorAll('.reveal').forEach(el => window._revealObserver.observe(el));
    }
  } catch {
    container.innerHTML = `<div class="empty-state"><div class="empty-state-text">加载失败</div></div>`;
  }
}

/* ---- Articles List Rendering (API-driven) ---- */
async function renderArticles(containerId) {
  const container = document.getElementById(containerId);
  if (!container) return;

  container.innerHTML = `<div class="empty-state"><div class="empty-state-text">加载中...</div></div>`;

  try {
    const resp = await fetch(API_BASE + '/api/articles');
    const data = await resp.json();
    const articles = data.articles || [];

    if (articles.length === 0) {
      container.innerHTML = `<div class="empty-state"><div class="empty-state-icon">📝</div><div class="empty-state-text">${t('articles.empty')}</div></div>`;
      return;
    }

    container.innerHTML = articles.map((a, i) => `
      <a href="/articles/${a.slug}" class="article-item reveal reveal-delay-${i + 1}">
        <span class="article-item-date">${a.created_at ? a.created_at.substring(0, 10) : ''}</span>
        <div class="article-item-content">
          <div class="article-item-title">${currentLang === 'zh' ? a.title_zh : a.title_en}</div>
          ${a.excerpt_zh ? `<div class="article-item-excerpt">${a.excerpt_zh}</div>` : ''}
        </div>
        <span class="article-item-arrow">→</span>
      </a>
    `).join('');

    if (window._revealObserver) {
      container.querySelectorAll('.reveal').forEach(el => window._revealObserver.observe(el));
    }
  } catch {
    container.innerHTML = `<div class="empty-state"><div class="empty-state-text">加载失败</div></div>`;
  }
}

/* ---- Init everything common ---- */
document.addEventListener('DOMContentLoaded', () => {
  initNav();
  initBackToTop();
  window._revealObserver = initScrollReveal();
  initMessageForm();
  initAdminLink();
});

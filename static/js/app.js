/* VoiceForge - Main Application Controller */
let currentPage = 'studio';

function showToast(message, type = 'info') {
  const container = document.getElementById('toasts');
  if (!container) return;
  const toast = document.createElement('div');
  toast.className = 'toast ' + type;
  const icons = {
    success: '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#008000" stroke-width="2"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/><polyline points="22 4 12 14.01 9 11.01"/></svg>',
    error: '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#ff0000" stroke-width="2"><circle cx="12" cy="12" r="10"/><line x1="15" y1="9" x2="9" y2="15"/><line x1="9" y1="9" x2="15" y2="15"/></svg>',
    info: '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#000080" stroke-width="2"><circle cx="12" cy="12" r="10"/><line x1="12" y1="16" x2="12" y2="12"/><line x1="12" y1="8" x2="12.01" y2="8"/></svg>'
  };
  const icon = document.createElement('span');
  icon.innerHTML = icons[type] || icons.info;
  const text = document.createElement('span');
  text.style.flex = '1';
  text.textContent = message;
  toast.append(icon, text);
  container.appendChild(toast);
  setTimeout(() => { toast.style.opacity = '0'; toast.style.transform = 'translateX(20px)'; setTimeout(() => toast.remove(), 300); }, 4000);
}

function navigateTo(page) {
  currentPage = page;
  document.querySelectorAll('.app-page').forEach(el => { el.style.display = 'none'; });
  const target = document.getElementById('page-' + page);
  if (target) { target.style.display = 'block'; target.style.animation = 'none'; target.offsetHeight; target.style.animation = 'fadeIn 0.3s ease'; }
  if (typeof setActiveTab === 'function') setActiveTab(page);
  if (page === 'studio' && !document.getElementById('ttsText')) initStudioPage();
  if (page === 'voices') initVoicesPage();
  if (page === 'clone') initClonePage();
  if (page === 'batch') initBatchPage();
}
function showPage(pageId) {
  document.querySelectorAll('.page').forEach(el => { el.style.display = 'none'; });
  const target = document.getElementById(pageId);
  if (target) target.style.display = 'block';
}
function showSetup() { showPage('page-setup'); initSetupPage(); }
function showGate() { showPage('page-gate'); initGatePage(); }
function showApp() {
  document.querySelectorAll('.page').forEach(el => { el.style.display = 'none'; });
  document.getElementById('app-container').style.display = 'block';
  initNavbar();
  initStudioPage();
  navigateTo('studio');
}
function appReady() {
  const verified = localStorage.getItem('vf_verified') === 'true';
  if (verified) { showApp(); return; }
  fetch('/api/verify').then(r => r.json()).then(data => {
    if (data.verified) { localStorage.setItem('vf_verified', 'true'); showApp(); }
    else showGate();
  }).catch(() => showGate());
}
document.addEventListener('DOMContentLoaded', async () => {
  try {
    const res = await fetch('/api/health');
    const data = await res.json();
    if (data.model_loaded) appReady();
    else showSetup();
  } catch { showSetup(); }
});

/* VoiceForge - Main Application Controller */
let currentPage = 'studio';
const PAGE_IDS = ['gate', 'setup', 'studio', 'voices', 'clone', 'batch'];

function showToast(message, type = 'info') {
  const container = document.getElementById('toast-container');
  if (!container) return;
  const toast = document.createElement('div');
  toast.className = 'toast ' + type;
  const label = document.createElement('span');
  label.textContent = message;
  toast.appendChild(label);
  container.appendChild(toast);
  window.setTimeout(() => toast.remove(), 4000);
}

function navigateTo(page) {
  currentPage = page;
  PAGE_IDS.forEach(id => {
    const el = document.getElementById(id + '-page');
    if (el) el.style.display = id === page ? 'block' : 'none';
  });
  if (typeof setActiveTab === 'function') setActiveTab(page);
  const initializers = {
    studio: initStudioPage,
    voices: initVoicesPage,
    clone: initClonePage,
    batch: initBatchPage,
    setup: initSetupPage,
    gate: initGatePage
  };
  if (initializers[page]) initializers[page]();
}

function showSetup() { navigateTo('setup'); }
function showGate() { navigateTo('gate'); }
function showApp() {
  const navbar = document.getElementById('navbar');
  if (navbar && typeof initNavbar === 'function') initNavbar();
  navigateTo('studio');
}

async function appReady() {
  try {
    const response = await fetch('/api/verify');
    const data = await response.json();
    if (data.verified) showApp();
    else showGate();
  } catch {
    showSetup();
  }
}

document.addEventListener('DOMContentLoaded', async () => {
  try {
    const res = await fetch('/api/health');
    if (!res.ok) throw new Error('Health check failed');
    const data = await res.json();
    if (data.model_loaded) await appReady();
    else showSetup();
  } catch {
    showSetup();
  }
});

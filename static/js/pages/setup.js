function initSetupPage() {
  const page = document.getElementById('setup-page');
  if (!page || page.dataset.initialized) return;
  page.dataset.initialized = 'true';
  page.innerHTML = `<div class="panel"><h2>Welcome to VoiceForge</h2><p>Initialize the speech engine before using the studio. The first model load may take time.</p><button id="startSetup" type="button">Initialize TTS Engine</button><p id="setupStatus" role="status">Waiting to start.</p></div>`;
  const button = document.getElementById('startSetup');
  const status = document.getElementById('setupStatus');
  let pollHandle = null;
  async function pollStatus() {
    try {
      const response = await fetch('/api/setup-status');
      if (!response.ok) return;
      const data = await response.json();
      status.textContent = (data.status || 'Loading model…') + (Number.isFinite(data.progress) && data.progress >= 0 ? ' (' + data.progress + '%)' : '');
      if (data.model_loaded) {
        if (pollHandle) window.clearInterval(pollHandle);
        showToast('TTS engine ready.', 'success');
        showApp();
      }
      if (data.progress < 0) {
        if (pollHandle) window.clearInterval(pollHandle);
        button.disabled = false;
      }
    } catch {}
  }
  button.addEventListener('click', async () => {
    button.disabled = true;
    status.textContent = 'Starting model setup…';
    try {
      const response = await fetch('/api/setup-start', {method:'POST'});
      if (!response.ok) throw new Error('Setup could not be started');
      await pollStatus();
      if (!pollHandle) pollHandle = window.setInterval(pollStatus, 2500);
    } catch (error) {
      status.textContent = error.message;
      button.disabled = false;
    }
  });
}

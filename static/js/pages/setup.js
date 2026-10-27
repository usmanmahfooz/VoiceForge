function initSetupPage() {
  const page = document.getElementById('setup-page');
  if (!page || page.dataset.initialized) return;
  page.dataset.initialized = 'true';
  page.innerHTML = `<div class="panel"><h2>Welcome to VoiceForge</h2><p>Initialize the speech engine before using the studio. The initial model download may take time.</p><button id="startSetup" type="button">Initialize TTS Engine</button><p id="setupStatus" role="status"></p></div>`;
  document.getElementById('startSetup').addEventListener('click', async () => {
    const status = document.getElementById('setupStatus');
    status.textContent = 'Starting model setup…';
    try {
      const res = await fetch('/api/setup-start', {method:'POST'});
      if (!res.ok) throw new Error('Setup could not be started');
      status.textContent = 'Model loading started. Refresh this page after the setup completes.';
    } catch (e) { status.textContent = e.message; }
  });
}

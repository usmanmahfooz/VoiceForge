function initGatePage() {
  const page = document.getElementById('gate-page');
  if (!page || page.dataset.initialized) return;
  page.dataset.initialized = 'true';
  page.innerHTML = `<div class="panel"><h2>VoiceForge</h2><p>Continue to the local speech studio.</p><button id="continueVoiceForge" type="button">Continue</button></div>`;
  document.getElementById('continueVoiceForge').addEventListener('click', async () => {
    try {
      const res = await fetch('/api/verify', {method:'POST'});
      if (!res.ok) throw new Error('Verification failed');
      showApp();
    } catch (e) { showToast(e.message, 'error'); }
  });
}

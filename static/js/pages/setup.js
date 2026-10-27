/* Setup Page */
function initSetupPage() {
  const progressBar = document.getElementById('setupProgress');
  const statusText = document.getElementById('setupStatus');
  if (!progressBar || !statusText) return;
  fetch('/api/setup-start', { method: 'POST' }).catch(() => {});
  const poll = setInterval(async () => {
    try {
      const res = await fetch('/api/setup-status');
      const data = await res.json();
      if (data.progress >= 0) progressBar.style.width = data.progress + '%';
      statusText.textContent = data.status || 'Loading...';
      if (data.model_loaded) {
        clearInterval(poll); progressBar.style.width = '100%';
        statusText.textContent = 'Ready!';
        setTimeout(() => appReady(), 800);
      }
      if (data.progress === -1) {
        clearInterval(poll); statusText.textContent = data.status || 'Setup failed. Check logs.';
        statusText.style.color = 'var(--error)';
      }
    } catch { statusText.textContent = 'Connecting to server...'; }
  }, 1500);
}

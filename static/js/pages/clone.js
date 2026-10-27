function initClonePage() {
  const page = document.getElementById('page-clone');
  if (!page || page.dataset.initialized) return;
  page.dataset.initialized = 'true';
  page.innerHTML = `
    <div class="clone-grid">
      <section class="panel">
        <h2>Voice Cloning</h2>
        <p>Use reference audio only when you own it or have permission from the speaker.</p>
        <form id="cloneForm">
          <label for="cloneName">Voice name</label>
          <input id="cloneName" name="name" required maxlength="60">
          <label for="cloneLanguage">Language</label>
          <select id="cloneLanguage" name="language"><option value="en">English</option></select>
          <label for="cloneAudio">Reference audio</label>
          <input id="cloneAudio" name="audio" type="file" accept="audio/*" required>
          <button type="submit">Create voice profile</button>
        </form>
        <p id="cloneStatus" role="status"></p>
      </section>
      <section class="panel">
        <h2>Model access</h2>
        <p>Some Pocket TTS installations require a Hugging Face token and accepted model terms before voice cloning is available. Enter it here only in this local application. Never commit a token to GitHub.</p>
        <label for="hfToken">Hugging Face token</label>
        <input id="hfToken" type="password" autocomplete="off" placeholder="hf_…">
        <button id="saveHfToken" type="button">Save token and check access</button>
        <button id="resetHfToken" type="button">Reset authentication</button>
        <p id="tokenStatus" role="status"></p>
      </section>
    </div>`;
  document.getElementById('cloneForm').addEventListener('submit', async event => {
    event.preventDefault();
    const audioFile = document.getElementById('cloneAudio').files[0];
    if (!audioFile) return;
    const form = new FormData();
    form.append('name', document.getElementById('cloneName').value.trim());
    form.append('language', document.getElementById('cloneLanguage').value);
    form.append('audio', audioFile);
    const status = document.getElementById('cloneStatus');
    status.textContent = 'Processing reference audio…';
    try {
      const response = await fetch('/api/clone', {method:'POST', body:form});
      const data = await response.json();
      if (!response.ok) throw new Error(data.detail || 'Voice cloning failed');
      status.textContent = data.message || 'Voice profile created.';
      showToast('Voice profile created.', 'success');
    } catch (error) {
      status.textContent = error.message;
      showToast(error.message, 'error');
    }
  });
  document.getElementById('saveHfToken').addEventListener('click', async () => {
    const token = document.getElementById('hfToken').value.trim();
    const status = document.getElementById('tokenStatus');
    if (!token) { status.textContent = 'Enter your token first.'; return; }
    status.textContent = 'Checking model access…';
    try {
      const response = await fetch('/api/set-token', {
        method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({token})
      });
      const data = await response.json();
      if (!response.ok) throw new Error(data.detail || 'Authentication failed');
      status.textContent = data.message || 'Model access updated.';
      document.getElementById('hfToken').value = '';
      showToast('Model access updated.', 'success');
    } catch (error) {
      status.textContent = error.message;
      showToast(error.message, 'error');
    }
  });
  document.getElementById('resetHfToken').addEventListener('click', async () => {
    const status = document.getElementById('tokenStatus');
    status.textContent = 'Resetting authentication…';
    try {
      const response = await fetch('/api/reset-token', {method:'POST'});
      const data = await response.json();
      if (!response.ok) throw new Error(data.detail || 'Reset failed');
      status.textContent = data.message || 'Authentication reset.';
      showToast('Authentication reset.', 'success');
    } catch (error) {
      status.textContent = error.message;
      showToast(error.message, 'error');
    }
  });
}

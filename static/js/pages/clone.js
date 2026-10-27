function initClonePage() {
  const page = document.getElementById('clone-page');
  if (!page || page.dataset.initialized) return;
  page.dataset.initialized = 'true';
  page.innerHTML = `<section class="panel"><h2>Voice Cloning</h2><p>Use a recording only if you own it or have explicit permission from the speaker.</p><form id="cloneForm"><label for="cloneName">Voice name</label><input id="cloneName" name="name" required maxlength="60"><label for="cloneLanguage">Language</label><select id="cloneLanguage" name="language"><option value="en">English</option></select><label for="cloneAudio">Reference audio</label><input id="cloneAudio" name="audio" type="file" accept="audio/*" required><button type="submit">Create voice</button></form><p id="cloneStatus" role="status"></p></section>`;
  document.getElementById('cloneForm').addEventListener('submit', async e => {
    e.preventDefault();
    const file = document.getElementById('cloneAudio').files[0];
    if (!file) return;
    const form = new FormData();
    form.append('name', document.getElementById('cloneName').value);
    form.append('language', document.getElementById('cloneLanguage').value);
    form.append('audio', file);
    const status = document.getElementById('cloneStatus');
    status.textContent = 'Processing reference audio…';
    try {
      const response = await fetch('/api/clone', {method:'POST', body:form});
      const data = await response.json();
      if (!response.ok) throw new Error(data.detail || 'Voice cloning failed');
      status.textContent = 'Voice created.';
      showToast('Voice created.', 'success');
    } catch (error) {
      status.textContent = error.message;
      showToast(error.message, 'error');
    }
  });
}

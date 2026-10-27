/* Community Gate. This is a convenience flow, not an authentication/security mechanism. */
function initGatePage() {
  const step1 = document.getElementById('gateStep1');
  const step2 = document.getElementById('gateStep2');
  const btnUnlock = document.getElementById('btnUnlock');
  const fbLink = document.getElementById('fbLink');
  const waLink = document.getElementById('waLink');
  if (!step1 || !step2 || !btnUnlock || !fbLink || !waLink) return;
  let fbDone = false, waDone = false;
  fbLink.addEventListener('click', () => { setTimeout(() => { fbDone = true; step1.classList.add('done'); checkReady(); }, 2000); });
  waLink.addEventListener('click', () => { setTimeout(() => { waDone = true; step2.classList.add('done'); checkReady(); }, 2000); });
  function checkReady() { btnUnlock.disabled = !(fbDone && waDone); }
  btnUnlock.addEventListener('click', async () => {
    if (!fbDone || !waDone) return;
    btnUnlock.textContent = 'Opening VoiceForge…';
    btnUnlock.disabled = true;
    try {
      await fetch('/api/verify', { method: 'POST' });
      localStorage.setItem('vf_verified', 'true');
      showToast('Welcome to VoiceForge!', 'success');
      setTimeout(showApp, 500);
    } catch {
      localStorage.setItem('vf_verified', 'true');
      showApp();
    }
  });
}

/* VoiceForge - Batch Generation Page */
function initBatchPage() {
  const page = document.getElementById('batch-page');
  if (!page || page.dataset.initialized) return;
  page.dataset.initialized = 'true';
  page.innerHTML = `
    <h2>Batch Generation</h2>
    <p>Generate speech for multiple text lines and download the audio files as a ZIP archive.</p>
    <div class="studio-grid">
      <div class="panel">
        <label for="batchText">Text input, one line per audio file</label>
        <textarea id="batchText" rows="14" maxlength="100000" placeholder="First line of speech&#10;Second line of speech"></textarea>
      </div>
      <div class="panel">
        <label for="batchVoice">Voice</label><select id="batchVoice"></select>
        <label for="batchLang">Language</label><select id="batchLang"><option value="en">English</option></select>
        <label for="batchFormat">Output format</label><select id="batchFormat"><option value="wav">WAV</option><option value="mp3">MP3</option></select>
        <label for="batchSpeed">Speed <span id="batchSpeedVal">1.0x</span></label><input type="range" id="batchSpeed" min="0.5" max="2" step="0.1" value="1">
        <label for="batchPitch">Pitch <span id="batchPitchVal">1.0x</span></label><input type="range" id="batchPitch" min="0.5" max="2" step="0.1" value="1">
        <label for="batchReverb">Reverb <span id="batchReverbVal">0%</span></label><input type="range" id="batchReverb" min="0" max="1" step="0.1" value="0">
        <button id="btnBatchGenerate" type="button">Generate Batch (ZIP)</button>
      </div>
    </div>`;
  for (const [id, out, suffix] of [['batchSpeed','batchSpeedVal','x'],['batchPitch','batchPitchVal','x']]) {
    document.getElementById(id).addEventListener('input', e => document.getElementById(out).textContent = e.target.value + suffix);
  }
  document.getElementById('batchReverb').addEventListener('input', e => document.getElementById('batchReverbVal').textContent = Math.round(Number(e.target.value) * 100) + '%');
  document.getElementById('btnBatchGenerate').addEventListener('click', runBatch);
  loadBatchVoices();
}

async function loadBatchVoices() {
  const select = document.getElementById('batchVoice');
  if (!select) return;
  try {
    const res = await fetch('/api/voices');
    const data = await res.json();
    select.innerHTML = (data.voices || []).map(v => {
      const option = document.createElement('option');
      option.value = v.id;
      option.textContent = v.name + (v.is_cloned ? ' (Cloned)' : '');
      return option.outerHTML;
    }).join('');
    select.value = 'alba';
  } catch { showToast('Could not load voices.', 'error'); }
}

async function runBatch() {
  const lines = document.getElementById('batchText').value.split('\n').map(s => s.trim()).filter(Boolean);
  if (!lines.length) return showToast('Enter text before generating.', 'error');
  if (lines.length > 100) return showToast('Maximum 100 lines per batch.', 'error');
  const btn = document.getElementById('btnBatchGenerate');
  btn.disabled = true;
  try {
    const res = await fetch('/api/batch', {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({
      texts:lines, voice_id:document.getElementById('batchVoice').value, language:document.getElementById('batchLang').value,
      output_format:document.getElementById('batchFormat').value, speed:Number(document.getElementById('batchSpeed').value),
      pitch:Number(document.getElementById('batchPitch').value), reverb:Number(document.getElementById('batchReverb').value)
    })});
    if (!res.ok) throw new Error('Batch endpoint returned ' + res.status);
    const url = URL.createObjectURL(await res.blob());
    const a = document.createElement('a'); a.href=url; a.download='VoiceForge-Batch.zip'; a.click(); URL.revokeObjectURL(url);
    showToast('Batch generated.', 'success');
  } catch (e) { showToast(e.message, 'error'); }
  finally { btn.disabled = false; }
}

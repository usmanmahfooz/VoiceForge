/* VoiceForge TTS Studio */
let studioPlayer = null;
let studioVoice = {id:'alba',name:'Alba',gender:'female',language:'en',description:'Clear, versatile female voice'};

function initStudioPage() {
  const page = document.getElementById('studio-page');
  if (!page || page.dataset.initialized) return;
  page.dataset.initialized = 'true';
  page.innerHTML = `
  <div class="studio-grid">
    <section class="panel studio-main">
      <h2>Text to Speech</h2>
      <div class="text-area-wrap"><textarea id="ttsText" maxlength="5000" placeholder="Type or paste text to turn it into speech…"></textarea><span class="char-count"><span id="charCount">0</span> / 5,000</span></div>
      <div class="controls-row">
        <div class="control-group"><label for="ttsLang">Language</label><select id="ttsLang"><option value="en">English</option></select></div>
        <div class="control-group"><label for="ttsSpeed">Speed <span id="speedVal">1.0x</span></label><input id="ttsSpeed" type="range" min=".5" max="2" step=".1" value="1"></div>
        <div class="control-group"><label for="ttsPitch">Pitch <span id="pitchVal">1.0x</span></label><input id="ttsPitch" type="range" min=".5" max="2" step=".1" value="1"></div>
        <div class="control-group"><label for="ttsReverb">Reverb <span id="reverbVal">0%</span></label><input id="ttsReverb" type="range" min="0" max="1" step=".1" value="0"></div>
      </div>
      <div class="controls-row">
        <div class="control-group"><label for="ttsBgm">Background music</label><select id="ttsBgm"><option value="">None</option></select><button id="btnUploadBgm" type="button">Upload</button><input type="file" id="bgmFileInput" accept="audio/*" hidden></div>
        <div class="control-group"><label for="ttsFormat">Output format</label><select id="ttsFormat"><option value="wav">WAV</option><option value="mp3">MP3</option></select></div>
      </div>
      <button id="btnGenerate" type="button" class="btn-generate">Generate Speech</button>
      <div id="resultSection" hidden><h3>Generated audio</h3><div id="studioPlayerContainer"></div></div>
    </section>
    <aside class="panel studio-sidebar">
      <h3>Selected voice</h3><button id="voiceSelector" type="button" class="voice-selector"><span id="selAvatar">A</span> <strong id="selName">Alba</strong><span id="selDesc">Clear, versatile female voice</span></button>
      <h3>Recent generations</h3><div id="historyList" class="history-list"><p>No generations yet.</p></div>
      <a href="/api/history/download-all">Download history (ZIP)</a>
    </aside>
  </div>`;
  const textarea = document.getElementById('ttsText');
  textarea.addEventListener('input', () => document.getElementById('charCount').textContent = textarea.value.length);
  [['ttsSpeed','speedVal','x'],['ttsPitch','pitchVal','x']].forEach(([id,out,suffix]) => document.getElementById(id).addEventListener('input', e => document.getElementById(out).textContent=e.target.value+suffix));
  document.getElementById('ttsReverb').addEventListener('input', e => document.getElementById('reverbVal').textContent=Math.round(Number(e.target.value)*100)+'%');
  document.getElementById('btnGenerate').addEventListener('click', generateSpeech);
  document.getElementById('voiceSelector').addEventListener('click', () => navigateTo('voices'));
  const bgmInput = document.getElementById('bgmFileInput');
  document.getElementById('btnUploadBgm').addEventListener('click', () => bgmInput.click());
  bgmInput.addEventListener('change', uploadBgm);
  studioPlayer = new AudioPlayer(document.getElementById('studioPlayerContainer'));
  updateVoiceSelector(); loadHistory(); loadBgmList();
}
async function loadBgmList() {
  try { const r=await fetch('/api/bgm'); if(!r.ok)return; const d=await r.json(); const s=document.getElementById('ttsBgm'); s.innerHTML='<option value="">None</option>'+(d.bgm_files||[]).map(f=>'<option value="'+encodeURIComponent(f)+'">'+f+'</option>').join(''); } catch {}
}
async function uploadBgm() {
  const input=document.getElementById('bgmFileInput'); if(!input.files[0])return;
  const fd=new FormData(); fd.append('audio',input.files[0]);
  try { const r=await fetch('/api/bgm/upload',{method:'POST',body:fd}); if(!r.ok)throw new Error('Upload failed'); showToast('Background music uploaded.','success'); loadBgmList(); } catch(e){showToast(e.message,'error');}
}
function updateVoiceSelector() {
  const avatar=document.getElementById('selAvatar'); if(!avatar)return;
  avatar.textContent=(studioVoice.name||'?')[0]; avatar.style.background=typeof getAvatarColor==='function'?getAvatarColor(studioVoice.name):'#008080';
  document.getElementById('selName').textContent=studioVoice.name;
  document.getElementById('selDesc').textContent=studioVoice.description||studioVoice.gender||'AI voice';
}
function selectVoice(voice) { studioVoice=voice; updateVoiceSelector(); navigateTo('studio'); showToast('Selected '+voice.name,'success'); }
async function generateSpeech() {
  const text=document.getElementById('ttsText').value.trim(); if(!text)return showToast('Enter some text first.','error');
  const btn=document.getElementById('btnGenerate'); btn.disabled=true;
  try {
    const r=await fetch('/api/generate',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({
      text,voice_id:studioVoice.id,speed:Number(document.getElementById('ttsSpeed').value),language:document.getElementById('ttsLang').value,
      pitch:Number(document.getElementById('ttsPitch').value),reverb:Number(document.getElementById('ttsReverb').value),
      bgm_file:document.getElementById('ttsBgm').value||null,output_format:document.getElementById('ttsFormat').value})});
    if(!r.ok){const e=await r.json();throw new Error(e.detail||'Speech generation failed');}
    const blob=await r.blob(); const format=document.getElementById('ttsFormat').value; const id=r.headers.get('X-File-Id')||'voiceforge-audio';
    document.getElementById('resultSection').hidden=false; studioPlayer.loadBlob(blob,id+'.'+format); showToast('Speech generated.','success'); loadHistory();
  } catch(e){showToast(e.message,'error');} finally {btn.disabled=false;btn.textContent='Generate Speech';}
}
async function loadHistory() {
  const list=document.getElementById('historyList'); if(!list)return;
  try {const r=await fetch('/api/history');if(!r.ok)return;const d=await r.json();list.textContent='';
    (d.history||[]).slice(0,10).forEach(item=>{const row=document.createElement('div');row.className='history-item';row.textContent=(item.text||'Speech')+' · '+new Date(item.timestamp*1000).toLocaleTimeString();list.appendChild(row);});
    if(!list.children.length)list.textContent='No generations yet.';
  } catch {}
}

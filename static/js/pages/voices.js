function initVoicesPage() {
  const page=document.getElementById('voices-page');if(!page||page.dataset.initialized)return;page.dataset.initialized='true';
  page.innerHTML=`<div class="panel"><h2>Voice Library</h2><input id="voiceSearch" type="search" placeholder="Search voices…" aria-label="Search voices"><div id="voicesGrid" class="voices-grid"></div></div>`;
  document.getElementById('voiceSearch').addEventListener('input',loadVoices);loadVoices();
}
async function loadVoices() {
  const grid=document.getElementById('voicesGrid');if(!grid)return;
  try {const q=document.getElementById('voiceSearch').value;const r=await fetch('/api/voices?search='+encodeURIComponent(q));const d=await r.json();grid.textContent='';(d.voices||[]).forEach(v=>grid.appendChild(createVoiceCard(v,{onSelect:selectVoice,onPreview:async voice=>{try{const audio=await fetch('/api/preview/'+encodeURIComponent(voice.id));if(!audio.ok)throw new Error('Preview failed');const blob=await audio.blob();const url=URL.createObjectURL(blob);const player=document.createElement('audio');player.controls=true;player.src=url;player.play();}catch(e){showToast(e.message,'error');}}})));}catch(e){showToast('Could not load voices.','error');}
}

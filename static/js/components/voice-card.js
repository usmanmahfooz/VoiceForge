function getAvatarColor(name) {
 const colors=['#8b5cf6','#06b6d4','#ec4899','#f59e0b','#22c55e','#6366f1','#f43f5e','#14b8a6'];
 let hash=0;for(let i=0;i<(name||'').length;i++)hash=name.charCodeAt(i)+((hash<<5)-hash);
 return colors[Math.abs(hash)%colors.length];
}
function createVoiceCard(voice,{onSelect,onPreview}={}) {
 const card=document.createElement('article');card.className='voice-card';const title=document.createElement('h3');title.textContent=voice.name;const description=document.createElement('p');description.textContent=voice.description||'AI voice';const preview=document.createElement('button');preview.type='button';preview.textContent='Preview';const select=document.createElement('button');select.type='button';select.textContent='Use Voice';
 preview.addEventListener('click',()=>onPreview&&onPreview(voice));select.addEventListener('click',()=>onSelect&&onSelect(voice));card.append(title,description,preview,select);return card;
}

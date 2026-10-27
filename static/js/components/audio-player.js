class AudioPlayer {
  constructor(container) {
    this.container=typeof container==='string'?document.querySelector(container):container;
    this.audio=new Audio();this.audioSrc=null;this.downloadName='voiceforge_audio.wav';
    this.render();
  }
  render() {
    this.container.classList.add('audio-player');
    this.container.innerHTML='<button type="button" class="ap-play" aria-label="Play or pause">Play</button><audio controls></audio><button type="button" class="ap-download">Download</button>';
    this.audio=this.container.querySelector('audio');
    this.container.querySelector('.ap-play').addEventListener('click',()=>this.audio.paused?this.audio.play():this.audio.pause());
    this.container.querySelector('.ap-download').addEventListener('click',()=>{if(!this.audioSrc)return;const a=document.createElement('a');a.href=this.audioSrc;a.download=this.downloadName;a.click();});
  }
  loadAudio(src){this.audioSrc=src;this.audio.src=src;}
  loadBlob(blob,name){this.downloadName=name||this.downloadName;this.loadAudio(URL.createObjectURL(blob));}
  stop(){this.audio.pause();this.audio.currentTime=0;}
}

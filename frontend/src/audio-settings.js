export const AUDIO_DEFAULTS = Object.freeze({master:.8,music:.45,ui:.7,battle:1,ambient:.35,muted:false});
const KEY='fortcamp.audio.v1';
export function normalizeAudioSettings(value={}){
  return Object.fromEntries(Object.entries(AUDIO_DEFAULTS).map(([key,fallback])=>[key,key==='muted'?value[key]===true:Number.isFinite(value[key])?Math.max(0,Math.min(1,value[key])):fallback]));
}
export function audioCategory(name){return name.startsWith('ui_')||name.startsWith('mission_')?'ui':'battle'}
export function audioVolume(settings,category,base=1){return settings.muted?0:Math.max(0,Math.min(1,base*settings.master*(settings[category]??1)))}
export function createAudioMixer(storage){
  let settings={...AUDIO_DEFAULTS};
  try{settings=normalizeAudioSettings(JSON.parse(storage?.getItem(KEY)||'{}'))}catch{}
  const active=new Map(),listeners=new Set();
  const notify=()=>{for(const [audio,{category,base}] of active)audio.volume=audioVolume(settings,category,base);for(const listener of listeners)listener({...settings})};
  return {
    get settings(){return {...settings}},
    volume:(category,base=1)=>audioVolume(settings,category,base),
    update(patch){settings=normalizeAudioSettings({...settings,...patch});try{storage?.setItem(KEY,JSON.stringify(settings))}catch{}notify()},
    track(audio,category,base=1){active.set(audio,{category,base});audio.volume=audioVolume(settings,category,base);const release=()=>active.delete(audio);audio.addEventListener('ended',release,{once:true});audio.addEventListener('error',release,{once:true});return release},
    subscribe(listener){listeners.add(listener);return()=>listeners.delete(listener)},
  };
}
export function mountAudioSettings(root,mixer,onPreview){
  const labels={master:'Master volume',music:'Music',ui:'Interface & mission sounds',battle:'Battle effects',ambient:'Ambient sounds'};
  root.innerHTML=`<div class="eyebrow">AUDIO</div><h2 id="audio-settings-title">Sound settings</h2><p class="muted">Saved on this device. Master volume affects every channel.</p><label class="audio-mute"><input type="checkbox" data-audio-mute> Mute all audio</label><div class="audio-sliders">${Object.entries(labels).map(([key,label])=>`<label><span>${label}</span><output data-audio-output="${key}"></output><input type="range" min="0" max="100" step="1" data-audio-level="${key}" aria-label="${label}"></label>`).join('')}</div><p class="muted small">Music follows regional events, base and battle scenarios. Ambient sounds include quiet environmental accents and wood-fire crackle during Goblin events; set their slider to zero to disable them.</p><div class="audio-previews"><button data-audio-preview="ui_click">Test UI</button><button data-audio-preview="melee_hit_light">Test battle</button><button data-audio-preview="mission_success">Test success</button><button data-audio-preview="mission_failure">Test failure</button></div><p><a class="music-audition-link" href="/assets/music/LISTEN.html" target="_blank" rel="noopener">Listen to the music library</a> ? <a href="/assets/sfx/ambient/preview.html" target="_blank" rel="noopener">Preview ambient sounds</a></p><button data-audio-reset>Restore defaults</button>`;
  const render=settings=>{root.querySelector('[data-audio-mute]').checked=settings.muted;for(const key of Object.keys(labels)){root.querySelector(`[data-audio-level="${key}"]`).value=Math.round(settings[key]*100);root.querySelector(`[data-audio-output="${key}"]`).textContent=`${Math.round(settings[key]*100)}%`}};
  render(mixer.settings);const unsubscribe=mixer.subscribe(render);
  root.querySelectorAll('[data-audio-level]').forEach(input=>input.oninput=()=>mixer.update({[input.dataset.audioLevel]:Number(input.value)/100}));
  root.querySelector('[data-audio-mute]').onchange=event=>mixer.update({muted:event.target.checked});
  root.querySelector('[data-audio-reset]').onclick=()=>mixer.update(AUDIO_DEFAULTS);
  root.querySelectorAll('[data-audio-preview]').forEach(button=>button.onclick=()=>onPreview(button.dataset.audioPreview));
  return unsubscribe;
}

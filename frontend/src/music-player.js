const ROOT='/assets/music/';
export const MUSIC_PLAYLISTS={
  board:['01_lanternlight','02_guildhall_shuffle','03_roads_waiting','04_mapmakers_clock'].map(id=>({id,url:`${ROOT}guild-board-candidates-v1/${id}.mp3`})),
  base:[{id:'05_hearth_and_camp',url:`${ROOT}location-themes-v1/05_hearth_and_camp.mp3`}],
  combat:[{id:'06_roads_under_pressure',url:`${ROOT}location-themes-v1/06_roads_under_pressure.mp3`}],
  goblin:[{id:'07_goblin_warcamp',url:`${ROOT}location-themes-v1/07_goblin_warcamp.mp3`}],
};
export function musicContext(tab,battle){
  if(battle){const goblins=/goblin/i.test(battle.encounter_id||'')||Object.values(battle.units||{}).some(u=>u.team==='enemy'&&/^(goblin|hobgoblin)$/i.test(u.race||''));return goblins?'goblin':'combat'}
  return tab==='base'?'base':'board';
}
export function createMusicPlayer(mixer,{AudioClass=globalThis.Audio,now=()=>performance.now(),schedule=fn=>setInterval(fn,50),cancel=clearInterval,playlists=MUSIC_PLAYLISTS}={}){
  let context=null,unlocked=false,current=null,timer=null,suspended=false,disposed=false;
  const entries=new Set(),failed=new Set(),cursors=new Map();
  const fadeMs=3000;
  function apply(){for(const entry of entries)entry.audio.volume=mixer.volume('music',.85*entry.gain)}
  function remove(entry){entry.audio.pause();entry.audio.removeAttribute('src');entry.audio.load();entries.delete(entry);if(current===entry)current=null}
  function fade(entry,to){entry.from=entry.gain;entry.to=to;entry.started=now();entry.fading=true}
  function tick(){
    if(suspended)return;
    const time=now();
    for(const entry of [...entries])if(entry.fading){const t=Math.max(0,Math.min(1,(time-entry.started)/fadeMs)),ease=t*t*(3-2*t);entry.gain=entry.from+(entry.to-entry.from)*ease;if(t===1){entry.fading=false;if(entry.to===0)remove(entry)}}
    apply();
    if(current&&!current.audio.paused&&Number.isFinite(current.audio.duration)&&current.audio.duration>10&&current.audio.currentTime>=current.audio.duration-3)start();
  }
  async function start(){
    if(disposed||!unlocked||!context||suspended)return;
    const pool=(playlists[context]||[]).filter(track=>!failed.has(track.id));if(!pool.length)return;
    const cursor=cursors.get(context)||0,track=pool[cursor%pool.length];cursors.set(context,cursor+1);
    const previous=current;
    const audio=new AudioClass(track.url);audio.preload='auto';audio.volume=0;
    const entry={audio,track,context,gain:0,from:0,to:1,started:now(),fading:false};entries.add(entry);current=entry;
    const fail=()=>{if(!entries.has(entry))return;failed.add(track.id);const wasCurrent=current===entry;remove(entry);if(wasCurrent)start()};
    audio.addEventListener('error',fail,{once:true});
    audio.addEventListener('ended',()=>{if(current===entry){remove(entry);start()}else if(entries.has(entry))remove(entry)},{once:true});
    try{await audio.play();if(!entries.has(entry))return;if(current!==entry||entry.context!==context){remove(entry);return}for(const old of entries)if(old!==entry)fade(old,0);fade(entry,1);if(!timer)timer=schedule(tick)}
    catch(error){if(!entries.has(entry))return;remove(entry);if(error.name==='NotAllowedError'){unlocked=false;if(previous&&entries.has(previous))current=previous}else{failed.add(track.id);start()}}
  }
  const unsubscribe=mixer.subscribe(apply);
  return {
    setContext(value){if(disposed||value===context)return;context=value;if(unlocked)start()},
    unlock(){if(disposed)return;if(!unlocked){unlocked=true;if(!current)start()}},
    suspend(value){if(disposed||value===suspended)return;suspended=value;if(value){for(const entry of entries)entry.audio.pause()}else{for(const entry of entries){entry.started=now();entry.from=entry.gain;entry.audio.play().catch(error=>{if(error.name==='NotAllowedError'){unlocked=false;if(entries.has(entry))remove(entry)}})}if(!current||current.context!==context)start()}},
    dispose(){disposed=true;unsubscribe();if(timer)cancel(timer);for(const entry of [...entries])remove(entry)},
    get currentTrack(){return current?.track.id||null},
  };
}

const ROOT='/assets/music/';
export const MUSIC_PLAYLISTS={
  board:['01_lanternlight','02_guildhall_shuffle','03_roads_waiting','04_mapmakers_clock'].map(id=>({id,url:`${ROOT}guild-board-candidates-v1/${id}.mp3`})),
  base:[{id:'05_hearth_and_camp',url:`${ROOT}location-themes-v1/05_hearth_and_camp.mp3`}],
  combat:[{id:'06_roads_under_pressure',url:`${ROOT}location-themes-v1/06_roads_under_pressure.mp3`}],
  goblin:[{id:'07_goblin_warcamp',url:`${ROOT}location-themes-v1/07_goblin_warcamp.mp3`}],
  boss:['boss_1','boss_2'].map(id=>({id,url:`${ROOT}mureka-import-v1/${id}.mp3`})),
  defense:['defense_1','defense_2'].map(id=>({id,url:`${ROOT}mureka-import-v1/${id}.mp3`})),
  undead:['undead_1','undead_2'].map(id=>({id,url:`${ROOT}mureka-import-v1/${id}.mp3`})),
  investigation:['investigation_1','investigation_2'].map(id=>({id,url:`${ROOT}mureka-import-v1/${id}.mp3`})),
  ...Object.fromEntries(['goblin_warhost','ashen_procession','arcane_convergence','great_beast_tide','starfall_omen'].map(event=>[event,[1,2].map(n=>({id:`${event}_${n}`,url:`${ROOT}regional-events-v1/${event}_${n}.mp3`}))])),
};
export function musicContext(tab,battle,scene,event){
  if(battle){
    if(MUSIC_PLAYLISTS[battle.music_theme])return battle.music_theme;
    const encounter=battle.encounter_id||'',enemies=Object.values(battle.units||{}).filter(u=>u.team==='enemy');
    if(battle.complication_boss||['contract:goblin_chieftain','contract:undead_death_knight','contract:black_banner_court'].includes(encounter))return 'boss';
    if(battle.preparation||/defense|siege/i.test(encounter))return 'defense';
    if(/undead|bone|grave|crypt/i.test(encounter)||enemies.some(u=>/^(undead|banshee|revenant|skeleton|zombie|lich)$/i.test(u.race||'')))return 'undead';
    const goblins=/goblin/i.test(encounter)||enemies.some(u=>/^(goblin|hobgoblin)$/i.test(u.race||''));return goblins?'goblin':'combat';
  }
  if(scene?.mission_form==='investigation')return 'investigation';
  return tab==='base'?'base':MUSIC_PLAYLISTS[event?.id]?event.id:'board';
}
export function musicTransitionPolicy(tab,battle,scene,currentContext,event){
  const context=musicContext(tab,battle,scene,event);
  const encounterContexts=['combat','goblin','boss','defense','undead','investigation'];
  const delayMs=battle||!currentContext?0:context==='investigation'?8000:encounterContexts.includes(currentContext)?5000:700;
  return {context,delayMs};
}
export function createMusicPlayer(mixer,{AudioClass=globalThis.Audio,now=()=>performance.now(),schedule=fn=>setInterval(fn,50),cancel=clearInterval,playlists=MUSIC_PLAYLISTS}={}){
  let context=null,unlocked=false,current=null,timer=null,suspended=false,disposed=false,pending=null;
  const entries=new Set(),failed=new Set(),cursors=new Map(),resumePoints=new Map();
  const fadeMs=3000;
  function apply(){for(const entry of entries)entry.audio.volume=mixer.volume('music',.85*entry.gain)}
  function remove(entry){
    if(entry.context!==context&&entry.audio.currentTime>0&&entry.audio.currentTime<entry.audio.duration-5)resumePoints.set(entry.context,{id:entry.track.id,time:entry.audio.currentTime});
    entry.audio.pause();entry.audio.removeAttribute('src');entry.audio.load();entries.delete(entry);if(current===entry)current=null;
  }
  function fade(entry,to){entry.from=entry.gain;entry.to=to;entry.started=now();entry.fading=true}
  function tick(){
    if(suspended)return;
    const time=now();
    if(pending&&time>=pending.due){context=pending.value;pending=null;start()}
    for(const entry of [...entries])if(entry.fading){const t=Math.max(0,Math.min(1,(time-entry.started)/fadeMs)),ease=t*t*(3-2*t);entry.gain=entry.from+(entry.to-entry.from)*ease;if(t===1){entry.fading=false;if(entry.to===0)remove(entry)}}
    apply();
    if(current&&!current.audio.paused&&Number.isFinite(current.audio.duration)&&current.audio.duration>10&&current.audio.currentTime>=current.audio.duration-3)start(true);
  }
  async function start(advance=false){
    if(disposed||!unlocked||!context||suspended)return;
    if(!advance){
      const retiring=[...entries].find(entry=>entry.context===context&&entry!==current&&!failed.has(entry.track.id));
      if(retiring){current=retiring;for(const old of entries)if(old!==retiring)fade(old,0);fade(retiring,1);retiring.audio.play().catch(()=>{});return}
    }
    const pool=(playlists[context]||[]).filter(track=>!failed.has(track.id));if(!pool.length)return;
    const remembered=advance?null:resumePoints.get(context),resume=remembered&&pool.find(track=>track.id===remembered.id);
    const cursor=cursors.get(context)||0,track=resume||pool[cursor%pool.length];if(!resume)cursors.set(context,cursor+1);resumePoints.delete(context);
    const previous=current;
    const audio=new AudioClass(track.url);audio.preload='auto';audio.volume=0;
    if(resume){const seek=()=>{if(Number.isFinite(audio.duration))audio.currentTime=Math.min(remembered.time,audio.duration-5)};audio.addEventListener('loadedmetadata',seek,{once:true});try{audio.currentTime=remembered.time}catch{}}
    const entry={audio,track,context,gain:0,from:0,to:1,started:now(),fading:false};entries.add(entry);current=entry;
    const fail=()=>{if(!entries.has(entry))return;failed.add(track.id);const wasCurrent=current===entry;remove(entry);if(wasCurrent)start()};
    audio.addEventListener('error',fail,{once:true});
    audio.addEventListener('ended',()=>{if(current===entry){remove(entry);start(true)}else if(entries.has(entry))remove(entry)},{once:true});
    try{await audio.play();if(!entries.has(entry))return;if(current!==entry||entry.context!==context){remove(entry);return}for(const old of entries)if(old!==entry)fade(old,0);fade(entry,1);if(!timer)timer=schedule(tick)}
    catch(error){if(!entries.has(entry))return;remove(entry);if(error.name==='NotAllowedError'){unlocked=false;if(previous&&entries.has(previous))current=previous}else{failed.add(track.id);start()}}
  }
  const unsubscribe=mixer.subscribe(apply);
  return {
    setContext(value,{delayMs=0}={}){
      if(disposed)return;
      if(value===context){pending=null;return}
      if(pending?.value===value)return;
      if(delayMs>0&&context){pending={value,due:now()+delayMs};if(!timer)timer=schedule(tick);return}
      pending=null;context=value;if(unlocked)start();
    },
    unlock(){if(disposed)return;if(!unlocked){unlocked=true;if(!current)start()}},
    suspend(value){if(disposed||value===suspended)return;suspended=value;if(value){for(const entry of entries)entry.audio.pause()}else{for(const entry of entries){entry.started=now();entry.from=entry.gain;entry.audio.play().catch(error=>{if(error.name==='NotAllowedError'){unlocked=false;if(entries.has(entry))remove(entry)}})}if(!current||current.context!==context)start()}},
    dispose(){disposed=true;unsubscribe();if(timer)cancel(timer);for(const entry of [...entries])remove(entry)},
    get currentTrack(){return current?.track.id||null},
    get currentContext(){return context},
  };
}

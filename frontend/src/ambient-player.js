const ROOT='/assets/sfx/ambient/';
export const AMBIENCE={
  goblin_warhost:['goblin_chatter','goblin_camp'],goblin:['goblin_chatter','goblin_camp'],
  ashen_procession:['ashen_procession'],undead:['ashen_procession'],
  arcane_convergence:['arcane_disturbance'],great_beast_tide:['beast_call','beast_passage'],starfall_omen:['starfall_machine'],
};
export function createAmbientPlayer(mixer,{context=()=>null,AudioClass=globalThis.Audio,now=()=>performance.now(),random=Math.random,schedule=fn=>setInterval(fn,250),cancel=clearInterval}={}){
  let unlocked=false,suspended=false,disposed=false,region=null,active=null,due=Infinity;
  const failed=new Set(),last=new Map();
  const wait=(initial=false)=>now()+(initial?18000:45000)+random()*(initial?17000:35000);
  function remove(entry){entry.audio.pause();entry.audio.removeAttribute('src');entry.audio.load();if(active===entry)active=null}
  function retire(){if(active&&!active.retiring)active.retiring={at:now(),gain:active.gain}}
  function tick(){
    if(disposed||suspended||!unlocked)return;
    const selected=AMBIENCE[context()]?context():null;
    if(selected!==region){region=selected;due=wait(true);retire()}
    if(mixer.volume('ambient')===0){if(active)remove(active);due=wait(true);return}
    if(active){
      const age=now()-active.started;
      active.gain=active.retiring?active.retiring.gain*Math.max(0,1-(now()-active.retiring.at)/700):Math.min(1,age/700);
      active.audio.volume=mixer.volume('ambient',.55*active.gain);
      if(active.retiring&&active.gain===0)remove(active);
      return;
    }
    if(!region||now()<due)return;
    const pool=AMBIENCE[region].filter(id=>!failed.has(id)),choices=pool.filter(id=>id!==last.get(region));
    if(!pool.length){due=Infinity;return}
    const options=choices.length?choices:pool,id=options[Math.min(options.length-1,Math.floor(random()*options.length))];
    const audio=new AudioClass(ROOT+id+'.mp3'),entry={audio,id,started:now(),gain:0};
    audio.preload='none';audio.volume=0;active=entry;last.set(region,id);due=Infinity;
    const finish=()=>{if(active===entry){remove(entry);due=wait()}};
    audio.addEventListener('ended',finish,{once:true});
    audio.addEventListener('error',()=>{failed.add(id);finish()},{once:true});
    audio.play().catch(error=>{if(active!==entry)return;if(error.name==='NotAllowedError')unlocked=false;else failed.add(id);finish()});
  }
  const timer=schedule(tick),unsubscribe=mixer.subscribe(()=>{if(active)active.audio.volume=mixer.volume('ambient',.55*active.gain)});
  return {
    unlock(){if(disposed)return;unlocked=true},
    suspend(value){if(disposed||suspended===value)return;suspended=value;if(value){if(active)remove(active)}else due=wait(true)},
    dispose(){disposed=true;cancel(timer);unsubscribe();if(active)remove(active)},
  };
}

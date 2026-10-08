// Decode short-lived spell sprites before starting their shared impact clock.
const root='/assets/mage-v1/';
const frozen=()=>['freeze','frozen','break','thaw'].flatMap(kind=>[1,2,3,4].map(i=>`/assets/mage-frozen-v2/${kind}_${i}.png`));
const scorch=()=>['/assets/mage-scorched-v3/fire_strip.png',...[1,2,3,4].flatMap(i=>[`/assets/mage-scorched-v2/soot_${i}.png`,`/assets/mage-scorched-v2/ash_${i}.png`])];
export function magePlaybackAssets(events=[]){
 const paths=new Set();const add=name=>paths.add(root+name+'.png');
 for(const e of events){
  if(e.status_id==='freeze'||e.statuses_snapshot?.some(s=>s.id==='freeze'&&s.elemental_freeze))frozen().forEach(p=>paths.add(p));
  const k=e.mage_skill;
  if(k==='meteor'){add('meteor_rock');add('fire_contact');scorch().forEach(p=>paths.add(p))}
  if(k==='fireball'){add('fire_contact');scorch().forEach(p=>paths.add(p))}
  if(k==='chain_lightning')add('lightning_arc');
  if(k==='singularity'||k==='meteor_armed')add('gravity_vortex');
  if(k==='typhoon')add('wind_ring');
  if(k==='flash_freeze'||k==='flash_freeze_armed'){add('frost_ground');frozen().forEach(p=>paths.add(p))}
  if(k==='enchant_weapon'){
   if(e.enchant_element==='fire')add('fire_contact');
   else if(e.enchant_element==='frost'){add('frost_ground');frozen().forEach(p=>paths.add(p))}
   else add('lightning_arc');
  }
  if(e.type==='zone_created')scorch().forEach(p=>paths.add(p));
 }
 return [...paths];
}
export function createDecodedAssetCache({ImageClass=globalThis.Image,timeoutMs=8000}={}){
 const cache=new Map();
 return paths=>Promise.all(paths.map(path=>{
  if(cache.has(path))return cache.get(path).promise;
  if(!ImageClass)return Promise.resolve(false);
  const image=new ImageClass();
  const promise=new Promise(resolve=>{
   let finished=false;
   const finish=ok=>{if(finished)return;finished=true;clearTimeout(timer);image.onload=image.onerror=null;resolve(ok)};
   const timer=setTimeout(()=>finish(false),timeoutMs);
   image.onload=async()=>{try{await image.decode?.();finish(true)}catch{finish(false)}};
   image.onerror=()=>finish(false);image.src=path;
  });
  cache.set(path,{image,promise});return promise;
 }));
}
let load;
const ready=paths=>(load??=createDecodedAssetCache())(paths);
export function prepareMagePlayback(battle){return ready(magePlaybackAssets(battle?.animation_events))}
export function warmMageBattle(battle){
 const events=Object.values(battle?.units||{}).flatMap(u=>(u.skills||[]).filter(s=>s.mage_kind).flatMap(s=>s.mage_kind==='enchant_weapon'?['fire','frost','lightning'].map(enchant_element=>({mage_skill:s.mage_kind,enchant_element})):[{mage_skill:s.mage_kind}]));
 return ready(magePlaybackAssets(events));
}

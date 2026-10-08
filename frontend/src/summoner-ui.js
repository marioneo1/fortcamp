import {bindPlacementPanel,placementPoint,placementCursor,clearPlacementCursor} from './combat-placement-panel.js';
let binding=null,session=null;
export function resetSummonerPlacement(){session=null;binding?.abort();document.querySelectorAll('.summoner-panel,.summoner-target-layer').forEach(n=>n.remove());document.querySelectorAll('.summoner-legal-target').forEach(n=>n.classList.remove('summoner-legal-target'))}
const pointKey=p=>`${p.x},${p.y}`;
export function summonCommand(view,s){
 const a=view.units[view.current_unit_id],kind=a.special?.summoner_kind,base={action:'skill',skill_id:a.special?.id};
 if(s.order){
  const order={action:'summon_order',entity_id:s.entity,order:s.order};
  if(s.order==='protect')return (s.entity==='all'?(view.summoner.protect_summons||[]).length:(view.summoner.protect_summons||[]).includes(s.entity))&&(view.summoner.protect_targets||[]).includes(s.target)?{...order,target_id:s.target}:null;
  return s.order==='hold'?(s.point?{...order,...s.point}:null):s.order==='focus'?(s.target?{...order,target_id:s.target}:null):order;
 }
 if(['bound_companion','wisp_swarm'].includes(kind)){
  if(a.special.availability?.reclaim)return base;
  const legal=new Set((kind==='wisp_swarm'?view.summoner.wisp_placement:view.summoner.placement).map(pointKey));
  if(s.positions.length!==(kind==='wisp_swarm'?3:1)||new Set(s.positions.map(pointKey)).size!==s.positions.length||s.positions.some(p=>!legal.has(pointKey(p)))||kind==='bound_companion'&&!s.element)return null;
  return {...base,positions:s.positions,...(s.element?{element:s.element}:{})};
 }
 if(kind==='transposition')return view.summoner.swaps[s.first]?.includes(s.target)?{...base,ally_id:s.first,target_id:s.target}:null;
 if(kind==='spirit_projection')return view.summoner.projection[s.target]>0?{...base,target_id:s.target}:null;
 if(kind==='sacrifice')return s.point&&view.summoner.sacrifice_cells.some(p=>pointKey(p)===pointKey(s.point))&&view.summoner.summons.some(id=>Math.max(Math.abs(view.units[id].x-s.point.x),Math.abs(view.units[id].y-s.point.y))<=1)?{...base,...s.point}:null;
 if(['overload','life_pact'].includes(kind))return view.summoner.summons.includes(s.target)&&!(kind==='overload'&&view.units[s.target].overloaded_once)&&!(kind==='life_pact'&&(a.hp<=Math.ceil(a.max_hp*.25)||view.units[s.target].hp>=view.units[s.target].max_hp))?{...base,target_id:s.target}:null;
 return null;
}
export function mountSummoner({view,mode,field,send,cancel,escape,blocked=()=>false}){
 binding?.abort();clearPlacementCursor(field);document.querySelectorAll('.summoner-panel,.summoner-target-layer,[data-summon-orders]').forEach(e=>e.remove());
 if(!field||!view.summoner)return;
 const a=view.units[view.current_unit_id],v=view.summoner,skill=a.special,kind=mode==='skill'?skill?.summoner_kind:null;
 const key=`${view.seed}:${a.id}:${a.ability_activation}:${mode}:${skill?.id}`;
 if(session?.key!==key)session={key,positions:[],element:null,first:null,target:null,point:null,order:null,entity:'all'};
 const s=session;if(kind==='orders'&&!s.order)s.order='choose';binding=new AbortController();const opts={signal:binding.signal},viewport=field.closest('.battle-viewport'),stage=viewport.parentElement;
 const panel=document.createElement('section'),layer=document.createElement('div');panel.className='summoner-panel';layer.className='summoner-target-layer';stage.append(panel);field.append(layer);
 bindPlacementPanel(panel,'summoner',binding.signal);
 const names={hold:'Hold Position',focus:'Focus Target',follow:'Follow Summoner',protect:'Protect Ally',stand_down:'Stand Down',clear:'Clear Order'};
 const close=()=>{session=null;binding?.abort();panel.remove();layer.remove();cancel()};
 panel.addEventListener('contextmenu',e=>{e.preventDefault();close()},opts);
 function paint(){
  if(!kind&&!s.order){panel.hidden=true;layer.innerHTML='';return}
  panel.hidden=false;
  const command=summonCommand(view,s),reclaim=!!skill?.availability?.reclaim;
  const canProtect=s.entity==='all'?(v.protect_summons||[]).length:(v.protect_summons||[]).includes(s.entity);
  let help;
  const select=s.order?`<label>Command <select data-summon-group><option value="all">All summons</option>${v.summons.map(id=>`<option value="${escape(id)}" ${s.entity===id?'selected':''}>${escape(view.units[id].name)}</option>`).join('')}</select></label><div class="summoner-choices">${Object.entries(names).filter(([id])=>id!=='protect'||canProtect).map(([id,name])=>`<button data-summon-order="${id}" class="${s.order===id?'selected':''}">${name}</button>`).join('')}</div>`:'';
  const elements=kind==='bound_companion'&&!reclaim&&!s.order?`<div class="summoner-choices">${['fire','earth','grass'].map(e=>`<button data-summon-element="${e}" class="${s.element===e?'selected':''}"><img src="/assets/summoner-v1/portrait_${e}.png" alt="">${e[0].toUpperCase()+e.slice(1)}</button>`).join('')}</div>`:'';
  const protect=s.order==='protect'?`<label>Protect ally <select data-summon-protect-target><option value="">Choose an ally</option>${(v.protect_targets||[]).map(id=>`<option value="${escape(id)}" ${s.target===id?'selected':''}>${escape(view.units[id].name)}${id===a.id?' (you)':''}</option>`).join('')}</select></label>`:'';
  if(s.order==='protect')help='Choose an ally on the map or from the list, including yourself. Grass heals them; Earth and Fire prioritize their threats. No attack interception. Applies only to the Bound Companion.';
  help=s.order?({choose:'Choose a summon or the whole group, then choose an order.',hold:'Choose a tile for your summons to travel to and hold.',focus:'Choose an enemy for your summons to pursue.',follow:'Keep summons near you while they attack nearby threats.',protect:'Choose an ally, including yourself, for your companion to heal or defend without intercepting attacks.',stand_down:'Keep summons in place without attacking.',clear:'Return summons to their normal independent behavior.'}[s.order]):reclaim?'Dismiss this group and begin its replacement cooldown.':kind==='bound_companion'?'Choose a companion and an empty tile within two cells.':kind==='wisp_swarm'?'Choose three empty tiles within two cells for your Wisps.':skill.description;
  const count=kind==='spirit_projection'&&s.target?`${v.projection[s.target]||0} contributions`:kind==='wisp_swarm'&&!reclaim?`${s.positions.length}/3 selected`:'';
  panel.innerHTML=`<header data-placement-handle><small>${s.order?'SUMMON COMMAND':'SUMMONER'} · DRAG TO MOVE</small><h3>${escape(s.order?'Summon orders':skill.name)}</h3></header><p>${escape(help)}</p>${count?`<small>${count}</small>`:''}${select}${elements}${protect}<footer><button data-summon-confirm ${!command||s.order==='choose'||blocked()?'disabled':''}><kbd>E</kbd> Confirm</button><button data-summon-cancel><kbd>C</kbd> Cancel</button></footer>`;
  panel.querySelector('[data-summon-cancel]').onclick=close;
  panel.querySelector('[data-summon-confirm]').onclick=()=>{if(blocked())return;const command=summonCommand(view,s);if(command&&s.order!=='choose'){session=null;panel.remove();layer.remove();send(command)}};
  panel.querySelector('[data-summon-group]')?.addEventListener('change',e=>{s.entity=e.target.value;if(s.order==='protect'&&s.entity!=='all'&&!(v.protect_summons||[]).includes(s.entity)){s.order='choose';s.target=null}paint()});
  panel.querySelector('[data-summon-protect-target]')?.addEventListener('change',e=>{s.target=e.target.value||null;paint()});
  panel.querySelectorAll('[data-summon-order]').forEach(b=>b.onclick=()=>{s.order=b.dataset.summonOrder;s.point=null;s.target=null;paint()});
  panel.querySelectorAll('[data-summon-element]').forEach(b=>b.onclick=()=>{s.element=b.dataset.summonElement;paint()});
  let cells=[];
  if(s.order==='hold')cells=s.point?[s.point]:[];
  else if(s.order==='protect')cells=(v.protect_targets||[]).map(id=>view.units[id]);
  else if(!s.order&&!reclaim&&['bound_companion','wisp_swarm'].includes(kind))cells=kind==='wisp_swarm'?v.wisp_placement:v.placement;
  else if(!s.order&&kind==='transposition')cells=(s.first?v.swaps[s.first]:Object.keys(v.swaps)).map(id=>view.units[id]);
  else if(!s.order&&kind==='spirit_projection')cells=Object.keys(v.projection).filter(id=>v.projection[id]>0).map(id=>view.units[id]);
  else if(!s.order&&['overload','life_pact'].includes(kind))cells=v.summons.map(id=>view.units[id]);
  else if(!s.order&&kind==='sacrifice')cells=s.point?Array.from({length:9},(_,i)=>({x:s.point.x+i%3-1,y:s.point.y+Math.floor(i/3)-1})).filter(p=>p.x>=0&&p.x<view.width&&p.y>=0&&p.y<view.height):v.sacrifice_cells;
  layer.innerHTML=cells.map(p=>`<i class="${s.positions.some(q=>pointKey(q)===pointKey(p))||s.target===p.id||s.first===p.id?'chosen':''} ${kind==='sacrifice'?'danger':''}" style="left:${p.x/view.width*100}%;top:${p.y/view.height*100}%;width:${100/view.width}%;height:${100/view.height}%"></i>`).join('');
  field.querySelectorAll('[data-battle-unit]').forEach(token=>{const id=token.dataset.battleUnit;token.classList.toggle('summoner-legal-target',cells.some(p=>p.id===id)||s.order==='focus'&&view.units[id].team!==a.team)});
 }
 field.addEventListener('click',e=>{
  if(!kind&&!s.order)return;e.stopImmediatePropagation();if(blocked())return;
  const rect=field.getBoundingClientRect(),cell=e.target.closest('[data-battle-cell]')?.dataset.battleCell,tokenId=e.target.closest('[data-battle-unit]')?.dataset.battleUnit;
  const p=tokenId?{x:view.units[tokenId].x,y:view.units[tokenId].y}:cell?{x:Number(cell.split(',')[0]),y:Number(cell.split(',')[1])}:{x:Math.floor((e.clientX-rect.left)/rect.width*view.width),y:Math.floor((e.clientY-rect.top)/rect.height*view.height)};
  const id=tokenId||Object.values(view.units).find(u=>u.x===p.x&&u.y===p.y&&u.alive!==false&&!u.extracted)?.id;
  if(s.order){if(s.order==='hold')s.point=p;else if(s.order==='focus'&&id&&view.units[id].team!==a.team)s.target=id;else if(s.order==='protect'&&(v.protect_targets||[]).includes(id))s.target=id}
  else if(['bound_companion','wisp_swarm'].includes(kind)){
   const legal=kind==='wisp_swarm'?v.wisp_placement:v.placement;if(legal.some(q=>pointKey(q)===pointKey(p))){
    if(kind==='bound_companion')s.positions=[p];else if(s.positions.some(q=>pointKey(q)===pointKey(p)))s.positions=s.positions.filter(q=>pointKey(q)!==pointKey(p));else if(s.positions.length<3)s.positions.push(p);
   }
  }else if(kind==='transposition'){if(!s.first&&v.swaps[id])s.first=id;else if(v.swaps[s.first]?.includes(id))s.target=id;else if(v.swaps[id]){s.first=id;s.target=null}}
  else if(kind==='sacrifice')s.point=p;
  else s.target=id;
  paint();
 },{...opts,capture:true});
 field.addEventListener('pointermove',e=>{if(!['bound_companion','wisp_swarm'].includes(kind)||skill.availability?.reclaim)return;const p=placementPoint(field,view,e),legal=kind==='wisp_swarm'?v.wisp_placement:v.placement;placementCursor(field,legal.some(q=>pointKey(q)===pointKey(p)))},opts);
 document.addEventListener('keydown',e=>{if(!field.isConnected){binding?.abort();return}if((kind||s.order)&&['c','escape','e'].includes(e.key.toLowerCase())&&!e.target.closest?.('input,textarea,select')){e.preventDefault();e.stopImmediatePropagation();if(e.key.toLowerCase()==='e'){if(!e.repeat)panel.querySelector('[data-summon-confirm]:not(:disabled)')?.click()}else close()}},{...opts,capture:true});
 paint();
}

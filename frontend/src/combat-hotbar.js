import {applySkillOrder} from './combat-skill-order.js';
import {furyMarkup,comboMarkup} from './martial-ui.js';
import {statusListMarkup,statusInspectMarkup,visibleStatuses} from './combat-status-presentation.js';
import {skillAvailability,skillTiming} from './equipment-skills.js';
import {tacticalPreviewText} from './combat-status-ui.js';
import {skillIconMarkup} from './ability-icons.js';
import {displacementPreviewMarkup} from './fighter-effects.js';
import {createHoverScheduler} from './combat-hover.js';
export function hotbarSkills(actor){
 const skills=[...(actor?.skills||[]).filter(s=>s.source_kind==='character'),...(actor?.passives||[]).filter(s=>s.source_kind==='character'||s.id?.startsWith('job:')),...(actor?.skills||[]).filter(s=>s.source_kind!=='character')];
 return applySkillOrder(skills,actor?.combat_skill_order||actor?.skill_slot_order||[]);
}
export function hotbarPage(actor,page=0){const skills=hotbarSkills(actor),pages=Math.max(1,Math.ceil(skills.length/10)),index=Math.max(0,Math.min(pages-1,page));return {index,pages,skills:skills.slice(index*10,index*10+10)}}
export function statHelpMarkup(text,escape){
 const [description,...formula]=String(text).split('\n');
 return `<p>${escape(description)}</p>${formula.length?`<div class="combat-stat-formula">${formula.map(line=>escape(line)).join('<br>')}</div>`:''}`;
}
export function hotbarMarkup(actor,page,selected,escape,arrange=false){
 const rows=arrange?{skills:hotbarSkills(actor),pages:1}:hotbarPage(actor,page);if(!rows.skills.length)return '';
 return `<section class="combat-hotbar" aria-label="Combat skills"><header><b>Skills</b><small>Drag to swap &middot; Passives trigger automatically &middot; 1-9 / 0</small>${!arrange?'<button data-battle-popup="skill-order" class="skill-order-button">Arrange</button>':''}${rows.pages>1?`<nav><button data-hotbar-page="${rows.index-1}" ${rows.index===0?'disabled':''} aria-label="Previous skills">&lsaquo;</button><span>${rows.index+1}/${rows.pages}</span><button data-hotbar-page="${rows.index+1}" ${rows.index===rows.pages-1?'disabled':''} aria-label="More skills">&rsaquo;</button></nav>`:''}</header><div class="hotbar-slots">${rows.skills.map((s,i)=>{
 const passive=s.type==='passive',ready=passive?{available:true}:skillAvailability(actor,s),status=s.passive_availability;
 const stopRest=!passive&&s.cleric_kind==='rest'&&actor?.cleric_rest;
 const stopSong=!passive&&actor?.bard_song&&s.bard_kind===actor.bard_song;
 const cooldown=stopSong?0:Math.max(0,Number(passive?status?.cooldown_remaining:s.availability?.cooldown_remaining)||0);
 const hasMaestro=(actor?.passives||[]).some(p=>p.bard_kind==='maestro'||p.id?.endsWith(':maestro'));
 const songSwitchLocked=!passive&&actor?.bard_song&&s.bard_kind&&['accelerando','quickening_chorus','war_anthem','song_of_peace'].includes(s.bard_kind)&&s.bard_kind!==actor.bard_song&&!hasMaestro;
 const usable=stopSong||(!songSwitchLocked&&ready.available);
 const timing=stopSong?'Stop now using your main action':passive?(status?.spent?'Used this battle':status?.active_window?'Active now':cooldown?`Ready in ${cooldown} of your turns`:'Automatic passive'):songSwitchLocked?`Stop ${actor.bard_song.replaceAll('_',' ')} first`:s.availability?.reason||ready.reason||skillTiming(s);
 const actionType=s.free_action?'Free command; no action or loadout slot':s.quick_action?'Quick Action; main action remains':s.type==='passive'?'Equipped passive':'Main action; ends activation';
 const displayName=stopRest?'End Rest':stopSong?'Stop Playing':s.name;
 return `<button data-hotbar-slot="${escape(s.id)}" draggable="true" ${passive||arrange?'data-hotbar-passive="true"':`data-hotbar-skill="${escape(s.id)}" data-hotbar-stop-song="${stopSong?'true':'false'}" data-hotbar-key="${(i+1)%10}"`} aria-label="${escape(displayName)} &middot; ${escape(actionType)} &middot; ${escape(timing)}" aria-disabled="${!usable||passive}" aria-pressed="${selected===s.id}" class="${passive?'passive-slot':''} ${selected===s.id?'selected':''} ${!usable||status?.spent?'unavailable':''} ${cooldown?'cooling-down':''}"><kbd>${passive?'P':(i+1)%10}</kbd>${skillIconMarkup(s,escape)}<b>${escape(displayName)}</b>${cooldown?`<span class="skill-cooldown" aria-hidden="true">${cooldown}</span>`:status?.spent?'<small class="skill-charges">Used</small>':!passive&&s.availability?.uses_remaining!=null?`<small class="skill-charges">${s.availability.uses_remaining} left</small>`:''}<span class="hotbar-tip"><strong>${escape(displayName)}</strong><em>${escape(passive?'Equipped passive':s.source_kind==='character'?'Job skill':s.source_name||'Equipment / proficiency')}</em><span>${escape(stopSong?'End the active Song.':s.description||'')}</span><em>${passive?'Triggers automatically':stopSong?'Uses your normal action':`${s.free_action?'Free command':`Range ${s.range}`}${s.fury_cost?` &middot; ${s.fury_cost} Fury`:''} &middot; ${s.free_action?'One summon or the whole group':s.self_only?'Target yourself':s.target==='ally'?'Target an ally':'Choose a target'}`} &middot; ${escape(timing)}</em><em>Drag onto another skill to swap positions. Order saves automatically.</em></span></button>`;
 }).join('')}</div></section>`;
}
export function unitInspectMarkup(unit,definitions,escape,preview=null,battle=null,{compact=false}={}){
 const abbreviations={Attack:'ATK',Armor:'ARM',Movement:'MOV',Range:'RNG',Accuracy:'ACC',Evasion:'EVA',Initiative:'INIT',Level:'LVL'};
 const stats=[['Attack',unit.effective_attack??unit.attack],['Armor',unit.effective_armor??unit.armor],['Movement',unit.effective_move??unit.move],['Range',unit.attack_range],['Accuracy',unit.accuracy??(unit.attack_elevation_rule==='ballistic'?90:100)],['Evasion',unit.evasion],['Initiative',unit.initiative],['Level',unit.level]];
 const statHelp=unit.stat_explanations||{};
 const forecast=preview?`<section class="inspect-forecast"><b>${preview.capture?'Capture attempt':preview.support?'Support preview':'Attack forecast'}</b>${preview.resolve_damage!=null?`<strong>${preview.resolve_damage} Resolve damage · ${preview.isolated?'Isolated':'Not isolated'}</strong>`:''}${preview.resolve_damage==null&&preview.damage_on_hit!=null?`<strong>${preview.damage_on_hit} ${preview.raw_damage?'impact power':'HP damage on hit'}</strong>`:''}<p>${preview.capture?`${preview.capture_chance??preview.chance}% capture when ready &middot; ${preview.hit_chance??100}% contact chance`:preview.chance!=null?`${preview.chance}% accuracy`:''}${preview.absorbed_damage?` · Barrier absorbs ${preview.absorbed_damage}`:''}</p>${preview.intercepted_by?`<p>Intercepted by ${escape(preview.intercepted_by)}</p>`:''}${preview.move_to?`<p>Approach: ${preview.movement_cost} movement</p>`:''}${preview.damage_note?`<small>${escape(preview.damage_note)}</small>`:''}</section>`:'';
 const tactics=preview?tacticalPreviewText(preview):'';
 const height=battle?.elevation?.find(t=>t.x===unit.x&&t.y===unit.y)?.height||0;
 const statAttributes=compact?'':' class="inspect-stat" tabindex="0"';
 const statExplanation=(label,value)=>compact?'':`<span class="inspect-stat-help">${escape(statHelp[label]||label+': '+value)}</span>`;
 const statLabel=(label,text)=>compact?text:`<abbr title="${label}">${text}</abbr>`;
 const identity=`<header><strong>${escape(unit.name)}</strong><small>${escape(unit.boss?'Boss':unit.team==='enemy'?'Enemy':'Ally')} · ${escape(unit.race||'')} · ${escape(unit.condition||'active')}</small></header><div class="inspect-health"><b${statAttributes}>${unit.hp}/${unit.max_hp} HP${compact?'':`<span class="inspect-stat-help">${escape(statHelp.Health||'Shared character health pool.')}</span>`}</b><meter min="0" max="${Math.max(1,unit.max_hp)}" value="${Math.max(0,unit.hp)}"></meter>${furyMarkup(unit)}${comboMarkup(unit)}${unit.max_resolve&&!unit.temporary?`<small class="inspect-resolve">${unit.resolve}/${unit.max_resolve} Resolve${unit.capture_ready?' · Capture Ready':''} · ${unit.capture_details?.resolve_reduction??0}% INT/AGI mitigation${!compact?` · ${unit.capture_details?.base_chance??35}% base capture chance`:''}</small>`:''}</div>`;
 const overview=`${!compact&&unit.job_description?`<p class="inspect-weapon">${escape(unit.job_description)}</p>`:''}${forecast}${tactics?`<p class="inspect-tactical-detail">${escape(tactics)}</p>`:""}<dl class="inspect-stat-grid">${stats.filter(([,value])=>value!=null).map(([label,value])=>`<div${statAttributes}><dt>${statLabel(label,abbreviations[label])}</dt><dd>${escape(value)}</dd>${statExplanation(label,value)}</div>`).join('')}<div><dt>${statLabel('Elevation','ELEV')}</dt><dd>${height}</dd></div></dl>${unit.weapon?`<p class="inspect-weapon">${escape(unit.weapon)}</p>`:''}`;
 if(!compact)return `<section class="unit-detail-summary">${identity}<div class="unit-stat-strip">${overview}</div></section><section class="unit-detail-effects" aria-label="Active effects">${statusListMarkup(unit,definitions,escape,{cards:true})}</section>${unit.passives?.length?`<details class="unit-detail-traits"><summary>Traits and passives (${unit.passives.length})</summary>${unit.passives.map(p=>`<article><b>${escape(p.name)}</b><p>${escape(p.description)}</p></article>`).join('')}</details>`:''}${unit.skills?.length?`<details class="unit-detail-techniques"><summary>Equipped techniques (${unit.skills.length})</summary>${unit.skills.map(s=>`<article><b>${escape(s.name)}</b><p>${escape(s.description)}</p></article>`).join('')}</details>`:''}<footer class="inspect-hint">Hover a stat for its calculation. Right-click an effect to keep its details open.</footer>`;
 return `${identity}<div class="inspect-columns ${!visibleStatuses(unit).length&&!unit.passives?.length?'no-effects':''}"><section class="inspect-overview">${overview}</section><section class="inspect-effects"><div class="inspect-statuses">${statusListMarkup(unit,definitions,escape,{compact:true,limit:3})}</div></section></div><footer class="inspect-hint">Right-click to inspect stats and effects.</footer>`;
}
export function resistanceMarkup(unit,escape){
 const profile=unit.resistance_details;if(!profile)return '';
 const rows=Object.entries(profile.statuses||{}).map(([id,value])=>`${id.replaceAll('_',' ')}: ${id==='burn'?value+'% damage reduction (Burn can still apply)':value===100?'immune':value+'% resistance'}`);
 if(profile.control_duration_limit)rows.push(`Stun, sleep, freeze, paralysis and binding last at most ${profile.control_duration_limit} turn`);
 if(unit.displacement_resistance)rows.push(`Knockback: ${unit.displacement_resistance}% resistance`);
 if(!rows.length)return '';
 return `<div class="inspect-resistances"><b>Innate resistances</b>${rows.map(row=>`<p>${escape(row)}</p>`).join('')}<p>Unlisted debuffs have no innate resistance.</p></div>`;
}
export function cursorCardPosition(x,y,width,height,viewportWidth,viewportHeight){
 return {left:Math.max(8,Math.min(viewportWidth-width-8,x+18)),top:Math.max(8,Math.min(viewportHeight-height-8,y+18))};
}
export function areaForecastMarkup(preview,battle,escape){
 if(!preview)return '';
 const forecasts=preview.target_forecasts||{};
 const cells=new Set((preview.zones||[]).flatMap(z=>z.cells||[]).map(p=>`${p.x},${p.y}`));
 const actor=battle.units?.[battle.current_unit_id];
 const hazard=preview.ground_damage&&preview.landing?`<div class="aoe-preview-chip friendly-fire-forecast" style="left:${(preview.landing.x+.5)/battle.width*100}%;top:${(preview.landing.y+.5)/battle.height*100}%" data-aoe-preview="dash-hazard"><b>${Number(preview.ground_damage)} ground damage to you</b><small>Committed dash path · future damage ticks excluded</small></div>`:'';
 return hazard+Object.values(battle.units||{}).filter(u=>u.alive&&u.conscious!==false&&!u.extracted&&!u.carried_by&&cells.has(`${u.x},${u.y}`))
  .map(unit=>{
   const forecast=forecasts[unit.id];
   const zones=(preview.zones||[]).filter(z=>(z.cells||[]).some(p=>p.x===unit.x&&p.y===unit.y)
    &&(z.kind!=='bard_song'||z.song==='song_of_peace'||unit.team===actor?.team&&unit.id!==actor?.id));
   const labels=zones.map(z=>({ember:'Burn on entry',binding:'Bind on entry',thorns:'3 damage on entry',sanctuary:'3 HP next turn',rally:'Remove Fear / next hit -25% / next attack +25%',bard_song:`${z.name||'Song'} performance space`}[z.kind])).filter(Boolean);
   if(!forecast&&!labels.length||zones.every(z=>['ember','binding','thorns'].includes(z.kind))&&unit.team===actor?.team||zones.every(z=>['sanctuary','rally'].includes(z.kind))&&unit.team!==actor?.team)return '';
   const friendly=!!forecast&&unit.team===actor?.team&&!forecast.support;
   const warning=friendly?(unit.id===actor?.id?'You':'Ally')+' &middot; ':'';
   return `<div class="aoe-preview-chip ${friendly?'friendly-fire-forecast':''}" style="left:${(unit.x+.5)/battle.width*100}%;top:${(unit.y+.5)/battle.height*100}%" data-aoe-preview="${escape(unit.id)}"><b>${warning}${forecast?forecast.delayed&&forecast.damage_on_hit===0?'Freeze after next caster action':`${forecast.damage_on_hit} damage${forecast.delayed?' · delayed':''}` :escape(labels.join(' / '))}</b>${forecast?`<small>${forecast.chance}% hit${forecast.push!=null?` · Push ${forecast.push}`:''}${forecast.resistance?` · ${forecast.resistance}% resist`:''}</small>`:''}</div>`;
  }).join('');
}
export function layoutAreaForecasts(layer){
 const occupied=[],bounds=layer.getBoundingClientRect();
 const overlaps=r=>occupied.some(p=>r.left<p.right+4&&r.right>p.left-4&&r.top<p.bottom+4&&r.bottom>p.top-4);
 for(const chip of layer.children){
  let r=chip.getBoundingClientRect(),lift=0,below=false;
  const step=r.height+8;
  for(let attempt=0;attempt<12&&(overlaps(r)||r.top<bounds.top+4);attempt++){
   if(!below&&r.top-step<bounds.top+4){below=true;lift=0}else lift+=step;
   chip.style.transform=`translate(-50%,${below?`${36+lift}px`:`calc(-100% - ${28+lift}px)`})`;
   r=chip.getBoundingClientRect();
  }
  chip.style.setProperty('--forecast-leader',`${lift}px`);
  chip.classList.toggle('forecast-below',below);occupied.push(r);
 }
}
export function bindUnitInspect(field,battle,escape,mode=()=> 'move'){
 refreshUnitInspector(battle,escape);
 refreshEffectInspector(battle,escape);
 let tip=document.getElementById('combat-unit-inspect');
 if(!tip){tip=document.createElement('aside');tip.id='combat-unit-inspect';tip.className='combat-unit-inspect';tip.setAttribute('role','tooltip');tip.hidden=true;document.body.append(tip)}
 tip._hoverCleanup?.();
 if(!tip._hoverCards||tip._hoverCards.battleId!==battle.id)tip._hoverCards={battleId:battle.id,entries:new Map()};
 const cards=tip._hoverCards.entries;
 let content=tip._hoverContent||null,size=tip._hoverSize||null;
 const hide=()=>{queue.cancel();tip.hidden=true};
 const leave=()=>hide();
 tip.onmouseenter=null;tip.onmouseleave=null;tip.oncontextmenu=null;
 const position=(token,event)=>{
  if(!size||size.viewportWidth!==innerWidth||size.viewportHeight!==innerHeight){size={width:tip.offsetWidth,height:tip.offsetHeight,viewportWidth:innerWidth,viewportHeight:innerHeight};tip._hoverSize=size;if(content)content.size=size}
  const pointer=event&&Number.isFinite(event.clientX)&&Number.isFinite(event.clientY)?event:token.getBoundingClientRect();
  const p=cursorCardPosition(pointer.clientX??pointer.right,pointer.clientY??pointer.bottom,size.width,size.height,innerWidth,innerHeight);
  const transform=`translate3d(${p.left}px,${p.top}px,0)`;
  if(tip.style.transform!==transform)tip.style.transform=transform;
 };
 const queue=createHoverScheduler((token,event)=>{
  if(tip._pinnedAt){if(!event||Math.hypot(event.clientX-tip._pinnedAt.x,event.clientY-tip._pinnedAt.y)<5)return;tip._pinnedAt=null}
  const resolved=battle.units[token.dataset.battleUnit],statuses=token.presentationStatuses||resolved?.statuses;
  if(!resolved||!token.isConnected||field.closest('.is-panning'))return;
  const action=mode(),preview=['attack','subdue','skill'].includes(action)?battle.attack_previews?.[resolved.id]?.[action]:action==='throw'&&battle.throw_profile?.target_ids?.includes(resolved.id)?battle.throw_profile:null;
  const badge=event?.target?.closest?.('[data-unit-status]'),statusId=badge?.dataset.unitStatus||'',owner=badge?.dataset.statusOwner||'';
  const key=resolved.id+':'+action+':'+statusId+':'+owner;
  let entry=cards.get(key);
  if(!entry||entry.unit!==resolved||entry.statuses!==statuses||entry.preview!==preview){
   const unit=statuses===resolved.statuses?resolved:{...resolved,statuses},status=statusId&&visibleStatuses(unit).find(s=>s.id===statusId&&(!owner||s.source_id===owner));
   const forecast=action==='throw'&&preview?{damage_on_hit:preview.damage,raw_damage:true,damage_note:'Impact power before target defenses.'}:preview;
   const html=status?statusInspectMarkup(unit,status,battle.status_definitions,escape):unitInspectMarkup(unit,battle.status_definitions,escape,forecast,battle,{compact:true});
   if(entry?.html===html){entry.unit=resolved;entry.statuses=statuses;entry.preview=preview}
   else{const template=document.createElement('template');template.innerHTML=html;
    entry={unit:resolved,statuses,preview,key,html,nodes:[...template.content.childNodes],effectId:status?.id||'',owner:status?.source_id||'',size:null};
   }
  }
  cards.delete(key);cards.set(key,entry);if(cards.size>48)cards.delete(cards.keys().next().value);
  if(content!==entry||tip.dataset.inspectKey!==key){
   tip.replaceChildren(...entry.nodes);content=entry;tip._hoverContent=entry;tip.dataset.inspectKey=key;
   tip.classList.toggle('unit-hover-card',!entry.effectId);tip.dataset.unitId=resolved.id;tip.dataset.effectId=entry.effectId;tip.dataset.effectOwner=entry.owner;size=entry.size;
  }
  tip.hidden=false;position(token,event);
 });
 tip._hoverCleanup=()=>queue.cancel();
 let hovered=false;
 field?.querySelectorAll('[data-battle-unit]').forEach(token=>{
  const show=event=>queue.show(token,event);
  if(token._inspectBindings)for(const [event,handler] of token._inspectBindings)token.removeEventListener(event,handler);
  token._inspectBindings=[['mouseenter',show],['mousemove',show],['focus',show],['mouseleave',leave],['blur',hide]];
  token.removeAttribute('title');for(const [event,handler] of token._inspectBindings)token.addEventListener(event,handler);
  if(token.matches(':hover')||token===document.activeElement){hovered=true;show()}
 });
 if(!hovered)hide();
 const viewport=field?.closest('.battle-viewport');if(viewport){if(viewport._inspectScroll)viewport.removeEventListener('scroll',viewport._inspectScroll);viewport._inspectScroll=hide;viewport.addEventListener('scroll',viewport._inspectScroll)}
}
function refreshUnitInspector(battle,escape){
 const panel=document.getElementById('combat-unit-window');if(!panel)return;
 document.getElementById('combat-stat-tooltip')?.remove();
 const unit=battle.units?.[panel.dataset.unitId];
 if(!unit){panel.remove();return}
 panel._battle=battle;panel._escape=escape;
 const body=panel.querySelector('.unit-window-body'),html=unitInspectMarkup(unit,battle.status_definitions,escape,null,battle);
 if(body._inspectHTML===html)return;
 const scroll=body.scrollTop,effectScroll=body.querySelector('.unit-detail-effects')?.scrollTop||0,traitsOpen=body.querySelector('.unit-detail-traits')?.open;
 body.innerHTML=html;body._inspectHTML=html;body.scrollTop=scroll;
 body.querySelector('.unit-detail-effects').scrollTop=effectScroll;
 if(traitsOpen&&body.querySelector('.unit-detail-traits'))body.querySelector('.unit-detail-traits').open=true;
}
export function openUnitInspector(battle,id,escape,event){
 if(!battle.units?.[id])return;
 const hover=document.getElementById('combat-unit-inspect');if(hover){hover._hoverCleanup?.();hover.hidden=true;hover._pinnedAt={x:event?.clientX||0,y:event?.clientY||0}}
 let panel=document.getElementById('combat-unit-window');
 if(!panel){
  panel=document.createElement('aside');panel.id='combat-unit-window';panel.className='combat-unit-inspect unit-inspect-window';panel.setAttribute('role','dialog');panel.setAttribute('aria-label','Unit details');
  panel.innerHTML='<div class="unit-window-handle"><b>Unit details · drag to move</b><button aria-label="Close unit details" title="Close unit details">×</button></div><div class="unit-window-body"></div>';
  document.body.append(panel);
  const close=()=>{document.getElementById('combat-stat-tooltip')?.remove();panel.remove()};
  panel.querySelector('button').onclick=close;
  const hideStat=()=>document.getElementById('combat-stat-tooltip')?.remove();
  const showStat=e=>{
   const stat=e.target.closest?.('.inspect-stat'),text=stat?.querySelector('.inspect-stat-help')?.textContent;
   if(!text){hideStat();return}
   let tip=document.getElementById('combat-stat-tooltip');if(!tip){tip=document.createElement('aside');tip.id='combat-stat-tooltip';tip.setAttribute('role','tooltip');document.body.append(tip)}
   if(tip._text!==text){tip.innerHTML=statHelpMarkup(text,panel._escape);tip._text=text}const r=stat.getBoundingClientRect(),p=cursorCardPosition(r.right,r.bottom,tip.offsetWidth,tip.offsetHeight,window.innerWidth,window.innerHeight);tip.style.left=p.left+'px';tip.style.top=p.top+'px';
  };
  panel.onpointermove=showStat;panel.onfocusin=showStat;panel.onpointerleave=hideStat;panel.onfocusout=hideStat;
  panel.querySelector('.unit-window-body').onscroll=hideStat;
  const handle=panel.querySelector('.unit-window-handle');let drag;
  handle.onpointerdown=e=>{if(e.button!==0||e.target.closest('button'))return;e.preventDefault();const r=panel.getBoundingClientRect();drag={id:e.pointerId,x:e.clientX-r.left,y:e.clientY-r.top};handle.setPointerCapture(e.pointerId)};
  handle.onpointermove=e=>{if(!drag||drag.id!==e.pointerId)return;panel.style.left=Math.max(0,Math.min(window.innerWidth-panel.offsetWidth,e.clientX-drag.x))+'px';panel.style.top=Math.max(0,Math.min(window.innerHeight-48,e.clientY-drag.y))+'px'};
  handle.onpointerup=handle.onpointercancel=()=>drag=null;
  panel.onkeydown=e=>{if(e.key==='Escape'){e.stopPropagation();close()}};
  panel.oncontextmenu=e=>{e.preventDefault();const effect=e.target.closest('[data-effect-id]'),badge=e.target.closest('[data-unit-status]');if(effect||badge)openEffectInspector(panel._battle,panel.dataset.unitId,effect?.dataset.effectId||badge.dataset.unitStatus,effect?.dataset.effectOwner||badge?.dataset.statusOwner||'',panel._escape,e)};
  const observer=new MutationObserver(()=>{if(!document.querySelector('.battlefield')){close();observer.disconnect()}else if(!panel.isConnected){hideStat();observer.disconnect()}});
  observer.observe(document.getElementById('modal')||document.body,{childList:true,subtree:true});
 }
 panel._battle=battle;panel._escape=escape;panel.dataset.unitId=id;refreshUnitInspector(battle,escape);
 if(!panel.style.left){const p=cursorCardPosition(event?.clientX||100,event?.clientY||100,panel.offsetWidth,panel.offsetHeight,window.innerWidth,window.innerHeight);panel.style.left=p.left+'px';panel.style.top=p.top+'px'}
 panel.querySelector('button').focus({preventScroll:true});
}
function refreshEffectInspector(battle,escape){
 const panel=document.getElementById('combat-effect-window');if(!panel)return;
 const unit=battle.units?.[panel.dataset.unitId];if(!unit){panel.remove();return}
 const status=visibleStatuses(unit).find(s=>s.id===panel.dataset.effectId&&(!panel.dataset.effectOwner||s.source_id===panel.dataset.effectOwner));
 const body=panel.querySelector('.effect-window-body'),scroll=body.scrollTop;
 const html=status?statusInspectMarkup(unit,status,battle.status_definitions,escape):'<p class="effect-ended">No longer active on this unit.</p>'+(panel._lastHTML||'');
 if(body._inspectHTML===html)return;
 body.innerHTML=html;body._inspectHTML=html;
 if(status){body.querySelector('.inspect-hint')?.remove();panel._lastHTML=body.innerHTML}
 body.scrollTop=scroll;
}
export function openEffectInspector(battle,unitId,effectId,owner,escape,event){
 const unit=battle.units?.[unitId];if(!unit||!visibleStatuses(unit).some(s=>s.id===effectId&&(!owner||s.source_id===owner)))return;
 const hover=document.getElementById('combat-unit-inspect');if(hover){hover._hoverCleanup?.();hover.hidden=true;hover._pinnedAt={x:event?.clientX||0,y:event?.clientY||0}}
 let panel=document.getElementById('combat-effect-window');
 if(!panel){
  panel=document.createElement('aside');panel.id='combat-effect-window';panel.className='combat-unit-inspect effect-inspect-window';panel.setAttribute('role','dialog');panel.setAttribute('aria-label','Effect details');
  panel.innerHTML='<div class="unit-window-handle"><b>Effect details · drag to move</b><button aria-label="Close effect details" title="Close effect details">&times;</button></div><div class="effect-window-body"></div>';document.body.append(panel);
  const close=()=>panel.remove();panel.querySelector('button').onclick=close;
  const handle=panel.querySelector('.unit-window-handle');let drag;
  handle.onpointerdown=e=>{if(e.button!==0||e.target.closest('button'))return;e.preventDefault();const r=panel.getBoundingClientRect();drag={id:e.pointerId,x:e.clientX-r.left,y:e.clientY-r.top};handle.setPointerCapture(e.pointerId)};
  handle.onpointermove=e=>{if(!drag||drag.id!==e.pointerId)return;panel.style.left=Math.max(0,Math.min(innerWidth-panel.offsetWidth,e.clientX-drag.x))+'px';panel.style.top=Math.max(0,Math.min(innerHeight-48,e.clientY-drag.y))+'px'};
  handle.onpointerup=handle.onpointercancel=()=>drag=null;
  panel.onkeydown=e=>{if(e.key==='Escape'){e.stopPropagation();close()}};panel.oncontextmenu=e=>e.preventDefault();
  const observer=new MutationObserver(()=>{if(!document.querySelector('.battlefield')){close();observer.disconnect()}else if(!panel.isConnected)observer.disconnect()});observer.observe(document.getElementById('modal')||document.body,{childList:true,subtree:true});
 }
 const same=panel.dataset.unitId===unitId&&panel.dataset.effectId===effectId&&panel.dataset.effectOwner===(owner||'');
 if(!same){panel._lastHTML='';panel.querySelector('.effect-window-body').scrollTop=0;panel.querySelector('.effect-window-body')._inspectHTML=null}
 panel.dataset.unitId=unitId;panel.dataset.effectId=effectId;panel.dataset.effectOwner=owner||'';refreshEffectInspector(battle,escape);
 if(!panel.style.left){const p=cursorCardPosition(event?.clientX||100,event?.clientY||100,panel.offsetWidth,panel.offsetHeight,innerWidth,innerHeight);panel.style.left=p.left+'px';panel.style.top=p.top+'px'}
 panel.querySelector('button').focus({preventScroll:true});
}
export function bindSpellTargets(field,battle,mode,onCast){
 if(!field)return;
 if(field._spellClick)field.removeEventListener('click',field._spellClick,true);
 field.onpointermove=null;field.onpointerleave=null;field.classList.remove('placement-cursor-valid','placement-cursor-invalid');
 field.querySelector('.aoe-preview-layer')?.remove();
 field.querySelectorAll('.spell-self-label').forEach(el=>el.remove());
 field.querySelectorAll('.spell-area,.spell-center,.spell-self-target,.spell-castable,.spell-inner,.spell-outer,.spell-landing,.spell-pull-path,.spell-pull-stop,.spell-collision-cell').forEach(el=>el.classList.remove('spell-area','spell-center','spell-self-target','spell-castable','spell-inner','spell-outer','spell-landing','spell-pull-path','spell-pull-stop','spell-collision-cell'));
 const actor=battle.units?.[battle.current_unit_id],skill=actor?.special;
 field.querySelectorAll('.spell-ground-target').forEach(el=>el.classList.remove('spell-ground-target'));
 if(mode!=='skill'||!skill)return;
 const entries=battle.ground_skill_previews?.[skill.id],self=skill.self_only||['prowler','bulwark','rat'].includes(skill.druid_kind)||['accelerando','quickening_chorus','war_anthem','song_of_peace'].includes(skill.bard_kind)||skill.mage_kind==='typhoon'||(skill.effects||[]).some(e=>['form','deploy'].includes(e.type)||e.type==='cleanse'&&e.radius);
 if(skill.engineer_kind&&!entries)field.querySelectorAll('[data-battle-unit]').forEach(el=>{const valid=!!battle.skill_previews?.[skill.id]?.[el.dataset.battleUnit];el.classList.toggle('valid-target',valid);el.classList.toggle('invalid-target',!valid)});
 if(self){const token=field.querySelector(`[data-battle-unit="${CSS.escape(actor.mounted_machine||actor.id)}"]`);token?.classList.add('spell-self-target');if(token){const label=document.createElement('span');label.className='spell-self-label';label.setAttribute('aria-hidden','true');label.textContent='SELF';token.append(label)}}
 const clear=()=>{field.querySelectorAll('.spell-invalid').forEach(el=>el.classList.remove('spell-invalid'));field.querySelectorAll('.spell-area,.spell-center,.attack-approach-path,.attack-approach-stop,.spell-inner,.spell-outer,.spell-landing,.spell-pull-path,.spell-pull-stop,.spell-collision-cell').forEach(el=>{el.classList.remove('spell-area','spell-center','attack-approach-path','attack-approach-stop','spell-inner','spell-outer','spell-landing','spell-pull-path','spell-pull-stop','spell-collision-cell');el.querySelector('.approach-step')?.remove()})};
 const forecastLayer=document.createElement('div');forecastLayer.className='aoe-preview-layer';forecastLayer.setAttribute('data-live-overlay','');field.append(forecastLayer);
 const paint=preview=>{
  clear();forecastLayer.innerHTML=areaForecastMarkup(preview,battle,escapeHTML)+displacementPreviewMarkup(preview,battle,escapeHTML);layoutAreaForecasts(forecastLayer);for(const zone of preview?.zones||[])for(const p of zone.cells||[]){const cell=field.querySelector(`[data-battle-cell="${p.x},${p.y}"]`);cell?.classList.add('spell-area');if(preview.landing)cell?.classList.add(Math.max(Math.abs(p.x-preview.landing.x),Math.abs(p.y-preview.landing.y))<=1?'spell-inner':'spell-outer')}
  if(preview?.landing)field.querySelector(`[data-battle-cell="${preview.landing.x},${preview.landing.y}"]`)?.classList.add('spell-landing');
  for(const p of preview?.path||[])field.querySelector(`[data-battle-cell="${p.x},${p.y}"]`)?.classList.add('attack-approach-path');
  if(preview?.move_to)field.querySelector(`[data-battle-cell="${preview.move_to.x},${preview.move_to.y}"]`)?.classList.add('attack-approach-stop');
  for(const effect of preview?.tactics||[]){
   for(const p of effect.path||[])field.querySelector(`[data-battle-cell="${p.x},${p.y}"]`)?.classList.add('spell-pull-path');
   const end=effect.destination,contact=effect.collision_cell;
   if(end)field.querySelector(`[data-battle-cell="${end.x},${end.y}"]`)?.classList.add('spell-pull-stop');
   if(contact&&effect.solid_collision)field.querySelector(`[data-battle-cell="${contact.x},${contact.y}"]`)?.classList.add('spell-collision-cell');
  }
 };
 if(self){const preview=battle.skill_previews?.[skill.id]?.[actor.id];if(preview)paint(preview)}
 const point=e=>{const r=field.getBoundingClientRect();return {x:Math.floor((e.clientX-r.left)/r.width*battle.width),y:Math.floor((e.clientY-r.top)/r.height*battle.height)}};
 if(entries){
  field.querySelectorAll('[data-battle-unit]').forEach(el=>{const unit=battle.units[el.dataset.battleUnit];el.classList.toggle('spell-ground-target',!!unit&&!!entries[`${unit.x},${unit.y}`])});
  field.querySelectorAll('[data-battle-cell]').forEach(el=>el.classList.toggle('spell-castable',!!entries[el.dataset.battleCell]));
  let lastPoint=null;field.onpointerleave=()=>{clear();forecastLayer.innerHTML='';lastPoint=null};field.onpointermove=e=>{const p=point(e),key=`${p.x},${p.y}`;if(key===lastPoint)return;lastPoint=key;const preview=entries[key];let shown=preview;if(skill.engineer_kind==='proximity_charge'){field.classList.toggle('placement-cursor-invalid',!preview);field.classList.toggle('placement-cursor-valid',!!preview);if(!preview){const cells=[];for(let y=Math.max(0,p.y-1);y<=Math.min(battle.height-1,p.y+1);y++)for(let x=Math.max(0,p.x-1);x<=Math.min(battle.width-1,p.x+1);x++)cells.push({x,y});shown={zones:[{cells}],invalid:true}}}paint(shown);field.querySelectorAll('.spell-area').forEach(el=>el.classList.toggle('spell-invalid',!!shown?.invalid));const help=document.getElementById('combat-action-help');if(help)help.textContent=preview?`${preview.move_to?`Move to cell ${preview.move_to.x+1}, ${preview.move_to.y+1} (${preview.movement_cost} movement), then `:'From this position, ' }${preview.landing?'leap with':'cast'} ${skill.name}. ${preview.zones.flatMap(z=>z.cells).length} affected cells.`:'Outside movement + spell range, blocked sight, or no valid ground.';if(preview)field.querySelector(`[data-battle-cell="${p.x},${p.y}"]`)?.classList.add('spell-center')};
  field._spellClick=e=>{const p=point(e),preview=entries[`${p.x},${p.y}`];e.stopImmediatePropagation();e.preventDefault();if(preview)onCast({action:'skill',skill_id:skill.id,x:p.x,y:p.y,...(preview.move_to?{move_to:preview.move_to}:{})})};
  field.addEventListener('click',field._spellClick,true);
 }else{
  field._spellClick=null;
  if(self){
   field._spellClick=e=>{const token=e.target.closest?.('[data-battle-unit]'),preview=battle.skill_previews?.[skill.id]?.[actor.id];if(token?.dataset.battleUnit!==actor.id&&!(actor.mounted_machine&&token?.dataset.battleUnit===actor.mounted_machine))return;e.stopImmediatePropagation();e.preventDefault();if(preview)onCast({action:'skill',skill_id:skill.id,target_id:actor.id})};
   field.addEventListener('click',field._spellClick,true);
  }
  field.onpointerleave=()=>{clear();forecastLayer.innerHTML=''};
  field.onpointermove=e=>{const token=e.target.closest?.('[data-battle-unit]');if(skill.engineer_kind){const id=token?.dataset.battleUnit,valid=self?(id===actor.id||id===actor.mounted_machine):!!battle.skill_previews?.[skill.id]?.[id];field.classList.toggle('placement-cursor-valid',!!valid);field.classList.toggle('placement-cursor-invalid',!valid)}if(self)return;if(token)paint(battle.attack_previews?.[token.dataset.battleUnit]?.skill);else{clear();forecastLayer.innerHTML=''}};
 }
}

function escapeHTML(value){return String(value??'').replaceAll('&','&amp;').replaceAll('<','&lt;').replaceAll('>','&gt;').replaceAll('"','&quot;')}

export function bindStatusTray(root,battle,escape){
 const tip=document.getElementById('combat-unit-inspect');if(!tip)return;
 root?._statusHoverCleanup?.();let size=null;
 const queue=createHoverScheduler((badge,event)=>{
  if(!badge.isConnected)return;
  if(tip._pinnedAt){if(!event||Math.hypot(event.clientX-tip._pinnedAt.x,event.clientY-tip._pinnedAt.y)<5)return;tip._pinnedAt=null}
  const unit=battle.units[badge.dataset.statusUnit];if(!unit)return;
  const status=visibleStatuses(unit).find(s=>s.id===badge.dataset.unitStatus&&(!badge.dataset.statusOwner||s.source_id===badge.dataset.statusOwner));if(!status)return;
  const key='tray:'+unit.id+':'+status.id+':'+(status.source_id||'');
  if(tip.dataset.inspectKey!==key){tip.innerHTML=statusInspectMarkup(unit,status,battle.status_definitions,escape);tip.classList.remove('unit-hover-card');tip.dataset.unitId=unit.id;tip.dataset.effectId=status.id;tip.dataset.effectOwner=status.source_id||'';tip.dataset.inspectKey=key;size=null}
  tip.hidden=false;
  if(!size||size.viewportWidth!==innerWidth||size.viewportHeight!==innerHeight)size={width:tip.offsetWidth,height:tip.offsetHeight,viewportWidth:innerWidth,viewportHeight:innerHeight};
  const pointer=event&&Number.isFinite(event.clientX)&&Number.isFinite(event.clientY)?event:badge.getBoundingClientRect();
  const p=cursorCardPosition(pointer.clientX??pointer.right,pointer.clientY??pointer.bottom,size.width,size.height,innerWidth,innerHeight);tip.style.transform=`translate3d(${p.left}px,${p.top}px,0)`;
 });
 if(root)root._statusHoverCleanup=()=>queue.cancel();
 const hide=()=>{queue.cancel();tip.hidden=true};
 root?.querySelectorAll('[data-unit-status]').forEach(badge=>{
  badge.oncontextmenu=e=>{queue.cancel();e.preventDefault();e.stopPropagation();openEffectInspector(battle,badge.dataset.statusUnit,badge.dataset.unitStatus,badge.dataset.statusOwner,escape,e)};
  const show=event=>queue.show(badge,event);
  if(badge._statusBindings)for(const [name,handler] of badge._statusBindings)badge.removeEventListener(name,handler);
  badge._statusBindings=[['mouseenter',show],['mousemove',show],['focus',show],['mouseleave',hide],['blur',hide]];
  for(const [name,handler] of badge._statusBindings)badge.addEventListener(name,handler);
 });
}

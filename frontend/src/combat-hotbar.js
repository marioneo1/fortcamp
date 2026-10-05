import {skillAvailability,skillTiming} from './equipment-skills.js';
import {statusDetails} from './combat-status-ui.js';
import {skillIconMarkup} from './ability-icons.js';
export function hotbarSkills(actor){return [...(actor?.skills||[]).filter(s=>s.source_kind==='character'),...(actor?.skills||[]).filter(s=>s.source_kind!=='character')]}
export function hotbarPage(actor,page=0){const skills=hotbarSkills(actor),pages=Math.max(1,Math.ceil(skills.length/10)),index=Math.max(0,Math.min(pages-1,page));return {index,pages,skills:skills.slice(index*10,index*10+10)}}
export function hotbarMarkup(actor,page,selected,escape){
 const rows=hotbarPage(actor,page);if(!rows.skills.length)return '';
 return `<section class="combat-hotbar" aria-label="Combat skills"><header><b>Skills</b><small>Choose a skill, then a target (C to cancel) · 1–9 / 0</small>${rows.pages>1?`<nav><button data-hotbar-page="${rows.index-1}" ${rows.index===0?'disabled':''} aria-label="Previous skills">‹</button><span>${rows.index+1}/${rows.pages}</span><button data-hotbar-page="${rows.index+1}" ${rows.index===rows.pages-1?'disabled':''} aria-label="More skills">›</button></nav>`:''}</header><div class="hotbar-slots">${rows.skills.map((s,i)=>{const ready=skillAvailability(actor,s);return `<button data-hotbar-skill="${escape(s.id)}" data-hotbar-key="${(i+1)%10}" aria-label="${escape(s.name)}" aria-pressed="${selected===s.id}" class="${selected===s.id?'selected':''}" ${ready.available?'':'disabled'} title="${escape(`${s.name}: ${s.description} ${ready.reason||''}`)}"><kbd>${(i+1)%10}</kbd>${skillIconMarkup(s,escape)}<b>${escape(s.name)}</b><small>${escape(skillTiming(s))}</small><span class="hotbar-tip"><strong>${escape(s.name)}</strong><em>${escape(s.source_kind==='character'?'Job skill':s.source_name||'Equipment / proficiency')}</em><span>${escape(s.description||'')}</span><em>Range ${s.range} · ${escape((s.effects||[]).some(e=>e.type==='leap_attack')?'Choose landing ground':(s.effects||[]).some(e=>e.type==='cleanse'&&e.radius)?'Target yourself: nearby allies':s.target==='ally'?'Target an ally':'Target an enemy')} · ${escape(ready.reason||skillTiming(s))}</em></span></button>`}).join('')}</div></section>`;
}
export function unitInspectMarkup(unit,definitions,escape,preview=null,battle=null){
 const statuses=[...(unit.statuses||[])];if(unit.guarding)statuses.unshift({id:'guard'});
 const stats=[['Attack',unit.attack],['Armor',unit.effective_armor??unit.armor],['Movement',unit.move],['Range',unit.attack_range],['Accuracy',unit.accuracy],['Evasion',unit.evasion],['Initiative',unit.initiative],['Level',unit.level]];
 const forecast=preview?`<section class="inspect-forecast"><b>${preview.capture?'Capture attempt':preview.support?'Support preview':'Attack forecast'}</b>${preview.damage_on_hit!=null?`<strong>${preview.damage_on_hit} ${preview.raw_damage?'impact power':'HP damage on hit'}</strong>`:''}<p>${preview.capture?`${preview.chance}% capture chance`:preview.chance!=null?`${preview.chance}% accuracy`:''}${preview.absorbed_damage?` · Barrier absorbs ${preview.absorbed_damage}`:''}</p>${preview.intercepted_by?`<p>Intercepted by ${escape(preview.intercepted_by)}</p>`:''}${preview.move_to?`<p>Approach: ${preview.movement_cost} movement</p>`:''}${preview.damage_note?`<small>${escape(preview.damage_note)}</small>`:''}</section>`:'';
 const height=battle?.elevation?.find(t=>t.x===unit.x&&t.y===unit.y)?.height||0;
 return `<header><strong>${escape(unit.name)}</strong><small>${escape(unit.boss?'Boss':unit.team==='enemy'?'Enemy':'Ally')} · ${escape(unit.race||'')} · ${escape(unit.condition||'active')}</small></header><div class="inspect-health"><b>${unit.hp}/${unit.max_hp} HP</b><meter min="0" max="${Math.max(1,unit.max_hp)}" value="${Math.max(0,unit.hp)}"></meter></div>${forecast}<dl class="inspect-stat-grid">${stats.filter(([,value])=>value!=null).map(([label,value])=>`<div><dt>${label}</dt><dd>${escape(value)}</dd></div>`).join('')}<div><dt>Elevation</dt><dd>${height}</dd></div></dl>${unit.weapon?`<p class="inspect-weapon">${escape(unit.weapon)}</p>`:''}<div class="inspect-statuses">${statuses.map(s=>{const d=s.id==='guard'?{name:'Guard',icon:'⬡',description:'The next direct hit deals 25% less damage. Consumed by that hit; expires at the next activation.',details:[]}:statusDetails(s,definitions);return `<article><b>${escape(d.icon)} ${escape(d.name)}</b><p>${escape(d.description)}</p>${d.details.map(t=>`<small>${escape(t)}</small>`).join('')}</article>`}).join('')||'<p>No active status effects.</p>'}</div>${unit.passives?.length?`<details><summary>Passives (${unit.passives.length})</summary>${unit.passives.map(p=>`<article><b>${escape(p.name)}</b><p>${escape(p.description)}</p></article>`).join('')}</details>`:''}`;
}
export function bindUnitInspect(field,battle,escape,mode=()=> 'move'){
 let tip=document.getElementById('combat-unit-inspect');
 if(!tip){tip=document.createElement('aside');tip.id='combat-unit-inspect';tip.className='combat-unit-inspect';tip.setAttribute('role','tooltip');document.body.append(tip)}
 tip.hidden=true;
 let hideTimer=null;const hide=()=>{hideTimer=setTimeout(()=>tip.hidden=true,140)};
 tip.onmouseenter=()=>clearTimeout(hideTimer);tip.onmouseleave=hide;
 const position=token=>{const r=token.getBoundingClientRect(),w=tip.offsetWidth,h=tip.offsetHeight,x=r.right+w+12<window.innerWidth?r.right+12:r.left-w-12;tip.style.left=`${Math.max(8,Math.min(window.innerWidth-w-8,x))}px`;tip.style.top=`${Math.max(8,Math.min(window.innerHeight-h-8,r.top))}px`};
 field?.querySelectorAll('[data-battle-unit]').forEach(token=>{
  const show=()=>{clearTimeout(hideTimer);const unit=battle.units[token.dataset.battleUnit];if(!unit||field.closest('.is-panning'))return;const action=mode(),preview=['attack','subdue','skill'].includes(action)?battle.attack_previews?.[unit.id]?.[action]:action==='throw'&&battle.throw_profile?.target_ids?.includes(unit.id)?{damage_on_hit:battle.throw_profile.damage,raw_damage:true,damage_note:'Impact power before target defenses.'}:null;tip.innerHTML=unitInspectMarkup(unit,battle.status_definitions,escape,preview,battle);tip.hidden=false;position(token)};
  if(token._inspectBindings)for(const [event,handler] of token._inspectBindings)token.removeEventListener(event,handler);
  token._inspectBindings=[['mouseenter',show],['focus',show],['mouseleave',hide],['blur',hide]];
  token.removeAttribute('title');for(const [event,handler] of token._inspectBindings)token.addEventListener(event,handler);
  if(token.matches(':hover')||token===document.activeElement)show();
 });
 const viewport=field?.closest('.battle-viewport');if(viewport){if(viewport._inspectScroll)viewport.removeEventListener('scroll',viewport._inspectScroll);viewport._inspectScroll=()=>tip.hidden=true;viewport.addEventListener('scroll',viewport._inspectScroll)}
}
export function bindSpellTargets(field,battle,mode,onCast){
 if(!field)return;
 if(field._spellClick)field.removeEventListener('click',field._spellClick,true);
 field.onpointermove=null;
 field.querySelectorAll('.spell-area,.spell-center,.spell-self-target,.spell-castable,.spell-inner,.spell-outer,.spell-landing').forEach(el=>el.classList.remove('spell-area','spell-center','spell-self-target','spell-castable','spell-inner','spell-outer','spell-landing'));
 const actor=battle.units?.[battle.current_unit_id],skill=actor?.special;
 if(mode!=='skill'||!skill)return;
 const entries=battle.ground_skill_previews?.[skill.id],self=(skill.effects||[]).some(e=>['form','deploy'].includes(e.type)||e.type==='cleanse'&&e.radius);
 if(self)field.querySelector(`[data-battle-unit="${CSS.escape(actor.id)}"]`)?.classList.add('spell-self-target');
 const clear=()=>field.querySelectorAll('.spell-area,.spell-center,.attack-approach-path,.attack-approach-stop,.spell-inner,.spell-outer,.spell-landing').forEach(el=>{el.classList.remove('spell-area','spell-center','attack-approach-path','attack-approach-stop','spell-inner','spell-outer','spell-landing');el.querySelector('.approach-step')?.remove()});
 const paint=preview=>{
  clear();for(const zone of preview?.zones||[])for(const p of zone.cells||[]){const cell=field.querySelector(`[data-battle-cell="${p.x},${p.y}"]`);cell?.classList.add('spell-area');if(preview.landing)cell?.classList.add(Math.max(Math.abs(p.x-preview.landing.x),Math.abs(p.y-preview.landing.y))<=1?'spell-inner':'spell-outer')}
  if(preview?.landing)field.querySelector(`[data-battle-cell="${preview.landing.x},${preview.landing.y}"]`)?.classList.add('spell-landing');
  for(const p of preview?.path||[])field.querySelector(`[data-battle-cell="${p.x},${p.y}"]`)?.classList.add('attack-approach-path');
  if(preview?.move_to)field.querySelector(`[data-battle-cell="${preview.move_to.x},${preview.move_to.y}"]`)?.classList.add('attack-approach-stop');
 };
 if(self){const preview=battle.skill_previews?.[skill.id]?.[actor.id];if(preview)paint(preview)}
 const point=e=>{const r=field.getBoundingClientRect();return {x:Math.floor((e.clientX-r.left)/r.width*battle.width),y:Math.floor((e.clientY-r.top)/r.height*battle.height)}};
 if(entries){
  field.querySelectorAll('[data-battle-cell]').forEach(el=>el.classList.toggle('spell-castable',!!entries[el.dataset.battleCell]));
  let lastPoint=null;field.onpointermove=e=>{const p=point(e),key=`${p.x},${p.y}`;if(key===lastPoint)return;lastPoint=key;const preview=entries[key];paint(preview);const help=document.getElementById('combat-action-help');if(help)help.textContent=preview?`${preview.move_to?`Move to cell ${preview.move_to.x+1}, ${preview.move_to.y+1} (${preview.movement_cost} movement), then `:'From this position, ' }${preview.landing?'leap with':'cast'} ${skill.name}. ${preview.zones.flatMap(z=>z.cells).length} affected cells.`:'Outside movement + spell range, blocked sight, or no valid ground.';if(preview)field.querySelector(`[data-battle-cell="${p.x},${p.y}"]`)?.classList.add('spell-center')};
  field._spellClick=e=>{const p=point(e),preview=entries[`${p.x},${p.y}`];e.stopImmediatePropagation();e.preventDefault();if(preview)onCast({action:'skill',skill_id:skill.id,x:p.x,y:p.y,...(preview.move_to?{move_to:preview.move_to}:{})})};
  field.addEventListener('click',field._spellClick,true);
 }else{
  field._spellClick=null;
  field.onpointermove=e=>{if(self)return;const token=e.target.closest?.('[data-battle-unit]');if(token)paint(battle.attack_previews?.[token.dataset.battleUnit]?.skill);else clear()};
 }
}

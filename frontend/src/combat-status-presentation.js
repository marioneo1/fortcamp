import {skillIcon} from './ability-icons.js';
import {statusDetails} from './combat-status-ui.js';
import {JOB_ICON_ART} from './ability-icon-manifest.js';
import {impactTimeline} from './combat-impact.js';

const META={
 palm_exposure:['debuff','monk:rapid_palm',8],iron_reversal_evasion:['buff','monk:iron_reversal',10],monk_siphon:['buff','monk:breaking_combination',12],dash_parry:['buff','monk:sweeping_dash',10],
 iron_reversal:['buff','monk:iron_reversal',10],flowing_footwork:['buff','monk:flowing_footwork',12],open_guard:['debuff','monk:breaking_combination',8],
 brace_defense:['buff','martial:brace-defense',10],reckless_exposure:['debuff','martial:reckless-exposure',8],death_defiance:['buff','martial:too-angry-to-fall',9],
 stun:['debuff','fighter:bash',0],sleep:['debuff','bard:discord',1],ambush_sleep:['debuff','bard:discord',1],
 freeze:['debuff','mage:binding',2],paralyze:['debuff','captor:bind',2],bind:['debuff','captor:bind',3],
 fear:['debuff','bard:discord',4],panic:['debuff','bard:discord',4],charm:['debuff','bard:refrain',4],
 confuse:['debuff','captor:dust',4],berserk:['debuff','barbarian:stand',4],mute:['debuff','bard:silence',4],
 blind:['debuff','captor:dust',5],poison:['debuff','ranger:poison',6],burn:['debuff','mage:scorch',6],
 bleed:['debuff','rogue:caltrops',6],hobbled:['debuff','rogue:crippling_cut',7],slow:['debuff','mage:binding',7],
 armor_fracture:['debuff','barbarian:expose',8],vulnerable:['debuff','barbarian:expose',8],
 mark:['debuff','ranger:mark',8],pit_trapped:['debuff','captor:bind',3],
 barrier:['buff','cleric:barrier',10],guard:['buff','fighter:intercept',10],
 rally_protection:['buff','fighter:intercept',10],rally_power:['buff','barbarian:drive',11],
 regeneration:['buff','cleric:mend',12],braced:['buff','barbarian:anchored',12],
 footing:['buff','captor:anchored',20],reaction:['other','fighter:riposte',20],
 deployment:['other','summoner:wisps',20],wild_form:['buff','druid:prowler',12],
 lifeline_ready:['buff','cleric:barrier',15],lifeline_spent:['other','cleric:barrier',20]
};
const guardDefinition={name:'Guard',icon:'',description:'The next direct hit deals 25% less damage. Consumed by that hit; expires at the next activation.'};
export function visibleStatuses(unit,{compact=false}={}){
 if(!unit||unit.alive===false||unit.conscious===false||unit.extracted||unit.carried_by)return [];
 const statuses=[...(unit.statuses||[])];
 if(unit.guarding&&!statuses.some(s=>s.id==='guard'))statuses.unshift({id:'guard'});
 const unique=[...new Map(statuses.map(s=>[`${s.id}:${['mark','passive_readiness'].includes(s.id)?s.source_id||'':''}`,s])).values()];
 return unique.filter(s=>!compact||!['footing','reaction','deployment','lifeline_spent'].includes(s.id))
  .sort((a,b)=>(META[a.id]?.[2]??30)-(META[b.id]?.[2]??30));
}
export function statusVisual(status){
 if(status.id==='passive_readiness')return {kind:'buff',image:skillIcon({id:status.skill_id,type:'passive'}),count:status.spent?'?':status.cooldown_remaining||null};
 const [kind,art]=META[status.id]||['other',null];
 const count=status.layers?status.layers.length:status.id==='barrier'?status.amount:
  ['rally_protection','rally_power','guard','vulnerable'].includes(status.id)?'1×':
  status.rounds??status.turns??status.duration;
 return {kind,image:(art?.startsWith('monk:')||art?.startsWith('rogue:'))?skillIcon({id:'job:'+art}):art?.startsWith('martial:')?`/assets/martial-jobs-v1/${art.slice(8)}.png`:art?JOB_ICON_ART['job:'+art]||null:null,count:count??null};
}
function details(status,definitions){return statusDetails(status,{guard:guardDefinition,...definitions})}
export function statusBadge(status,definitions,escape,{unitId='',compact=false}={}){
 const d=details(status,definitions),v=statusVisual(status);
 return `<span class="status-badge status-${v.kind} ${status.id==='passive_readiness'?'passive-readiness':''} ${status.id==='passive_readiness'&&!status.ready?'passive-cooling':''}" data-unit-status="${escape(status.id)}" data-status-owner="${escape(status.source_id||'')}" data-status-unit="${escape(unitId)}" tabindex="0" role="img" aria-label="${escape([d.name,d.description,...d.details].join('. '))}">${v.image?`<img src="${v.image}" alt="" draggable="false">`:'<span class="status-fallback" aria-hidden="true">?</span>'}${v.count!==null?`<span class="status-count" aria-hidden="true">${escape(v.count)}</span>`:''}${compact?'':`<span class="status-short-name" aria-hidden="true">${escape(d.name.replace('Hold Together: ',''))}</span>`}</span>`;
}
export function mapStatusMarkup(unit,definitions,escape){
 const statuses=visibleStatuses(unit,{compact:true});if(!statuses.length)return '';
 return `<span class="status-row readable-statuses">${statuses.map(s=>statusBadge(s,definitions,escape,{unitId:unit.id,compact:true})).join('')}</span>`;
}
export function statusTrayMarkup(unit,definitions,escape){
 const statuses=visibleStatuses(unit);if(!statuses.length)return '';
 return `<section class="combat-status-tray" aria-label="Acting character effects">${['buff','debuff','other'].map(kind=>{
  const rows=statuses.filter(s=>statusVisual(s).kind===kind);if(!rows.length)return '';
  return `<div class="status-group status-${kind}"><b>${kind==='buff'?'Buffs':kind==='debuff'?'Debuffs':'Other effects'}</b><div>${rows.map(s=>statusBadge(s,definitions,escape,{unitId:unit.id})).join('')}</div></div>`;
 }).join('')}</section>`;
}
export function statusListMarkup(unit,definitions,escape){
 const statuses=visibleStatuses(unit);if(!statuses.length)return '<p>No active status effects.</p>';
 return ['buff','debuff','other'].map(kind=>{
  const rows=statuses.filter(s=>statusVisual(s).kind===kind);if(!rows.length)return '';
  return `<section class="inspect-status-group status-${kind}"><h4>${kind==='buff'?'Buffs':kind==='debuff'?'Debuffs':'Other effects'}</h4>${rows.map(s=>{
   const d=details(s,definitions);return `<article>${statusBadge(s,definitions,escape,{compact:true})}<div><b>${escape(d.name)}</b><p>${escape(d.description)}</p>${d.details.map(t=>`<small>${escape(t)}</small>`).join('')}</div></article>`;
  }).join('')}</section>`;
 }).join('');
}
export function statusInspectMarkup(unit,status,definitions,escape){
 const d=details(status,definitions);
 return `<header><strong>${escape(d.name)}</strong><small>${escape(unit.name)}</small></header><div class="inspect-statuses">${statusListMarkup({...unit,statuses:[status],guarding:false},definitions,escape)}</div>`;
}
const star='<svg viewBox="0 0 24 24" aria-hidden="true"><path d="m12 1 3.2 7.1 7.8 1-5.7 5.4 1.5 7.7-6.8-3.8-6.8 3.8 1.5-7.7L1 9.1l7.8-1Z"/><path class="star-glint" d="m12 4 1.7 5.5 5.3.7-5 1-2 5.5-1.2-5.5-4.8-1 4.8-.7Z"/></svg>';
export function stunOnsets(events){
 const result=new Map();
 for(const {event,start} of impactTimeline(events))if(event.kind==='status'&&event.status_id==='stun'&&!result.has(event.unit_id))result.set(event.unit_id,start);
 return result;
}
export function stunMarkup(unit,delay=0){
 return visibleStatuses(unit).some(s=>s.id==='stun')?`<span class="unit-stun-effect" aria-hidden="true" style="--stun-onset:${Math.max(0,delay)}ms"><span class="stun-orbit-ring"></span>${[0,1,2].map(i=>`<span class="stun-star" style="--star-phase:${-i*.6}s">${star}</span>`).join('')}</span>`:'';
}

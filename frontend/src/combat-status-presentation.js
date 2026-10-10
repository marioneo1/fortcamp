import {skillIcon} from './ability-icons.js';
import {statusDetails,statusSummary} from './combat-status-ui.js';
import {JOB_ICON_ART} from './ability-icon-manifest.js';
import {impactTimeline} from './combat-impact.js';

const META={
 intimidated:['debuff','fighter:driving_strike',6],feigned_death:['buff','rogue:backflip',12],
 sword_exposed:['debuff','npc:bandit:goliath_shot',8],heel_wound:['debuff','npc:bandit:heel_cut',8],tag_team_power:['buff','npc:bandit:tag_team',10],
 disarm:['debuff','captor:restraint',2],captor_held:['debuff','captor:restraining_hold',0],captor_holding:['buff','captor:restraining_hold',0],captor_blitz:['buff','captor:blitz',5],captor_abducted:['debuff','captor:abduct',4],
 summon_order:['other','summoner:bound_companion',5],summon_overload:['buff','summoner:overload',6],
 druid_rejuvenation:['buff','druid:rejuvenation',10],living_armor:['buff','druid:living_armor',10],
 cleric_rest:['debuff','cleric:rest',7],cleric_smite:['buff','cleric:smite',10],cleric_regeneration:['buff','cleric:sanctuary',12],
 engineer_machine:['other','engineer:sentry_turret',10],engineer_overclock:['buff','engineer:overclock',10],engineer_mounted:['buff','engineer:man_the_guns',10],engineer_construction:['other','engineer:rapid_assembly',12],engineer_rapid_assembly:['buff','engineer:rapid_assembly',8],engineer_disruption:['debuff','engineer:proximity_charge',0],
 wet:['debuff','mage:typhoon',7],blister:['debuff','mage:fireball',8],weapon_enchant:['buff','mage:enchant_weapon',12],channeling:['other','mage:meteor',15],
 pestilence:['debuff','ranger:pestilence_shot',8],poison_imbue:['buff','ranger:poison_attack',12],sharpshooter:['buff','ranger:sharpshooter',12],
 palm_exposure:['debuff','monk:rapid_palm',8],iron_reversal_evasion:['buff','monk:iron_reversal',10],monk_siphon:['buff','monk:breaking_combination',12],dash_parry:['buff','monk:sweeping_dash',10],
 iron_reversal:['buff','monk:iron_reversal',10],flowing_footwork:['buff','monk:flowing_footwork',12],open_guard:['debuff','monk:breaking_combination',8],
 brace_defense:['buff','martial:brace-defense',10],reckless_exposure:['debuff','martial:reckless-exposure',8],death_defiance:['buff','martial:too-angry-to-fall',9],
 stun:['debuff','fighter:bash',0],sleep:['debuff','bard:discord',1],ambush_sleep:['debuff','bard:discord',1],
 bard_accelerando:['buff','bard:accelerando',9],bard_quickening:['buff','bard:quickening_chorus',10],bard_war_anthem:['buff','bard:war_anthem',11],bard_song_peace:['other','bard:song_of_peace',9],
 bard_jeering:['debuff','bard:jeering_verse',9],bard_jeer_vulnerable:['debuff','bard:jeering_verse',10],
 freeze:['debuff','mage:flash_freeze',2],paralyze:['debuff','captor:bind',2],bind:['debuff','captor:bind',3],
 fear:['debuff','bard:discord',4],panic:['debuff','bard:discord',4],charm:['debuff','bard:refrain',4],
 confuse:['debuff','captor:dust',4],berserk:['debuff','barbarian:stand',4],mute:['debuff','bard:silence',4],
 blind:['debuff','captor:dust',5],poison:['debuff','ranger:poison_attack',6],burn:['debuff','mage:fireball',6],
 rat_weakness:['debuff','rogue:exploit_weakness',6],rat_swarm:['buff','druid:rat',12],
 bleed:['debuff','rogue:caltrops',6],hobbled:['debuff','rogue:crippling_cut',7],slow:['debuff','mage:binding',7],
 armor_fracture:['debuff','barbarian:expose',8],vulnerable:['debuff','barbarian:expose',8],
 mark:['debuff','ranger:mark_quarry',8],pit_trapped:['debuff','captor:bind',3],
 barrier:['buff','cleric:barrier',10],guard:['buff','fighter:intercept',10],
 rally_protection:['buff','fighter:intercept',10],rally_power:['buff','barbarian:drive',11],
 regeneration:['buff','cleric:mend',12],braced:['buff','barbarian:anchored',12],
 innate_resistance:['buff','captor:anchored',20],footing:['buff','captor:anchored',20],reaction:['other','fighter:riposte',20],
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
 if(status.id==='animal_mounted')return {kind:'buff',image:'/assets/boar-mount-v1/mount_icon.png',count:null};
 if(status.id.startsWith('engineer_')){const [kind,art]=META[status.id]||['other','engineer:sentry_turret'];return {kind,image:skillIcon({id:'job:'+art,engineer_kind:art.split(':')[1]}),count:status.turns??null}}

 if(status.id==='summon_order')return {kind:'other',image:skillIcon({id:'job:summoner:bound_companion'}),count:null};
 if(status.id==='summon_overload')return {kind:'buff',image:skillIcon({id:'job:summoner:overload'}),count:status.turns??null};
 if(status.id==='wild_form'&&status.form_id)return {kind:'buff',image:skillIcon({id:'job:druid:'+status.form_id}),count:null};
 if(status.id==='passive_readiness')return {kind:'buff',image:skillIcon({id:status.skill_id,type:'passive'}),count:status.spent?'0':status.cooldown_remaining||null};
 const [kind,art]=META[status.id]||['other',null];
 const count=['burn','poison','bleed'].includes(status.id)?status.layers?.length??status.stacks??(status.id==='poison'?status.turns:1)??1:status.layers?status.layers.length:status.id==='barrier'?status.amount:
  ['rally_protection','rally_power','guard','vulnerable'].includes(status.id)?'1×':
  status.ticks??status.rounds??status.turns??status.duration;
 return {kind,image:art?.startsWith('npc:')?skillIcon({id:art}):(art?.startsWith('captor:')||art?.startsWith('druid:')||art?.startsWith('cleric:')||art?.startsWith('mage:')||art?.startsWith('monk:')||art?.startsWith('rogue:')||art?.startsWith('ranger:')||art?.startsWith('bard:'))?skillIcon({id:'job:'+art}):art?.startsWith('martial:')?`/assets/martial-jobs-v1/${art.slice(8)}.png`:art?JOB_ICON_ART['job:'+art]||null:null,count:count??null};
}
function details(status,definitions){return statusDetails(status,{guard:guardDefinition,...definitions})}
export function statusCardNotes(s,definitions={}){
 if(s.id==='summon_order')return ['Persistent order; acts automatically after its owner.'];
 if(s.id==='summon_overload')return [`${s.turns} owner turns until automatic death.`];
 if(s.id==='rat_weakness')return [`${s.stacks||1} stacks: -${Math.min(30,5*(s.stacks||1))}% damage dealt; +${Math.min(30,5*(s.stacks||1))}% damage taken; lose one stack at turn end.`];
 if(s.id==='rat_swarm')return [`${s.stacks||1} rats; HP and attack combined; ${s.stacks||1} Weakness stacks per landed bite.`];
 const d=details(s,definitions),source=s.source_name?[`From ${s.source_name}`]:[];
 if(s.id==='innate_resistance')return ['Always active; unlisted debuffs have no innate resistance.'];
 if(['poison','burn','bleed'].includes(s.id))return [...d.details.slice(0,1),...source];
 if(s.id==='passive_readiness'||s.id==='wild_form'||s.id==='reaction'||s.id==='deployment')return d.details;
 if(s.bard_no_linger||['bard_accelerando','bard_song_peace'].includes(s.id))return ['Only while inside the active Song',...source];
 if(['bard_quickening','bard_war_anthem'].includes(s.id))return ['Through your next turn; staying inside refreshes it',...source];
 if(s.layers)return [`${s.layers.length} stacks; each expires independently`,...source];
 if(s.id==='mark'||s.id==='weapon_enchant')return d.details;
 if(s.id==='barrier')return d.details;
 if(['open_guard','flowing_footwork','iron_reversal','iron_reversal_evasion','dash_parry','monk_siphon','freeze'].includes(s.id))return d.details;
 if(s.ticks!=null)return [`${s.ticks} healing ticks remaining at turn start`,...source];
 const time=s.rounds??s.turns??s.duration;
 return [...(time!=null?[`${time} ${s.rounds!=null?'battlefield round':'target turn'}${time===1?'':'s'} remaining${s.expiry==='target_end'?'; expires at turn end':''}`]:[]),...source];
}
export function statusBadge(status,definitions,escape,{unitId='',compact=false}={}){
 const d=details(status,definitions),v=statusVisual(status);
 return `<span class="status-badge status-${v.kind} ${status.id==='passive_readiness'?'passive-readiness':''} ${status.id==='passive_readiness'&&!status.ready?'passive-cooling':''}" data-unit-status="${escape(status.id)}" data-status-owner="${escape(status.source_id||'')}" data-status-unit="${escape(unitId)}" tabindex="0" role="img" aria-label="${escape([d.name,d.description,...d.details].join('. '))}">${v.image?`<img src="${v.image}" alt="" draggable="false">`:'<span class="status-fallback" aria-hidden="true">&diams;</span>'}${v.count!==null?`<span class="status-count" aria-hidden="true">${escape(v.count)}</span>`:''}${compact?'':`<span class="status-short-name" aria-hidden="true">${escape(d.name.replace('Hold Together: ',''))}</span>`}</span>`;
}
export function mapStatusMarkup(unit,definitions,escape,units={}){
 if(unit.boar_mount&&unit.rider_id)return '';
 // Permanent machinery properties stay inspectable without covering the gun/seat.
 const statuses=visibleStatuses(unit,{compact:true}).filter(s=>!unit.engineer_machine||!['engineer_machine','innate_resistance'].includes(s.id));
 const rows=statuses.map(s=>({status:s,unitId:unit.id}));
 const animal=units[unit.animal_mount_id];
 if(animal){
  const key=s=>JSON.stringify([s.id,s.source_id,s.turns,s.stacks,s.amount,s.ready]);
  const seen=new Set(statuses.map(key));
  for(const s of visibleStatuses(animal,{compact:true}))if(!seen.has(key(s))){rows.push({status:s,unitId:animal.id});seen.add(key(s))}
 }
 return rows.length?`<span class="status-row readable-statuses">${rows.map(({status,unitId})=>statusBadge(status,definitions,escape,{unitId,compact:true})).join('')}</span>`:'';
}
export function statusTrayMarkup(unit,definitions,escape){
 const statuses=visibleStatuses(unit);
 return `<section class="combat-status-tray" aria-label="Acting character buffs, debuffs and other effects"><b class="status-tray-heading">Effects</b><div class="status-tray-icons">${statuses.slice(0,24).map(s=>statusBadge(s,definitions,escape,{unitId:unit.id})).join('')}${statuses.length?'':'<span class="effects-empty">No active effects</span>'}</div><button class="effects-overflow" data-all-effects data-effect-count="${statuses.length}">${statuses.length>24?`+${statuses.length-24} more`:'All effects'}</button></section>`;
}
export function statusListMarkup(unit,definitions,escape,{compact=false,cards=false,limit=Infinity}={}){
 const all=visibleStatuses(unit);if(!all.length)return '<p>No active status effects.</p>';
 const statuses=all.slice(0,limit),remaining=all.length-statuses.length;
 const groups=['buff','debuff','other'].map(kind=>{
  const rows=statuses.filter(s=>statusVisual(s).kind===kind);if(!rows.length)return '';
  return `<section class="inspect-status-group status-${kind}"><h4>${kind==='buff'?'Buffs':kind==='debuff'?'Debuffs':'Other effects'}</h4>${cards?'<div class="effect-card-grid">':''}${rows.map(s=>{
   const d=details(s,definitions);return `<article class="${cards?'effect-detail-card':compact?'compact-effect':''}" data-effect-id="${escape(s.id)}" data-effect-owner="${escape(s.source_id||'')}">${statusBadge(s,definitions,escape,{compact:true})}<div><b>${escape(d.name)}</b><p>${escape(cards||compact?statusSummary(s,definitions):d.description)}</p>${(compact?[]:cards?statusCardNotes(s,definitions):d.details).map(t=>`<small>${escape(t)}</small>`).join('')}</div></article>`;
  }).join('')}${cards?'</div>':''}</section>`;
 }).join('');
 return groups+(remaining?`<p class="inspect-more">+${remaining} more ${remaining===1?'effect':'effects'} &middot; Right-click for all</p>`:'');
}
export function statusInspectMarkup(unit,status,definitions,escape){
 const d=details(status,definitions);
 return `<header><strong>${escape(d.name)}</strong><small>${escape(unit.name)}</small></header><div class="inspect-statuses">${statusListMarkup({...unit,statuses:[status],guarding:false},definitions,escape)}</div><footer class="inspect-hint">Right-click to keep this effect open.</footer>`;
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

// Replay resolved status facts on the same contact clock as attacks; never simulate rules.
import {mapStatusMarkup} from './combat-status-presentation.js';
import {playbackDuration} from './combat-playback.js';
export function statusPlaybackPlan(previous,battle,timeline){
 const end=Math.max(playbackDuration(timeline),...timeline.map(r=>r.start),0);
 return Object.entries(battle.units||{}).flatMap(([id,unit])=>{
  const before=previous?.units?.[id]?.statuses||[],after=unit.statuses||[];
  const changes=timeline.filter(r=>r.event.unit_id===id&&Array.isArray(r.event.statuses_snapshot))
   .map(r=>({at:r.start,statuses:r.event.statuses_snapshot})).sort((a,b)=>a.at-b.at);
  if(!changes.length&&JSON.stringify(before)===JSON.stringify(after))return [];
  return [{id,initial:before,changes:[...changes,{at:end,statuses:after,final:true}]}];
 });
}
export function animateStatusPlayback(previous,battle,timeline,tokenFor,escape){
 const presented=Object.fromEntries(Object.entries(battle.units||{}).map(([id,u])=>[id,{...u,statuses:previous?.units?.[id]?.statuses||[]} ]));
 for(const plan of statusPlaybackPlan(previous,battle,timeline)){
  const token=tokenFor(plan.id);if(!token)continue;
  const generation=Symbol();token.statusPlaybackGeneration=generation;
  const paint=(statuses,final=false)=>{
   if(!token.isConnected||token.statusPlaybackGeneration!==generation)return;
   token.presentationStatuses=final?null:statuses;
   presented[plan.id]={...battle.units[plan.id],alive:true,conscious:true,statuses};
   const owner=presented[plan.id].rider_id||plan.id,display=tokenFor(owner)||token;
   display.querySelector('.status-row')?.remove();
   display.insertAdjacentHTML('beforeend',mapStatusMarkup(presented[owner]||presented[plan.id],battle.status_definitions,escape,presented));
   const tip=document.getElementById('combat-unit-inspect');if(tip){tip.hidden=true;tip.dataset.inspectKey=''}
  };
  paint(plan.initial);
  for(const change of plan.changes)setTimeout(()=>paint(change.statuses,change.final),change.at);
 }
}

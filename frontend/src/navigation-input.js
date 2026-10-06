// Suppress an unchanged entrance request; any traversal-relevant change permits it again.
export function createNavigationInput(){
 let last=null;
 return {
  clear(){last=null},
  accept(context,battle,command){
   const a=battle?.units?.[battle.current_unit_id];
   const key=JSON.stringify([context,command.x,command.y,command.position,a?.x,a?.y,battle.action_count,
    Object.values(battle.units||{}).map(u=>[u.id,u.x,u.y,u.conscious,u.extracted,u.carried_by]),
    (battle.terrain||[]).map(t=>[t.id,t.state,t.blocking,t.destroyed,t.hp]),
    Object.values(battle.objects||{}).map(o=>[o.id,o.x,o.y,o.state,o.carried_by])]);
   if(key===last)return false;last=key;return true;
  },
 };
}

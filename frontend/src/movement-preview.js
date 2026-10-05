// Use the server's compact movement tree; do not duplicate terrain/race rules.
const key=p=>`${p.x},${p.y}`;
export function previewMovement(battle,destination,visiblePosition){
  const unit=battle?.units?.[battle.current_unit_id];
  if(battle?.status!=='active'||unit?.team!=='player'||unit.acted)return null;
  const nodes=new Map((battle.movement_tree||[]).map(p=>[key(p),p]));
  if(!nodes.has(key(destination)))return null;
  function route(point){
    const result=[],visited=new Set();let node=nodes.get(key(point));
    while(node&&!visited.has(key(node))){
      visited.add(key(node));result.unshift({x:node.x,y:node.y,cost:node.cost});
      if(!node.parent)return result;
      node=nodes.get(node.parent.join(','));
    }
    return null;
  }
  const path=route(destination);if(!path)return null;
  const position=visiblePosition||unit;
  const start=[...nodes.values()].reduce((best,p)=>Math.hypot(p.x-position.x,p.y-position.y)<Math.hypot(best.x-position.x,best.y-position.y)?p:best);
  const from=route(start);if(!from)return null;
  let shared=0;while(shared<from.length&&shared<path.length&&key(from[shared])===key(path[shared]))shared++;
  let points=[...from.slice(Math.max(0,shared-1)).reverse(),...path.slice(shared)];
  // Parents describe turn-origin costs, not all legal connections. Use the
  // server's directed step graph for walking from the displayed position.
  if(Array.isArray(start.steps)){
    const costs=new Map([[key(start),0]]),parents=new Map([[key(start),null]]),pending=new Set([key(start)]);
    while(pending.size){
      const here=[...pending].reduce((a,b)=>costs.get(a)<=costs.get(b)?a:b);pending.delete(here);
      if(here===key(destination))break;
      for(const [x,y,cost] of nodes.get(here)?.steps||[]){
        const next=`${x},${y}`,total=costs.get(here)+cost;
        if(!nodes.has(next)||total>=(costs.get(next)??Infinity))continue;
        costs.set(next,total);parents.set(next,here);pending.add(next);
      }
    }
    if(!parents.has(key(destination)))return null;
    points=[];
    for(let here=key(destination);here!==null;here=parents.get(here)){
      const node=nodes.get(here);points.unshift({x:node.x,y:node.y,cost:node.cost});
    }
  }
  const preview=structuredClone(battle),actor=preview.units[unit.id];
  actor.x=destination.x;actor.y=destination.y;
  const origin=path[0];actor.movement_origin={x:origin.x,y:origin.y};
  actor.movement_path=path.slice(1);actor.moved=key(destination)!==key(origin);
  if(key(destination)!==key(unit))actor.exit_ready=false;
  if(actor.carrying&&preview.units[actor.carrying])Object.assign(preview.units[actor.carrying],destination);
  preview.movement_origin=actor.movement_origin;preview.movement_path=actor.movement_path;
  preview.animation_events=[];preview.preview_movement_points=points;
  return preview;
}

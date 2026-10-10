export function preparationCells(option,x,y,vertical=false){
 return option?.deploy_kind==='caltrops'?[-1,0,1].map(n=>({x:x+(vertical?0:n),y:y+(vertical?n:0)})):[{x,y}];
}
export function preparationPreview(battle,option,x,y,vertical=false){
 const cells=preparationCells(option,x,y,vertical),zone=new Set((battle.preparation?.zone||[]).map(p=>`${p.x},${p.y}`));
 const occupied=new Set();
 for(const row of battle.preparation?.placements||[])for(const p of row.cells||[row])occupied.add(`${p.x},${p.y}`);
 for(const u of Object.values(battle.units||{}))if(u.alive&&u.conscious!==false&&!u.extracted)occupied.add(`${u.x},${u.y}`);
 const valid=!!option&&cells.every(p=>zone.has(`${p.x},${p.y}`)&&!occupied.has(`${p.x},${p.y}`));
 const trigger=option?.id==='proximity_dynamite'||option?.deploy_kind==='proximity_charge';
 const area=trigger?[-1,0,1].flatMap(dx=>[-1,0,1].map(dy=>({x:x+dx,y:y+dy}))):[];
 const enemyTouching=trigger&&Object.values(battle.units||{}).some(u=>u.team==='enemy'&&u.alive&&u.conscious!==false&&!u.extracted&&Math.max(Math.abs(u.x-x),Math.abs(u.y-y))<=1);
 return {cells,area,valid:valid&&!enemyTouching};
}

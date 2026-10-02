// Assemble short matching wall sleeves beneath generated connection ends.
// Clipping the existing texture preserves beam thickness and brushwork.
function turn([x,y],rotation){for(let i=0;i<rotation/90;i++)[x,y]=[-y,x];return [x,y]}

export function structuralLayout(item,geometry){
  const base=item.art_offset||[0,0],match=/^structure:(timber|fieldstone|limestone|iron)_(corner|edge_junction)$/.exec(item.sprite||'');
  if(!match||item.destroyed)return {offset:base,connectors:[]};
  const [,family,piece]=match,g=geometry[family];
  if(!g)return {offset:base,connectors:[]};
  const rotation=((Number(item.rotation)||0)%360+360)%360;
  const delta=piece==='corner'?turn(g.corner_offset||[0,0],rotation):[0,0];
  const ports=piece==='corner'?[[[-.5,-g.join_offset],0],[[g.join_offset,.5],90]]:[[[0,.5],90]];
  const connectors=ports.map(([point,direction],index)=>{
    const [x,y]=turn(point,rotation),anchor=piece==='corner'?base:[0,0];
    return {id:`${item.id}_sleeve_${index}`,parent_id:item.id,x:item.x,y:item.y,
      sprite:`structure:${family}_wall`,art_scale:item.art_scale||1.25,
      rotation:(direction+rotation)%360,art_offset:[x+anchor[0],y+anchor[1]],
      art_clip:[0,33,0,33]};
  });
  return {offset:[base[0]+delta[0],base[1]+delta[1]],connectors};
}

export function structuralConnectors(terrain,geometry){
  return terrain.flatMap(item=>structuralLayout(item,geometry).connectors);
}

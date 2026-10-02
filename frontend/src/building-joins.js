// Assemble grid connections from matching painted beams without stretching.
// Generated damage art keeps separately calibrated surviving arms.
function turn([x,y],rotation){for(let i=0;i<rotation/90;i++)[x,y]=[-y,x];return [x,y]}

export function structuralLayout(item,geometry){
  const base=item.art_offset||[0,0],match=/^structure:(timber|fieldstone|limestone|iron)_(corner_broken|corner|edge_junction|junction|cross|end|breach)$/.exec(item.sprite||'');
  if(!match)return {offset:base,connectors:[]};
  const [,family,piece]=match,g=geometry[family];
  if(!g)return {offset:base,connectors:[]};
  const rotation=((Number(item.rotation)||0)%360+360)%360;
  if(piece==='breach'){
    const [x,y]=turn(g.breach_offset||[0,0],rotation);
    return {offset:[base[0]+x,base[1]+y],connectors:[]};
  }
  if(piece==='end'){
    // A half-length terminal attaches to its right-hand neighbor, rather than
    // floating in the middle of its cell. Rotation chooses the attached side.
    const [x,y]=turn(g.end_offset||[.25,0],rotation);
    return {offset:[base[0]+x,base[1]+y],connectors:[]};
  }
  if(item.destroyed)return {offset:base,connectors:[]};
  // Build exact ports from the material's straight painted beam. Clipping
  // changes its length, never its thickness or aspect ratio. Corner/T source
  // silhouettes cannot establish a reliable grid contract on their own.
  const scale=item.art_scale||1.25,o=g.join_offset,half=g.wall_half_thickness||.09;
  const anchor=piece==='edge_junction'?[0,0]:base;
  const beam=(index,point,direction,left=-.625,right=.625)=>{
    const [x,y]=turn(point,rotation);
    return {id:`${item.id}_sleeve_${index}`,parent_id:item.id,x:item.x,y:item.y,
      sprite:`structure:${family}_wall`,art_scale:scale,rotation:(direction+rotation)%360,
      art_offset:[x+anchor[0],y+anchor[1]],
      art_clip:[0,Math.max(0,(.5-right/scale)*100),0,Math.max(0,(.5+left/scale)*100)]};
  };
  if(['corner','edge_junction','junction','cross'].includes(piece)){
    let connectors;
    if(piece==='corner')connectors=[beam(0,[0,-o],0,-scale/2,o+half),beam(1,[o,0],90,-o,scale/2)];
    else if(piece==='edge_junction'){
      // Backend T offsets described the old silhouette; the wall edge itself
      // is anchored by direction rather than those obsolete image offsets.
      connectors=[beam(0,[0,-o],0),beam(1,[0,0],90,-o,scale/2)];
    }else connectors=[beam(0,[0,0],0),beam(1,[0,0],90,piece==='cross'?-scale/2:0,scale/2)];
    return {offset:base,connectors,hideArt:true};
  }
  if(piece==='corner_broken'){
    const [x,y]=turn(g.broken_corner_offset||g.corner_offset||[0,0],rotation);
    return {offset:[base[0]+x,base[1]+y],connectors:[
      beam(0,[0,-o],0,-scale/2,-.24),beam(1,[o,0],90,.24,scale/2)]};
  }
  return {offset:base,connectors:[]};
}

export function structuralConnectors(terrain,geometry){
  return terrain.flatMap(item=>structuralLayout(item,geometry).connectors);
}

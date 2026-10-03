// Painted modular connections: plain mating ends, caps only at exposed ports.
function turn([x,y],rotation){for(let i=0;i<rotation/90;i++)[x,y]=[-y,x];return [x,y]}
const matchPiece=item=>/^structure:(timber|fieldstone|limestone|iron)_(.+)$/.exec(item.sprite||'');
const rotationOf=item=>((Number(item.rotation)||0)%360+360)%360;
const inward={north:[0,1],east:[-1,0],south:[0,-1],west:[1,0]};
function faceMirror(item){
 const face=inward[item.wall_edges?.length===1?item.wall_edges[0]:null];
 // Centered dividers share a stable face convention, even after a half turn.
 if(!face)return rotationOf(item)>=180?-1:1;
 const normal=turn([0,1],rotationOf(item));
 return normal[0]*face[0]+normal[1]*face[1]<0?-1:1;
}
// Clip the texture at a diagonal mating plane instead of drawing two rims
// over one another. Coordinates remain local to each unscaled texture strip.
function matingPolygon(scale,left,right,[a,b,c]){
 let points=[[left,-scale/2],[right,-scale/2],[right,scale/2],[left,scale/2]];
 const output=[];
 for(let i=0;i<points.length;i++){
  const p=points[i],q=points[(i+1)%points.length],dp=a*p[0]+b*p[1]-c,dq=a*q[0]+b*q[1]-c;
  if(dp<=0)output.push(p);
  if((dp<=0)!==(dq<=0)){const t=dp/(dp-dq);output.push([p[0]+t*(q[0]-p[0]),p[1]+t*(q[1]-p[1])]);}
 }
 return output.map(([x,y])=>[(x/scale+.5)*100,(y/scale+.5)*100]);
}
export function wallArtStyle(item,layout){
 const mirrorY=item.art_mirror_y??layout.mirrorY??1;
 const match=matchPiece(item),band=match&&/^(wall|end|breach|window|door_(open|closed)|gate_(open|closed))$/.test(match[2]);
 const layer=item.art_layer??layout.layer??(band&&rotationOf(item)%180===0?3:2);
 // CSS mirrors both the image and its clip. Reflect the clip first so that
 // mirroring the painted face never changes the physical mating plane.
 const clip=item.art_clip_polygon?'polygon('+item.art_clip_polygon.map(([x,y])=>`${x}% ${mirrorY===-1?100-y:y}%`).join(',')+')':
  item.art_clip?'inset('+item.art_clip.map(v=>v+'%').join(' ')+')':'none';
 return `--asset-mirror-y:${mirrorY};--asset-clip:${clip};--wall-art-layer:${layer}`;
}
function offsetOf(item,g,piece){
 if(piece==='edge_junction')return [0,0];
 if(item.edge_wall&&item.wall_edges?.length===1){
  const o=g.join_offset;
  return {north:[0,-o],east:[o,0],south:[0,o],west:[-o,0]}[item.wall_edges[0]]||item.art_offset||[0,0];
 }
 return item.art_offset||[0,0];
}

export function connectionPorts(item,geometry){
 const match=matchPiece(item);if(!match||item.destroyed)return [];
 const [,family,piece]=match,g=geometry[family];if(!g)return [];
 const o=g.join_offset,rotation=rotationOf(item),base=offsetOf(item,g,piece);
 let ports;
 if(['corner','corner_broken'].includes(piece))ports=[[[-.5,-o],0],[[o,.5],270]];
 else if(piece==='edge_junction')ports=[[[-.5,-o],0],[[.5,-o],180],[[0,.5],270]];
 else if(piece==='junction')ports=[[[-.5,0],0],[[.5,0],180],[[0,.5],270]];
 else if(piece==='cross')ports=[[[-.5,0],0],[[.5,0],180],[[0,-.5],90],[[0,.5],270]];
 else if(piece==='end')ports=[[[.5,0],180]];
 else if(/^(wall|breach|window|door_(open|closed)|gate_(open|closed))$/.test(piece))ports=[[[-.5,0],0],[[.5,0],180]];
 else return [];
 return ports.map(([point,direction],index)=>{
  const [x,y]=turn(point,rotation);
  return {item,index,x:(item.x||0)+x+base[0],y:(item.y||0)+y+base[1],
    point:[x+base[0],y+base[1]],rotation:(direction+rotation)%360};
 });
}
function portIndex(terrain,geometry){
 const index=new Map();
 for(const item of terrain)for(const p of connectionPorts(item,geometry)){
  const key=`${Math.round(p.x*20)},${Math.round(p.y*20)}`;
  if(!index.has(key))index.set(key,[]);index.get(key).push(p);
 }
 return index;
}
function connected(port,index){
 const x=Math.round(port.x*20),y=Math.round(port.y*20);
 for(let dx=-1;dx<=1;dx++)for(let dy=-1;dy<=1;dy++)
  if((index.get(`${x+dx},${y+dy}`)||[]).some(p=>p.item!==port.item&&Math.hypot(p.x-port.x,p.y-port.y)<.035))return true;
 return false;
}

export function structuralLayout(item,geometry,neighbors=[]){
 // Decorations are already resolved texture sections, never another wall.
 if(item.parent_id)return {offset:item.art_offset||[0,0],connectors:[]};
 const match=matchPiece(item);
 if(!match)return {offset:item.art_offset||[0,0],connectors:[]};
 const [,family,piece]=match,g=geometry[family];if(!g)return {offset:item.art_offset||[0,0],connectors:[]};
 const base=offsetOf(item,g,piece),mirrorY=faceMirror(item);
 const rotation=rotationOf(item);
 if(piece==='breach'){
  const [dx,dy]=g.breach_offset||[0,0];
  const [x,y]=turn([dx,dy*mirrorY],rotation);
  return {offset:[base[0]+x,base[1]+y],connectors:[],mirrorY};
 }
 if(item.destroyed)return {offset:base,connectors:[]};
 if(piece==='end'&&g.cap_mode!=='pillar'){
  const [x,y]=turn(g.end_offset||[.25,0],rotation);
  return {offset:[base[0]+x,base[1]+y],connectors:[],mirrorY};
 }
 const scale=item.art_scale||1.25,o=g.join_offset,half=g.wall_half_thickness||.09;
 const anchor=piece==='edge_junction'?[0,0]:base;
 let serial=0;
 const raw=(point,direction,left,right,cut)=>{
  const [x,y]=turn(point,rotation);
  const beamRotation=(direction+rotation)%360;
  // A rotated T/cross changes where its arms go, not which side of an
  // interior wall carries the painted face. Match the ordinary divider runs.
  const interiorArm=['junction','cross'].includes(piece)||(piece==='edge_junction'&&direction===90);
  const armMirror=interiorArm?(beamRotation>=180?-1:1):
   ['wall','end'].includes(piece)?mirrorY:((piece==='corner'||piece==='corner_broken')&&base.some(v=>Math.abs(v)>.5)?-1:1);
  return {id:`${item.id}_sleeve_${serial++}`,parent_id:item.id,x:item.x,y:item.y,
   sprite:`structure:${family}_wall`,art_scale:scale,rotation:beamRotation,
   art_offset:[x+anchor[0],y+anchor[1]],
   art_mirror_y:armMirror,
   art_layer:beamRotation%180===0?3:2,
   ...(cut?{art_clip_polygon:matingPolygon(scale,left,right,cut)}:{}),
   art_clip:[0,Math.max(0,(.5-right/scale)*100),0,Math.max(0,(.5+left/scale)*100)]};
 };
 const beam=(point,direction,left=-scale/2,right=scale/2,cut)=>{
  if(g.cap_mode!=='trim')return [raw(point,direction,left,right,cut)];
  // Reuse only the post-free center of the metal texture. Overlapping these
  // center strips fills the span without overlapping the baked terminal posts.
  left=Math.max(-.5,left);right=Math.min(.5,right);
  return [-.3,0,.3].flatMap(shift=>{
   const l=Math.max(-scale*.25,left-shift),r=Math.min(scale*.25,right-shift);
   if(r<=l)return [];
   const [dx,dy]=turn([shift,0],direction);
   return [raw([point[0]+dx,point[1]+dy],direction,l,r,cut?[cut[0],cut[1],cut[2]-cut[0]*shift]:undefined)];
  });
 };
 const caps=()=>{
  if(!g.cap_mode)return [];
  const index=neighbors instanceof Map?neighbors:portIndex(neighbors,geometry);
  return connectionPorts(item,geometry).filter(p=>!connected(p,index)).map(p=>{
   const trim=g.cap_mode==='trim',[dx,dy]=turn([.5,0],p.rotation);
   return {id:`${item.id}_cap_${p.index}`,parent_id:item.id,wall_cap:true,x:item.x,y:item.y,
    sprite:`structure:${family}_${trim?'wall':'pillar'}`,rotation:p.rotation,
    art_mirror_y:trim?1:faceMirror({...item,rotation:p.rotation}),
    art_scale:trim?scale:g.cap_scale||.4,
    art_offset:trim?[p.point[0]+dx,p.point[1]+dy]:p.point,
    ...(trim?{art_clip:[0,72,0,0]}:{})};
  });
 };
 let connectors,hideArt=false;
 if(piece==='junction'&&g.native_junction_rotations?.includes(rotation)){
  const [x,y]=turn(g.native_junction_offset,rotation);
  // The dedicated stone T has the correct faces for this orientation.
  // Its measured bar anchor keeps it on the existing divider centerline.
  return {offset:[base[0]+x,base[1]+y],connectors:caps(),mirrorY:1,layer:3};
 }
 if(piece==='end'){
  // This terminal occupies half a cell even if the generated source is longer.
  connectors=[...beam([0,0],0,0,.5),{id:`${item.id}_terminal_cap`,parent_id:item.id,wall_cap:true,
   x:item.x,y:item.y,sprite:`structure:${family}_pillar`,rotation,art_mirror_y:mirrorY,art_scale:g.cap_scale||.4,art_offset:base}];hideArt=true;
 }else if(piece==='wall'){
  connectors=g.cap_mode==='trim'?beam([0,0],0):[];hideArt=g.cap_mode==='trim';
 }else if(piece==='corner'){
  const miter=g.cap_mode==='trim';
  connectors=[...beam([0,-o],0,-scale/2,o+half,miter?[1,1,o]:undefined),
   ...beam([o,0],90,-o-(miter?half:0),scale/2,miter?[-1,1,o]:undefined)];hideArt=true;
 }else if(piece==='edge_junction'){
  connectors=[...beam([0,-o],0),...beam([0,0],90,-o,scale/2)];hideArt=true;
 }else if(piece==='junction'||piece==='cross'){
  connectors=[...beam([0,0],0),...beam([0,0],90,piece==='cross'?-scale/2:0,scale/2)];hideArt=true;
 }else if(piece==='corner_broken'){
  const [x,y]=turn(g.broken_corner_offset||g.corner_offset||[0,0],rotation);
  return {offset:[base[0]+x,base[1]+y],connectors:[...beam([0,-o],0,-scale/2,-.24),...beam([o,0],90,.24,scale/2),...caps()]};
 }else return {offset:base,connectors:[],mirrorY};
 return {offset:base,connectors:[...connectors,...caps()],mirrorY,...(hideArt?{hideArt:true}:{})};
}

export function structuralConnectors(terrain,geometry){
 const index=portIndex(terrain,geometry);
 return terrain.flatMap(item=>structuralLayout(item,geometry,index).connectors);
}

import {Mesh,MeshGeometry,MeshMaterial} from '@pixi/mesh';
export function updateRibbonVertices(vertices,width,height,time,{y,phase,amplitude,thickness}){
  const count=vertices.length/4;
  for(let i=0;i<count;i++){
    const u=i/(count-1),x=u*(width+160)-80;
    const center=height*y+Math.sin(u*6+time*.32+phase)*amplitude+Math.sin(u*13-time*.21+phase)*amplitude*.3;
    const half=thickness*(.75+.25*Math.sin(u*7-time*.4+phase));
    vertices[i*4]=vertices[i*4+2]=x;vertices[i*4+1]=center-half;vertices[i*4+3]=center+half;
  }
}
export function createEnergyRibbon(texture,width,height,options){
  const count=40,vertices=new Float32Array(count*4),uvs=new Float32Array(count*4),indices=[];
  for(let i=0;i<count;i++){const u=i/(count-1);uvs.set([u,0,u,1],i*4);if(i<count-1){const a=i*2;indices.push(a,a+1,a+2,a+1,a+3,a+2)}}
  updateRibbonVertices(vertices,width,height,0,options);
  const geometry=new MeshGeometry(vertices,uvs,new Uint16Array(indices)),material=new MeshMaterial(texture),mesh=new Mesh(geometry,material);
  mesh.tint=options.tint;mesh.alpha=options.alpha;
  return {mesh,update(time){updateRibbonVertices(vertices,width,height,time,options);geometry.getBuffer('aVertexPosition').update();mesh.alpha=options.alpha*(.85+.15*Math.sin(time*.4+options.phase))},destroy(){mesh.destroy();geometry.destroy();material.destroy()}};
}

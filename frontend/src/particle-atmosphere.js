import {Mesh,MeshGeometry,MeshMaterial} from '@pixi/mesh';

// A strip of light bends around a gravity well, or rises as a flickering flame.
// Geometry moves continuously: these are not drifting illustrations.
export function atmosphereVertices(vertices,width,height,time,{kind,index}){
  const count=vertices.length/4;
  for(let i=0;i<count;i++){
    const u=i/(count-1);let x,y,nx,ny,half;
    if(kind==='gravity'){
      const angle=u*Math.PI*1.65+time*(index?-.055:.07)+index*2;
      const radius=Math.min(width,height)*(.3+index*.09)*(1+.025*Math.sin(time*.6+u*7));
      const cx=width*(index?.92:.08),cy=height*(index?.22:.76);
      x=cx+Math.cos(angle)*radius;y=cy+Math.sin(angle)*radius*.62;
      nx=Math.cos(angle);ny=Math.sin(angle)*.62;half=5+Math.sin(u*Math.PI)*14;
    }else{
      const base=index===0?12:index===1?width-12:width*.72,rise=80+index*16;
      x=base+Math.sin(time*3.4+u*8+index)*u*13+Math.sin(time*5-u*11)*u*5;
      y=height+14-u*rise;nx=1;ny=0;half=(1-u)*24*(1+.24*Math.sin(time*5+u*14+index));
    }
    vertices[i*4]=x-nx*half;vertices[i*4+1]=y-ny*half;
    vertices[i*4+2]=x+nx*half;vertices[i*4+3]=y+ny*half;
  }
}
export function flameStrength(time,index){
  // Short bursts with long rests, staggered by source. No flashing screen wash.
  const phase=(time+index*6+2)%19;
  return phase<5?Math.sin(phase/5*Math.PI)**2*(.68+.12*Math.sin(time*9+index)):0;
}
export function createAtmosphere(texture,width,height,kind,index){
  const vertices=new Float32Array(128),uvs=new Float32Array(128),indices=[];
  for(let i=0;i<32;i++){const u=i/31;uvs.set([u,0,u,1],i*4);if(i<31){const a=i*2;indices.push(a,a+1,a+2,a+1,a+3,a+2)}}
  const geometry=new MeshGeometry(vertices,uvs,new Uint16Array(indices)),material=new MeshMaterial(texture),mesh=new Mesh(geometry,material);
  mesh.tint=kind==='gravity'?(index?0x718bba:0xab7bdb):0xffffff;
  const update=time=>{atmosphereVertices(vertices,width,height,time,{kind,index});geometry.getBuffer('aVertexPosition').update();mesh.alpha=kind==='gravity'?.2+.09*Math.sin(time*.38+index*2):flameStrength(time,index)};
  update(0);
  return {mesh,update,destroy(){mesh.destroy();geometry.destroy();material.destroy()}};
}

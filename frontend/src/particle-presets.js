// Authoring values are pixels / seconds in logical viewport coordinates.
// V3 emitter configurations: no dependency on the legacy visual editor format.
const fade=peak=>({type:'alpha',config:{alpha:{list:[{time:0,value:0},{time:.14,value:peak},{time:.7,value:peak*.75},{time:1,value:0}]}}});
function layer(name,textures,rect,{count=20,life=[9,15],size=[10,20],velocity=[4,14,8,20],sway=12,spin=20,alpha=.4,grow=1,frequency}={}){
  return {name,config:{lifetime:{min:life[0],max:life[1]},frequency:frequency||life[1]/count*.72,maxParticles:count,emitterLifetime:-1,pos:{x:0,y:0},emit:true,autoUpdate:false,behaviors:[
    {type:'spawnShape',config:{type:'rect',data:{x:rect.x,y:rect.y,w:rect.width,h:rect.height}}},
    {type:'textureRandom',config:{textures}},fade(alpha),
    {type:'fortcampWind',config:{size,velocity,sway,spin,grow}},
  ]}};
}
export const PARTICLE_PRESETS=['beast','goblin','undead','arcane','starfall','rain','snow'];
export function createParticlePreset(theme,width,height){
  const field={x:-40,y:-60,width:width+80,height:height+100};
  const leaves=['leaf_oak_gold','leaf_maple_rust','leaf_birch_green','leaf_curled_brown'];
  if(theme==='beast')return [
    layer('distant leaves',leaves,field,{count:22,life:[16,24],size:[10,17],velocity:[5,14,12,22],sway:14,spin:18,alpha:.28}),
    layer('near leaves',leaves,field,{count:16,life:[12,20],size:[21,32],velocity:[10,24,24,42],sway:32,spin:48,alpha:.52}),
    layer('windborne seeds',['grass_seeds','petal_ochre'],field,{count:6,life:[12,18],size:[9,17],velocity:[14,27,6,14],sway:14,spin:15,alpha:.24}),
  ];
  if(theme==='goblin')return [
    layer('green embers',['ember_green'],field,{count:24,life:[5,10],size:[7,15],velocity:[-9,9,-38,-18],sway:8,spin:8,alpha:.5,grow:.3}),
    layer('warm sparks',['ember_orange'],field,{count:8,life:[4,8],size:[5,10],velocity:[-14,14,-48,-24],sway:5,spin:10,alpha:.48,grow:.2}),
    layer('camp smoke',['mist_gray'],{x:-100,y:height*.65,width:width+200,height:height*.4},{count:6,life:[16,24],size:[150,230],velocity:[4,16,-18,-7],sway:14,spin:4,alpha:.08,grow:1.6}),
  ];
  if(theme==='undead')return [
    layer('ash',['ash_flake','ash_cluster'],field,{count:24,life:[12,20],size:[5,12],velocity:[4,15,9,21],sway:12,spin:30,alpha:.34}),
    layer('low mist',['mist_gray','mist_violet'],field,{count:9,life:[18,28],size:[210,350],velocity:[5,12,-3,3],sway:10,spin:3,alpha:.13,grow:1.5}),
  ];
  if(theme==='arcane')return [layer('arcane sparks',['alien_mote'],field,{count:18,life:[7,13],size:[5,11],velocity:[-4,4,-14,-5],sway:10,spin:5,alpha:.26,grow:.5})];
  if(theme==='starfall')return [
    layer('alien sparks',['alien_mote'],field,{count:18,life:[9,16],size:[8,18],velocity:[-8,8,-13,-4],sway:16,spin:8,alpha:.37,grow:.6}),
    layer('alien haze',['alien_ribbon'],field,{count:5,life:[20,30],size:[160,280],velocity:[-5,5,-3,3],sway:8,spin:3,alpha:.11,grow:1.3}),
  ];
  if(theme==='rain')return [layer('rain',['rain_streaks'],field,{count:80,life:[1.2,2.2],size:[5,9],velocity:[-100,-75,380,500],sway:0,spin:0,alpha:.32})];
  if(theme==='snow')return [
    layer('distant snow',['snowflake'],field,{count:32,life:[16,24],size:[3,6],velocity:[3,8,12,22],sway:9,spin:12,alpha:.25}),
    layer('near snow',['snowflake'],field,{count:18,life:[10,18],size:[7,11],velocity:[5,14,25,40],sway:22,spin:25,alpha:.45}),
  ];
  return [];
}

// Movement is independent of sprite rotation. Turning a leaf does not turn its velocity.
export class WindBehavior {
  static type='fortcampWind';
  order=5;
  constructor(config){this.config=config}
  initParticles(first){
    const c=this.config,between=(a,b)=>a+Math.random()*(b-a);
    for(let p=first;p;p=p.next){
      const [vx0,vx1,vy0,vy1]=c.velocity;
      p.config.wind={vx:between(vx0,vx1),vy:between(vy0,vy1),phase:between(0,Math.PI*2),frequency:between(.45,.9),spin:between(-c.spin,c.spin)*Math.PI/180,scale:between(...c.size)/Math.max(1,p.texture.width)};
      p.rotation=c.spin?between(0,Math.PI*2):0;
      p.scale.set(p.config.wind.scale);
    }
  }
  updateParticle(p,dt){
    const w=p.config.wind,c=this.config,now=p.age*w.frequency+w.phase,previous=(p.age-dt)*w.frequency+w.phase;
    p.x+=w.vx*dt+c.sway*(Math.sin(now)-Math.sin(previous));p.y+=w.vy*dt;
    p.rotation+=w.spin*dt;p.scale.set(w.scale*(1+(c.grow-1)*p.agePercent));
  }
}

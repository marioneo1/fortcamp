// Authoring values are pixels / seconds in logical viewport coordinates.
// V3 emitter configurations: no dependency on the legacy visual editor format.
const fade=peak=>({type:'alpha',config:{alpha:{list:[{time:0,value:0},{time:.14,value:peak},{time:.7,value:peak*.75},{time:1,value:0}]}}});
function layer(name,textures,rect,{count=20,life=[9,15],size=[10,20],velocity=[4,14,8,20],sway=12,spin=20,alpha=.4,grow=1,frequency,tint='ffffff',blend='normal'}={}){
  return {name,config:{lifetime:{min:life[0],max:life[1]},frequency:frequency||life[1]/count*.72,maxParticles:count,emitterLifetime:-1,pos:{x:0,y:0},emit:true,autoUpdate:false,behaviors:[
    {type:'spawnShape',config:{type:'rect',data:{x:rect.x,y:rect.y,w:rect.width,h:rect.height}}},
    {type:'textureRandom',config:{textures}},fade(alpha),{type:'colorStatic',config:{color:tint}},{type:'blendMode',config:{blendMode:blend}},
    {type:'fortcampWind',config:{size,velocity,sway,spin,grow}},
  ]}};
}
export const PARTICLE_PRESETS=['beast','goblin','undead','arcane','starfall','rain','snow'];
export function createParticlePreset(theme,width,height){
  const field={x:-40,y:-60,width:width+80,height:height+100};
  const leaves=['leaf_oak_gold','leaf_maple_rust','leaf_birch_green','leaf_curled_brown'];
  const smoke=['fx:smoke0','fx:smoke1','fx:smoke2','fx:smoke3'];
  if(theme==='beast')return [
    layer('distant leaves',leaves,field,{count:26,life:[16,24],size:[13,20],velocity:[5,14,12,22],sway:14,spin:18,alpha:.4}),
    layer('near leaves',leaves,field,{count:22,life:[12,20],size:[22,36],velocity:[10,24,24,42],sway:32,spin:48,alpha:.72}),
    layer('windborne seeds',['grass_seeds','petal_ochre'],field,{count:10,life:[12,18],size:[10,19],velocity:[14,27,6,14],sway:14,spin:15,alpha:.36}),
  ];
  if(theme==='goblin')return [
    layer('green embers',['ember_green'],field,{count:36,life:[5,10],size:[10,20],velocity:[-9,9,-38,-18],sway:8,spin:8,alpha:.7,grow:.3}),
    layer('warm sparks',['ember_orange'],field,{count:14,life:[4,8],size:[7,15],velocity:[-14,14,-48,-24],sway:5,spin:10,alpha:.65,grow:.2}),
    layer('camp smoke',smoke,field,{count:12,life:[16,24],size:[230,390],velocity:[8,20,-16,-5],sway:18,spin:5,alpha:.3,grow:1.7,tint:'b5c394'}),
  ];
  if(theme==='undead')return [
    layer('ash',['ash_flake','ash_cluster'],field,{count:32,life:[12,20],size:[7,15],velocity:[4,15,9,21],sway:12,spin:30,alpha:.48}),
    layer('low mist',smoke,field,{count:14,life:[18,28],size:[300,480],velocity:[8,18,-3,3],sway:18,spin:4,alpha:.4,grow:1.6,tint:'c1b6d6'}),
  ];
  if(theme==='arcane')return [
    layer('blue fireflies',['fx:mote'],field,{count:32,life:[7,13],size:[8,17],velocity:[12,28,-12,8],sway:38,spin:0,alpha:.75,grow:.45,tint:'82ceff',blend:'add'}),
    layer('violet glimmers',['fx:beam'],field,{count:16,life:[4,9],size:[22,48],velocity:[-24,-10,-9,9],sway:22,spin:18,alpha:.65,grow:.5,tint:'b89cff',blend:'add'}),
    layer('arcane vapor',smoke,field,{count:10,life:[14,23],size:[250,430],velocity:[8,16,-3,5],sway:20,spin:5,alpha:.3,grow:1.5,tint:'8c9fe0'}),
  ];
  if(theme==='starfall')return [
    layer('alien sparks',['alien_mote'],field,{count:30,life:[9,16],size:[12,25],velocity:[-8,8,-13,-4],sway:24,spin:8,alpha:.62,grow:.6}),
    layer('alien haze',smoke,field,{count:10,life:[20,30],size:[280,470],velocity:[-9,9,-3,3],sway:18,spin:4,alpha:.35,grow:1.5,tint:'b48ddc'}),
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

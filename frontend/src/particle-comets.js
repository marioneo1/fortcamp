import {Sprite} from '@pixi/sprite';
export function createShootingStar(texture,width,height,random=Math.random,{manual=false}={}){
  const head=new Sprite(texture('fx:mote')),trail=new Sprite(texture('fx:comet'));
  head.anchor.set(.5);trail.anchor.set(.5);head.tint=0xe8f1ff;trail.tint=0xbc9bff;head.width=head.height=16;head.visible=trail.visible=false;
  let remaining=manual?Infinity:2.5+random()*2,flight=null,flights=0;
  function launch(){
    if(flight)return false;
    const speed=Math.max(1000,width*.95)*(manual?.8+random()*.4:1),x=manual?width*(.55+random()*.55):width+60;
    flight={x,y:height*(manual?-.1+random()*.42:.05+random()*.18),vx:-speed,vy:manual?speed*(.38+random()*.18):Math.max(380,height*.52),age:0,life:(x+60)/speed};
    const size=manual?7+random()*7:16;head.width=head.height=size;flight.thickness=manual?4+random()*5:12;flights++;return true;
  }
  function update(dt){
    if(!flight){remaining-=dt;if(remaining>0)return;
      launch();
    }
    const f=flight;f.age+=dt;f.x+=f.vx*dt;f.y+=f.vy*dt;
    const speed=Math.hypot(f.vx,f.vy),length=Math.min(220,speed*Math.min(.13,f.age));
    head.position.set(f.x,f.y);head.visible=f.age<f.life;head.alpha=Math.min(1,f.age/.035)*.9;
    trail.position.set(f.x-f.vx/speed*length*.5,f.y-f.vy/speed*length*.5);trail.rotation=Math.atan2(f.vy,f.vx);
    trail.width=Math.max(1,length);trail.height=f.thickness;trail.visible=true;trail.alpha=f.age<f.life?.7:Math.max(0,1-(f.age-f.life)/.16)*.7;
    if(f.age>=f.life+.16){flight=null;head.visible=trail.visible=false;remaining=manual?Infinity:9+random()*9}
  }
  return {head,trail,update,launch,diagnostics:()=>({flights,inFlight:!!flight}),destroy(){head.destroy();trail.destroy()}};
}

export function createMeteorShower(texture,width,height,random=Math.random){
  const stars=Array.from({length:4},()=>createShootingStar(texture,width,height,random,{manual:true}));
  let wait=1.8,queued=0,bursts=0;
  return {
    sprites:stars.flatMap(s=>[s.trail,s.head]),
    update(dt){
      stars.forEach(s=>s.update(dt));wait-=dt;if(wait>0)return;
      if(!queued){queued=6+Math.floor(random()*5);bursts++}
      const free=stars.find(s=>!s.diagnostics().inFlight);
      if(!free){wait=.1;return}
      free.launch();queued--;
      wait=queued?.4+random()*.65:9+random()*7;
    },
    diagnostics(){const flights=stars.reduce((n,s)=>n+s.diagnostics().flights,0),active=stars.filter(s=>s.diagnostics().inFlight).length;return {flights,inFlight:active>0,active,bursts,queued}},
    destroy(){stars.forEach(s=>s.destroy())},
  };
}

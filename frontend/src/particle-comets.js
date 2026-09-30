import {Sprite} from '@pixi/sprite';
export function createShootingStar(texture,width,height,random=Math.random){
  const head=new Sprite(texture('fx:mote')),trail=new Sprite(texture('fx:comet'));
  head.anchor.set(.5);trail.anchor.set(.5);head.tint=0xe8f1ff;trail.tint=0xbc9bff;head.width=head.height=16;head.visible=trail.visible=false;
  let remaining=2.5+random()*2,flight=null,flights=0;
  function update(dt){
    if(!flight){remaining-=dt;if(remaining>0)return;
      const speed=Math.max(1000,width*.95);flight={x:width+60,y:height*(.05+random()*.18),vx:-speed,vy:Math.max(380,height*.52),age:0,life:(width+120)/speed};flights++;
    }
    const f=flight;f.age+=dt;f.x+=f.vx*dt;f.y+=f.vy*dt;
    const speed=Math.hypot(f.vx,f.vy),length=Math.min(220,speed*Math.min(.13,f.age));
    head.position.set(f.x,f.y);head.visible=f.age<f.life;head.alpha=Math.min(1,f.age/.035)*.9;
    trail.position.set(f.x-f.vx/speed*length*.5,f.y-f.vy/speed*length*.5);trail.rotation=Math.atan2(f.vy,f.vx);
    trail.width=Math.max(1,length);trail.height=12;trail.visible=true;trail.alpha=f.age<f.life?.7:Math.max(0,1-(f.age-f.life)/.16)*.7;
    if(f.age>=f.life+.16){flight=null;head.visible=trail.visible=false;remaining=9+random()*9}
  }
  return {head,trail,update,diagnostics:()=>({flights,inFlight:!!flight}),destroy(){head.destroy();trail.destroy()}};
}

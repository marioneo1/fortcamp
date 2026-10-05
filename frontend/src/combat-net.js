import {COMBAT_MOTION} from './combat-animation.js';

// Lightweight painted sprite flight. No new renderer or gameplay simulation.
export function emitNetCast(field,event,battle,delay=0){
  const cw=field.clientWidth/battle.width,ch=field.clientHeight/battle.height;
  const from={x:(event.from.x+.5)*cw,y:(event.from.y+.5)*ch},to={x:(event.to.x+.5)*cw,y:(event.to.y+.5)*ch};
  const reduced=window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  const sprite=(name,frames,duration,offset)=>{
    const node=document.createElement('i');node.className='combat-net-sprite';node.dataset.liveOverlay='';
    node.style.cssText=`position:absolute;pointer-events:none;z-index:98;left:0;top:0;width:${cw*1.3}px;height:${ch*1.3}px;background:center/contain no-repeat url('/assets/capture-net-v1/${name}.png')`;
    field.append(node);
    const a=node.animate(frames,{duration,delay:delay+offset,fill:'both',easing:'linear'});
    a.onfinish=()=>node.remove();a.oncancel=()=>node.remove();
  };
  const pose=(p,scale,angle=0)=>`translate(${p.x}px,${p.y}px) translate(-50%,-50%) rotate(${angle}deg) scale(${scale})`;
  if(reduced){sprite(event.hit?'cinched':'spread',[{transform:pose(to,.85),opacity:.7},{transform:pose(to,.85),opacity:0}],240,COMBAT_MOTION.netContact);return}
  const mid={x:from.x+(to.x-from.x)*.5,y:from.y+(to.y-from.y)*.5-ch*.16};
  const near={x:from.x+(to.x-from.x)*.78,y:from.y+(to.y-from.y)*.78-ch*.09};
  sprite('folded',[{transform:pose(from,.2,-35),opacity:0},{transform:pose(from,.2,-35),opacity:1,offset:.1},{transform:pose(mid,.5,-10),opacity:0}],170,20);
  sprite('opening',[{transform:pose(from,.25,-30),opacity:0},{transform:pose(mid,.75,0),opacity:.9,offset:.6},{transform:pose(near,1,12),opacity:0}],240,60);
  sprite('spread',[{transform:pose(mid,.65,-8),opacity:0},{transform:pose(to,1.12,18),opacity:.85,offset:event.hit ? .68 : 170/350},{transform:pose(to,event.hit ? .85 : 1.05,25),opacity:0}],event.hit?250:350,150);
  if(event.hit)sprite('cinched',[{transform:pose(to,1.05,18),opacity:0},{transform:pose(to,.8,9),opacity:.9,offset:.35},{transform:pose(to,.8,9),opacity:0}],240,COMBAT_MOTION.netContact);
}

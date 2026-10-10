export const COMBAT_MOTION={contact:185,melee:400,partingSkid:360,recoil:170,netContact:320,netDuration:560,collisionMove:420,collisionContact:220,collisionHold:70,collisionRecoil:240,collisionRest:100,stationaryBounce:320,stationaryContact:100,collapse:440};
// A single approach/contact/retreat pose: no neutral return between slash and skid.
export function partingCutFrames(from,target,destination,unit,cw,ch,scale=1){
  const duration=COMBAT_MOTION.contact+COMBAT_MOTION.partingSkid;
  const x=(from.x-unit.x)*cw,y=(from.y-unit.y)*ch;
  const dx=Math.sign(target.x-from.x)*cw*.44,dy=Math.sign(target.y-from.y)*ch*.44;
  const endX=(destination.x-unit.x)*cw,endY=(destination.y-unit.y)*ch;
  const side=dx<0?-1:1;
  const pose=(px,py,s,angle,offset,easing='linear')=>({transform:`translate(${px}px,${py}px) scale(${scale*s}) rotate(${angle}deg)`,offset,easing});
  return [pose(x,y,1,0,0),pose(x-dx*.08,y-dy*.08,.99,-8*side,.16),
    pose(x+dx,y+dy,1.035,10*side,COMBAT_MOTION.contact/duration,'cubic-bezier(.12,.65,.25,1)'),
    pose(endX+(x-endX)*.12,endY+(y-endY)*.12,.97,-7*side,(COMBAT_MOTION.contact+210)/duration,'ease-out'),
    pose(endX,endY,.99,-3*side,.92,'ease-out'),pose(endX,endY,1,0,1)];
}
export function skidBackFrames(points,unit,cw,ch,scale=1){
  const from=points[0],to=points.at(-1),dx=(to.x-from.x)*cw,dy=(to.y-from.y)*ch;
  const x=(from.x-unit.x)*cw,y=(from.y-unit.y)*ch;
  const pose=(p,s,angle,offset,easing='linear')=>({transform:`translate(${x+dx*p}px,${y+dy*p}px) scale(${scale*s}) rotate(${angle}deg)`,offset,easing});
  return [pose(0,1,0,0,'cubic-bezier(.12,.65,.25,1)'),pose(.88,.97,-7,.6,'ease-out'),pose(1,.99,-3,.9),pose(1,1,0,1)];
}
export function meleeFrames(dx,dy,scale=1){
  return [{transform:`translate(0,0) scale(${scale})`,offset:0},
    {transform:`translate(${-dx*.12}px,${-dy*.12}px) scale(${scale*.98})`,offset:.22},
    {transform:`translate(${dx}px,${dy}px) scale(${scale*1.06})`,offset:COMBAT_MOTION.contact/COMBAT_MOTION.melee},
    {transform:`translate(${dx*.92}px,${dy*.92}px) scale(${scale*1.04})`,offset:(COMBAT_MOTION.contact+25)/COMBAT_MOTION.melee},
    {transform:`translate(0,0) scale(${scale})`,offset:1}];
}
export function recoilFrames(dx,dy,scale=1){
  return [{transform:`translate(0px,0px) scale(${scale})`,filter:'brightness(1)',offset:0},
    {transform:`translate(${dx*.12}px,${dy*.12}px) scale(${scale*.95})`,filter:'brightness(1.65)',offset:.08},
    {transform:`translate(${dx}px,${dy}px) scale(${scale*.94})`,filter:'brightness(1.15)',offset:.25},
    {transform:`translate(${-dx*.22}px,${-dy*.22}px) scale(${scale})`,filter:'brightness(1)',offset:.65},
    {transform:`translate(0,0) scale(${scale})`,filter:'brightness(1)',offset:1}];
}
export function collisionFrames(points,unit,toward,cw,ch,scale=1){
  const first=points[0]||unit,last=points.at(-1)||unit;
  const dx=Math.sign(toward.x-last.x)*cw*.28,dy=Math.sign(toward.y-last.y)*ch*.28;
  const moving=points.length>1,contact=(moving?COMBAT_MOTION.collisionContact:COMBAT_MOTION.stationaryContact)/(moving?COMBAT_MOTION.collisionMove:COMBAT_MOTION.stationaryBounce);
  const hold=contact+COMBAT_MOTION.collisionHold/(moving?COMBAT_MOTION.collisionMove:COMBAT_MOTION.stationaryBounce);
  return [{transform:`translate(${(first.x-unit.x)*cw}px,${(first.y-unit.y)*ch}px) scale(${scale})`,filter:'brightness(1)',offset:0},
    {transform:`translate(${(last.x-unit.x)*cw+dx}px,${(last.y-unit.y)*ch+dy}px) scale(${scale*.88})`,filter:'brightness(1.65)',offset:contact},
    {transform:`translate(${(last.x-unit.x)*cw+dx}px,${(last.y-unit.y)*ch+dy}px) scale(${scale*.88})`,filter:'brightness(1.4)',offset:hold},
    {transform:`translate(${(last.x-unit.x)*cw-dx*.4}px,${(last.y-unit.y)*ch-dy*.4}px) scale(${scale})`,filter:'brightness(1)',offset:Math.min(.93,hold+.14)},
    {transform:`translate(${(last.x-unit.x)*cw}px,${(last.y-unit.y)*ch}px) scale(${scale})`,filter:'brightness(1)',offset:1}];
}
// All families keep the same 185 ms contact marker and neutral final pose.
// These are token poses, never extra attacks or gameplay displacement.
export function weaponAttackFrames(style,dx,dy,scale=1){
  if(!style||style==='blunt')return meleeFrames(dx,dy,scale);
  const p={x:-dy,y:dx},side=dx<0?-1:1,contact=COMBAT_MOTION.contact/COMBAT_MOTION.melee;
  const pose=(x,y,s,angle,offset)=>({transform:`translate(${x}px,${y}px) scale(${scale*s}) rotate(${angle}deg)`,offset});
  const neutral=pose(0,0,1,0,0),end=pose(0,0,1,0,1);
  if(style==='slash')return [neutral,pose(-dx*.08+p.x*.25,-dy*.08+p.y*.25,.99,-12*side,.22),pose(dx*.83,dy*.83,1.04,9*side,contact),pose(dx*.5-p.x*.18,dy*.5-p.y*.18,1.01,3*side,.65),end];
  if(style==='hack')return [neutral,pose(-dx*.2,-dy*.2-6,1.02,-9*side,.24),pose(dx*.94,dy*.94+2,1.07,8*side,contact),pose(dx*.7,dy*.7,1.02,3*side,.65),end];
  if(style==='crush')return [neutral,pose(-dx*.24,-dy*.24-5,1.04,-5*side,.28),pose(dx,dy+2,.99,4*side,contact),pose(dx*.88,dy*.88,.97,2*side,.62),end];
  if(style==='fist')return [neutral,pose(-dx*.05,-dy*.05,.99,-3*side,.33),pose(dx*.8,dy*.8,1.035,3*side,contact),pose(dx*.13,dy*.13,1,0,.62),end];
  if(style==='stab')return [neutral,pose(-dx*.16,-dy*.16,.98,0,.31),pose(dx*1.03,dy*1.03,1.03,0,contact),pose(dx*.45,dy*.45,1,0,.62),end];
  return meleeFrames(dx,dy,scale);
}
export function weaponHitFrames(style,dx,dy,scale=1){
  if(!style||style==='blunt')return recoilFrames(dx,dy,scale);
  const side=dx<0?-1:1;
  const pose=(x,y,s,angle,offset,light=1)=>({transform:`translate(${x}px,${y}px) scale(${scale*s}) rotate(${angle}deg)`,filter:`brightness(${light})`,offset});
  const end=pose(0,0,1,0,1),start=pose(0,0,1,0,0);
  if(style==='crush')return [start,pose(0,3,.86,0,.18,1.6),pose(-3,2,.94,-3,.4,1.15),pose(2,0,1,2,.7),end];
  const weight=style==='hack'?.7:style==='slash'?.3:style==='fist'?.5:.4;
  const twist=style==='slash'?10:style==='hack'?6:2;
  return [start,pose(dx*weight,dy*weight,.96,twist*side,.22,1.6),pose(-dx*.1,-dy*.1,1,-twist*side*.25,.65),end];
}
export function collisionRecipientFrames(dx,dy,scale=1){
 const frames=recoilFrames(dx,dy,scale);
 return [frames[0],{...frames[1],offset:.08},{...frames[2],offset:.2},
  {...frames[2],offset:.48},{...frames[3],offset:.78},frames[4]];
}
export function collapsePlacement(living,body){
  return {x:body.x+body.width/2-living.x-living.width/2,y:body.y+body.height/2-living.y-living.height/2,
    scale:body.width/living.width};
}
export function collapseFrames(knockout=false,placement={x:0,y:17,scale:.82}){
  const translate=`${placement.x}px ${placement.y}px`,rotation=knockout?'-9deg':'-18deg';
  return [{translate:'0 0',rotate:'0deg',scale:'1',opacity:1,filter:'brightness(1)',offset:0},
    {translate:'0 3px',rotate:knockout?'5deg':'-8deg',scale:'.97',opacity:1,filter:'saturate(.65)',offset:.25},
    {translate,rotate:rotation,scale:String(placement.scale),opacity:.85,filter:'saturate(.2) brightness(.7)',offset:.7},
    {translate,rotate:rotation,scale:String(placement.scale),opacity:0,filter:'saturate(0) brightness(.55)',offset:1}];
}

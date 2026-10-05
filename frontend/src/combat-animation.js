export const COMBAT_MOTION={contact:185,melee:400,recoil:170,collisionMove:420,collisionContact:220,stationaryBounce:320,stationaryContact:100,collapse:440};
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
  return [{transform:`translate(${(first.x-unit.x)*cw}px,${(first.y-unit.y)*ch}px) scale(${scale})`,filter:'brightness(1)',offset:0},
    {transform:`translate(${(last.x-unit.x)*cw+dx}px,${(last.y-unit.y)*ch+dy}px) scale(${scale*.88})`,filter:'brightness(1.65)',offset:contact},
    {transform:`translate(${(last.x-unit.x)*cw-dx*.4}px,${(last.y-unit.y)*ch-dy*.4}px) scale(${scale})`,filter:'brightness(1)',offset:Math.min(.93,contact+.17)},
    {transform:`translate(${(last.x-unit.x)*cw}px,${(last.y-unit.y)*ch}px) scale(${scale})`,filter:'brightness(1)',offset:1}];
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

export const COMBAT_MOTION={contact:185,melee:400,recoil:170,collisionMove:320,collisionContact:220,stationaryBounce:220,stationaryContact:80,collapse:440};
export function meleeFrames(dx,dy,scale=1){
  return [{transform:`translate(0,0) scale(${scale})`,offset:0},
    {transform:`translate(${-dx*.12}px,${-dy*.12}px) scale(${scale*.98})`,offset:.22},
    {transform:`translate(${dx}px,${dy}px) scale(${scale*1.06})`,offset:COMBAT_MOTION.contact/COMBAT_MOTION.melee},
    {transform:`translate(${dx*.92}px,${dy*.92}px) scale(${scale*1.04})`,offset:(COMBAT_MOTION.contact+25)/COMBAT_MOTION.melee},
    {transform:`translate(0,0) scale(${scale})`,offset:1}];
}
export function recoilFrames(dx,dy,scale=1){
  return [{transform:`translate(${dx*.12}px,${dy*.12}px) scale(${scale*.95})`,filter:'brightness(1.65)',offset:0},
    {transform:`translate(${dx}px,${dy}px) scale(${scale*.94})`,filter:'brightness(1.15)',offset:.25},
    {transform:`translate(${-dx*.22}px,${-dy*.22}px) scale(${scale})`,filter:'brightness(1)',offset:.65},
    {transform:`translate(0,0) scale(${scale})`,filter:'brightness(1)',offset:1}];
}
export function collisionFrames(points,unit,toward,cw,ch,scale=1){
  const first=points[0]||unit,last=points.at(-1)||unit;
  const dx=Math.sign(toward.x-last.x)*cw*.18,dy=Math.sign(toward.y-last.y)*ch*.18;
  const moving=points.length>1,contact=(moving?COMBAT_MOTION.collisionContact:COMBAT_MOTION.stationaryContact)/(moving?COMBAT_MOTION.collisionMove:COMBAT_MOTION.stationaryBounce);
  return [{transform:`translate(${(first.x-unit.x)*cw}px,${(first.y-unit.y)*ch}px) scale(${scale})`,filter:'brightness(1)',offset:0},
    {transform:`translate(${(last.x-unit.x)*cw+dx}px,${(last.y-unit.y)*ch+dy}px) scale(${scale*.93})`,filter:'brightness(1.65)',offset:contact},
    {transform:`translate(${(last.x-unit.x)*cw-dx*.18}px,${(last.y-unit.y)*ch-dy*.18}px) scale(${scale})`,filter:'brightness(1)',offset:Math.min(.93,contact+.17)},
    {transform:`translate(${(last.x-unit.x)*cw}px,${(last.y-unit.y)*ch}px) scale(${scale})`,filter:'brightness(1)',offset:1}];
}
export function collapseFrames(knockout=false){
  return [{translate:'0 0',rotate:'0deg',scale:'1',opacity:1,filter:'brightness(1)',offset:0},
    {translate:'0 3px',rotate:knockout?'5deg':'-8deg',scale:'.97',opacity:1,filter:'saturate(.65)',offset:.25},
    {translate:'0 13px',rotate:knockout?'12deg':'-18deg',scale:'.88',opacity:.8,filter:'saturate(.2) brightness(.7)',offset:.65},
    {translate:'0 17px',rotate:knockout?'12deg':'-18deg',scale:'.82',opacity:0,filter:'saturate(0) brightness(.55)',offset:1}];
}

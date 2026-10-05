import {COMBAT_MOTION} from './combat-animation.js';
// Shared contact markers for sound, visible contact, recoil and feedback.
export function movementDuration(event){return event.preview_settle?Math.max(80,Math.min(350,event.duration||220)):event.leap?420:event.forced?(event.collision?COMBAT_MOTION.collisionMove:220):Math.max(220,Math.min(850,Math.max(1,(event.points||[]).length-1)*155))}
export function impactTimeline(events){
  // Defeat facts can precede their lethal hit's displacement in server order.
  // Resolve the body's push/rebound first, then collapse at its final cell.
  events=events.slice();
  for(const defeat of events.filter(e=>['death_burst','knockout'].includes(e.type))){
    const at=events.indexOf(defeat);
    const end=events.findLastIndex(e=>e.attack_packet!=null&&e.attack_packet===defeat.attack_packet&&
      (e.type==='movement'&&e.forced||e.type==='collision_recoil'));
    if(end>at){events.splice(at,1);events.splice(end,0,defeat)}
  }
  let cursor=0;const packets=new Map();
  const collisions=new Map(events.filter(e=>e.type==='collision_recoil').map(e=>[`${e.attack_packet}:${e.unit_id}`,e]));
  return events.map(event=>{
    if(event.type==='movement'&&event.forced)event={...event,collision:collisions.get(`${event.attack_packet}:${event.unit_id}`)};
    const key=event.attack_packet;
    let packet=packets.get(key),start=cursor,duration=0;
    if(!packet&&event.impact_origin_packet!=null){
      const origin=packets.get(event.impact_origin_packet);
      if(origin){const impact=origin.impact+(event.impact_offset||0);packet={start:impact,impact,land:impact,recovery:impact+COMBAT_MOTION.recoil};packets.set(key,packet)}
    }
    const attack=event.type==='melee_attack'||event.attack_event||event.type==='magic_projectile'||event.type==='chain_attack'||event.type==='ground_impact';
    if(key!=null&&attack){
      if(!packet){const impact=cursor+(event.type==='ground_impact'?0:event.type==='melee_attack'?COMBAT_MOTION.contact:220);packet={start:cursor,impact,land:impact,recovery:impact+COMBAT_MOTION.recoil};packets.set(key,packet)}
      start=packet.start;
    }else if(packet){start=event.before_contact?packet.start:event.after_displacement?packet.land:packet.impact}
    if(event.type==='movement'){
      duration=movementDuration(event);
      if(event.forced&&packet){start=packet.impact;packet.land=start+(event.collision?COMBAT_MOTION.collisionContact:duration);packet.recovery=start+duration}
      cursor=Math.max(cursor,start+duration+70);
    }else if(event.type==='ground_impact'){
      duration=650;cursor=Math.max(cursor,start+duration);
    }else if(event.type==='chain_attack'){
      duration=400;cursor=Math.max(cursor,start+duration);
    }else if(event.type==='melee_attack'){
      duration=490;cursor=Math.max(cursor,start+duration);
    }else if(event.type==='sound'){
      if(packet&&!event.attack_event)start=event.after_displacement?packet.land:packet.start;
      duration=event.duration||0;cursor=Math.max(cursor,start+duration);
    }else if(event.type==='magic_projectile'){
      duration=250;cursor=Math.max(cursor,start+duration);
    }else if(event.type==='collision_recoil'){
      const moved=events.some(e=>e.type==='movement'&&e.forced&&e.unit_id===event.unit_id&&e.attack_packet===key);
      if(packet&&!moved){packet.land=packet.impact+COMBAT_MOTION.stationaryContact;packet.recovery=packet.impact+COMBAT_MOTION.stationaryBounce;start=packet.land}
      duration=COMBAT_MOTION.recoil;cursor=Math.max(cursor,start+duration+50);
    }else if(event.type==='death_burst'||event.type==='knockout'){
      if(packet)start=packet.recovery;
      duration=COMBAT_MOTION.collapse;cursor=Math.max(cursor,start+duration+60);
    }else if(event.type==='combat_feedback'){
      // Text can linger while the next unit acts; it does not hold up the turn.
      duration=900;if(!packet)cursor+=100;
    }
    return {event,start,duration};
  });
}

export const feedbackStyles={
  physical:{label:'Hit',icon:'✦',color:'#fff0cd'},
  magic:{label:'Magic',icon:'✧',color:'#c5b3ff'},
  fire:{label:'Fire',icon:'♨',color:'#ffb466'},burn:{label:'Burn',icon:'♨',color:'#ffad58'},
  poison:{label:'Poison',icon:'☠',color:'#bbed82'},bleed:{label:'Bleed',icon:'◆',color:'#ff909c'},
  collision:{label:'Collision',icon:'✷',color:'#ffd58a'},fall:{label:'Fall',icon:'↓',color:'#ffd58a'},
  thorns:{label:'Thorns',icon:'✣',color:'#bee798'},ice:{label:'Ice',icon:'❄',color:'#a2e5ff'},
  holy:{label:'Holy',icon:'✧',color:'#fff0a8'},lightning:{label:'Lightning',icon:'ϟ',color:'#dac4ff'},
  heal:{label:'Heal',icon:'+',color:'#9beeb9'},barrier:{label:'Barrier',icon:'◇',color:'#b5dfff'},
  guard:{label:'Guard',icon:'◇',color:'#dfc788'},cleanse:{label:'Cleansed',icon:'+',color:'#9beeb9'},
  form:{label:'Form changed',icon:'◆',color:'#9beeb9'},deploy:{label:'Deployed',icon:'◆',color:'#a8ded8'},
  intercept:{label:'Intercept',icon:'◇',color:'#b5dfff'},counter:{label:'Counter',icon:'↶',color:'#ffe6b5'},resisted:{label:'Resisted',icon:'◆',color:'#dccfae'},
  miss:{label:'Miss',icon:'↗',color:'#ded9cb'},captured:{label:'Subdued',icon:'◇',color:'#d5c6ff'},
  status:{label:'Status',icon:'•',color:'#dfcbff'},
};
export function feedbackText(event,definitions={}){
  const style=feedbackStyles[event.kind]||feedbackStyles.physical;
  if(event.kind==='status')return {...style,...(event.status_id==='stun'?{color:'#f2ce72'}:{}),label:definitions[event.status_id]?.name||event.status_id,icon:definitions[event.status_id]?.icon||style.icon,value:''};
  return {...style,value:event.amount?`${['heal','barrier'].includes(event.kind)?'+':'−'}${event.amount}`:event.absorbed?'Blocked':''};
}
export function protectionMarkup(unit){
  if(unit.condition&&unit.condition!=='active')return '';
  const barrier=(unit.statuses||[]).find(s=>s.id==='barrier'&&s.amount>0);
  return `${barrier?`<span class="unit-barrier-halo" aria-hidden="true"></span><span class="unit-barrier-front" aria-hidden="true"></span><span class="unit-barrier-capacity" title="Barrier: absorbs ${Number(barrier.amount)} damage">◇ ${Number(barrier.amount)}</span>`:''}${unit.guarding?'<span class="unit-guard-halo" aria-hidden="true"></span>':''}`;
}
export function impactArtwork(event){
  if(['intercept','counter','resisted'].includes(event.kind))return [];
  if(event.absorbed)return [event.barrier_broken?'barrier_break':'barrier_hit'];
  if(event.kind==='barrier')return ['barrier_shell'];
  if(['heal','cleanse','form'].includes(event.kind))return ['restoration_wisp'];
  if(['guard','deploy'].includes(event.kind))return ['magic_hit'];
  if(event.kind==='status'&&event.status_id==='stun')return [];
  if(event.kind==='status')return ['bind','mute','slow','hobbled','stun','freeze'].includes(event.status_id)?['binding_tether']:event.status_id==='burn'?['flame_lick']:event.status_id==='poison'?['poison_cloud']:['magic_hit'];
  if(['burn','fire'].includes(event.kind))return ['flame_lick'];
  if(event.kind==='poison')return ['poison_cloud'];
  if(['magic','holy','ice','lightning'].includes(event.kind))return ['magic_hit'];
  return event.kind==='miss'?[]:['physical_hit'];
}
export function createImpactFeedback(){
  let field,layer,epoch=0;const timers=new Set();
  function clear(){epoch++;for(const timer of timers)clearTimeout(timer);timers.clear();field?.querySelectorAll('.combat-float,.combat-impact-ring,.combat-impact-particle,.painted-hit-sprite').forEach(n=>n.remove())}
  function mount(next){
    if(field!==next){clear();field=next}
    if(field&&!layer?.isConnected){layer=document.createElement('div');layer.className='combat-feedback-layer';layer.setAttribute('aria-hidden','true');layer.setAttribute('data-live-overlay','');field.append(layer)}
  }
  function emit(event,battle,delay=0){
    const generation=epoch;
    const timer=setTimeout(()=>{
      timers.delete(timer);if(generation!==epoch||!field?.isConnected||field.closest('.hidden')||document.hidden)return;
      const style=feedbackText(event,battle.status_definitions),reduced=window.matchMedia('(prefers-reduced-motion: reduce)').matches;
      const x=(event.x+.5)/battle.width*100,y=(event.y+.5)/battle.height*100;
      const node=document.createElement('span');node.className=`combat-float kind-${event.kind}`;
      node.style.cssText=`left:${x}%;top:${y}%;--impact-color:${style.color}`;
      const value=document.createElement('b');value.textContent=style.value;
      const label=document.createElement('small');label.textContent=`${style.icon} ${style.label}`;
      node.append(value,label);
      if(event.absorbed){const shield=document.createElement('em');shield.textContent=`◇ ${event.absorbed} absorbed`;node.append(shield)}
      // Alternate overlapping labels around the same tile, without covering the face.
      const tile=`${event.x},${event.y}`;node.dataset.impactTile=tile;
      const siblings=[...field.querySelectorAll('.combat-float')].filter(n=>n.dataset.impactTile===tile);
      const spread=field.clientWidth/battle.width*.48;
      if(siblings.length===1){siblings[0].style.marginLeft=`${-spread}px`;node.style.marginLeft=`${spread}px`}
      else if(siblings.length>1)node.style.setProperty('--float-lane',`${(siblings.length-1)*48}px`);
      layer.append(node);node.animate([{opacity:1,transform:'translate(-50%,-65%) scale(1.1)'},{opacity:1,transform:'translate(-50%,-85%) scale(1)',offset:.15},{opacity:1,transform:'translate(-50%,-115%) scale(1)',offset:.68},{opacity:0,transform:'translate(-50%,-150%) scale(.96)'}],{duration:reduced?1400:950,fill:'forwards'}).onfinish=()=>node.remove();
      if(reduced||event.kind==='miss')return;
      for(const art of impactArtwork(event)){
        const sprite=document.createElement('i');sprite.className=`painted-hit-sprite ${event.absorbed||event.kind==='barrier'?'barrier-impact-sprite':''}`;
        const size=field.clientWidth/battle.width*(event.absorbed||event.kind==='barrier'?1.5:1.05);
        sprite.style.cssText=`left:${x}%;top:${y}%;width:${size}px;height:${size}px;background-image:url('/assets/combat-presentation-v2/effects/${art}.png')`;layer.append(sprite);
        sprite.animate([{transform:'translate(-50%,-50%) scale(.85)',opacity:.9},{transform:'translate(-50%,-50%) scale(1.05)',opacity:.72,offset:.3},{transform:'translate(-50%,-50%) scale(1.25)',opacity:0}],{duration:art==='poison_cloud'?550:event.kind==='barrier'||event.absorbed?360:240,easing:'ease-out'}).onfinish=()=>sprite.remove();
      }
      if(event.kind==='status'||['intercept','counter','resisted'].includes(event.kind))return;
      const count=['burn','fire','poison','bleed','collision','thorns'].includes(event.kind)?7:4;
      for(let i=0;i<count;i++){
        const p=document.createElement('i');p.className=`combat-impact-particle kind-${event.kind}`;p.style.cssText=`left:${x}%;top:${y}%;--impact-color:${style.color}`;layer.append(p);
        const angle=i/count*Math.PI*2,span=field.clientWidth/battle.width*.38;
        const dx=Math.cos(angle)*span,dy=Math.sin(angle)*span;
        p.animate([{transform:'translate(-50%,-50%) scale(1)',opacity:.95},{transform:`translate(calc(-50% + ${dx}px),calc(-50% + ${dy}px)) scale(.2)`,opacity:0}],{duration:event.kind==='poison'?600:380}).onfinish=()=>p.remove();
      }
    },delay);timers.add(timer);
  }
  return {mount,emit,clear};
}

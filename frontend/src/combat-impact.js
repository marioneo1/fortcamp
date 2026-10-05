// Shared timing for sound, tokens and feedback. Forced movement begins at the hit.
export function movementDuration(event){return event.forced?220:Math.max(220,Math.min(850,Math.max(1,(event.points||[]).length-1)*155))}
export function impactTimeline(events){
  let cursor=0;const packets=new Map();
  return events.map(event=>{
    const key=event.attack_packet;
    let packet=packets.get(key),start=cursor,duration=0;
    const attack=event.type==='melee_attack'||event.attack_event||event.type==='magic_projectile';
    if(key!=null&&attack){
      if(!packet){packet={start:cursor,impact:cursor+(event.type==='melee_attack'?185:220),land:cursor+(event.type==='melee_attack'?185:220)};packets.set(key,packet)}
      start=packet.start;
    }else if(packet){start=event.after_displacement?packet.land:packet.impact}
    if(event.type==='movement'){
      duration=movementDuration(event);
      if(event.forced&&packet){start=packet.impact;packet.land=start+duration}
      cursor=Math.max(cursor,start+duration+70);
    }else if(event.type==='melee_attack'){
      duration=490;cursor=Math.max(cursor,start+duration);
    }else if(event.type==='sound'){
      if(packet&&!event.attack_event)start=event.after_displacement?packet.land:packet.start;
      duration=event.duration||0;cursor=Math.max(cursor,start+duration);
    }else if(event.type==='magic_projectile'){
      duration=250;cursor=Math.max(cursor,start+duration);
    }else if(event.type==='death_burst'){
      duration=460;cursor=Math.max(cursor,start+duration+60);
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
  miss:{label:'Miss',icon:'↗',color:'#ded9cb'},captured:{label:'Subdued',icon:'◇',color:'#d5c6ff'},
  status:{label:'Status',icon:'•',color:'#dfcbff'},
};
export function feedbackText(event,definitions={}){
  const style=feedbackStyles[event.kind]||feedbackStyles.physical;
  if(event.kind==='status')return {...style,label:definitions[event.status_id]?.name||event.status_id,icon:definitions[event.status_id]?.icon||style.icon,value:''};
  return {...style,value:event.amount?`${['heal','barrier'].includes(event.kind)?'+':'−'}${event.amount}`:event.absorbed?'Blocked':''};
}
export function protectionMarkup(unit){
  if(unit.condition&&unit.condition!=='active')return '';
  const barrier=(unit.statuses||[]).find(s=>s.id==='barrier'&&s.amount>0);
  return `${barrier?`<span class="unit-barrier-halo" aria-hidden="true"></span><span class="unit-barrier-capacity" title="Barrier: absorbs ${Number(barrier.amount)} damage">◇ ${Number(barrier.amount)}</span>`:''}${unit.guarding?'<span class="unit-guard-halo" aria-hidden="true"></span>':''}`;
}
export function createImpactFeedback(){
  let field,epoch=0;const timers=new Set();
  function clear(){epoch++;for(const timer of timers)clearTimeout(timer);timers.clear();field?.querySelectorAll('.combat-float,.combat-impact-ring,.combat-impact-particle').forEach(n=>n.remove())}
  function mount(next){if(field!==next){clear();field=next}}
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
      const siblings=[...field.querySelectorAll('.combat-float')].filter(n=>n.style.left===`${x}%`&&n.style.top===`${y}%`).length;
      node.style.setProperty('--float-lane',`${siblings%3*22}px`);
      field.append(node);node.animate([{opacity:0,transform:'translate(-50%,-45%) scale(.8)'},{opacity:1,transform:'translate(-50%,-75%) scale(1.12)',offset:.12},{opacity:1,transform:'translate(-50%,-100%) scale(1)',offset:.68},{opacity:0,transform:'translate(-50%,-150%) scale(.96)'}],{duration:reduced?1400:1050,fill:'forwards'}).onfinish=()=>node.remove();
      if(reduced||event.kind==='miss'||event.kind==='status')return;
      const ring=document.createElement('i');ring.className=`combat-impact-ring kind-${event.kind}`;ring.style.cssText=`left:${x}%;top:${y}%;--impact-color:${style.color};width:${field.clientWidth/battle.width*.78}px;height:${field.clientHeight/battle.height*.78}px`;field.append(ring);
      ring.animate([{transform:'translate(-50%,-50%) scale(.65)',opacity:.9},{transform:'translate(-50%,-50%) scale(1.3)',opacity:0}],{duration:350}).onfinish=()=>ring.remove();
      const count=['burn','fire','poison','bleed','collision','thorns'].includes(event.kind)?7:4;
      for(let i=0;i<count;i++){
        const p=document.createElement('i');p.className=`combat-impact-particle kind-${event.kind}`;p.style.cssText=`left:${x}%;top:${y}%;--impact-color:${style.color}`;field.append(p);
        const angle=i/count*Math.PI*2,span=field.clientWidth/battle.width*.38;
        const dx=Math.cos(angle)*span,dy=Math.sin(angle)*span;
        p.animate([{transform:'translate(-50%,-50%) scale(1)',opacity:.95},{transform:`translate(calc(-50% + ${dx}px),calc(-50% + ${dy}px)) scale(.2)`,opacity:0}],{duration:event.kind==='poison'?600:380}).onfinish=()=>p.remove();
      }
    },delay);timers.add(timer);
  }
  return {mount,emit,clear};
}

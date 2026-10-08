const ART={summoner_dissolve:'conjure',summoner_conjure:'conjure',summoner_transposition:'conjure',summoner_spirit_projection:'projectile',summoner_sacrifice:'explosion',summoner_overload:'conjure',summoner_life_pact:'nature_burst',summoner_nature_burst:'nature_burst'};
export function emitSummonerEffect(field,event,battle,delay){
 const file=ART[event.skill];if(!file)return false;
 const token=[...field.querySelectorAll('[data-battle-unit]')].find(n=>n.dataset.battleUnit===event.unit_id||n.dataset.battleUnit===`transition-${event.unit_id}`);
 if(event.skill==='summoner_conjure'&&token)token.animate([{opacity:0},{opacity:1}],{duration:300,delay:delay+220,fill:'backwards'});
 setTimeout(()=>{
  if(!field.isConnected||document.hidden)return;
  const layer=field.querySelector('.combat-feedback-layer');if(!layer)return;
  const ring=document.createElement('span');ring.className='summoner-effect';
  ring.style.cssText=`left:${(event.x+.5)/battle.width*100}%;top:${(event.y+.5)/battle.height*100}%;width:${(file==='explosion'?3:1.8)/battle.width*100}%`;
  ring.innerHTML=`<img src="/assets/summoner-v1/${file}.png" alt="">`;layer.append(ring);
  const reduced=matchMedia('(prefers-reduced-motion: reduce)').matches;
  const frames=[{opacity:0,transform:'translate(-50%,-50%) scale(.35) rotate(-20deg)'},{opacity:1,transform:'translate(-50%,-50%) scale(1) rotate(0deg)',offset:.38},{opacity:0,transform:'translate(-50%,-50%) scale(1.3) rotate(15deg)'}];
  if(event.skill==='summoner_dissolve'){frames[0].transform='translate(-50%,-50%) scale(1.2)';frames[2].transform='translate(-50%,-50%) scale(.1)'}
  ring.animate(reduced?[{opacity:0},{opacity:.8},{opacity:0}]:frames,{duration:file==='explosion'?650:560,easing:'ease-out'}).finished.then(()=>ring.remove(),()=>ring.remove());
 },delay);return true;
}

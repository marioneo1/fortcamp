export const attributeHelp={
  str:'Strength sets melee weapon scaling and carrying ability. Basic melee damage = 5 + half your effective STR (rounded down) + weapon power + combat proficiency rank. Carrying and throwing also compare STR with the payload’s weight.',
  dex:'Dexterity scales ranged weapons. Basic ranged damage = 5 + half your effective DEX (rounded down) + weapon power + combat proficiency rank. Mission checks use DEX when their relevant proficiency lists it.',
  agi:'Agility sets initiative: 10 + effective AGI + racial and perk bonuses. At 8 AGI you gain 1 movement; movement normally starts at 3 and is limited to 2–8 after racial and perk modifiers.',
  vit:'Vitality sets CON directly. Base combat HP = 24 + 4 × effective VIT, then racial HP scaling and flat bonuses apply. Base armor = effective VIT divided by 3, rounded down, plus racial and perk bonuses.',
  int:'Intelligence scales magic weapons. Basic magic damage = 5 + half your effective INT (rounded down) + weapon power + combat proficiency rank. Individual spells may use their own scaling and elevation rules.',
  luk:'Luck can contribute to mission capabilities that list LUK. It does not automatically add critical chance to every attack or mission. Mission critical outcomes depend on the mission check, team advantage and any special criteria.'
};
export const attributeTotalHelp='Effective attribute = base attribute + equipped gear bonuses + 1 for each trained proficiency linked to this attribute + applicable perk bonuses.';
export function mountHoverHelp(doc=document){
  const popup=doc.createElement('div');popup.className='floating-help';popup.setAttribute('role','tooltip');popup.id='roster-hover-help';popup.hidden=true;doc.body.append(popup);
  let anchor;
  const hide=()=>{anchor?.removeAttribute('aria-describedby');anchor=null;popup.hidden=true};
  const show=event=>{
    const next=event.target.closest('.perk-card,.perk-pill,[data-stat-help]');
    const source=next?.querySelector('.perk-tooltip,.stat-tooltip');if(!source)return;
    anchor?.removeAttribute('aria-describedby');anchor=next;anchor.setAttribute('aria-describedby',popup.id);
    popup.innerHTML=source.innerHTML;popup.hidden=false;
    const box=next.getBoundingClientRect(),rect=popup.getBoundingClientRect();
    popup.style.left=`${Math.max(8,Math.min(box.left,innerWidth-rect.width-8))}px`;
    popup.style.top=`${Math.max(8,Math.min(box.bottom+8,innerHeight-rect.height-8))}px`;
  };
  doc.addEventListener('pointerover',show);doc.addEventListener('focusin',show);
  const leave=event=>{if(anchor?.contains(event.relatedTarget)||popup.contains(event.relatedTarget))return;hide()};
  doc.addEventListener('pointerout',event=>{if(anchor?.contains(event.target)||popup.contains(event.target))leave(event)});
  doc.addEventListener('focusout',leave);doc.addEventListener('keydown',event=>{if(event.key==='Escape')hide()});
  doc.addEventListener('scroll',event=>{if(popup.contains(event.target))return;if(anchor?.isConnected)requestAnimationFrame(()=>{if(anchor?.isConnected)show({target:anchor})});else hide()},true);window.addEventListener('resize',hide);
}

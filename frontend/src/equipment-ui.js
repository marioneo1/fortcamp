const filters = new Map();
export function readHideEquipped(storage,key){
  try{return storage?.getItem(key)!=='false'}catch{return true}
}
export function saveHideEquipped(storage,key,value){
  try{storage?.setItem(key,String(value))}catch{}
}
const ranks = ['common','uncommon','rare','epic','legendary','mythic','event','story'];
const escape = value => String(value??'').replace(/[&<>"']/g, c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const label = value => String(value??'').replaceAll('_',' ').replace(/\b\w/g,c=>c.toUpperCase());
export const iconPath = (id, kind='items') => `/assets/catalogue/${kind}/${id.toLowerCase().replaceAll('-','_').replaceAll(' ','_').replaceAll("'",'')}.png`;
const icon = id => `<img class="catalogue-icon" src="${escape(iconPath(id))}" alt="" loading="lazy">`;

export function describeGear(item, perks={}) {
  const lines=[];
  if(item.description)lines.push(item.description);
  if(item.power)lines.push(`Weapon power: ${item.power}; scales with ${(item.weapon_scaling||'str').toUpperCase()}.`);
  for(const [key,value] of Object.entries(item.attribute_bonuses||{}))lines.push(`${value>=0?'+':''}${value} ${key.toUpperCase()}`);
  for(const [key,value] of Object.entries(item.bonuses||{}))lines.push(`${value>=0?'+':''}${value} ${label(key)} capability`);
  if(item.element)lines.push(`${label(item.element)} attacks: racial resistance −25%, weakness +25% damage. Nonlethal strikes ignore enchantments.`);
  if(item.combat_skill)lines.push(`Grants ${item.combat_skill.name}: ${item.combat_skill.description} Uses ${(item.combat_skill.scaling||item.weapon_scaling||'str').toUpperCase()}.`);
  if(item.on_hit)lines.push(`${item.on_hit.chance}% ${label(item.on_hit.id)} chance on a successful lethal hit; ${item.on_hit.turns} activations. 4% maximum HP per activation (2–5 damage). Does not stack.`);
  for(const perk of item.granted_perks||[])lines.push(`${perks[perk]?.name||label(perk)}: ${perks[perk]?.effect||perks[perk]?.description||'Granted while equipped.'}`);
  return lines;
}

export function inventoryGroups(state,content,character,filter) {
  const owners=new Map();
  for(const owner of state.characters||[])for(const iid of Object.values(owner.equipment||{}))if(iid)owners.set(iid,owner);
  const groups=new Map();
  for(const instance of state.inventory||[]){
    const item=content.items[instance.item_id];if(!item)continue;
    if(filter.hideEquipped&&owners.has(instance.instance_id))continue;
    if(filter.slot&&item.slot!==filter.slot)continue;
    if(filter.rarity&&item.rarity!==filter.rarity)continue;
    const query=filter.query.trim().toLowerCase();
    if(query&&!`${item.name} ${item.description} ${item.element||''} ${item.combat_skill?.name||''} ${(item.granted_perks||[]).join(' ')}`.toLowerCase().includes(query))continue;
    if(!groups.has(instance.item_id))groups.set(instance.item_id,{id:instance.item_id,item,instances:[]});
    groups.get(instance.item_id).instances.push({...instance,owner:owners.get(instance.instance_id)});
  }
  const wearable = item => (content.slots||['weapon','offhand','head','body','hands','legs','feet','accessory']).includes(item.slot);
  return [...groups.values()].sort((a,b)=>filter.sort==='name'?a.item.name.localeCompare(b.item.name):(Number(wearable(b.item))-Number(wearable(a.item))||ranks.indexOf(b.item.rarity)-ranks.indexOf(a.item.rarity)||a.item.name.localeCompare(b.item.name)));
}

export function mountEquipmentBrowser(panel,{state,content,character,onEquip,onError,editable,preferenceKey='fortcamp:hide-equipped'}) {
  const f=filters.get(character.id)||{query:'',slot:'',rarity:'',sort:'rarity',page:0};filters.set(character.id,f);
  let storage;try{storage=globalThis.localStorage}catch{}
  f.hideEquipped=readHideEquipped(storage,preferenceKey);
  let pending=false;
  const wearables=new Set(content.slots);
  panel.innerHTML=`<div class="armory-heading"><h3>Equipment & Inventory</h3><span>${state.inventory.length} items · duplicate gear is stacked</span></div>
    <div class="armory-equipped"></div><div class="armory-filters">
    <input type="search" aria-label="Search inventory" placeholder="Find gear, abilities or elements…" value="${escape(f.query)}">
    <select aria-label="Equipment slot" data-filter="slot"><option value="">All items</option>${content.slots.map(s=>`<option value="${s}" ${f.slot===s?'selected':''}>${label(s)}</option>`).join('')}</select>
    <select aria-label="Item rarity" data-filter="rarity"><option value="">All rarities</option>${ranks.map(r=>`<option value="${r}" ${f.rarity===r?'selected':''}>${label(r)}</option>`).join('')}</select>
    <select aria-label="Sort inventory" data-filter="sort"><option value="rarity" ${f.sort==='rarity'?'selected':''}>Rarity first</option><option value="name" ${f.sort==='name'?'selected':''}>Name</option></select></div>
    <label class="armory-hide-equipped"><input type="checkbox" data-hide-equipped ${f.hideEquipped?'checked':''}> Hide equipped gear <small>Show spare copies only</small></label>
    <div class="armory-result-count" aria-live="polite"></div><div class="armory-grid"></div><div class="armory-pages"></div>`;
  const find=selector=>panel.querySelector(selector);
  const render=()=>{
    const locked=!editable(character);
    find('.armory-equipped').innerHTML=content.slots.map(slot=>{
      const inst=state.inventory.find(i=>i.instance_id===character.equipment?.[slot]),item=content.items[inst?.item_id];
      return `<div class="armory-slot ${item?'filled':''}"><span>${label(slot)}</span>${item?`${icon(inst.item_id)}<b>${escape(item.name)}</b><button data-remove="${slot}" ${locked||pending?'disabled':''}>Unequip</button>`:'<b>Empty</b>'}</div>`;
    }).join('');
    const groups=inventoryGroups(state,content,character,f),pages=Math.max(1,Math.ceil(groups.length/18));f.page=Math.min(f.page,pages-1);
    find('.armory-result-count').textContent=`${groups.length} matching item types${locked?' · Equipment locked during a mission':''}`;
    find('.armory-grid').innerHTML=groups.slice(f.page*18,(f.page+1)*18).map(group=>{
      const {id,item,instances}=group;
      const owned=instances.some(i=>i.owner?.id===character.id)&&!instances.some(i=>!i.owner);
      const candidate=instances.find(i=>!i.owner)||instances.find(i=>i.owner?.id!==character.id&&editable(i.owner));
      const owners=[...new Set(instances.filter(i=>i.owner).map(i=>i.owner.name))];
      const current=content.items[state.inventory.find(i=>i.instance_id===character.equipment?.[item.slot])?.item_id];
      const change=Object.entries({...current?.attribute_bonuses,...item.attribute_bonuses}).map(([a])=>[a,(item.attribute_bonuses?.[a]||0)-(current?.attribute_bonuses?.[a]||0)]).filter(([,v])=>v);
      if(item.slot==='weapon'&&current)change.unshift(['power',(item.power||0)-(current.power||0)]);
      return `<article class="armory-card rarity-${escape(item.rarity||'common')}"><div class="armory-card-head">${icon(id)}<div><b>${escape(item.name)}</b><small>${label(item.rarity||'common')} · ${label(item.slot||'material')} · ×${instances.length}</small></div></div>
        ${owners.length?`<small class="armory-owners">Equipped: ${escape(owners.join(', '))}</small>`:'<small class="armory-owners">In inventory</small>'}
        <p>${escape(item.description||'')}</p>
        ${item.combat_skill?`<small>Ability: ${escape(item.combat_skill.name)}</small>`:''}${item.element?`<small>${label(item.element)} enchantment</small>`:''}
        <details class="armory-effects"><summary>Stats, abilities & perks</summary><p>${describeGear(item,content.standalone_perks).slice(item.description?1:0).map(escape).join('<br>')||'No direct stat effects.'}</p></details>
        ${current&&change.length?`<div class="armory-compare">Compared with ${escape(current.name)}: ${change.map(([a,v])=>`<span class="${v>0?'better':'worse'}">${v>0?'+':''}${v} ${escape(a.toUpperCase())}</span>`).join(' ')}</div>`:''}
        <button data-instance="${escape(candidate?.instance_id||'')}" data-slot="${escape(item.slot||'')}" ${!wearables.has(item.slot)||!candidate||owned||locked||pending?'disabled':''}>${owned?'Equipped here':!wearables.has(item.slot)?'Training / material item':candidate?.owner?`Transfer from ${escape(candidate.owner.name)}`:!candidate?'Equipped on a mission':'Equip'}</button></article>`;
    }).join('')||'<p class="muted">No items match these filters.</p>';
    find('.armory-pages').innerHTML=`<button data-page="-1" ${f.page===0?'disabled':''}>Previous</button><span>Page ${f.page+1} of ${pages}</span><button data-page="1" ${f.page>=pages-1?'disabled':''}>Next</button>`;
    panel.querySelectorAll('[data-page]').forEach(b=>b.onclick=()=>{f.page+=Number(b.dataset.page);render()});
    panel.querySelectorAll('[data-instance],[data-remove]').forEach(b=>b.onclick=async()=>{
      if(pending)return;pending=true;render();
      try{await onEquip(b.dataset.slot||b.dataset.remove,b.dataset.instance||null)}catch(error){onError(error)}finally{pending=false;if(panel.isConnected)render()}
    });
    panel.querySelectorAll('.catalogue-icon').forEach(img=>img.onerror=()=>{img.classList.add('missing');img.removeAttribute('src')});
  };
  find('input[type="search"]').oninput=e=>{f.query=e.target.value;f.page=0;render()};
  find('[data-hide-equipped]').onchange=e=>{f.hideEquipped=e.target.checked;saveHideEquipped(storage,preferenceKey,f.hideEquipped);f.page=0;render()};
  panel.querySelectorAll('[data-filter]').forEach(el=>el.onchange=()=>{f[el.dataset.filter]=el.value;f.page=0;render()});
  render();
}

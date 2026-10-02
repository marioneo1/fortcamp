import {confirmAction} from './confirmation-ui.js';
import {inventoryGroups,describeGear,iconPath} from './equipment-ui.js';
import {escapeHTML as esc} from './mission-board-ui.js';
const filter={query:'',slot:'',rarity:'',sort:'name',page:0,hideEquipped:false};
let category='';
const pendingSales=new Set();
export function itemCategory(item,content){
 if(content.slots.includes(item.slot))return 'equipment';
 if((item.tags||[]).includes('training')||Object.values(content.perk_training_items||{}).includes(item.id))return 'training';
 return 'materials';
}
export function mountInventoryBrowser(root,{state,content,onEquipment,onSell,onError,onRefresh}){
 const all=inventoryGroups(state,content,null,{...filter,query:'',rarity:''});
 root.innerHTML=`<div class="workspace-heading"><div><div class="eyebrow">PARTY STORAGE</div><h2>Inventory</h2><p>Equipment, training supplies, and collected materials. Duplicate items are stacked.</p></div><span>${state.inventory.length} items / ${all.length} types</span></div><div class="inventory-toolbar"><label>Search<input type="search" placeholder="Name or description" value="${esc(filter.query)}"></label><label>Category<select data-inventory-category><option value="">All items</option>${[['equipment','Equipment'],['training','Training supplies'],['materials','Materials & other items']].map(([id,name])=>`<option value="${id}" ${id===category?'selected':''}>${name}</option>`).join('')}</select></label><label>Rarity<select data-inventory-rarity><option value="">All rarities</option>${['common','uncommon','rare','epic','legendary','mythic','event','story'].map(r=>`<option value="${r}" ${r===filter.rarity?'selected':''}>${r}</option>`).join('')}</select></label></div><div class="inventory-count" role="status"></div><div class="inventory-grid"></div><div class="inventory-pages"></div>`;
 const render=()=>{
  const groups=inventoryGroups(state,content,null,filter).filter(g=>!category||itemCategory({...g.item,id:g.id},content)===category),pages=Math.max(1,Math.ceil(groups.length/24));filter.page=Math.min(filter.page,pages-1);
  root.querySelector('.inventory-count').textContent=`${groups.length} matching item types`;
  root.querySelector('.inventory-grid').innerHTML=groups.slice(filter.page*24,(filter.page+1)*24).map(({id,item,instances})=>{
   const free=instances.filter(i=>!i.owner),price=content.sale_prices?.[id]??0;
   const kind=itemCategory({...item,id},content),owners=[...new Set(instances.filter(i=>i.owner).map(i=>i.owner.name))];
   return `<article class="inventory-card rarity-${esc(item.rarity||'common')}"><header><img src="${esc(item.icon||iconPath(id))}" alt="" loading="lazy"><div><small>${esc(item.rarity||'common')} / ${kind==='training'?'Training supply':kind==='equipment'?'Equipment':'Collected item'}</small><h3>${esc(item.name)}</h3></div><b class="inventory-quantity">×${instances.length}</b></header><p>${esc(item.description||'No description available.')}</p>${kind==='equipment'?`<div class="inventory-effects">${describeGear(item,content.standalone_perks).slice(item.description?1:0).map(esc).join('<br>')}</div><small>${owners.length?`Equipped by ${esc(owners.join(', '))}`:'Available to equip'}</small><button data-inventory-equipment>Manage equipment</button>`:kind==='training'?'<small class="inventory-use">Used at the appropriate training facility in Base. Requires a qualified teacher for higher tiers.</small>':'<small class="inventory-use">Stored for requests and discoveries. This item cannot be equipped.</small>'}<div class="inventory-sale"><label>Quantity<input data-sale-quantity="${esc(id)}" type="number" value="1" min="1" max="${free.length}" ${free.length?'':'disabled'}></label><button data-sell-item="${esc(id)}" ${free.length&&price>0&&!pendingSales.has(id)?'':'disabled'}>Sell / ${price} gold each</button><small>${free.length} unequipped available${owners.length?' / equipped copies protected':''}</small></div></article>`;
  }).join('')||'<div class="workspace-empty"><h3>No matching items</h3><p>Change the filters, or complete missions to collect more items.</p></div>';
  root.querySelector('.inventory-pages').innerHTML=`<button data-inventory-page="-1" ${filter.page===0?'disabled':''}>Previous</button><span>${filter.page+1} / ${pages}</span><button data-inventory-page="1" ${filter.page+1===pages?'disabled':''}>Next</button>`;
  root.querySelectorAll('[data-inventory-page]').forEach(b=>b.onclick=()=>{filter.page+=Number(b.dataset.inventoryPage);render()});
  root.querySelectorAll('[data-inventory-equipment]').forEach(b=>b.onclick=onEquipment);
  root.querySelectorAll('[data-sell-item]').forEach(button=>button.onclick=async()=>{
   const id=button.dataset.sellItem;if(pendingSales.has(id))return;
   const group=groups.find(g=>g.id===id),free=group.instances.filter(i=>!i.owner),quantity=Number(root.querySelector(`[data-sale-quantity="${CSS.escape(id)}"]`).value),price=content.sale_prices[id];
   if(!Number.isInteger(quantity)||quantity<1||quantity>free.length)return onError('Choose a quantity within your unequipped stock');
   pendingSales.add(id);button.disabled=true;
   try{if(await confirmAction({title:`Sell ${group.item.name}?`,message:'Sold items are removed from inventory. Equipped copies are kept.',details:[['Quantity',quantity],['You receive',`${quantity*price} gold`]],confirmLabel:'Sell items',danger:true}))await onSell(free.slice(0,quantity).map(i=>i.instance_id))}catch(error){onError(error.message)}finally{pendingSales.delete(id);if(root.isConnected)onRefresh()}
  });
  root.querySelectorAll('.inventory-card img').forEach(img=>img.onerror=()=>{img.hidden=true});
 };
 root.querySelector('input').oninput=e=>{filter.query=e.target.value;filter.page=0;render()};
 root.querySelector('[data-inventory-category]').onchange=e=>{category=e.target.value;filter.page=0;render()};
 root.querySelector('[data-inventory-rarity]').onchange=e=>{filter.rarity=e.target.value;filter.page=0;render()};
 render();
}

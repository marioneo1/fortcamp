import {test} from 'node:test';
import assert from 'node:assert/strict';
import {describeGear,inventoryGroups,iconPath,readHideEquipped,saveHideEquipped} from './equipment-ui.js';

test('inventory stacks copies without losing ownership, and filters skills/elements',()=>{
  const content={items:{rod:{name:'Storm Rod',rarity:'rare',slot:'weapon',element:'lightning',combat_skill:{name:'Storm Lance'}},coat:{name:'Coat',rarity:'common',slot:'body'}}};
  const c={id:'player',equipment:{weapon:'a'}},state={characters:[c],inventory:[{item_id:'rod',instance_id:'a'},{item_id:'rod',instance_id:'b'},{item_id:'coat',instance_id:'c'}]};
  const f={query:'storm lance',slot:'',rarity:'',sort:'rarity'};
  const groups=inventoryGroups(state,content,c,f);assert.equal(groups.length,1);assert.equal(groups[0].instances.length,2);assert.equal(groups[0].instances[0].owner.id,'player');assert.equal(groups[0].instances[1].owner,undefined);
  f.query='';f.slot='body';assert.equal(inventoryGroups(state,content,c,f)[0].id,'coat');
});
test('descriptions include actual skills, enchantment and granted perk effects',()=>{
  const text=describeGear({description:'A rod.',element:'fire',combat_skill:{name:'Flare',description:'Once per battle.'},granted_perks:['guard']},{guard:{name:'Guard',effect:'+1 armor'}}).join(' ');
  assert.match(text,/Flare/);assert.match(text,/25%/);assert.match(text,/\+1 armor/);assert.equal(iconPath('Half-Orc','races').split('?')[0],'/assets/catalogue/races/half_orc.png');assert.match(iconPath('Half-Orc','races'),/\?v=/);
});

test('hide equipped removes occupied copies but keeps spares and the equipped slots intact',()=>{
 const c={id:'player',equipment:{weapon:'a'}},other={id:'other',equipment:{body:'c'}};
 const state={characters:[c,other],inventory:[{item_id:'rod',instance_id:'a'},{item_id:'rod',instance_id:'b'},{item_id:'coat',instance_id:'c'}]},content={items:{rod:{name:'Rod',slot:'weapon'},coat:{name:'Coat',slot:'body'}}};
 const filter={query:'',hideEquipped:true};const groups=inventoryGroups(state,content,c,filter);
 assert.equal(groups.length,1);assert.deepEqual(groups[0].instances.map(i=>i.instance_id),['b']);assert.equal(c.equipment.weapon,'a');
 filter.hideEquipped=false;assert.equal(inventoryGroups(state,content,c,filter).length,2);
});
test('hide-equipped preference defaults on and remembers opt-out per player',()=>{
 const data=new Map(),storage={getItem:k=>data.get(k)??null,setItem:(k,v)=>data.set(k,v)};
 assert.equal(readHideEquipped(storage,'player-a'),true);saveHideEquipped(storage,'player-a',false);
 assert.equal(readHideEquipped(storage,'player-a'),false);assert.equal(readHideEquipped(storage,'player-b'),true);
 assert.equal(readHideEquipped({getItem(){throw Error('blocked')}},'a'),true);
});

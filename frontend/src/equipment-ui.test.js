import {test} from 'node:test';
import assert from 'node:assert/strict';
import {describeGear,inventoryGroups,iconPath} from './equipment-ui.js';

test('inventory stacks copies without losing ownership, and filters skills/elements',()=>{
  const content={items:{rod:{name:'Storm Rod',rarity:'rare',slot:'weapon',element:'lightning',combat_skill:{name:'Storm Lance'}},coat:{name:'Coat',rarity:'common',slot:'body'}}};
  const c={id:'player',equipment:{weapon:'a'}},state={characters:[c],inventory:[{item_id:'rod',instance_id:'a'},{item_id:'rod',instance_id:'b'},{item_id:'coat',instance_id:'c'}]};
  const f={query:'storm lance',slot:'',rarity:'',sort:'rarity'};
  const groups=inventoryGroups(state,content,c,f);assert.equal(groups.length,1);assert.equal(groups[0].instances.length,2);assert.equal(groups[0].instances[0].owner.id,'player');assert.equal(groups[0].instances[1].owner,undefined);
  f.query='';f.slot='body';assert.equal(inventoryGroups(state,content,c,f)[0].id,'coat');
});
test('descriptions include actual skills, enchantment and granted perk effects',()=>{
  const text=describeGear({description:'A rod.',element:'fire',combat_skill:{name:'Flare',description:'Once per battle.'},granted_perks:['guard']},{guard:{name:'Guard',effect:'+1 armor'}}).join(' ');
  assert.match(text,/Flare/);assert.match(text,/25%/);assert.match(text,/\+1 armor/);assert.equal(iconPath('Half-Orc','races'),'/assets/catalogue/races/half_orc.png');
});

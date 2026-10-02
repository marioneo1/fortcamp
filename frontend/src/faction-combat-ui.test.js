import test from 'node:test';
import assert from 'node:assert/strict';
import {tradeMarkup} from './trade-ui.js';
import {battleSupplyPanel} from './battle-support-ui.js';
import {selectBattleSkill} from './equipment-skills.js';
import {describeGear} from './equipment-ui.js';
const esc=s=>String(s).replaceAll('<','&lt;').replaceAll('>','&gt;');
test('control weapons explain their real effects rather than claiming damage over time',()=>{
  const freeze=describeGear({on_hit:{id:'freeze',chance:18,turns:1}}).join(' ');
  assert.match(freeze,/No movement/);
  assert.match(freeze,/Boss control lasts one activation/);
  assert.doesNotMatch(freeze,/4% maximum HP/);
  assert.match(describeGear({on_hit:{id:'poison',chance:20,turns:2}}).join(' '),/4% maximum HP/);
});

test('trade separates the visiting stock, absent contacts and permanent supplies',()=>{
  const trade={factions:[{id:'watch',name:'Watch',visiting:true,relationship:20,offers:[{id:'faction:1:watch:brooch',item:'brooch',price:12,stock:0}],contracts:[]},
    {id:'lantern',name:'Lantern',visiting:false,relationship:6,offers:[],contracts:[{id:'manifest',name:'<Manifest>',rank:'E',required_relationship:6,locked:false,completed:false}]}],
    rotation:{ends_at:172800,next_name:'Lantern'},merchant:null,camp_items:[{id:'camp:dressing',item:'dressing',stock:999,price:8}],supplies:[{resource:'food',price:2}]};
  const html=tradeMarkup(trade,{resources:{gold:20}},{items:{brooch:{name:'Brooch'},dressing:{name:'Dressing'}}});
  assert.match(html,/Traders rotate every 48 hours/);
  assert.match(html,/data-faction-contract="manifest"/);
  assert.match(html,/&lt;Manifest&gt;/);
  assert.match(html,/data-offer="faction:1:watch:brooch" disabled/);
  assert.match(html,/data-offer="camp:dressing"/);
  assert.match(html,/No independent merchant is visiting/);
});

test('supply choices show actual copies, consolidate stock and disable needless treatment',()=>{
  const unit={id:'p',name:'Captain',hp:40,max_hp:40,statuses:[],acted:false};
  const b={current_unit_id:'p',units:{p:unit},supply_targets:['p'],supply_uses_remaining:3,
    supplies:[{instance_id:'i1',item_id:'dressing',name:'Dressing',heal:18,cleanses:['bleed']},{instance_id:'i2',item_id:'dressing',name:'Dressing',heal:18,cleanses:['bleed']}]};
  assert.match(battleSupplyPanel(b,esc),/Dressing ×2/);
  assert.match(battleSupplyPanel(b,esc),/data-supply="i1" data-supply-target="p" disabled/);
  unit.hp=20;
  assert.match(battleSupplyPanel(b,esc),/data-supply="i1" data-supply-target="p" >Self/);
  b.supply_uses_remaining=0;
  assert.match(battleSupplyPanel(b,esc),/data-supply="i1" data-supply-target="p" disabled/);
});

test('selecting an ally technique changes targeting without retaining an enemy skill preview',()=>{
  const attack={chance:90},heal={chance:100,support:true,heal:18};
  const b={current_unit_id:'p',units:{p:{skills:[{id:'heal',target:'ally'}]}},
    attack_previews:{enemy:{attack,skill:attack},p:{skill:null}},skill_previews:{heal:{p:heal}}};
  const selected=selectBattleSkill(b,'heal');
  assert.equal(selected.attack_previews.enemy.skill,null);
  assert.equal(selected.attack_previews.enemy.attack,attack);
  assert.equal(selected.attack_previews.p.skill,heal);
  assert.equal(b.attack_previews.enemy.skill,attack);
});

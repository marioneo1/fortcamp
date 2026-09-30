import {test} from 'node:test';
import assert from 'node:assert/strict';
import {raceEffects,perkModifiers} from './character-effects.js';
test('Goblin traits disclose real HP, movement and evasion modifiers',()=>{
  const effects=raceEffects({hp_multiplier:.7,move_bonus:2,evasion:15,mission_bonuses:{scavenging:2},form_bonuses:{infiltration:2}});
  assert.ok(effects.includes('-30% maximum HP'));assert.ok(effects.includes('+2 movement'));assert.ok(effects.some(e=>e.includes('+15 evasion')));
});
test('equipped and permanent copies of a perk apply once and obey caps',()=>{
  const definitions={scout:{modifiers:{combat:{move:1}}},pathfinder:{modifiers:{combat:{move:1}}},extra:{modifiers:{combat:{move:1}}}};
  assert.equal(perkModifiers({traits:['scout']},[{granted_perks:['scout']}],definitions,'combat').move,1);
  assert.equal(perkModifiers({traits:['scout','pathfinder','extra']},[],definitions,'combat').move,2);
});

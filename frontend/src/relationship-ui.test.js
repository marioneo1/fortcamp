import test from 'node:test';
import assert from 'node:assert/strict';
import {recordSummary} from './relationship-ui.js';
import {bloodKind} from './combat-effects.js';
test('career rate ignores pending missions and does not invent historic damage',()=>{
 assert.equal(recordSummary({}).success_rate,null);
 const r=recordSummary({service_record:{missions_taken:10,missions_completed:4,missions_failed:1,total_damage:25,combat_turns:4,highest_turn_damage:12}});
 assert.equal(r.success_rate,80);assert.equal(r.damage_per_turn,6.3);assert.equal(r.highest_turn_damage,12);
});
test('blood categories use appropriate nonhuman particles',()=>{
 assert.equal(bloodKind('Human'),'blood');assert.equal(bloodKind('Slimefolk'),'slime');assert.equal(bloodKind('Automaton'),'sparks');assert.equal(bloodKind('Undead'),'dust');
});

import test from 'node:test';
import assert from 'node:assert/strict';
import {rankedCandidates,suggestAssignments,matchesMission,equipmentEditable} from './mission-planner.js';

test('large roster filters availability before ranking and searches name/race',()=>{
  const roster=Array.from({length:300},(_,i)=>({id:`c${i}`,name:`Unit ${i}`,race:i%2?'Goblin':'Human',status:i%3?'idle':'incapacitated',rating:i}));
  const found=rankedCandidates(roster,c=>c.rating,'goblin');
  assert.equal(found[0].character.id,'c299');
  assert.ok(found.every(entry=>entry.character.status==='idle'&&entry.character.race==='Goblin'));
  assert.equal(rankedCandidates(roster,c=>c.rating,'unit 299').length,1);
});
test('suggested roles never reuse a unit or assign an unavailable unit',()=>{
  const roster=[{id:'a',name:'A',status:'idle',tank:10,dps:9},{id:'b',name:'B',status:'idle',tank:3,dps:8},{id:'c',name:'C',status:'claimed',tank:99,dps:99}];
  const roles=[{key:'tank',metric:'tank'},{key:'dps',metric:'dps'}];
  assert.deepEqual(suggestAssignments(roster,roles,(c,s)=>c[s.metric]),{tank:'a',dps:'b'});
  assert.equal(Object.keys(suggestAssignments(roster.slice(0,1),roles,(c,s)=>c[s.metric])).length,1);
});
test('board filters apply together and recovery equipment remains editable',()=>{
  const m={name:'Goblin Camp',rank:'D',mission_form:'hunt',status:'available'};
  assert.ok(matchesMission(m,{query:'goblin',rank:'D',form:'hunt',available:true}));
  assert.ok(!matchesMission({...m,status:'claimed'},{available:true}));
  assert.ok(!matchesMission(m,{rank:'C'}));
  assert.ok(equipmentEditable({status:'incapacitated'}));
  assert.ok(!equipmentEditable({status:'deployed'}));
});

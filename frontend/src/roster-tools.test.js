import {test} from 'node:test';
import assert from 'node:assert/strict';
import {rosterPage} from './roster-tools.js';
const characters = Array.from({length:300},(_,i)=>({id:String(i),name:`Unit ${String(i).padStart(3,'0')}`,race:i%2?'Goblin':'Human',status:i%3?'idle':'incapacitated',source_kind:'generic',perks:i===25?{medic:'basic'}:{},dps:i}));
const metrics=c=>({constitution:300-c.dps,dps:c.dps});
test('large rosters remain paged and sort by useful combat ratings',()=>{
  const page=rosterPage(characters,{sort:'dps'},metrics);
  assert.equal(page.rows.length,24);assert.equal(page.pages,13);assert.equal(page.rows[0].id,'299');
  assert.equal(rosterPage(characters,{page:999},metrics).page,12);
});
test('filters combine availability, race and perk searches',()=>{
  const page=rosterPage(characters,{query:'medic',status:'idle',race:'Goblin'},metrics);
  assert.equal(page.total,1);assert.equal(page.rows[0].id,'25');
  assert.equal(rosterPage(characters,{query:'missing'},metrics).total,0);
});

import test from 'node:test';
import assert from 'node:assert/strict';
import {radiantMarkup} from './battle-radiant-ui.js';
test('entry encounter acknowledges an existing same-map encounter, only while pending',()=>{
 const e={state:'pending',title:'Bear',text:'Optional fight',reward:'Extra loot'};
 const html=radiantMarkup({radiant_encounter:e},s=>s);
 assert.match(html,/data-radiant-choice="continue"/);assert.doesNotMatch(html,/Confront the bear|Keep your distance/);
 for(const state of ['absent','active'])assert.equal(radiantMarkup({radiant_encounter:{...e,state}},s=>s),'');
});

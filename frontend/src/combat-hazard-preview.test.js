import test from 'node:test';
import assert from 'node:assert/strict';
import {movementHazardMarkup} from './combat-hazard-preview.js';
const esc=x=>String(x).replaceAll('<','&lt;');
test('route warning separates entry damage and delayed trap effects',()=>{
 const html=movementHazardMarkup({damage:6,effects:{burn:{stacks:2,chance:100},bleed:{stacks:3,chance:100},hobbled:{stacks:3,chance:100}}},esc);
 assert.match(html,/6 HP damage on this path/);assert.match(html,/Burn \+2/);assert.match(html,/Bleed \+3.*hurts at turn end/);assert.match(html,/Final path from START/);assert.match(html,/Hobble \+3/);
 assert.equal(movementHazardMarkup(null,esc),'');
});
test('uncertain applications and lethal routes are labelled honestly',()=>{
 const html=movementHazardMarkup({damage:0,uncertain:true,lethal:false,effects:{bleed:{stacks:2,chance:50}}},esc);
 assert.match(html,/Hazards on this path/);assert.match(html,/up to \+2 \(50% per entry\)/);
 assert.match(movementHazardMarkup({damage:50,lethal:true,effects:{}},esc),/Lethal route risk/);
});

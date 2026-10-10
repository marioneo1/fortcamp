import test from 'node:test';
import assert from 'node:assert/strict';
import {rankedAttribute} from './combat-stat-rules.js';
const ranks={E:100,D:130,C:160,B:190,A:220,S:250};
test('rank uses the server policy once, with half-up rounding',()=>{
 assert.equal(rankedAttribute(6,'S',ranks),15);
 assert.equal(rankedAttribute(5,'D',ranks),7);
 assert.equal(rankedAttribute(6,'S',ranks)+1,16); // Flat perk is added afterward.
});
test('legacy characters without rank remain at their saved allocation',()=>{
 assert.equal(rankedAttribute(8,undefined,ranks),8);
 assert.equal(rankedAttribute(8,'unknown',ranks),8);
});

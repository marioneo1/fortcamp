import test from 'node:test';
import assert from 'node:assert/strict';
import {startingRaces} from './character-creator.js';

test('starting race list follows the catalogue, puts Human first and excludes limited gods',()=>{
  const races=startingRaces({races:{Goblin:{rarity:'Common'},Celestial:{rarity:'Limited'},Human:{rarity:'Common'},Dwarf:{rarity:'Uncommon'}}});
  assert.deepEqual(races.map(([name])=>name),['Human','Dwarf','Goblin']);
});

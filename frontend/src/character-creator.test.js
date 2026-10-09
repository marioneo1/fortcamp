import test from 'node:test';
import assert from 'node:assert/strict';
import {startingRaces} from './character-creator.js';

test('starting race list follows explicit eligibility, puts Human first and excludes discovery races',()=>{
  const races=startingRaces({races:{Goblin:{starting_selectable:true},Celestial:{starting_selectable:false},Human:{starting_selectable:true},Dwarf:{starting_selectable:true},Werewolf:{rarity:'Secret'},Ogre:{rarity:'Rare',starting_selectable:false}}});
  assert.deepEqual(races.map(([name])=>name),['Human','Dwarf','Goblin']);
});

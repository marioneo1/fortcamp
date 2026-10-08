import test from 'node:test';
import assert from 'node:assert/strict';
import {summonCommand} from './summoner-ui.js';
const fixture=kind=>({current_unit_id:'owner',units:{owner:{id:'owner',hp:80,max_hp:100,special:{id:'job:summoner:'+kind,summoner_kind:kind}},w:{id:'w',x:2,y:2,hp:1,max_hp:1}},summoner:{summons:['w'],placement:[{x:2,y:2}],wisp_placement:[{x:2,y:2},{x:3,y:2},{x:4,y:2}],swaps:{owner:['w'],w:['owner']},projection:{enemy:3},sacrifice_cells:[{x:3,y:2}]}});
test('Wisp placement waits for all three legal tiles; companion needs a choice',()=>{
 const v=fixture('wisp_swarm');assert.equal(summonCommand(v,{positions:[{x:2,y:2}]}),null);
 const positions=v.summoner.wisp_placement;assert.deepEqual(summonCommand(v,{positions}),{action:'skill',skill_id:'job:summoner:wisp_swarm',positions});
 assert.equal(summonCommand(fixture('bound_companion'),{positions:[{x:2,y:2}]}),null);
});
test('Reclaim needs no new placement and swap uses two distinct owned bodies',()=>{
 const v=fixture('bound_companion');v.units.owner.special.availability={reclaim:true};assert.equal(summonCommand(v,{positions:[]}).skill_id,'job:summoner:bound_companion');
 const swap=fixture('transposition');assert.equal(summonCommand(swap,{first:'owner',target:'owner'}),null);assert.equal(summonCommand(swap,{first:'owner',target:'w'}).ally_id,'owner');
});
test('Orders are innate; Projection and Sacrifice require contributing summons',()=>{
 const v=fixture('spirit_projection');assert.equal(summonCommand(v,{target:'enemy'}).target_id,'enemy');assert.equal(summonCommand(v,{target:'missing'}),null);
 assert.deepEqual(summonCommand(v,{order:'follow',entity:'all'}),{action:'summon_order',entity_id:'all',order:'follow'});
 assert.equal(summonCommand(v,{order:'hold',entity:'w'}),null);
 assert.equal(summonCommand(fixture('sacrifice'),{point:{x:3,y:2}}).x,3);
});
test('Overload cannot refresh and Life Pact cannot spend the last HP',()=>{
 const v=fixture('overload');v.units.w.overloaded_once=true;assert.equal(summonCommand(v,{target:'w'}),null);
 const pact=fixture('life_pact');pact.units.w.hp=0;pact.units.owner.hp=25;assert.equal(summonCommand(pact,{target:'w'}),null);
});
test('Protect Ally requires a bound companion and a legal ally, including the Summoner',()=>{
 const v=fixture('orders');v.summoner.protect_summons=['companion'];v.summoner.protect_targets=['owner','ally'];
 for(const target of ['owner','ally'])assert.deepEqual(summonCommand(v,{order:'protect',entity:'all',target}),{action:'summon_order',entity_id:'all',order:'protect',target_id:target});
 assert.equal(summonCommand(v,{order:'protect',entity:'w',target:'owner'}),null);
 assert.equal(summonCommand(v,{order:'protect',entity:'companion',target:'enemy'}),null);
 assert.equal(summonCommand(v,{order:'protect',entity:'companion'}),null);
 v.summoner.protect_summons=[];assert.equal(summonCommand(v,{order:'protect',entity:'all',target:'owner'}),null);
});

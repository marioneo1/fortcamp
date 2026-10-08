import test from 'node:test';
import assert from 'node:assert/strict';
import {engineerCommand,engineerHazardsMarkup,hazardDeparturePlans} from './engineer-ui.js';
const view=(k,extra={})=>({current_unit_id:'e',width:8,height:8,units:{e:{id:'e',special:{id:'job:engineer:'+k,engineer_kind:k},...extra}},engineer:{placement:[{x:2,y:3}],dynamite_cells:[{x:4,y:3}],mounts:['m'],exits:[{x:3,y:2}]}});
test('Engineer placement confirms legal cells, rejects missing or occupied destinations',()=>{const b=view('sentry_turret');assert.equal(engineerCommand(b,{}),null);assert.equal(engineerCommand(b,{point:{x:0,y:0}}),null);assert.deepEqual(engineerCommand(b,{point:{x:2,y:3}}),{action:'skill',skill_id:'job:engineer:sentry_turret',x:2,y:3})});
test('Mounting and exiting validate their own target sets',()=>{assert.equal(engineerCommand(view('man_the_guns'),{target:'enemy'}),null);assert.equal(engineerCommand(view('man_the_guns'),{target:'m'}).target_id,'m');assert.equal(engineerCommand(view('man_the_guns',{mounted_machine:'m'}),{point:{x:2,y:3}}),null);assert.equal(engineerCommand(view('man_the_guns',{mounted_machine:'m'}),{point:{x:3,y:2}}).x,3)});
test('Preparation and cancel construction need no random map target',()=>{for(const b of [view('rapid_assembly'),view('overclock'),view('sentry_turret',{construction:{}})])assert.equal(engineerCommand(b,{}).action,'skill')});
test('Dynamite uses its legal throw cells and hazards use transparent map art',()=>{assert.equal(engineerCommand(view('dynamite'),{point:{x:2,y:3}}),null);assert.equal(engineerCommand(view('dynamite'),{point:{x:4,y:3}}).x,4);const html=engineerHazardsMarkup({width:8,height:8,engineer_hazards:[{kind:'mine',x:1,y:2}]});assert.match(html,/engineer-v1\/mine.png/);assert.match(html,/allies and enemies/)});
test('Exploding mines remain visible through earlier enemy actions, then disappear at their explosion',()=>{const hazard={id:'mine',kind:'mine',x:2,y:2};const timeline=[{event:{type:'movement'},start:0},{event:{type:'martial_effect',skill:'engineer_explosion',hazard_id:'mine'},start:780},{event:{type:'sound',hazard_id:'mine'},start:780}];assert.deepEqual(hazardDeparturePlans({engineer_hazards:[hazard]},{engineer_hazards:[]},timeline),[{hazard,start:780}]);assert.deepEqual(hazardDeparturePlans({engineer_hazards:[]},{engineer_hazards:[]},timeline),[])});
test('Scuttle accepts only owned machines without requiring the Engineer to mount',()=>{const b=view('scuttle_protocol');b.engineer.machines=['m'];assert.equal(engineerCommand(b,{target:'enemy'}),null);assert.equal(engineerCommand(b,{target:'m'}).target_id,'m');b.units.e.mounted_machine='other';assert.equal(engineerCommand(b,{target:'m'}),null)});

test('Dynamite created and exploded in one response remains between landing and explosion',()=>{
 const hazard={id:'d',kind:'dynamite',x:3,y:2};
 const timeline=[{start:0,event:{type:'martial_effect',skill:'engineer_dynamite_throw',hazard_id:'d',hazard_snapshot:hazard}},
 {start:1900,event:{type:'martial_effect',skill:'engineer_explosion',hazard_id:'d',hazard_snapshot:hazard}}];
 assert.deepEqual(hazardDeparturePlans({engineer_hazards:[]},{engineer_hazards:[]},timeline),[{hazard,start:1900,appear:600}]);
});

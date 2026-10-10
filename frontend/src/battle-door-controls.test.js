import test from 'node:test';
import assert from 'node:assert/strict';
import {doorControlsMarkup,bindDoorControls,doorCommand} from './battle-door-controls.js';
const escape=s=>String(s).replaceAll('&','&amp;').replaceAll('"','&quot;').replaceAll('<','&lt;');
const battle={width:8,height:8,door_controls:[
 {x:3,y:2.5,gate_id:'door',operation:'Open',label:'Open Door',help:'Free; once per activation.',command:{action:'interact',target_id:'door'}}]};
test('one control is rendered at the doorway with an accessible label',()=>{
 const html=doorControlsMarkup(battle,escape);
 assert.equal((html.match(/data-door-control=/g)||[]).length,1);
 assert.equal((html.match(/aria-label="Open Door"/g)||[]).length,1);
 assert.ok(html.includes('top:37.5%'));
 assert.equal(doorControlsMarkup({width:8,height:8},escape),'');
});
test('click uses the selected side command and does not bubble into targeting',()=>{
 const buttons=[0].map(i=>({dataset:{doorControl:String(i)}}));
 const sent=[];let stopped=0;
 bindDoorControls({querySelectorAll:()=>buttons},battle,c=>sent.push(c));
 buttons[0].onpointerdown({stopPropagation:()=>stopped++});
 buttons[0].onclick({stopPropagation:()=>stopped++});
 assert.equal(stopped,2);assert.deepEqual(sent,[battle.door_controls[0].command]);
});
test('disabled controls remain visible and never send commands',()=>{
 const disabled={...battle,door_controls:battle.door_controls.map(c=>({...c,disabled:true}))};
 assert.equal((doorControlsMarkup(disabled,escape).match(/ disabled/g)||[]).length,1);
 const button={dataset:{doorControl:'0'}};let sent=false;
 bindDoorControls({querySelectorAll:()=>[button]},disabled,()=>sent=true);
 button.onclick({stopPropagation(){}});assert.equal(sent,false);
});

test('open and close controls use distinct painted icons rather than browser-style hands',()=>{
 assert.match(doorControlsMarkup(battle,escape),/combat-navigation-v1\/door_open.png/);
 assert.match(doorControlsMarkup({...battle,door_controls:battle.door_controls.map(c=>({...c,operation:'Close'}))},escape),/combat-navigation-v1\/door_close.png/);
});

test('nearby doorway uses a validated immediate move on the reachable side',()=>{
 const b={status:'active',current_unit_id:'p',units:{p:{id:'p',team:'player',x:0,y:0}},movement_tree:[
  {x:0,y:0,cost:0,parent:null,steps:[[1,0,1]]},
  {x:1,y:0,cost:1,parent:[0,0],steps:[[0,0,1]]}]};
 const c={operation:'Open',approaches:[{x:1,y:1},{x:1,y:0}],command:{action:'navigate',gate_id:'door',x:1,y:1}};
 assert.deepEqual(doorCommand(b,c),{...c.command,operate_gate:true,gate_operation:'Open',position:{x:1,y:0}});
 assert.deepEqual(doorCommand({...b,movement_tree:[]},c),{...c.command,operate_gate:true,gate_operation:'Open'});
 assert.equal(doorCommand(b,battle.door_controls[0]),battle.door_controls[0].command);
});

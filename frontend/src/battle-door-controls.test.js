import test from 'node:test';
import assert from 'node:assert/strict';
import {doorControlsMarkup,bindDoorControls} from './battle-door-controls.js';
const escape=s=>String(s).replaceAll('&','&amp;').replaceAll('"','&quot;').replaceAll('<','&lt;');
const battle={width:8,height:8,door_controls:[
 {x:3,y:2.3,gate_id:'door',operation:'Open',label:'Open Door',help:'Uses your action.',command:{action:'interact',target_id:'door'}},
 {x:3,y:2.7,gate_id:'door',operation:'Open',label:'Open Door',help:'Approach this side.',command:{action:'navigate',x:3,y:3}}]};
test('both controls are always rendered with accessible labels and distinct positions',()=>{
 const html=doorControlsMarkup(battle,escape);
 assert.equal((html.match(/data-door-control=/g)||[]).length,2);
 assert.equal((html.match(/aria-label="Open Door"/g)||[]).length,2);
 assert.ok(html.includes('top:35%'));assert.ok(html.includes('top:40%'));
 assert.equal(doorControlsMarkup({width:8,height:8},escape),'');
});
test('click uses the selected side command and does not bubble into targeting',()=>{
 const buttons=[0,1].map(i=>({dataset:{doorControl:String(i)}}));
 const sent=[];let stopped=0;
 bindDoorControls({querySelectorAll:()=>buttons},battle,c=>sent.push(c));
 buttons[1].onpointerdown({stopPropagation:()=>stopped++});
 buttons[1].onclick({stopPropagation:()=>stopped++});
 assert.equal(stopped,2);assert.deepEqual(sent,[battle.door_controls[1].command]);
});
test('disabled controls remain visible and never send commands',()=>{
 const disabled={...battle,door_controls:battle.door_controls.map(c=>({...c,disabled:true}))};
 assert.equal((doorControlsMarkup(disabled,escape).match(/ disabled/g)||[]).length,2);
 const button={dataset:{doorControl:'0'}};let sent=false;
 bindDoorControls({querySelectorAll:()=>[button]},disabled,()=>sent=true);
 button.onclick({stopPropagation(){}});assert.equal(sent,false);
});

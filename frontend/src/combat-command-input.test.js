import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import vm from 'node:vm';
import {createLatestMovement} from './latest-movement.js';

// Exercise the actual UI request handler with a deliberately delayed connection.
const main=readFileSync(new URL('./main.js',import.meta.url),'utf8');
const handler=main.slice(main.indexOf('async function sendCombat('),main.indexOf('async function resumeMercenaryContract('));
function harness(){
  const requests=[],renders=[];
  const battle=(x=0,unit='hero')=>({status:'active',current_unit_id:unit,round:1,units:{hero:{x,y:0}},x});
  const context={activeBattleMissionId:'lab',activeBattleView:battle(),combatRequestPending:false,inFlightCombatAction:null,
    latestMovement:createLatestMovement(),combatPlaybackBlocked:()=>false,movementSubmitTimer:null,setTimeout,clearTimeout,updatePlaybackControls:()=>{},
    $$:()=>[],$:selector=>selector==='#mission-modal'?{classList:{contains:()=>false}}:null,
    CSS:{escape:s=>s},previewMovement:()=>null,battleEndpoint:()=>'/command',
    rawApi:(_url,options)=>new Promise((resolve,reject)=>requests.push({command:options?JSON.parse(options.body):null,resolve,reject})),
    nextCombatMode:()=> 'move',selectedCombatAction:'move',tileActionMenu:null,
    renderBattle:b=>{context.activeBattleView=b;renders.push(b)},toast:()=>{},
  };
  vm.createContext(context);vm.runInContext(handler,context);
  return {context,requests,renders,battle};
}
const settle=()=>new Promise(resolve=>setImmediate(resolve));
test('one Guard press during slow movement executes once after the newest destination is acknowledged',async()=>{
  const {context:c,requests:r,battle}=harness();
  const first=c.sendCombat({action:'move',x:1,y:0},null,true);
  await c.sendCombat({action:'move',x:2,y:0});
  await c.sendCombat({action:'guard'});
  await c.sendCombat({action:'guard'});
  await c.sendCombat({action:'move',x:3,y:0});
  assert.equal(r.length,1);
  r[0].resolve({battle:battle(1)});await first;await settle();
  assert.deepEqual(r.map(q=>q.command.action),['move','guard']);
  assert.deepEqual(r[1].command.position,{x:2,y:0});
  r[1].resolve({battle:battle(2,'next')});await settle();assert.equal(r.length,2);
});
test('Guard buffered behind movement cannot execute for a changed actor',async()=>{
  const {context:c,requests:r,battle}=harness();
  const move=c.sendCombat({action:'move',x:1,y:0},null,true);await c.sendCombat({action:'guard'});
  r[0].resolve({battle:battle(1,'next')});await move;await settle();assert.equal(r.length,1);
});
test('failed movement clears buffered Guard before resynchronizing the map',async()=>{
  const {context:c,requests:r,battle}=harness();
  const move=c.sendCombat({action:'move',x:1,y:0},null,true);await c.sendCombat({action:'guard'});
  r[0].reject(new Error('blocked'));await settle();
  assert.equal(r.length,2);assert.equal(r[1].command,null);
  r[1].resolve({battle:battle()});await move;await settle();assert.equal(r.length,2);
});

test('move then immediate Guard uses a single combined request without waiting for a move POST',async()=>{
  const {context:c,requests:r,battle}=harness();
  await c.sendCombat({action:'move',x:1,y:0});
  await c.sendCombat({action:'move',x:2,y:0});
  assert.equal(r.length,0);
  const guard=c.sendCombat({action:'guard'});
  assert.equal(r.length,1);assert.deepEqual(r[0].command,{action:'guard',position:{x:2,y:0}});
  r[0].resolve({battle:battle(2,'next')});await guard;
  await new Promise(resolve=>setTimeout(resolve,120));assert.equal(r.length,1);
});

test('a scouting interruption cancels buffered Guard rather than hiding the revealed map',async()=>{
 const {context:c,requests:r,battle}=harness();
 const move=c.sendCombat({action:'move',x:1,y:0},null,true);
 await c.sendCombat({action:'guard'});
 r[0].resolve({battle:battle(0)});await move;await settle();
 assert.equal(r.length,1);assert.equal(c.activeBattleView.x,0);
});

test('Guard retains the destination after the debounce has taken it for an in-flight request',async()=>{
 const {context:c,requests:r,battle}=harness();
 await c.sendCombat({action:'move',x:2,y:0});
 await new Promise(resolve=>setTimeout(resolve,120));
 assert.equal(r.length,1);assert.equal(c.latestMovement.peek('lab:hero:1'),null);
 await c.sendCombat({action:'guard'});
 r[0].resolve({battle:battle(2)});await settle();
 assert.equal(r.length,2);assert.deepEqual(r[1].command.position,{x:2,y:0});
 r[1].resolve({battle:battle(2,'next')});await settle();
});

test('a flood of alternating clicks followed by Guard commits only the final intended cell',async()=>{
 const {context:c,requests:r,battle}=harness();
 const first=c.sendCombat({action:'move',x:1,y:0},null,true);
 for(let i=0;i<200;i++)await c.sendCombat({action:'move',x:i%2?2:1,y:0});
 await c.sendCombat({action:'guard'});
 r[0].resolve({battle:battle(1)});await first;await settle();
 assert.equal(r.length,2);assert.equal(r[1].command.action,'guard');
 assert.deepEqual(r[1].command.position,{x:2,y:0});
 r[1].resolve({battle:battle(2,'next')});await settle();
 assert.equal(c.activeBattleView.x,2);
});

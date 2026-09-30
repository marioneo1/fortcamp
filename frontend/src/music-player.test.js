import {test} from 'node:test';
import assert from 'node:assert/strict';
import {createMusicPlayer,musicContext,musicTransitionPolicy} from './music-player.js';
import {createAudioMixer} from './audio-settings.js';
class FakeAudio extends EventTarget{
  static instances=[];
  constructor(url){super();this.src=url;this.paused=true;this.currentTime=0;this.duration=120;this.volume=0;FakeAudio.instances.push(this)}
  async play(){this.paused=false}
  pause(){this.paused=true}removeAttribute(){this.src=''}load(){}
}
function setup(){
  FakeAudio.instances=[];let time=0,tick;
  const mixer=createAudioMixer(),player=createMusicPlayer(mixer,{AudioClass:FakeAudio,now:()=>time,schedule:fn=>{tick=fn;return 1},cancel:()=>{}});
  return {mixer,player,advance:ms=>{time+=ms;tick?.()},settle:()=>new Promise(resolve=>setImmediate(resolve))};
}
test('music starts after a gesture, stays on ordinary redraws, rotates and fades',async()=>{
  const s=setup();s.player.setContext('board');assert.equal(FakeAudio.instances.length,0);
  s.player.unlock();await s.settle();s.advance(3000);const first=FakeAudio.instances[0];assert.ok(first.volume>0);
  s.player.setContext('board');s.player.unlock();assert.equal(FakeAudio.instances.length,1);
  first.currentTime=117;s.advance(50);await s.settle();assert.equal(FakeAudio.instances.length,2);
  s.advance(1500);assert.ok(first.volume>0);assert.ok(FakeAudio.instances[1].volume>0);
  s.advance(1500);assert.equal(first.paused,true);assert.equal(s.player.currentTrack,'02_guildhall_shuffle');s.player.dispose();
});
test('settings immediately affect music, contexts switch, and hidden pages pause',async()=>{
  const s=setup();s.player.setContext('base');s.player.unlock();await s.settle();s.advance(3000);
  s.mixer.update({muted:true});assert.equal(FakeAudio.instances[0].volume,0);
  s.mixer.update({muted:false});assert.ok(FakeAudio.instances[0].volume>0);
  s.player.setContext('goblin');await s.settle();s.advance(3000);assert.equal(s.player.currentTrack,'07_goblin_warcamp');
  s.player.suspend(true);assert.ok(FakeAudio.instances.every(a=>a.paused));s.player.setContext('combat');s.player.suspend(false);await s.settle();assert.ok(!FakeAudio.instances.at(-1).paused);assert.equal(s.player.currentTrack,'06_roads_under_pressure');s.player.dispose();
});
test('rapid context changes do not leave older music playing underneath',async()=>{
  const s=setup();s.player.setContext('board');s.player.unlock();await s.settle();s.advance(3000);
  s.player.setContext('base');s.player.setContext('combat');await s.settle();s.advance(3000);
  assert.equal(FakeAudio.instances.filter(a=>!a.paused).length,1);assert.equal(s.player.currentTrack,'06_roads_under_pressure');s.player.dispose();
});
test('encounter music uses faction and base uses a separate context',()=>{
  assert.equal(musicContext('base',null),'base');assert.equal(musicContext('private',null),'board');
  assert.equal(musicContext('missions',{encounter_id:'contract:highway_ambush'}),'combat');
  assert.equal(musicContext('base',{encounter_id:'goblin_warcamp'}),'goblin');
  assert.equal(musicContext('missions',{units:{enemy:{team:'enemy',race:'Hobgoblin'}}}),'goblin');
});
test('blocked autoplay can retry on the next user gesture',async()=>{
  FakeAudio.instances=[];
  class BlockedAudio extends FakeAudio{async play(){if(FakeAudio.instances.length===1){const error=new Error('gesture required');error.name='NotAllowedError';throw error}this.paused=false}}
  const player=createMusicPlayer(createAudioMixer(),{AudioClass:BlockedAudio,schedule:()=>1,cancel:()=>{}});
  player.setContext('board');player.unlock();await new Promise(resolve=>setImmediate(resolve));assert.equal(player.currentTrack,null);
  player.unlock();await new Promise(resolve=>setImmediate(resolve));assert.ok(player.currentTrack);assert.equal(FakeAudio.instances.at(-1).paused,false);player.dispose();
});
test('brief investigation popups cancel the delayed change without restarting the guild track',async()=>{
  const s=setup();s.player.setContext('board');s.player.unlock();await s.settle();s.advance(3000);
  const original=FakeAudio.instances[0];original.currentTime=42;
  const policy=musicTransitionPolicy('private',null,{mission_form:'investigation'},'board');
  assert.equal(policy.delayMs,8000);s.player.setContext(policy.context,{delayMs:policy.delayMs});s.advance(4000);
  assert.equal(s.player.currentTrack,'01_lanternlight');s.player.setContext('board');s.advance(5000);await s.settle();
  assert.equal(FakeAudio.instances.length,1);assert.equal(original.currentTime,42);s.player.dispose();
});
test('long investigation scenes switch once and return to the same guild position',async()=>{
  const s=setup();s.player.setContext('board');s.player.unlock();await s.settle();s.advance(3000);FakeAudio.instances[0].currentTime=42;
  s.player.setContext('investigation',{delayMs:8000});s.advance(8000);await s.settle();s.advance(3000);
  assert.equal(s.player.currentTrack,'investigation_1');s.player.setContext('board');await s.settle();s.advance(3000);
  assert.equal(s.player.currentTrack,'01_lanternlight');assert.equal(FakeAudio.instances.at(-1).currentTime,42);s.player.dispose();
});
test('returning before a fade ends reverses it instead of restarting or layering copies',async()=>{
  const s=setup();s.player.setContext('board');s.player.unlock();await s.settle();s.advance(3000);const first=FakeAudio.instances[0];first.currentTime=27;
  s.player.setContext('base');await s.settle();s.advance(500);s.player.setContext('board');await s.settle();s.advance(3000);
  assert.equal(FakeAudio.instances.length,2);assert.equal(s.player.currentTrack,'01_lanternlight');assert.equal(first.currentTime,27);assert.equal(FakeAudio.instances.filter(a=>!a.paused).length,1);s.player.dispose();
});
test('major boss and defense override faction music while ordinary undead use their own tracks',()=>{
  assert.equal(musicContext('missions',{encounter_id:'contract:undead_death_knight'}),'boss');
  assert.equal(musicContext('missions',{encounter_id:'frontier_watch_defense',units:{enemy:{team:'enemy',race:'Goblin'}}}),'defense');
  assert.equal(musicContext('missions',{encounter_id:'contract:bone_patrol'}),'undead');
  assert.equal(musicContext('missions',{encounter_id:'goblin_warcamp',complication_boss:'chief'}),'boss');
  assert.equal(musicTransitionPolicy('private',null,null,'boss').delayMs,5000);
});

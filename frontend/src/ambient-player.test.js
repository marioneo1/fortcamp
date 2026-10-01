import {test} from 'node:test';
import assert from 'node:assert/strict';
import {createAmbientPlayer,ambientContext} from './ambient-player.js';
import {createAudioMixer} from './audio-settings.js';
class Audio extends EventTarget{
  static instances=[];
  constructor(src){super();this.src=src;this.paused=true;Audio.instances.push(this)}
  async play(){this.paused=false}pause(){this.paused=true}removeAttribute(){this.src=''}load(){}
}
function setup(){
  Audio.instances=[];let time=0,tick,context='goblin_warhost',fire=false;const mixer=createAudioMixer();
  const player=createAmbientPlayer(mixer,{context:()=>context,fireContext:()=>fire,AudioClass:Audio,now:()=>time,random:()=>0,schedule:fn=>{tick=fn;return 1},cancel:()=>{}});
  return {player,mixer,advance:ms=>{time+=ms;tick()},context:value=>context=value,fire:value=>fire=value};
}

test('wood fire is one quiet continuous bed with independent occasional accents',()=>{
  const s=setup();s.fire(true);s.advance(50000);assert.equal(Audio.instances.length,0);
  s.player.unlock();s.advance(0);const fire=Audio.instances[0];assert.match(fire.src,/wood_fire/);assert.equal(fire.loop,true);
  s.advance(1800);assert.equal(fire.volume,s.mixer.volume('ambient',.48));
  s.advance(16200);assert.equal(Audio.instances.length,2);assert.match(Audio.instances[1].src,/goblin_chatter/);
  s.advance(100000);assert.equal(Audio.instances.length,2);assert.equal(fire.paused,false);
  s.fire(false);s.advance(0);s.advance(1200);assert.equal(fire.paused,true);s.player.dispose();
});

test('fire bed respects master/ambient mute, hidden pages and failed assets',()=>{
  const s=setup();s.context(null);s.fire(true);s.player.unlock();s.advance(0);s.advance(1800);const fire=Audio.instances[0];
  s.mixer.update({muted:true});assert.equal(fire.volume,0);s.advance(0);assert.equal(fire.paused,true);
  s.mixer.update({muted:false});s.advance(0);assert.equal(Audio.instances.length,2);
  s.player.suspend(true);assert.equal(Audio.instances[1].paused,true);s.advance(100000);assert.equal(Audio.instances.length,2);
  s.player.suspend(false);s.advance(0);assert.equal(Audio.instances.length,3);
  Audio.instances[2].dispatchEvent(new Event('error'));s.advance(100000);assert.equal(Audio.instances.length,3);s.player.dispose();
});
test('ambient clips wait for a gesture, remain sparse, and alternate without layering',()=>{
  const s=setup();s.advance(100000);assert.equal(Audio.instances.length,0);s.player.unlock();s.advance(0);s.advance(18000);
  assert.equal(Audio.instances.length,1);const first=Audio.instances[0];s.advance(700);assert.ok(first.volume>0);s.advance(90000);assert.equal(Audio.instances.length,1);
  first.dispatchEvent(new Event('ended'));s.advance(44999);assert.equal(Audio.instances.length,1);s.advance(1);assert.equal(Audio.instances.length,2);assert.match(Audio.instances[1].src,/goblin_camp/);assert.equal(first.paused,true);s.player.dispose();
});
test('context changes fade old ambience and base has no regional accents',()=>{
  const s=setup();s.player.unlock();s.advance(0);s.advance(18700);s.advance(700);const first=Audio.instances[0];s.context('starfall_omen');s.advance(0);s.advance(700);assert.equal(first.paused,true);
  s.advance(17300);assert.equal(Audio.instances.length,2);assert.match(Audio.instances[1].src,/starfall_machine/);
  s.context('base');s.advance(0);s.advance(700);s.advance(200000);assert.equal(Audio.instances.length,2);s.player.dispose();
});
test('ambient mute, channel volume and hidden pages apply without catch-up bursts',()=>{
  const s=setup();s.player.unlock();s.advance(0);s.advance(18000);s.advance(700);const clip=Audio.instances[0];
  s.mixer.update({ambient:0});assert.equal(clip.volume,0);s.advance(0);assert.equal(clip.paused,true);s.advance(200000);
  s.mixer.update({ambient:.5});s.advance(17999);assert.equal(Audio.instances.length,1);s.advance(1);assert.equal(Audio.instances.length,2);
  s.player.suspend(true);assert.equal(Audio.instances[1].paused,true);s.advance(100000);s.player.suspend(false);s.advance(17999);assert.equal(Audio.instances.length,2);s.advance(1);assert.equal(Audio.instances.length,3);s.player.dispose();
});
test('a missing ambience clip is skipped rather than retried repeatedly',async()=>{
  const s=setup();s.player.unlock();s.advance(0);s.advance(18000);Audio.instances[0].dispatchEvent(new Event('error'));s.advance(45000);assert.match(Audio.instances[1].src,/goblin_camp/);s.player.dispose();
});

test('guild chatter belongs only to the ordinary Mission Board and yields to events and battles',()=>{
  assert.equal(ambientContext('board','missions'),'guild');
  for(const tab of ['roster','private','base'])assert.equal(ambientContext('board',tab),null);
  assert.equal(ambientContext('goblin_warhost','missions'),'goblin_warhost');
  assert.equal(ambientContext('goblin','missions'),'goblin');
  const s=setup();s.context('guild');s.player.unlock();s.advance(0);s.advance(18000);assert.match(Audio.instances[0].src,/guild_chatter/);
  s.context(null);s.advance(0);s.advance(700);assert.equal(Audio.instances[0].paused,true);s.player.dispose();
});

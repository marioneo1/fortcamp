import {test} from 'node:test';
import assert from 'node:assert/strict';
import {AUDIO_DEFAULTS,normalizeAudioSettings,audioCategory,audioVolume,createAudioMixer} from './audio-settings.js';
test('master and category gains multiply and mute affects every channel',()=>{
  const settings={...AUDIO_DEFAULTS,master:.5,ui:.4,battle:.8};
  assert.equal(audioVolume(settings,'ui',.5),.1);
  assert.equal(audioVolume(settings,'battle',.5),.2);
  assert.equal(audioVolume({...settings,muted:true},'music'),0);
  assert.equal(audioCategory('mission_critical_failure'),'ui');
  assert.equal(audioCategory('ui_click'),'ui');assert.equal(audioCategory('melee_hit_heavy'),'battle');
});
test('invalid preferences are bounded and unavailable storage does not break audio',()=>{
  assert.equal(normalizeAudioSettings({master:10,ui:-2,music:NaN}).master,1);
  assert.equal(normalizeAudioSettings({master:10,ui:-2,music:NaN}).ui,0);
  assert.equal(normalizeAudioSettings({music:NaN}).music,AUDIO_DEFAULTS.music);
  const mixer=createAudioMixer({getItem(){throw Error('blocked')},setItem(){throw Error('blocked')}});
  mixer.update({master:0});assert.equal(mixer.volume('battle'),0);
});
test('preferences survive reload and active sounds follow volume and mute immediately',()=>{
  let saved;const storage={getItem:()=>saved,setItem:(_,value)=>saved=value};
  const mixer=createAudioMixer(storage),audio=new EventTarget();
  mixer.track(audio,'ui',.5);mixer.update({master:.5,ui:.4});assert.equal(audio.volume,.1);
  mixer.update({muted:true});assert.equal(audio.volume,0);
  assert.equal(createAudioMixer(storage).settings.muted,true);
  mixer.update({muted:false});assert.equal(audio.volume,.1);
  audio.dispatchEvent(new Event('ended'));mixer.update({master:0});assert.equal(audio.volume,.1);
});

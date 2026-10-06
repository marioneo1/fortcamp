import test from 'node:test';
import assert from 'node:assert/strict';
import {createDecodedAssetCache,magePlaybackAssets} from './mage-assets.js';

test('Meteor playback waits for load AND decode, caches repeated casts',async()=>{
 const images=[];let decoded;
 class Image {constructor(){images.push(this)}set src(value){this.url=value}decode(){return new Promise(resolve=>{decoded=resolve})}}
 const ready=createDecodedAssetCache({ImageClass:Image,timeoutMs:500});let done=false;
 const waiting=ready(['/meteor.png']).then(()=>{done=true});await Promise.resolve();assert.equal(done,false);
 images[0].onload();await Promise.resolve();assert.equal(done,false);decoded();await waiting;assert.equal(done,true);
 await ready(['/meteor.png']);assert.equal(images.length,1);
});
test('asset failure and missing response do not lock combat forever',async()=>{
 const images=[];class Image {constructor(){images.push(this)}set src(value){}}
 const ready=createDecodedAssetCache({ImageClass:Image,timeoutMs:20});const broken=ready(['/missing.png']);images[0].onerror();assert.deepEqual(await broken,[false]);
 assert.deepEqual(await ready(['/timeout.png']),[false]);
});
test('Meteor and fire preload their ground as well as projectile; Freeze includes shards',()=>{
 const meteor=magePlaybackAssets([{mage_skill:'meteor'}]);assert.ok(meteor.includes('/assets/mage-v1/meteor_rock.png'));assert.ok(meteor.includes('/assets/mage-scorched-v3/fire_strip.png'));
 const freeze=magePlaybackAssets([{mage_skill:'flash_freeze'}]);assert.ok(freeze.includes('/assets/mage-frozen-v2/break_4.png'));
 assert.deepEqual(magePlaybackAssets([]),[]);assert.equal(new Set(meteor).size,meteor.length);
});

import {test} from 'node:test';
import assert from 'node:assert/strict';
import {createVFXTextureLibrary,VFX_ROOT} from './vfx-textures.js';
test('texture loads are lazy, shared, and cache failed files without repeated requests',async()=>{
  const images=[];
  class Image {constructor(){images.push(this)}}
  const library=createVFXTextureLibrary(Image);
  assert.equal(images.length,0);
  const first=library.load(['mist_gray','leaf_oak_gold']);
  const second=library.load(['mist_gray']);
  assert.equal(images.length,2);assert.equal(images[0].src,VFX_ROOT+'mist_gray.png');
  images[0].onload();images[1].onerror();await Promise.all([first,second]);
  assert.equal(library.get('mist_gray'),images[0]);assert.equal(library.get('leaf_oak_gold'),null);
  await library.load(['leaf_oak_gold','mist_gray']);assert.equal(images.length,2);
});

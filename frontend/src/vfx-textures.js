// Shared static sprites. Weather and skills can reuse these without coupling to the board.
export const VFX_ROOT='/assets/vfx/environment-v1/';
export const BOARD_TEXTURES={
  beast:['leaf_oak_gold','leaf_maple_rust','leaf_birch_green','leaf_curled_brown','grass_seeds','petal_ochre','wind_curl'],
  undead:['ash_flake','ash_cluster','mist_gray','mist_violet'],
  goblin:['ember_green','ember_orange','dust_gold'],
  arcane:['glyph_cyan','glyph_violet','arcane_ribbon','electric_arc'],
  starfall:['alien_mote','alien_ribbon','alien_comet'],
};
export function createVFXTextureLibrary(ImageClass=globalThis.Image){
  const cache=new Map();
  return {
    get(name){return cache.get(name)?.image||null},
    load(names){return Promise.all(names.map(name=>{
      if(cache.has(name))return cache.get(name).ready;
      if(!ImageClass)return Promise.resolve(null);
      const entry={image:null,ready:null};cache.set(name,entry);
      entry.ready=new Promise(resolve=>{
        const image=new ImageClass();image.onload=()=>{entry.image=image;resolve(image)};
        image.onerror=()=>resolve(null);image.src=VFX_ROOT+name+'.png';
      });return entry.ready;
    }))},
  };
}
export const vfxTextures=createVFXTextureLibrary();

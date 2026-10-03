import artwork from './environment-ground-art.json' with {type:'json'};

// Visual ground overrides never replace the material used for movement.
// A texture can cover a 2x2 patch continuously instead of repeating each cell.
export function environmentGroundStyle(tile){
  const file=artwork[tile?.sprite];if(!file)return '';
  const span=Math.max(1,Math.min(4,Number(tile.texture_span)||1));
  const origin=tile.origin||[0,0];
  const phase=(value,start)=>((value-start)%span+span)%span;
  const position=value=>span===1?50:100*value/(span-1);
  return `--authored-ground:url('/assets/combat-terrain/${file}?v=activity-v1');--ground-span:${span*100}%;--ground-x:${position(phase(tile.x,origin[0]))}%;--ground-y:${position(phase(tile.y,origin[1]))}%;`;
}

// A foreground blaze below the camera: only its upper tongues enter the viewport.
// World Y rises from the bottom; smoke/embers emerge above the hidden fire bed.
export function burningSources(width,height){
  const narrow=width<700;
  const positions=narrow?[.12,.85]:[.13,.49,.88];
  const heights=[1,.88,1.08],depths=[.76,.72,.82],breadths=[1.8,2.1,1.65];
  const scale=Math.max(100,Math.min(440,height*.32));
  return positions.map((fraction,index)=>({
    x:width*fraction,y:-height*depths[index],
    scaleX:Math.min(width*(narrow?.9:.52),scale*breadths[index]),
    scaleY:scale*heights[index],
    smokeY:height*(.08+index*.02),spread:width*(narrow?.46:.24),
    phase:index*2.1,delay:index*1.3,
  }));
}

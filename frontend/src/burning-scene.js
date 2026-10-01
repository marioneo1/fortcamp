// Shared screen-space sources keep flames, embers and smoke in the same scene.
export function burningSources(width,height){
  const positions=width<700?[.16,.79]:[.12,.48,.86];
  return positions.map((fraction,index)=>({x:width*fraction,y:height*(.06+index*.035),scale:Math.min(170,Math.max(105,height*.145)),delay:index*2.4}));
}

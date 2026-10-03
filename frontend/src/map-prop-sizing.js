import sizes from './map-prop-sizes.json' with {type:'json'};
import retiredAliases from './retired-prop-aliases.json' with {type:'json'};

// Calibrate visible alpha, not PNG canvas size. Modular walls keep their
// independent join geometry; explicitly scaled unregistered artwork still works.
export function propArtScale(item){
  if(item.edge_wall||/^structure:.*(?:wall|palisade|gate|door|corner|junction|pillar)/.test(item.sprite||''))return Number(item.art_scale)||1;
  const profile=sizes[retiredAliases[item.sprite] || item.sprite];
  return Math.max(.1,Math.min(3,profile?.scale??(Number(item.art_scale)||1)));
}

export function propVisualSpan(item,footprint){return sizes[retiredAliases[item.sprite] || item.sprite]?.art_span||footprint}

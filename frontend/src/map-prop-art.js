import overheadProps from './map-prop-art.json';
import retiredAliases from './retired-prop-aliases.json';

// Stable gameplay sprite IDs select versioned art; old libraries remain the fallback.
export function overheadPropStyle(sprite) {
  const file=overheadProps[retiredAliases[sprite] || sprite];
  return typeof file==='string' && /^(props|structures)\/(overhead-v2|location-v1|armory-v1|camp-v1|garden-toolkit-v2|building-v1|building-v2|building-v3|building-v4|building-v5-topdown|building-v10-polished)\/[a-z0-9_]+\.png$/.test(file)
    ? `--battle-prop:url('/assets/combat-terrain/${file}?v=20261003-garden-toolkit');--prop-scale:100%;`
    : '';
}

import overheadProps from './map-prop-art.json';

// Stable gameplay sprite IDs select versioned art; old libraries remain the fallback.
export function overheadPropStyle(sprite) {
  const file=overheadProps[sprite];
  return typeof file==='string' && /^(props|structures)\/(overhead-v2|location-v1|armory-v1|camp-v1|garden-v1|building-v1|building-v2|building-v3|building-v4|building-v5-topdown|building-v10-polished)\/[a-z0-9_]+\.png$/.test(file)
    ? `--battle-prop:url('/assets/combat-terrain/${file}?v=20261003-prop-sizes');--prop-scale:100%;`
    : '';
}

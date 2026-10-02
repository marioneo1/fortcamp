import overheadProps from './map-prop-art.json';

// Stable gameplay sprite IDs select versioned art; old libraries remain the fallback.
export function overheadPropStyle(sprite) {
  const file=overheadProps[sprite];
  return typeof file==='string' && /^(props|structures)\/overhead-v2\/[a-z0-9_]+\.png$/.test(file)
    ? `--battle-prop:url('/assets/combat-terrain/${file}?v=20261002-overhead2');--prop-scale:100%;`
    : '';
}

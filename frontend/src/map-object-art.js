// Shared by battle and preparation rendering, including older saved encounters.
const terrainSprites={palisade:'structure:palisade_straight',wall:'structure:stone_wall_straight',cookfire:'campfire_lit',watchtower:'structure:wooden_watch_platform',wagon:'wooden_handcart',pit:'terrain:pit_deep_earthen'};
const objectSprites={
  alarm_horn:{default:'alarm_bell_active',active:'alarm_bell_active',disabled:'alarm_bell_disabled'},
  dispatch_satchel:{default:'dispatch_satchel'},
  loose_wheel:{default:'wagon_wheel'},
  signal_chart:{default:'marked_farm_chart'},
  prisoner_pen:{default:'structure:wooden_rescue_cage_closed',opened:'structure:wooden_rescue_cage_open'},
  iron_rescue_cage:{default:'structure:iron_rescue_cage_closed',opened:'structure:iron_rescue_cage_open'},
  wooden_rescue_cage:{default:'structure:wooden_rescue_cage_closed',opened:'structure:wooden_rescue_cage_open'},
  prisoner_stocks:{default:'structure:prisoner_stocks_closed',opened:'structure:prisoner_stocks_open'},
  stone_sarcophagus:{default:'structure:stone_sarcophagus_closed',opened:'structure:stone_sarcophagus_open'},
  ritual_altar:{default:'structure:ritual_altar_dormant',active:'structure:ritual_altar_active'},
  supply_crate:{default:'crate_closed',opened:'crate_open'},
  military_supply_coffer:{default:'military_supply_coffer_closed',opened:'military_supply_coffer_open'},
  treasure_chest_bronze:{default:'treasure_chest_bronze_closed',opened:'treasure_chest_bronze_open'},
  treasure_chest_silver:{default:'treasure_chest_silver_closed',opened:'treasure_chest_silver_open'},
  treasure_chest_gold:{default:'treasure_chest_gold_closed',opened:'treasure_chest_gold_open'},
  ancient_reliquary:{default:'ancient_reliquary_closed',opened:'ancient_reliquary_open'},
  arcane_crystal:{default:'arcane_crystal_intact',broken:'arcane_crystal_shattered',destroyed:'arcane_crystal_shattered'},
  floor_lever:{default:'floor_lever_off',active:'floor_lever_on',opened:'floor_lever_on'},
  loose_stone:{default:'scattered_stones'},
};
export function paintedObjectSprite(object){const set=objectSprites[object.id];return object.sprite||set?.[object.state]||set?.default||''}
export function paintedTerrainSprite(item){return item.sprite||(item.id==='cart_body'?'prison_wagon':terrainSprites[item.kind])||''}
export function paintedDestroyedTerrainSprite(item){
  const intact=paintedTerrainSprite(item);
  if(item.prepared_trap&&['spike_trap','iron_jaw_trap'].includes(intact))return `${intact}_spent`;
  if(item.id==='cart_body'&&(!item.destroyed_sprite||item.destroyed_sprite==='structure:wooden_barricade'))return 'prison_wagon_broken';
  return item.destroyed_sprite||((item.original_kind||item.kind)==='palisade'?'structure:palisade_breached':'structure:wall_rubble');
}

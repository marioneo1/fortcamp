# Item catalogue audit

October 1, 2026. Generated from the live Python catalogue by `tools/audit_item_catalogue.py`. This describes implemented effects, not promises inferred from item names.

The catalogue contains **180 items**, including **56 additions** in this pass. All have installed local icons. Generated art stays outside the public code repository.

## Equipment coverage

| Slot | Before | Now | Added |
|---|---:|---:|---:|
| Weapon | 43 | 51 | 8 |
| Head | 4 | 10 | 6 |
| Body | 8 | 14 | 6 |
| Hands | 5 | 11 | 6 |
| Legs | 1 | 9 | 8 |
| Feet | 6 | 12 | 6 |
| Offhand | 10 | 18 | 8 |
| Accessory | 34 | 42 | 8 |
| Non-Equipment | 13 | 13 | 0 |

## Primary gameplay categories

Each item is counted once, using the first applicable category. Active techniques take precedence over enchantments and passives. Stat-focused equipment includes attribute bonuses, armor, HP, movement, initiative and mission-capability bonuses. It can still be useful; a named perk does not automatically make it a new mechanic.

| Category | Count |
|---|---:|
| Active technique | 30 |
| Conditional combat perk | 7 |
| Enchantment / attack effect | 8 |
| Non-equipment | 13 |
| Stat / capability focused | 84 |
| Tactical equipment rule | 38 |

Rarities: common 22, uncommon 27, rare 65, epic 26, legendary 13, mythic 17, event 5, story 5.

“Mission exclusive” means a restricted acquisition source, not one globally owned copy. Completed chains can produce another copy. Champions keep their separate ownership rules.

## What to chase

| Mission | Exclusive item | Success / critical success | Gameplay reason |
|---|---|---|---|
| Rats in the Storehouse (E) | Second-Chance Button | 1% / 2% | A storehouse keepsake that prevents one lethal defeat per battle, leaving you at 1 HP. Does not protect against a nonlethal capture. |
| Survey the Outcrop (E) | Quarry Greaves | 4% / 6% | A survey crew’s plated leggings. Stronger armor in exchange for agility. |
| The Snagged Fishing Line (E) | Ferryman’s Boots | 3% / 5% | An old fisher’s boots make shallow-water movement cost 1; elevation rules still apply. |
| The Goblin Pickpockets (E) | Padded Capture Gloves | 3% / 5% | A padded gauntlet lets its wearer choose melee Subdue even with a sharp or magical weapon. |
| Herbs Behind the Wall (E) | Bogkeeper’s Mask | 3% / 5% | A fitted herb-filter mask. Prevents weapon-inflicted Poison; useful far beyond the garden wall. |
| Bells in the Scrap Heap (E) | Rescue Gloves | 3% / 5% | Grip straps provide +6 effective STR for carrying, without increasing attacks or throws. |
| The Hidden Goblin Armory (C) | Breach Gauntlets | 5% / 8% | Add 3 damage against destructible structures. Their weight costs agility. |
| The Meridian Calibration (C) | Meridian Coil Grips | 6% / 10% | Choose a lightning discharge from the equipped skill list, even while carrying a melee weapon. |
| The Chapel Gatekeepers (C) | Saltward Flail | 4% / 6% | A chapel flail with Holy affinity and Exorcist’s anti-Deathless bonus. |
| The Ward Concord (A) | Tide Bastion | 4% / 6% | An opening ward and poison-proof lining for a defender crossing contaminated ground. |
| Court of the Empty Crown (A) | Empty Court Diadem | 4% / 6% · chain required | A small crown clasp from the Empty Court. Adds damage against bosses without improving ordinary attacks. |
| The Procession's Empty Hearse (A) | Mercythread Robe | 4% / 6% · chain required | The procession’s repaired burial cloth prevents one lethal defeat per battle, leaving its wearer at 1 HP. Escape is still essential. |
| The Meridian Engine (A) | Meridian Field Projector | 4% / 6% · chain required | The engine’s salvaged field lens grants a long-range lightning technique to any equipped weapon build. |
| The Shepherd of Titans (A) | Shepherd’s Carrier Wraps | 4% / 6% · chain required | The titan shepherd’s load harness improves carrying and thrown-payload range; it gives no ordinary attack power. |
| The Door Between Dead Stars (S) | Starless Anchor Boots | 4% / 6% · chain required | Anchor against the first impact and cross broken terrain normally. They keep their wearer grounded, not flying. |
| Tomb Beyond the Sky · Starfall | Deadstar Orbit Pendant | 2% / 4% | A pendant found beyond the final signal. Offers a long-range void strike and +2 direct damage against bosses. |
| Goblin Warcamp | Chieftain’s Chain Grips | 4% live capture; 6% secured field | Recovered only by bringing a chieftain back alive. Offer a two-tile nonlethal restraint and improved carrying. |
| The Captive Cart | Cartmaster’s Tether Reel | 6% live capture; 8% secured field | The cartmaster’s intact hauling reel provides +3 effective carrying STR. It must be recovered from a living captive. |

These are independent, once-per-resolution checks after success. Killing the required captive prevents the capture-exclusive check. Escaped enemies do not qualify. Failure does not trigger these new discoveries. The existing five chain weapons remain additional independent 14% / 22% checks, with chain provenance required. No guarantee or pity system is added.

## Full catalogue

Cache placement shows eligibility, not an unconditional award. An authored reward check still uses its normal rank/outcome reward chances. Item rarity and minimum rank are separate: a low-rank exclusive can be valuable without entering higher-rank random caches. Items without a listed mission/cache source may be starting gear, training supplies, trade stock or retained legacy content.

### Weapon

| Item (ID) | Rarity | Primary category | Implemented identity | Acquisition |
|---|---|---|---|---|
| Rusty Knife (`rusty_knife`) | common | Stat / capability focused | Capabilities: {'combat': 1}; Weapon power 1 | General cache, minimum E |
| Scrap Hatchet (`scrap_hatchet`) | uncommon | Stat / capability focused | Capabilities: {'combat': 2, 'building': 1}; Weapon power 2 | Abandoned Raider Checkpoint: rewards check; Bone Patrol: critical rewards check |
| Short Bow (`short_bow`) | uncommon | Stat / capability focused | Capabilities: {'combat': 2}; Weapon power 2 | Ash Tunnel: critical rewards check; General cache, minimum D; Goblin Supply Carts: critical rewards check; Goblin Warcamp: critical rewards check; Stampede Route: critical rewards check |
| Ember Staff (`ember_staff`) | rare | Enchantment / attack effect | Element: fire; On hit: {'id': 'burn', 'chance': 20, 'turns': 2}; Capabilities: {'combat': 1, 'magic': 2}; Weapon power 3 | Ashen Necropolis: critical rewards check; Haunted Foundry: critical rewards check; Heart of the Leyline: critical rewards check; Impossible Summoning Trace: rewards check; Mirror Labyrinth: critical rewards check; Planar Breach: critical rewards check; Ruined Arcane Observatory: critical rewards check; Starfall Crater: critical rewards check; The Sealed Crypt: critical rewards check |
| Knight's Blade (`knight_blade`) | rare | Stat / capability focused | Capabilities: {'combat': 3}; Weapon power 4 | Chieftain's Redoubt: critical rewards check; Fortress of the Goblin King: critical rewards check; Hunt the Alpha: critical rewards check; Iron Ogre Bridge: critical rewards check; Sealed Old Armory: rewards check; The Tithe Convoy: critical rewards check; Tomb Beyond the Sky: critical rewards check; Young Dragon's Roost: critical rewards check |
| Guildsteel Spear (`guildsteel_spear`) | rare | Stat / capability focused | Capabilities: {'combat': 3, 'survival': 1}; Weapon power 4 | General cache, minimum B |
| Siegebreaker Warhammer (`warhammer`) | epic | Stat / capability focused | Granted perks: masterwork; Attributes: {'str': 1}; Capabilities: {'combat': 4, 'building': 2}; Weapon power 5 | General cache, minimum A |
| Moonwood Longbow (`moonwood_longbow`) | epic | Stat / capability focused | Attributes: {'dex': 1, 'agi': 1}; Capabilities: {'combat': 4, 'survival': 2}; Weapon power 5 | General cache, minimum A; The Forest Without Footprints: critical rewards check |
| Crooked Shaman Staff (`crooked_shaman_staff`) | epic | Stat / capability focused | Granted perks: warhost_command; Attributes: {'int': 2}; Capabilities: {'magic': 5, 'combat': 2}; Weapon power 5 | Smoke over the Hedgerows: cache, minimum A; goblin_warhost cache, minimum A |
| Warlord's Cleaver (`warlords_cleaver`) | mythic | Active technique | Warhost Cleave, range 1, STR, lethal; Granted perks: warhost_command, orcish_might; Attributes: {'str': 2, 'vit': 1}; Capabilities: {'combat': 5}; Weapon power 6 | Goblin Warcamp: cache, minimum S; goblin_warhost cache, minimum S |
| Mourning Blade (`mourning_blade`) | mythic | Active technique | Grave Sever, range 1, STR, lethal; Element: holy; Granted perks: graveward, soul_anchor; Attributes: {'str': 1, 'luk': 1}; Capabilities: {'combat': 5, 'magic': 2}; Weapon power 6 | The Procession's Empty Hearse: cache, minimum S; The Procession's Empty Hearse: critical rewards check; The Weight of a Living Heart: critical rewards check; ashen_procession cache, minimum S |
| Titanbone Spear (`titanbone_spear`) | mythic | Active technique | Titan Thrust, range 1, STR, lethal; Granted perks: titan_strength; Attributes: {'str': 2}; Capabilities: {'combat': 5, 'survival': 3}; Weapon power 6 | The Last Arrow of Diana: critical rewards check; The Shepherd of Titans: cache, minimum S; great_beast_tide cache, minimum S |
| Star-Metal Blade (`star_metal_blade`) | epic | Active technique | Impact Cut, range 1, STR, lethal; Element: void; Granted perks: stellar_aegis; Attributes: {'str': 2, 'luk': 1}; Capabilities: {'combat': 6, 'magic': 2}; Weapon power 7 | The Door Between Dead Stars: cache, minimum B; starfall_omen cache, minimum B |
| Comet-String Bow (`comet_string_bow`) | mythic | Active technique | Comet Pierce, range 6, DEX, lethal; Element: void; Granted perks: gravity_walker; Attributes: {'dex': 2, 'agi': 1}; Capabilities: {'combat': 6, 'scavenging': 2}; Weapon power 7 | The Door Between Dead Stars: cache, minimum A; starfall_omen cache, minimum A |
| Warhost Marshal’s Hook (`marshal_hook`) | epic | Stat / capability focused | Granted perks: guard; Attributes: {'str': 2}; Weapon power 2 | No mission/cache placement in this audit |
| Watchman's Cudgel (`watchmans_cudgel`) | common | Stat / capability focused | Weapon power 1 | Court of the Empty Crown: cache, minimum E; General cache, minimum E; The Black-Banner Ledger: cache, minimum E |
| Apprentice Wand (`apprentice_wand`) | common | Stat / capability focused | Weapon power 1 | General cache, minimum E |
| Hooked Spear (`hooked_spear`) | uncommon | Active technique | Hook Thrust, range 1, STR, lethal; Weapon power 2 | Court of the Empty Crown: cache, minimum D; General cache, minimum D; The Black-Banner Ledger: cache, minimum D |
| Weighted Sling (`weighted_sling`) | uncommon | Active technique | Dazing Stone, range 3, DEX, nonlethal; Weapon power 1 | General cache, minimum D |
| Coalbrand Sabre (`coalbrand_sabre`) | rare | Enchantment / attack effect | Element: fire; On hit: {'id': 'burn', 'chance': 25, 'turns': 2}; Weapon power 3 | Court of the Empty Crown: cache, minimum C; General cache, minimum C |
| Venomthorn Bow (`venomthorn_bow`) | rare | Enchantment / attack effect | On hit: {'id': 'poison', 'chance': 30, 'turns': 2}; Weapon power 2 | General cache, minimum C |
| Stormglass Rod (`stormglass_rod`) | epic | Active technique | Storm Lance, range 5, INT, lethal; Element: lightning; Weapon power 3 | General cache, minimum B |
| Mercykeeper's Maul (`mercykeepers_maul`) | legendary | Active technique | Mercy Strike, range 1, STR, nonlethal; Weapon power 4 | Court of the Empty Crown: cache, minimum A; General cache, minimum A |
| Goblin Notched Axe (`goblin_notched_axe`) | common | Stat / capability focused | Weapon power 1 | Goblin Warcamp: cache, minimum E; Smoke over the Hedgerows: cache, minimum E; The Captive Cart: cache, minimum E; goblin_warhost cache, minimum E |
| Goblin Net Bow (`goblin_net_bow`) | uncommon | Active technique | Net Shot, range 3, DEX, nonlethal; Weapon power 1 | Goblin Warcamp: cache, minimum D; Smoke over the Hedgerows: cache, minimum D; The Captive Cart: cache, minimum D; goblin_warhost cache, minimum D |
| Smokecaller Staff (`smokecaller_staff`) | rare | Enchantment / attack effect | Element: fire; On hit: {'id': 'burn', 'chance': 25, 'turns': 2}; Weapon power 2 | Smoke over the Hedgerows: cache, minimum C; goblin_warhost cache, minimum C |
| Gravekeeper's Spade (`gravekeepers_spade`) | common | Stat / capability focused | Weapon power 1 | The Procession's Empty Hearse: cache, minimum E; ashen_procession cache, minimum E |
| Mourning Censer (`mourning_censer`) | uncommon | Conditional combat perk | Granted perks: exorcist; Weapon power 1 | The Procession's Empty Hearse: cache, minimum D; ashen_procession cache, minimum D |
| Pale Watch Lance (`pale_watch_lance`) | rare | Active technique | Vigil Thrust, range 1, STR, lethal; Element: holy; Weapon power 3 | The Procession's Empty Hearse: cache, minimum C; ashen_procession cache, minimum C |
| Cracked Ley Wand (`cracked_ley_wand`) | common | Stat / capability focused | Weapon power 1 | The Meridian Engine: cache, minimum E; arcane_convergence cache, minimum E |
| Prism Tuning Fork (`prism_tuning_fork`) | uncommon | Active technique | Prism Discharge, range 4, INT, lethal; Element: lightning; Weapon power 1 | The Meridian Engine: cache, minimum D; arcane_convergence cache, minimum D |
| Winterglass Grimoire (`winterglass_grimoire`) | rare | Active technique | Winter Ray, range 4, INT, lethal; Element: ice; Weapon power 2 | The Meridian Engine: cache, minimum C; arcane_convergence cache, minimum C |
| Antler Hatchet (`antler_hatchet`) | common | Stat / capability focused | Weapon power 1 | The Shepherd of Titans: cache, minimum E; great_beast_tide cache, minimum E |
| Hunter's Bola (`hunters_bola`) | uncommon | Active technique | Bola Takedown, range 3, DEX, nonlethal; Weapon power 1 | The Shepherd of Titans: cache, minimum D; great_beast_tide cache, minimum D |
| Razorvine Spear (`razorvine_spear`) | rare | Enchantment / attack effect | On hit: {'id': 'poison', 'chance': 25, 'turns': 2}; Weapon power 3 | The Shepherd of Titans: cache, minimum C; great_beast_tide cache, minimum C |
| Meteor-Iron Knife (`meteor_iron_knife`) | common | Stat / capability focused | Weapon power 1 | The Door Between Dead Stars: cache, minimum E; starfall_omen cache, minimum E |
| Skyfall Focus (`skyfall_focus`) | uncommon | Active technique | Distant Echo, range 4, INT, lethal; Element: void; Weapon power 1 | The Door Between Dead Stars: cache, minimum D; starfall_omen cache, minimum D |
| Voidglass Crossbow (`voidglass_crossbow`) | rare | Active technique | Glasspiercer, range 5, DEX, lethal; Element: void; Weapon power 2 | The Door Between Dead Stars: cache, minimum C; starfall_omen cache, minimum C |
| Empty Crown's Verdict (`empty_crowns_verdict`) | mythic | Active technique | Royal Verdict, range 1, STR, lethal; Granted perks: guard; Weapon power 4 | Court of the Empty Crown: 14% / 22% critical · completed chain required |
| Processional Last Light (`processional_last_light`) | mythic | Active technique | Last Light, range 5, INT, lethal; Element: holy; Granted perks: exorcist; Weapon power 3 | The Procession's Empty Hearse: 14% / 22% critical · completed chain required |
| Meridian Arc Driver (`meridian_arc_driver`) | mythic | Active technique | Meridian Bolt, range 6, DEX, lethal; Element: lightning; Granted perks: precision_core; Weapon power 3 | The Meridian Engine: 14% / 22% critical · completed chain required |
| Shepherd's Gentle Hand (`shepherds_gentle_hand`) | mythic | Active technique | Colossus Restraint, range 1, STR, nonlethal; Granted perks: beast_bond; Weapon power 4 | The Shepherd of Titans: 14% / 22% critical · completed chain required |
| Starless Door Key (`starless_door_key`) | mythic | Active technique | Threshold Ray, range 6, INT, lethal; Element: void; Weapon power 3 | The Door Between Dead Stars: 14% / 22% critical · completed chain required |
| Field Crossbow (`field_crossbow`) | common | Stat / capability focused | Weapon power 1 | General cache, minimum E; starfall_omen cache, minimum E |
| Brace-Hook Pike (`brace_hook_pike`) | uncommon | Tactical equipment rule | Rules: {'breach_damage': 2}; Weapon power 1 | General cache, minimum E |
| Triage Baton (`triage_baton`) | rare | Tactical equipment rule | Rules: {'guard_heal': 2}; Granted perks: medic; Weapon power 2 | General cache, minimum C |
| Cinderhook Blade (`cinderhook_blade`) | rare | Enchantment / attack effect | Element: fire; On hit: {'id': 'burn', 'chance': 20, 'turns': 2}; Weapon power 2 | General cache, minimum C |
| Serpentglass Wand (`serpentglass_wand`) | epic | Enchantment / attack effect | On hit: {'id': 'poison', 'chance': 25, 'turns': 2}; Weapon power 2 | General cache, minimum B |
| Mooncord Sling (`mooncord_sling`) | rare | Active technique | Mooncord Takedown, range 4, DEX, nonlethal; Weapon power 1 | General cache, minimum C |
| Saltward Flail (`saltward_flail`) | rare | Enchantment / attack effect | Element: holy; Granted perks: exorcist; Weapon power 2 | The Chapel Gatekeepers: 4% / 6% critical |
| Starburst Caster (`starburst_caster`) | legendary | Active technique | Starburst Discharge, range 6, INT, lethal; Element: void; Weapon power 3 | General cache, minimum A; starfall_omen cache, minimum A |

### Head

| Item (ID) | Rarity | Primary category | Implemented identity | Acquisition |
|---|---|---|---|---|
| Hard Hat (`hard_hat`) | uncommon | Stat / capability focused | Attributes: {'vit': 1}; Capabilities: {'building': 2} | Cold Charcoal Camp: critical rewards check; Silent Industrial Yard: critical rewards check; The Brass Foreman Wakes: critical rewards check |
| Salvager Goggles (`salvager_goggles`) | uncommon | Stat / capability focused | Attributes: {'luk': 1}; Capabilities: {'scavenging': 2, 'building': 1} | General cache, minimum D |
| Death Knight Helm (`death_knight_helm`) | epic | Conditional combat perk | Granted perks: undead_hunter, soul_anchor; Attributes: {'vit': 2, 'str': 1}; Capabilities: {'combat': 5, 'survival': 2} | The Procession's Empty Hearse: cache, minimum A; ashen_procession cache, minimum A |
| Celestial Halo (`celestial_halo`) | mythic | Stat / capability focused | Granted perks: stellar_aegis, astral_sense; Attributes: {'int': 2, 'luk': 2}; Capabilities: {'magic': 6, 'medicine': 3} | Freyja's Share of the Fallen: critical rewards check; The Door Between Dead Stars: cache, minimum S; starfall_omen cache, minimum S |
| Padded Travel Hood (`padded_travel_hood`) | common | Stat / capability focused | Attributes: {'vit': 1} | General cache, minimum E; ashen_procession cache, minimum E |
| Surveyor’s Visor (`surveyors_visor`) | uncommon | Stat / capability focused | Granted perks: scout | General cache, minimum E; arcane_convergence cache, minimum E |
| Cinder Visor (`cinder_visor`) | rare | Tactical equipment rule | Rules: {'resistances': ['fire', 'burn']} | General cache, minimum C |
| Bogkeeper’s Mask (`bogkeeper_mask`) | rare | Tactical equipment rule | Rules: {'resistances': ['poison']}; Granted perks: medic | Herbs Behind the Wall: 3% / 5% critical |
| Lastwatch Helm (`lastwatch_helm`) | epic | Tactical equipment rule | Rules: {'opening_guard': True}; Attributes: {'agi': -1, 'vit': 1} | General cache, minimum B; Smoke over the Hedgerows: cache, minimum B; The Captive Cart: cache, minimum B; goblin_warhost cache, minimum B |
| Empty Court Diadem (`empty_court_diadem`) | legendary | Tactical equipment rule | Rules: {'boss_damage': 2}; Attributes: {'int': 1} | Court of the Empty Crown: 4% / 6% critical · completed chain required |

### Body

| Item (ID) | Rarity | Primary category | Implemented identity | Acquisition |
|---|---|---|---|---|
| Worn Jacket (`worn_jacket`) | common | Stat / capability focused | Attributes: {'vit': 1}; Capabilities: {'survival': 1} | General cache, minimum E |
| Medic Coat (`medic_coat`) | uncommon | Stat / capability focused | Capabilities: {'medicine': 2} | Quarantine House: critical rewards check; Ruined Field Clinic: critical rewards check |
| Reinforced Vest (`reinforced_vest`) | uncommon | Stat / capability focused | Attributes: {'vit': 1}; Capabilities: {'combat': 1, 'survival': 2} | General cache, minimum D; The Black-Banner Ledger: cache, minimum D |
| Ranger Cloak (`ranger_cloak`) | rare | Stat / capability focused | Attributes: {'agi': 1}; Capabilities: {'survival': 3, 'scavenging': 2} | General cache, minimum C; The Black-Banner Ledger: cache, minimum C; Tracks Under the Second Moon: critical rewards check |
| Thunderhide Coat (`thunderhide_coat`) | epic | Stat / capability focused | Granted perks: titan_strength; Attributes: {'vit': 3}; Capabilities: {'survival': 5, 'combat': 2} | The Shepherd of Titans: cache, minimum A; great_beast_tide cache, minimum A |
| Razorwing Cloak (`razorwing_cloak`) | epic | Stat / capability focused | Granted perks: apex_instinct; Attributes: {'agi': 2, 'dex': 1}; Capabilities: {'survival': 4, 'scavenging': 2} | The Shepherd of Titans: cache, minimum B; great_beast_tide cache, minimum B |
| Voidglass Mantle (`voidglass_mantle`) | mythic | Stat / capability focused | Granted perks: void_sight, stellar_aegis; Attributes: {'int': 2, 'vit': 2}; Capabilities: {'magic': 5, 'survival': 4} | The Door Between Dead Stars: cache, minimum A; The Signal Knows Your Name: critical rewards check; starfall_omen cache, minimum A |
| Highway Guard Mantle (`highway_guard_mantle`) | rare | Stat / capability focused | Granted perks: guard; Attributes: {'vit': 1} | Highway Ambush: 18% / 30% critical |
| Quilted Field Vest (`quilted_field_vest`) | common | Stat / capability focused | Attributes: {'vit': 1} | General cache, minimum E; arcane_convergence cache, minimum E |
| Porter’s Coat (`porters_coat`) | uncommon | Tactical equipment rule | Rules: {'carry_strength': 3} | General cache, minimum E; great_beast_tide cache, minimum E |
| Embersmith’s Apron (`embersmith_apron`) | rare | Tactical equipment rule | Rules: {'resistances': ['fire', 'burn'], 'breach_damage': 1} | General cache, minimum C |
| Trollstitch Coat (`trollstitch_coat`) | epic | Conditional combat perk | Granted perks: regeneration; Attributes: {'agi': -1} | General cache, minimum B; ashen_procession cache, minimum B |
| Roadward Mantle (`roadward_mantle`) | rare | Tactical equipment rule | Rules: {'guard_heal': 2} | General cache, minimum C |
| Mercythread Robe (`mercythread_robe`) | legendary | Tactical equipment rule | Rules: {'lifeline': True}; Attributes: {'vit': -1} | The Procession's Empty Hearse: 4% / 6% critical · completed chain required |

### Hands

| Item (ID) | Rarity | Primary category | Implemented identity | Acquisition |
|---|---|---|---|---|
| Work Gloves (`work_gloves`) | common | Stat / capability focused | Capabilities: {'building': 1, 'scavenging': 1} | Collapsed Workshop: critical rewards check; Creekside Scrap Run: critical rewards check; General cache, minimum E |
| Duelist Gloves (`duelist_gloves`) | rare | Stat / capability focused | Attributes: {'dex': 1}; Capabilities: {'combat': 3} | General cache, minimum C |
| Engineer's Bracers (`engineers_bracers`) | epic | Stat / capability focused | Granted perks: masterwork; Attributes: {'str': 1, 'int': 1}; Capabilities: {'building': 4, 'scavenging': 1} | General cache, minimum B; The Price of the Brísingamen: critical rewards check |
| Creekwright Gloves (`creekwright_gloves`) | rare | Stat / capability focused | Granted perks: engineer | Timber Across the Creek: 3% / 5% critical · combat required |
| Armory Breach Gloves (`armory_breach_gloves`) | rare | Stat / capability focused | Granted perks: engineer | The Hidden Goblin Armory: 3% / 5% critical |
| Riveted Work Grips (`riveted_work_grips`) | common | Stat / capability focused | Attributes: {'str': 1} | General cache, minimum E |
| Padded Capture Gloves (`padded_capture_gloves`) | uncommon | Tactical equipment rule | Rules: {'subdue_gloves': True} | The Goblin Pickpockets: 3% / 5% critical |
| Rescue Gloves (`rescue_gloves`) | rare | Tactical equipment rule | Rules: {'carry_strength': 6} | Bells in the Scrap Heap: 3% / 5% critical |
| Breach Gauntlets (`breach_gauntlets`) | rare | Tactical equipment rule | Rules: {'breach_damage': 3}; Attributes: {'agi': -1} | The Hidden Goblin Armory: 5% / 8% critical |
| Meridian Coil Grips (`meridian_coil_grips`) | epic | Active technique | Coil Discharge, range 4, INT, lethal; Element: lightning | The Meridian Calibration: 6% / 10% critical |
| Chieftain’s Chain Grips (`chieftains_chain_grips`) | legendary | Active technique | Chain Restraint, range 2, STR, nonlethal; Rules: {'carry_strength': 3} | Goblin Warcamp: live capture 4% / 6% secured |

### Legs

| Item (ID) | Rarity | Primary category | Implemented identity | Acquisition |
|---|---|---|---|---|
| Cargo Pants (`cargo_pants`) | common | Stat / capability focused | Capabilities: {'survival': 1} | General cache, minimum E |
| Patched Travel Trousers (`patched_travel_trousers`) | common | Stat / capability focused | Attributes: {'vit': 1} | General cache, minimum E |
| Scout’s Trail Leggings (`scout_trail_leggings`) | uncommon | Stat / capability focused | Granted perks: pathfinder | General cache, minimum E |
| Quarry Greaves (`quarry_greaves`) | uncommon | Stat / capability focused | Granted perks: guard; Attributes: {'agi': -1} | Survey the Outcrop: 4% / 6% critical |
| Creekwarden Waders (`creekwarden_waders`) | rare | Tactical equipment rule | Rules: {'water_walk': True} | General cache, minimum C |
| Bramble Chaps (`bramble_chaps`) | rare | Tactical equipment rule | Rules: {'resistances': ['poison']}; Attributes: {'vit': 1} | General cache, minimum C; great_beast_tide cache, minimum C |
| Emberlined Battle Skirt (`emberlined_skirt`) | rare | Tactical equipment rule | Rules: {'resistances': ['fire', 'burn']}; Attributes: {'dex': 1} | General cache, minimum C |
| Astral Fold Wraps (`astral_fold_wraps`) | epic | Tactical equipment rule | Rules: {'opening_guard': True}; Granted perks: magic_resistance | General cache, minimum B; arcane_convergence cache, minimum B |
| Shepherd’s Carrier Wraps (`shepherds_carrier_wraps`) | legendary | Tactical equipment rule | Rules: {'carry_strength': 6, 'throw_range': 1}; Attributes: {'agi': -1} | The Shepherd of Titans: 4% / 6% critical · completed chain required |

### Feet

| Item (ID) | Rarity | Primary category | Implemented identity | Acquisition |
|---|---|---|---|---|
| Work Boots (`work_boots`) | common | Stat / capability focused | Attributes: {'agi': 1}; Capabilities: {'scavenging': 1} | Fresh Goblin Tracks: critical rewards check; General cache, minimum E |
| Trailblazer Boots (`trailblazer_boots`) | rare | Stat / capability focused | Attributes: {'agi': 2}; Capabilities: {'survival': 3, 'scavenging': 1} | General cache, minimum C |
| Gravity Boots (`gravity_boots`) | epic | Tactical equipment rule | Rules: {'water_walk': True, 'rubble_walk': True}; Granted perks: gravity_walker; Attributes: {'agi': 2, 'int': 1}; Capabilities: {'magic': 3, 'survival': 3} | The Meridian Engine: cache, minimum B; The Thread North of Time: critical rewards check; arcane_convergence cache, minimum B |
| Warcamp Command Spur (`warcamp_command_spur`) | rare | Stat / capability focused | Granted perks: pathfinder; Attributes: {'agi': 1} | Goblin Warcamp: 18% / 30% critical |
| Ford Runner Boots (`ford_runner_boots`) | rare | Stat / capability focused | Granted perks: pathfinder | The Unwanted Toll: 3% / 5% critical |
| Raider’s Route Spur (`raiders_route_spur`) | rare | Stat / capability focused | Granted perks: pathfinder | The Road Raiders’ Cache: 3% / 5% critical |
| Softstep Boots (`softstep_boots`) | common | Stat / capability focused | Attributes: {'agi': 1} | General cache, minimum E; great_beast_tide cache, minimum E |
| Rubble Cleats (`rubble_cleats`) | uncommon | Tactical equipment rule | Rules: {'rubble_walk': True} | General cache, minimum E; starfall_omen cache, minimum E |
| Ferryman’s Boots (`ferrymans_boots`) | rare | Tactical equipment rule | Rules: {'water_walk': True}; Granted perks: pathfinder | The Snagged Fishing Line: 3% / 5% critical |
| Counterweight Boots (`counterweight_boots`) | rare | Tactical equipment rule | Rules: {'throw_range': 1} | General cache, minimum C; starfall_omen cache, minimum C |
| Cometstep Boots (`cometstep_boots`) | epic | Tactical equipment rule | Rules: {'water_walk': True, 'rubble_walk': True} | General cache, minimum B; starfall_omen cache, minimum B |
| Starless Anchor Boots (`starless_anchor_boots`) | legendary | Tactical equipment rule | Rules: {'opening_guard': True, 'rubble_walk': True}; Granted perks: magic_resistance | The Door Between Dead Stars: 4% / 6% critical · completed chain required |

### Offhand

| Item (ID) | Rarity | Primary category | Implemented identity | Acquisition |
|---|---|---|---|---|
| Breaching Charge (`breaching_charge`) | rare | Stat / capability focused | Capabilities: {'building': 1} | Abandoned Raider Checkpoint: critical rewards check; Bandit Outpost: critical rewards check; General cache, minimum C; Goblin Warren Purge: critical rewards check; Sealed Old Armory: critical rewards check; The Black-Banner Ledger: critical rewards check |
| Guild Tower Shield (`tower_shield`) | epic | Tactical equipment rule | Rules: {'guard_heal': 2}; Granted perks: shield_wall, guard; Attributes: {'vit': 2}; Capabilities: {'combat': 3, 'survival': 2} | Court of the Empty Crown: cache, minimum B; Court of the Empty Crown: critical rewards check; General cache, minimum B; The Siege That Never Happened: critical rewards check |
| Archmage's Grimoire (`archmage_grimoire`) | mythic | Stat / capability focused | Granted perks: magic_resistance; Attributes: {'int': 2}; Capabilities: {'magic': 5, 'alchemy': 2} | Audience at the Aegis Hall: critical rewards check; General cache, minimum S; The Meridian Engine: critical rewards check |
| Saint's Censer (`saints_censer`) | mythic | Tactical equipment rule | Rules: {'guard_heal': 4}; Granted perks: divine_magic, soul_anchor; Attributes: {'int': 1, 'luk': 1}; Capabilities: {'medicine': 4, 'magic': 4} | General cache, minimum S; The Hall of Unfinished Names: critical rewards check |
| Ironcap Buckler (`ironcap_buckler`) | rare | Tactical equipment rule | Rules: {'opening_guard': True}; Granted perks: shield_wall; Attributes: {'vit': 2}; Capabilities: {'combat': 3, 'survival': 2} | Goblin Warcamp: cache, minimum C; The Captive Cart: cache, minimum C; The Captive Cart: critical rewards check; goblin_warhost cache, minimum C |
| Corpse Lantern (`corpse_lantern`) | epic | Stat / capability focused | Granted perks: soul_anchor; Attributes: {'int': 1}; Capabilities: {'magic': 4, 'survival': 3} | The Bell Beneath the Mud: critical rewards check; The Procession's Empty Hearse: cache, minimum B; ashen_procession cache, minimum B |
| Bottled Storm (`bottled_storm`) | epic | Active technique | Storm Release, range 4, INT, lethal; Granted perks: stormbound; Attributes: {'int': 1, 'luk': 2}; Capabilities: {'magic': 5, 'combat': 2} | The Meridian Engine: cache, minimum A; arcane_convergence cache, minimum A |
| Living Grimoire (`living_grimoire`) | mythic | Stat / capability focused | Granted perks: ley_touched, dream_sense; Attributes: {'int': 2, 'luk': 1}; Capabilities: {'magic': 6, 'alchemy': 3} | The Meridian Engine: cache, minimum S; arcane_convergence cache, minimum S |
| Bell of Last Rites (`bell_of_last_rites`) | legendary | Tactical equipment rule | Rules: {'guard_heal': 3}; Granted perks: keeper_of_last_rites, soul_anchor; Attributes: {'int': 1, 'luk': 2}; Capabilities: {'magic': 4, 'medicine': 4} | The Procession's Empty Hearse: 65% / 85% critical |
| Oathkeeper’s Ward (`oathkeeper_shard`) | epic | Conditional combat perk | Granted perks: magic_resistance, graveward | No mission/cache placement in this audit |
| Plank Buckler (`plank_buckler`) | common | Stat / capability focused | Granted perks: guard | General cache, minimum E; Smoke over the Hedgerows: cache, minimum E; The Captive Cart: cache, minimum E; goblin_warhost cache, minimum E |
| Riveted Guard Shield (`riveted_guard_shield`) | uncommon | Tactical equipment rule | Rules: {'guard_heal': 2} | General cache, minimum E; Smoke over the Hedgerows: cache, minimum E; The Captive Cart: cache, minimum E; goblin_warhost cache, minimum E |
| Field Triage Kit (`field_triage_kit`) | rare | Tactical equipment rule | Rules: {'guard_heal': 4}; Granted perks: medic | General cache, minimum C; ashen_procession cache, minimum C |
| Cartmaster’s Tether Reel (`cartmasters_tether_reel`) | uncommon | Tactical equipment rule | Rules: {'carry_strength': 3} | The Captive Cart: live capture 6% / 8% secured |
| Charred Signal Lantern (`charred_signal_lantern`) | rare | Active technique | Signal Flare, range 3, INT, lethal; Element: fire | General cache, minimum C |
| Glacier Page Focus (`glacier_page_focus`) | rare | Active technique | Glacier Ray, range 4, INT, lethal; Element: ice | General cache, minimum C; arcane_convergence cache, minimum C |
| Tide Bastion (`tide_bastion`) | epic | Tactical equipment rule | Rules: {'opening_guard': True, 'resistances': ['poison']} | The Ward Concord: 4% / 6% critical |
| Meridian Field Projector (`meridian_field_projector`) | legendary | Active technique | Field Lance, range 5, INT, lethal; Element: lightning | The Meridian Engine: 4% / 6% critical · completed chain required |

### Accessory

| Item (ID) | Rarity | Primary category | Implemented identity | Acquisition |
|---|---|---|---|---|
| Field Pack (`field_pack`) | uncommon | Stat / capability focused | Capabilities: {'scavenging': 2} | Abandoned Roadside Store: critical rewards check; Blackpowder Mill: critical rewards check; Breeding Hollow: critical rewards check; Deep Wilds Expedition: critical rewards check; Flooded Underpass: critical rewards check; General cache, minimum D; Map the Under-Roads: critical rewards check; Missing Trapper's Cache: critical rewards check; Plague Ossuary: critical rewards check; Razorwing Cliffs: critical rewards check; Signal from the Hollow Stone: critical rewards check; The Drowned Choir: critical rewards check; The Glasswood: critical rewards check; The Living Library: critical rewards check; Titan Migration: critical rewards check; Yesterday's Caravan: critical rewards check |
| Ember Charm (`ember_charm`) | rare | Stat / capability focused | Capabilities: {'magic': 2} | Mana Squall: critical rewards check; Restless Graves: critical rewards check |
| Reinforced Supply Satchel (`supply_satchel`) | common | Stat / capability focused | Capabilities: {'scavenging': 1, 'survival': 1} | General cache, minimum E |
| Warding Token (`warding_token`) | uncommon | Stat / capability focused | Capabilities: {'magic': 1, 'survival': 1} | General cache, minimum C; The Owl Above the Ruins: critical rewards check |
| Apothecary Belt (`apothecary_belt`) | rare | Stat / capability focused | Attributes: {'int': 1}; Capabilities: {'medicine': 3, 'alchemy': 3} | General cache, minimum C |
| Chieftain's Command Horn (`chieftain_command_horn`) | epic | Stat / capability focused | Granted perks: warhost_command; Attributes: {'luk': 1}; Capabilities: {'combat': 2, 'survival': 2} | No mission/cache placement in this audit |
| Cartmaster's Route Book (`cartmaster_route_book`) | rare | Stat / capability focused | Granted perks: bannerbreaker; Attributes: {'int': 1, 'luk': 1}; Capabilities: {'scavenging': 3, 'survival': 1} | The Captive Cart: cache, minimum C |
| Warhost Banner (`warhost_banner`) | epic | Stat / capability focused | Granted perks: warhost_command; Attributes: {'vit': 1, 'luk': 1}; Capabilities: {'combat': 4, 'survival': 3} | Goblin Warcamp: cache, minimum B; goblin_warhost cache, minimum B |
| Ashen Reliquary (`ashen_reliquary`) | rare | Stat / capability focused | Granted perks: soul_anchor; Attributes: {'luk': 1}; Capabilities: {'magic': 3, 'medicine': 2} | Footprints of the Black Jackal: critical rewards check; The Procession's Empty Hearse: cache, minimum C; ashen_procession cache, minimum C |
| Spellglass Lens (`spellglass_lens`) | rare | Stat / capability focused | Attributes: {'int': 1, 'luk': 1}; Capabilities: {'magic': 4, 'scavenging': 2} | The Meridian Engine: cache, minimum C; arcane_convergence cache, minimum C |
| Alpha Fang (`alpha_fang`) | rare | Stat / capability focused | Granted perks: apex_instinct; Attributes: {'str': 1, 'agi': 1}; Capabilities: {'combat': 3, 'survival': 3} | The Shepherd of Titans: cache, minimum C; great_beast_tide cache, minimum C |
| Starfall Core (`starfall_core`) | mythic | Tactical equipment rule | Rules: {'lifeline': True}; Granted perks: star_touched, stellar_aegis, void_sight; Attributes: {'int': 3, 'luk': 3}; Capabilities: {'magic': 7, 'combat': 3} | The Door Between Dead Stars: cache, minimum S; The Door Between Dead Stars: critical rewards check; starfall_omen cache, minimum S |
| Standard of the Empty Crown (`empty_crown_standard`) | legendary | Stat / capability focused | Granted perks: bannerbreaker, warhost_command; Attributes: {'luk': 2}; Capabilities: {'combat': 3, 'scavenging': 3} | Court of the Empty Crown: 65% / 85% critical |
| Heart of the Meridian (`meridian_heart`) | legendary | Stat / capability focused | Granted perks: meridian_attunement, stormbound; Attributes: {'int': 2, 'luk': 1}; Capabilities: {'magic': 5, 'building': 4} | The Meridian Engine: 60% / 80% critical |
| Titan Shepherd's Horn (`titan_shepherds_horn`) | legendary | Stat / capability focused | Granted perks: titan_speaker, beast_bond; Attributes: {'vit': 2, 'luk': 1}; Capabilities: {'survival': 5, 'combat': 2} | The Shepherd of Titans: 60% / 80% critical |
| Sigil of the Starless Gate (`starless_gate_sigil`) | legendary | Stat / capability focused | Granted perks: riftwalker, void_sight; Attributes: {'int': 2, 'luk': 2}; Capabilities: {'magic': 6, 'survival': 3} | The Door Between Dead Stars: 55% / 75% critical |
| Trapper's Roll (`trappers_roll`) | uncommon | Stat / capability focused | Granted perks: trapper; Attributes: {'dex': 1}; Capabilities: {'survival': 2} | Hold the Hedgerow Watch: 38% / 50% critical |
| Hedgerow Engineer's Kit (`hedgerow_engineers_kit`) | rare | Stat / capability focused | Granted perks: field_fortifier; Attributes: {'int': 1}; Capabilities: {'building': 3, 'survival': 1} | Hold the Hedgerow Watch: 18% / 35% critical |
| Signal-Lens Charm (`signal_lens`) | rare | Stat / capability focused | Granted perks: scout | No mission/cache placement in this audit |
| Toll Clerk’s Signet (`ledger_ring`) | rare | Stat / capability focused | Granted perks: precision_core; Attributes: {'int': 1} | No mission/cache placement in this audit |
| Chapel Binding Thread (`chapel_thread`) | rare | Conditional combat perk | Granted perks: exorcist | No mission/cache placement in this audit |
| Banner Retrieval Seal (`retrieval_seal`) | epic | Stat / capability focused | Granted perks: engineer, bannerbreaker | No mission/cache placement in this audit |
| Cellar Guard Charm (`cellar_guard_charm`) | rare | Stat / capability focused | Granted perks: guard | Rats in the Storehouse: 3% / 5% critical |
| Fencekeeper’s Buckle (`fencekeepers_buckle`) | rare | Stat / capability focused | Granted perks: guard | Wolves at the Fence: 3% / 5% critical |
| Lockkeeper’s Lens (`lockkeepers_lens`) | rare | Stat / capability focused | Granted perks: scout | The Locked Tool Shed: 3% / 5% critical · combat required |
| Garden Healer’s Pin (`garden_healers_pin`) | rare | Stat / capability focused | Granted perks: medic | Herbs Behind the Wall: 3% / 5% critical · combat required |
| Caravan Ledger Seal (`caravan_ledger_seal`) | rare | Stat / capability focused | Granted perks: precision_core | The Caravan’s False Account: 3% / 5% critical |
| Chapel Watch Bead (`chapel_watch_bead`) | rare | Conditional combat perk | Granted perks: graveward | The Chapel Patrol: 3% / 5% critical |
| Calibrator’s Focus (`calibrators_focus`) | rare | Stat / capability focused | Granted perks: magic_resistance | The Meridian Calibration: 3% / 5% critical |
| Ford Envoy’s Signet (`ford_envoys_signet`) | rare | Stat / capability focused | Granted perks: guard | A Compact at the Ford: 3% / 5% critical |
| Wayfarer’s Trade Ring (`merchant_wayfarer_ring`) | rare | Stat / capability focused | Granted perks: pathfinder; Capabilities: {'survival': 1} | No mission/cache placement in this audit |
| Watch-Ford Medallion (`watch_ford_medallion`) | rare | Stat / capability focused | Granted perks: guard, bannerbreaker | No mission/cache placement in this audit |
| Meridian Workshop Ward (`meridian_workshop_ward`) | rare | Stat / capability focused | Granted perks: magic_resistance, engineer | No mission/cache placement in this audit |
| Lantern Route Compass (`lantern_route_compass`) | rare | Stat / capability focused | Granted perks: pathfinder, scout | No mission/cache placement in this audit |
| Parcelkeeper’s String (`parcelkeepers_string`) | common | Stat / capability focused | Capabilities: {'scavenging': 1} | General cache, minimum E |
| Glass Filter Charm (`glass_filter_charm`) | uncommon | Tactical equipment rule | Rules: {'resistances': ['poison']} | General cache, minimum E; ashen_procession cache, minimum E |
| Flicker Charm (`flicker_charm`) | uncommon | Tactical equipment rule | Rules: {'resistances': ['fire', 'burn']} | General cache, minimum E |
| Field Seal Knot (`field_seal_knot`) | rare | Tactical equipment rule | Rules: {'guard_heal': 2} | General cache, minimum C |
| Bloodtrail Pendant (`bloodtrail_pendant`) | rare | Tactical equipment rule | Rules: {'wounded_damage': 2} | General cache, minimum C; Smoke over the Hedgerows: cache, minimum C; The Captive Cart: cache, minimum C; goblin_warhost cache, minimum C |
| Second-Chance Button (`second_chance_button`) | rare | Tactical equipment rule | Rules: {'lifeline': True} | Rats in the Storehouse: 1% / 2% critical |
| Rootbound Heart (`rootbound_heart`) | epic | Conditional combat perk | Granted perks: regeneration | General cache, minimum B; great_beast_tide cache, minimum B |
| Deadstar Orbit Pendant (`deadstar_orbit_pendant`) | mythic | Active technique | Deadstar Orbit, range 5, INT, lethal; Element: void; Rules: {'boss_damage': 2} | Tomb Beyond the Sky: 2% / 4% critical |

### Non-Equipment

| Item (ID) | Rarity | Primary category | Implemented identity | Acquisition |
|---|---|---|---|---|
| Training Manual (`training_manual`) | common | Non-equipment | Consumed to train a perk from Basic to Skilled. | Boar-Rider Patrol: critical rewards check; Bone Collectors: critical rewards check; Bridge-Trapper Gang: critical rewards check; Compass Storm: critical rewards check; Corpse-Lantern Road: critical rewards check; Crystal Rain: critical rewards check; Gather the Fallen Sparks: critical rewards check; General cache, minimum E; Highway Ambush: critical rewards check; Razorboar Nest: critical rewards check; Runaway Clay Golem: critical rewards check; Smoke over the Hedgerows: critical rewards check; Spellglass Field: critical rewards check; Star-Metal Thieves: critical rewards check; The Bottled Storm: critical rewards check; The Silent Farm: critical rewards check; The Thirteenth Bell: critical rewards check; The Tithe Convoy: critical rewards check; The Webbed Caravan: critical rewards check; The Whispering Well: critical rewards check; Tracks Larger than Wagons: critical rewards check; Turn the Horned Stampede: critical rewards check |
| Specialist Tome (`specialist_tome`) | rare | Non-equipment | Consumed to train a perk from Skilled to Expert. | Beneath the Thunderherd: critical rewards check; Black Observatory: critical rewards check; Break the Siege Line: critical rewards check; Circle of Crooked Staves: critical rewards check; General cache, minimum B; Gravity Well: critical rewards check; Hollow Cathedral: critical rewards check; Hunt of the White Fang: critical rewards check; Knight without a Grave: critical rewards check; Leviathan Crossing: critical rewards check; Market of Borrowed Dreams: critical rewards check; The Black Hearse: critical rewards check; The Blood-Moon Den: critical rewards check; The Forest Without Footprints: critical rewards check; The Gravity Scar: critical rewards check; The Hall of Unfinished Names: critical rewards check; The Ironcap Vanguard: critical rewards check; The Price of the Brísingamen: critical rewards check; The Prism Tower: critical rewards check; The Procession's Empty Hearse: critical rewards check; The Shepherd of Titans: critical rewards check; The Siege That Never Happened: critical rewards check; Voidsent Pilgrims: critical rewards check; Young Dragon's Roost: critical rewards check |
| Mastery Codex (`mastery_codex`) | mythic | Non-equipment | Consumed to train a perk from Expert to Master. | Audience at the Aegis Hall: critical rewards check; Court of the Empty Crown: critical rewards check; Fallen-Star Citadel: critical rewards check; Freyja's Share of the Fallen: critical rewards check; General cache, minimum S; The Door Between Dead Stars: critical rewards check; The Emerald Throne: critical rewards check; The Last Arrow of Diana: critical rewards check; The Last Funeral: critical rewards check; The Meridian Engine: critical rewards check; The Second Sun: critical rewards check; The Weight of a Living Heart: critical rewards check; Wake of the World-Eater: critical rewards check; Zero Hour: critical rewards check |
| Goblin War Token (`goblin_war_token`) | event | Non-equipment | A marked token recovered from the Green Warhost. | goblin_warhost keepsake check |
| Consecrated Grave Ash (`grave_ash`) | event | Non-equipment | Ash gathered after quieting one of the restless dead. | ashen_procession keepsake check |
| Raw Mana Prism (`mana_prism`) | event | Non-equipment | A stable prism formed during an Arcane Convergence. | arcane_convergence keepsake check |
| Great Beast Heartstone (`beast_heart`) | event | Non-equipment | A hardened core left by a creature of the Great Beast Tide. | great_beast_tide keepsake check |
| Starfall Shard (`starfall_shard`) | event | Non-equipment | A warm fragment of matter that fell from beyond the sky. | starfall_omen keepsake check |
| Black-Banner Cipher (`black_banner_cipher`) | story | Non-equipment | A decoded strip of the raiders' tribute ledger. It proves the attacks were organized around old royal sites. | The Black-Banner Ledger: 70% / 90% critical |
| Mudbound Bell Clapper (`mudbound_clapper`) | story | Non-equipment | The silenced heart of a chapel bell that once called Lareth's forgotten dead by name. | The Bell Beneath the Mud: 65% / 85% critical |
| Brass Foreman's Key (`brass_foreman_key`) | story | Non-equipment | A command key carrying the three-ring seal of the Meridian Collegium. | The Brass Foreman Wakes: 65% / 85% critical |
| Colossus Heartblood (`colossus_heartblood`) | story | Non-equipment | A crystallized drop freely given by the wounded titan after its treatment. | The Wounded Colossus: 60% / 80% critical |
| Echoing Starstone (`echoing_starstone`) | story | Non-equipment | A hollow fragment that remembers the names of those who answered its signal. | The Signal Knows Your Name: 55% / 75% critical |


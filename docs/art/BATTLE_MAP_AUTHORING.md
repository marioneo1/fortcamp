# Battle Map Authoring

Fortcamp battle maps live in `backend/battle_maps.py`. An encounter chooses a map by calling `compile_battle_map(map_id)`. The compiler expands compact painted regions into a complete tile grid and copies the result into combat state, so saved battles retain the exact map they started with.

## Blueprint shape

```python
"example_crossing": {
    "name": "Example Crossing",
    "theme": "wilds",
    "width": 12,
    "height": 8,
    "default_ground": "grass",
    "paint": [
        {"material": "dirt", "rect": [0, 3, 12, 2]},
        {"material": "water", "tiles": [[5, 0], [5, 1], [5, 2]]},
    ],
    "void_tiles": [],
    "terrain": [],
    "elevation": [],
    "extraction": {"name": "West Road", "tiles": [{"x": 0, "y": 3}]},
    "enemy_extraction": {"name": "East Road", "tiles": [{"x": 11, "y": 3}]},
}
```

`rect` is `[x, y, width, height]`. Later paint entries overwrite earlier ones, which makes it easy to lay a road over grass and then add puddles or timber sections. `tiles` is a list of `[x, y]` coordinates for irregular shapes.

Available ground materials are `grass`, `dirt`, `mud`, `timber`, `stone`, and `water`. Their movement rules and descriptions live in `GROUND_MATERIALS`. Ground movement costs are enforced by the combat engine, not only displayed by the browser.

Props belong in `terrain`. Every prop needs a unique `id`, coordinate, `kind`, and blocking state. Destructible props also declare `hp`, `armor`, `destroyed_kind`, and `destroyed_movement_cost`. Elevation tiles declare `height`; add `impassable: True` for sheer terrain.

The frontend derives texture variation and material boundary edges from coordinates. Authors should describe terrain rather than choose a visual variant. This preserves the art direction and keeps maps deterministic.

## Validation

Run:

```text
.venv\Scripts\python.exe tools\validate_battle_maps.py
```

The validator catches unknown materials, out-of-bounds paint, duplicate terrain IDs, and invalid terrain, elevation, void, or extraction coordinates. The full test suite also compiles every registered map.

## Generated scenario process

Reusable mission forms call `compile_generated_battle_map(scenario, mission_seed)`. The seed makes a claimed mission stable across restarts. A scenario generator should follow this order:

1. Choose map dimensions from the scenario family and rank band. Rank controls complexity and threat quality; party size controls enemy count. Do not scale every number at once.
2. Author broad regions first: roads, rooms, fields, water, and elevation bands. Never choose an unrelated ground material independently for every cell.
3. Reserve the critical routes, objective space, deployment area, enemy entry area, and exits before placing scenery.
4. Roll decoration only in non-reserved cells. A small subset may become blocking or destructible terrain so decoration cannot accidentally seal the mission route.
5. Add scenario metadata such as `spawn_zones`, `preparation_zone`, `deployment_zone`, and `objective_position`.
6. Validate the finished blueprint and copy the compiled result into battle state.

`hedgerow_signal_site` is the investigation example. `frontier_watch_defense` is the prepared-defense example. New maps should reuse this compiler and add a named scenario generator rather than embedding random tile placement in combat code.

## Props and interactables

Add a prop when it creates a decision or communicates the objective. Current useful categories are:

- cover and route control: barricades, gates, walls, trees, boulders;
- hazards: spike traps, snares, fire, water, pits;
- elevation access: platforms, ladders, banks;
- objectives: cages, signal devices, levers, altars, chests;
- portable battlefield objects: crates, stones, bodies, and mission evidence.

Pure visual clutter belongs in `decorations`. Anything that blocks, breaks, opens, triggers, can be carried, or changes elevation belongs in `terrain` or `objects`. Generate new art only when an encounter needs a readable new interaction; a different mission name alone does not justify another prop.

## Defense preparation

A defense battle begins with `status: "preparing"`. Its `preparation` record contains a budget, legal placement and deployment zones, available defenses, and current placements. Basic barricades and spike traps are universal. Party composition and equipped gear can add options or budget:

- Kobold, Trapper, or trapping gear unlocks snares;
- Engineer or construction gear unlocks a raised firing platform;
- defense gear adds preparation points;
- racial defense bonuses add a capped budget bonus.

Players may reposition party members and refund placements until they start the battle. Once initiative begins, prepared objects use the normal terrain, elevation, destructible-object, and tile-entry systems. This keeps defense preparation compatible with AI, pathfinding, attacks, and future larger maps.

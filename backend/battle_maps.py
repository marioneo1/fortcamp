"""Declarative tactical-map blueprints and the small compiler used by combat."""

from copy import deepcopy
import random
from .location_maps import MATERIALS as LOCATION_MATERIALS, location_blueprint


GROUND_MATERIALS = {
    "grass": {"name": "Grass", "movement_cost": 1, "description": "Firm natural ground."},
    "dirt": {"name": "Packed Dirt", "movement_cost": 1, "description": "A worn trail or camp floor."},
    "mud": {"name": "Deep Mud", "movement_cost": 2, "description": "Wet ground that costs 2 movement."},
    "timber": {"name": "Timber", "movement_cost": 1, "description": "Boards, platforms, and wagon decking."},
    "stone": {"name": "Stone", "movement_cost": 1, "description": "Hard rock or laid masonry."},
    "water": {"name": "Shallow Water", "movement_cost": 2, "description": "Costs 2 movement and extinguishes Burn."},
}
GROUND_MATERIALS.update(LOCATION_MATERIALS)


BATTLE_MAPS = {
    "goblin_warcamp": {
        "name": "Goblin Warcamp",
        "theme": "warhost",
        "width": 8,
        "height": 8,
        "default_ground": "grass",
        "paint": [
            {"material": "dirt", "rect": [1, 1, 6, 6]},
            {"material": "water", "tiles": [[4, 7], [5, 7], [6, 7]]},
            {"material": "stone", "tiles": [[0, 0], [1, 0], [4, 1]]},
            {"material": "timber", "tiles": [[5, 0], [6, 2]]},
        ],
        "void_tiles": [],
        "decorations": [
            {"id": "camp_oak", "name": "Old Camp Oak", "x": 7, "y": 0, "sprite": "oak_tree"},
            {"id": "camp_pine", "name": "Boundary Pine", "x": 0, "y": 1, "sprite": "pine_tree"},
            {"id": "cliff_boulder", "name": "Mossy Cliff Boulder", "x": 1, "y": 0, "sprite": "mossy_boulder"},
            {"id": "camp_logs", "name": "Cut Camp Logs", "x": 1, "y": 5, "sprite": "cut_log_pile"},
            {"id": "camp_shrub", "name": "Thorny Camp Brush", "x": 7, "y": 7, "sprite": "thorny_bramble"},
        ],
        "terrain": [
            *[
                {"id": f"palisade_{x}", "name": "Scrap Palisade", "x": x, "y": 3,
                 "kind": "palisade", "blocking": True, "destructible": True,
                 "hp": 12, "max_hp": 12, "armor": 2, "movement_cost": 1,
                 "destroyed_kind": "rubble", "destroyed_movement_cost": 2}
                for x in (0, 2, 3, 4, 5, 7)
            ],
            {"id": "cookfire", "name": "Cookfire", "x": 2, "y": 5, "kind": "cookfire", "blocking": False, "movement_cost": 1},
            {"id": "watchtower", "name": "Watchtower", "x": 5, "y": 0, "kind": "watchtower", "blocking": True, "movement_cost": 1},
            *[
                {"id": f"water_{x}", "name": "Shallow Water", "x": x, "y": 7,
                 "kind": "shallow_water", "blocking": False, "movement_cost": 2, "tags": ["water"]}
                for x in (4, 5, 6)
            ],
            {"id": "camp_pit", "name": "Refuse Pit", "x": 7, "y": 6, "kind": "pit",
             "blocking": True, "blocks_sight": False, "requires_flying": True, "movement_cost": 1},
        ],
        "elevation": [
            {"x": 4, "y": 1, "height": 1, "kind": "command_mound"},
            {"x": 6, "y": 2, "height": 1, "kind": "firing_platform"},
            {"x": 0, "y": 0, "height": 2, "kind": "rocky_rise"},
            {"x": 1, "y": 0, "height": 4, "kind": "high_cliff"},
        ],
        "extraction": {"name": "South Approach", "tiles": [{"x": x, "y": 7} for x in range(4)]},
        "enemy_extraction": {"name": "Broken Camp Perimeter", "tiles": [{"x": 7, "y": y} for y in range(8)] + [{"x": x, "y": 0} for x in (2, 3, 4, 6)]},
    },
    "captive_cart_road": {
        "name": "Warhost Cart Road",
        "theme": "warhost-road",
        "width": 10,
        "height": 7,
        "default_ground": "grass",
        "paint": [
            {"material": "dirt", "rect": [0, 2, 10, 4]},
            {"material": "mud", "tiles": [[4, 3], [5, 3], [5, 4]]},
            {"material": "timber", "tiles": [[8, 2], [8, 3]]},
            {"material": "stone", "tiles": [[9, 2]]},
        ],
        "void_tiles": [{"x": 4, "y": 0}, {"x": 5, "y": 0}, {"x": 4, "y": 6}, {"x": 5, "y": 6}],
        "decorations": [
            {"id": "road_oak", "name": "Roadside Oak", "x": 2, "y": 0, "sprite": "oak_tree"},
            {"id": "road_pine", "name": "Roadside Pine", "x": 7, "y": 0, "sprite": "pine_tree"},
            {"id": "road_boulder", "name": "Roadside Boulder", "x": 9, "y": 6, "sprite": "rounded_boulder"},
            {"id": "road_brush", "name": "Roadside Brush", "x": 2, "y": 6, "sprite": "dense_shrub"},
        ],
        "terrain": [
            {"id": "cart_body", "name": "Shielded Prison Cart", "x": 8, "y": 3,
             "kind": "wagon", "sprite": "prison_wagon", "art_scale": 2, "blocking": True, "blocks_sight": True, "destructible": True,
             "hp": 20, "max_hp": 20, "armor": 3, "destroyed_kind": "rubble",
             "destroyed_sprite": "prison_wagon_broken", "destroyed_movement_cost": 2},
            *[
                {"id": f"road_mud_{index}", "name": "Deep Road Mud", "x": x, "y": y,
                 "kind": "shallow_water", "blocking": False, "movement_cost": 2, "tags": ["water"]}
                for index, (x, y) in enumerate(((4, 3), (5, 3), (5, 4)), 1)
            ],
        ],
        "elevation": [
            {"x": 8, "y": 2, "height": 1, "kind": "wagon_roof"},
            {"x": 9, "y": 2, "height": 1, "kind": "road_bank"},
        ],
        "extraction": {"name": "Guild Ambush Line", "tiles": [{"x": 0, "y": y} for y in range(2, 7)]},
        "enemy_extraction": {"name": "Warhost Escape Road", "tiles": [{"x": 9, "y": y} for y in range(1, 6)]},
    },
}


def _coordinates(entry: dict) -> list[tuple[int, int]]:
    coordinates = [tuple(tile) for tile in entry.get("tiles", [])]
    if "rect" in entry:
        x, y, width, height = entry["rect"]
        coordinates.extend((column, row) for row in range(y, y + height) for column in range(x, x + width))
    return coordinates


def occupied_tiles(entry: dict) -> list[tuple[int, int]]:
    """Return every grid cell covered by an anchored map entity."""
    footprint = entry.get("footprint", [1, 1])
    width, height = max(1, int(footprint[0])), max(1, int(footprint[1]))
    if int(entry.get("rotation", 0)) % 180:
        width, height = height, width
    x, y = int(entry.get("x", -1)), int(entry.get("y", -1))
    return [(x + dx, y + dy) for dy in range(height) for dx in range(width)]


def validate_battle_map(map_id: str, blueprint: dict | None = None) -> list[str]:
    data = blueprint or BATTLE_MAPS.get(map_id)
    if not data:
        return [f"Unknown battle map: {map_id}"]
    problems: list[str] = []
    width, height = int(data.get("width", 0)), int(data.get("height", 0))
    if width < 1 or height < 1:
        problems.append("width and height must be positive")

    def check(x: int, y: int, label: str) -> None:
        if x < 0 or y < 0 or x >= width or y >= height:
            problems.append(f"{label} ({x}, {y}) is outside {width}x{height}")

    if data.get("default_ground") not in GROUND_MATERIALS:
        problems.append(f"unknown default ground {data.get('default_ground')!r}")
    for index, entry in enumerate(data.get("paint", [])):
        if entry.get("material") not in GROUND_MATERIALS:
            problems.append(f"paint {index} uses unknown material {entry.get('material')!r}")
        for x, y in _coordinates(entry):
            check(x, y, f"paint {index}")
    for index, decoration in enumerate(data.get("decorations", [])):
        for x, y in occupied_tiles(decoration):
            check(x, y, f"decoration {decoration.get('id', index)}")
    ids: set[str] = set()
    for index, terrain in enumerate(data.get("terrain", [])):
        terrain_id = terrain.get("id")
        if not terrain_id or terrain_id in ids:
            problems.append(f"terrain {index} has a missing or duplicate id")
        ids.add(terrain_id)
        for x, y in occupied_tiles(terrain):
            check(x, y, f"terrain {terrain_id or index}")
    for group in ("void_tiles", "elevation"):
        for index, tile in enumerate(data.get(group, [])):
            check(int(tile.get("x", -1)), int(tile.get("y", -1)), f"{group} {index}")
    for group in ("extraction", "enemy_extraction"):
        for index, tile in enumerate(data.get(group, {}).get("tiles", [])):
            check(int(tile.get("x", -1)), int(tile.get("y", -1)), f"{group} {index}")
    return problems


def compile_battle_map(map_id: str) -> dict:
    blueprint = BATTLE_MAPS.get(map_id)
    problems = validate_battle_map(map_id, blueprint)
    if problems:
        raise ValueError(f"Invalid battle map {map_id}: {'; '.join(problems)}")
    data = deepcopy(blueprint)
    width, height = data["width"], data["height"]
    material_by_coordinate = {
        (x, y): data["default_ground"] for y in range(height) for x in range(width)
    }
    for entry in data.pop("paint", []):
        for coordinate in _coordinates(entry):
            material_by_coordinate[coordinate] = entry["material"]
    data["map_id"] = map_id
    data["ground_materials"] = deepcopy(GROUND_MATERIALS)
    data["ground_tiles"] = [
        {"x": x, "y": y, "material": material_by_coordinate[(x, y)]}
        for y in range(height) for x in range(width)
    ]
    data.pop("default_ground", None)
    data.pop("name", None)
    return data


def generated_scenario_blueprint(scenario: str, seed: str) -> dict:
    """Build a coherent, repeatable map from authored zones and safe lanes.

    Generated maps use large regions and reserved routes instead of choosing a
    random material for every cell.  The same mission seed always produces the
    same map, so an active encounter cannot change after a restart.
    """
    if scenario.startswith('location_'):
        return location_blueprint(scenario.removeprefix('location_'), seed)
    if scenario.startswith("contract_"):
        return _contract_blueprint(scenario.removeprefix("contract_"), seed)
    if scenario == "frontier_watch_defense":
        return _frontier_watch_defense_blueprint(seed)
    if scenario != "hedgerow_signal_site":
        raise ValueError(f"Unknown generated scenario: {scenario}")
    rng = random.Random(f"map:{scenario}:{seed}")
    width, height = 12, 9
    road_y = rng.choice((3, 4, 5))
    clearing_x = rng.choice((7, 8, 9))
    reserved = {
        *((x, road_y) for x in range(width)),
        *((x, y) for x in range(0, 3) for y in range(max(0, road_y - 1), min(height, road_y + 2))),
        *((x, y) for x in range(clearing_x - 1, min(width, clearing_x + 2)) for y in range(road_y - 1, road_y + 2)),
    }
    edge_cells = [
        (x, y) for y in range(height) for x in range(width)
        if (x, y) not in reserved and (y <= 1 or y >= height - 2 or x >= width - 2)
    ]
    rng.shuffle(edge_cells)
    tree_cells = edge_cells[:14]
    remaining = [cell for cell in edge_cells if cell not in set(tree_cells)]
    boulder_cells = remaining[:4]
    decorations = [
        {"id": f"signal_tree_{index}", "name": "Hedgerow Tree", "x": x, "y": y,
         "sprite": rng.choice(("oak_tree", "pine_tree"))}
        for index, (x, y) in enumerate(tree_cells[5:], 1)
    ] + [
        {"id": f"signal_rock_{index}", "name": "Field Boulder", "x": x, "y": y,
         "sprite": rng.choice(("rounded_boulder", "mossy_boulder"))}
        for index, (x, y) in enumerate(boulder_cells, 1)
    ]
    # Decorations provide visual mass. A smaller subset blocks movement and
    # creates tactical cover without closing the route between both sides.
    terrain = [
        {"id": f"blocking_tree_{index}", "name": "Dense Hedgerow", "x": x, "y": y,
         "kind": "tree", "sprite": rng.choice(("oak_tree", "pine_tree")),
         "blocking": True, "blocks_sight": True, "destructible": True,
         "hp": 18, "max_hp": 18, "armor": 1, "destroyed_kind": "rubble",
         "destroyed_sprite": "cut_log_pile", "destroyed_movement_cost": 2}
        for index, (x, y) in enumerate(tree_cells[:5], 1)
    ]
    return {
        "name": "Hedgerow Signal Site", "theme": "woodland-investigation",
        "width": width, "height": height, "default_ground": "grass",
        "paint": [
            {"material": "dirt", "rect": [0, road_y, width, 1]},
            {"material": "dirt", "rect": [clearing_x - 1, road_y - 1, 3, 3]},
            {"material": "mud", "tiles": [[4, road_y], [5, road_y]]},
        ],
        "void_tiles": [], "decorations": decorations, "terrain": terrain,
        "elevation": [
            {"x": clearing_x, "y": max(0, road_y - 2), "height": 1, "kind": "low_rise"},
            {"x": clearing_x + 1, "y": max(0, road_y - 2), "height": 1, "kind": "low_rise"},
        ],
        "extraction": {"name": "Fortcamp Road", "tiles": [{"x": 0, "y": y} for y in range(max(0, road_y - 1), min(height, road_y + 2))]},
        "enemy_extraction": {"name": "Far Hedgerow", "tiles": [{"x": width - 1, "y": y} for y in range(height)]},
        "spawn_zones": {
            "player": [{"x": x, "y": y} for x in range(0, 3) for y in range(max(0, road_y - 1), min(height, road_y + 2))],
            "enemy": [{"x": x, "y": y} for x in range(clearing_x - 1, clearing_x + 2) for y in range(road_y - 1, road_y + 2)],
        },
    }


def _frontier_watch_defense_blueprint(seed: str) -> dict:
    """Create a readable defense map with a road, fields, and wooded flanks.

    The layout is authored in broad regions and only its dressing varies by
    seed. This avoids noisy tile soup while keeping repeat contracts distinct.
    """
    rng = random.Random(f"map:frontier_watch_defense:{seed}")
    width, height = 14, 10
    road_y = rng.choice((4, 5))
    # The central road and both staging areas must stay open regardless of
    # decorative rolls. Preparation may deliberately close parts of them.
    reserved = {
        *((x, y) for x in range(width) for y in range(road_y - 1, road_y + 2)),
        *((x, y) for x in range(1, 5) for y in range(2, 8)),
        *((x, y) for x in range(10, 14) for y in range(1, 9)),
    }
    candidates = [
        (x, y) for y in range(height) for x in range(width)
        if (x, y) not in reserved and x not in {0, width - 1}
    ]
    rng.shuffle(candidates)
    blocking_cells = candidates[:8]
    dressing_cells = candidates[8:20]
    terrain = [
        {
            "id": f"watch_tree_{index}", "name": "Hedgerow Tree", "x": x, "y": y,
            "kind": "tree", "sprite": rng.choice(("oak_tree", "pine_tree")),
            "blocking": True, "blocks_sight": True, "destructible": True,
            "hp": 18, "max_hp": 18, "armor": 1, "destroyed_kind": "rubble",
            "destroyed_sprite": "cut_log_pile", "destroyed_movement_cost": 2,
        }
        for index, (x, y) in enumerate(blocking_cells, 1)
    ]
    decorations = [
        {
            "id": f"watch_dressing_{index}", "name": "Frontier Growth", "x": x, "y": y,
            "sprite": rng.choice(("dense_shrub", "thorny_bramble", "rounded_boulder")),
        }
        for index, (x, y) in enumerate(dressing_cells, 1)
    ]
    preparation_zone = [
        {"x": x, "y": y} for x in range(5, 10) for y in range(1, 9)
        if (x, y) not in blocking_cells
    ]
    deployment_zone = [
        {"x": x, "y": y} for x in range(1, 5) for y in range(2, 8)
    ]
    return {
        "name": "Hedgerow Watch", "theme": "frontier-defense",
        "width": width, "height": height, "default_ground": "grass",
        "paint": [
            {"material": "dirt", "rect": [0, road_y - 1, width, 3]},
            {"material": "mud", "tiles": [[7, road_y - 1], [8, road_y], [9, road_y + 1]]},
            {"material": "timber", "rect": [2, road_y - 1, 2, 3]},
            {"material": "stone", "tiles": [[4, road_y - 1], [4, road_y], [4, road_y + 1]]},
        ],
        "void_tiles": [], "decorations": decorations, "terrain": terrain,
        "elevation": [
            {"x": 3, "y": road_y - 2, "height": 1, "kind": "watch_bank"},
            {"x": 3, "y": road_y + 2, "height": 1, "kind": "watch_bank"},
        ],
        "extraction": {"name": "Fortcamp Road", "tiles": [{"x": 0, "y": y} for y in range(2, 8)]},
        "enemy_extraction": {"name": "Eastern Tree Line", "tiles": [{"x": width - 1, "y": y} for y in range(1, 9)]},
        "spawn_zones": {
            "player": deployment_zone,
            "enemy": [{"x": x, "y": y} for x in range(11, 14) for y in range(1, 9)],
        },
        "preparation_zone": preparation_zone,
        "deployment_zone": deployment_zone,
        "objective_position": {"x": 2, "y": road_y},
    }


def compile_generated_battle_map(scenario: str, seed: str) -> dict:
    map_id = f"generated:{scenario}:{seed}"
    blueprint = generated_scenario_blueprint(scenario, seed)
    problems = validate_battle_map(map_id, blueprint)
    if problems:
        raise ValueError(f"Invalid generated battle map {scenario}: {'; '.join(problems)}")
    data = deepcopy(blueprint)
    width, height = data["width"], data["height"]
    material_by_coordinate = {(x, y): data["default_ground"] for y in range(height) for x in range(width)}
    for entry in data.pop("paint", []):
        for coordinate in _coordinates(entry):
            material_by_coordinate[coordinate] = entry["material"]
    data["map_id"] = map_id
    data["scenario_id"] = scenario
    data["ground_materials"] = deepcopy(GROUND_MATERIALS)
    data["ground_tiles"] = [
        {"x": x, "y": y, "material": material_by_coordinate[(x, y)]}
        for y in range(height) for x in range(width)
    ]
    data.pop("default_ground", None)
    data.pop("name", None)
    return data


def _contract_blueprint(layout: str, seed: str) -> dict:
    """Broad material zones, two open lanes, and reserved deployment cells."""
    if layout not in {"road", "camp", "ruin", "court"}:
        raise ValueError(f"Unknown contract layout: {layout}")
    rng = random.Random(f"contract-map:{layout}:{seed}")
    width, height = 12, 9
    stone = layout in {"ruin", "court"}
    terrain = []
    # Cover lies between both forces but never closes the central or flank lanes.
    for index, (x,y) in enumerate(((5,2),(6,6),(7,2),(4,6))):
        terrain.append({"id": f"contract_cover_{index}", "name": "Broken Masonry" if stone else "Road Barricade",
            "x":x,"y":y,"kind":"wall" if stone else "palisade", "blocking":True,
            "destructible":True,"hp":16,"max_hp":16,"armor":2,"destroyed_kind":"rubble","destroyed_movement_cost":2})
    decorations = [] if stone else [
        {"id": f"edge_tree_{x}_{y}", "name": "Boundary Tree", "x":x,"y":y,"sprite":rng.choice(("oak_tree","pine_tree"))}
        for x,y in ((2,0),(5,0),(8,0),(3,8),(7,8),(10,8))
    ]
    paint = [{"material":"dirt","rect":[0,3,width,3]}] if not stone else []
    if layout == "camp":
        paint.append({"material":"dirt","rect":[8,1,4,6]})
    return {"name": f"Contract {layout}", "theme":f"contract-{layout}","width":width,"height":height,
        "default_ground":"stone" if stone else "grass", "paint":paint,"void_tiles":[],
        "terrain":terrain,"decorations":decorations,
        "elevation":[{"x":9,"y":2,"height":1,"kind":"firing_bank"}],
        "extraction":{"name":"Guild Approach","tiles":[{"x":0,"y":y} for y in range(2,7)]},
        "enemy_extraction":{"name":"Far Approach","tiles":[{"x":11,"y":y} for y in range(1,8)]},
        "spawn_zones":{"player":[{"x":x,"y":y} for x,y in ((1,4),(1,3),(1,5),(2,4))],
                       "enemy":[{"x":x,"y":y} for x,y in ((9,4),(8,3),(8,5),(9,2),(9,6),(10,3),(10,5),(10,4))]}}

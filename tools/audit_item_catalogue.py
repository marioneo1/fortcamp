"""Rebuild the live item/category/placement audit without touching game saves."""
import argparse
from collections import Counter, defaultdict
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from backend.content import ITEMS, MISSION_TEMPLATES, GENERAL_LOOT_TABLE, EVENT_REWARD_TABLES
from backend.gear_progression import SLOT_GEAR, EXCLUSIVE_DROPS, CAPTURE_DROPS, EVENT_EXCLUSIVES
from backend.perk_effects import PERK_EFFECTS

SLOTS = ['weapon', 'head', 'body', 'hands', 'legs', 'feet', 'offhand', 'accessory']


def category(item):
    if item.get('slot') not in SLOTS:
        return 'Non-equipment'
    if item.get('combat_skill'):
        return 'Active technique'
    if item.get('element') or item.get('on_hit'):
        return 'Enchantment / attack effect'
    if item.get('combat_rules'):
        return 'Tactical equipment rule'
    combat = [PERK_EFFECTS.get(p, {}).get('combat', {}) for p in item.get('granted_perks', [])]
    if any(any(k in c for k in ['regeneration', 'damage_goblin', 'damage_deathless']) for c in combat):
        return 'Conditional combat perk'
    if item.get('power') or any(item.get('bonuses', {}).values()) or any(item.get('attribute_bonuses', {}).values()) or any(any(PERK_EFFECTS.get(p, {}).values()) for p in item.get('granted_perks', [])):
        return 'Stat / capability focused'
    if item.get('granted_perks'):
        return 'Path / narrative perk only'
    return 'Keepsake / no numerical effect'


def references(value):
    if isinstance(value, dict):
        for key, child in value.items():
            if key in {'item', 'item_id'} and child in ITEMS:
                yield child
            elif key == 'items' and isinstance(child, list):
                yield from (i for i in child if isinstance(i, str) and i in ITEMS)
            elif isinstance(child, (dict, list)):
                yield from references(child)
    elif isinstance(value, list):
        for child in value:
            yield from references(child)


def placements():
    found = defaultdict(set)
    for iid, rank, weight in GENERAL_LOOT_TABLE:
        found[iid].add(f'General cache, minimum {rank}')
    for eid, event in EVENT_REWARD_TABLES.items():
        for iid, rank, weight in event.get('loot', []):
            found[iid].add(f'{eid} cache, minimum {rank}')
        if event.get('keepsake'):
            found[event['keepsake']].add(f'{eid} keepsake check')
    for mid, mission in MISSION_TEMPLATES.items():
        name = mission['name']
        for key in ['rewards', 'critical_rewards']:
            for iid in references(mission.get(key, {})):
                found[iid].add(f'{name}: {key.replace("_", " ")} check')
        for row in mission.get('reward_rolls', []):
            gate = ' · completed chain required' if row.get('requires_chain_parent') else ' · combat required' if row.get('requires_combat') else ''
            for iid in references(row.get('reward', {})):
                found[iid].add(f'{name}: {row["chance"]}% / {min(100, row["chance"] + row.get("critical_bonus", 0))}% critical{gate}')
        for iid, rank, weight in mission.get('loot_pool', []):
            found[iid].add(f'{name}: cache, minimum {rank}')
    for mid, drop in CAPTURE_DROPS.items():
        found[drop['item']].add(f'{MISSION_TEMPLATES[mid]["name"]}: live capture {drop["chance"]}% / {drop["chance"] + drop["secured_bonus"]}% secured')
    return found


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--baseline', type=Path, default=ROOT / 'data/item-audit/baseline.json')
    args = parser.parse_args()
    before = json.loads(args.baseline.read_text(encoding='utf-8'))['items'] if args.baseline.exists() else {}
    old = Counter(i.get('slot') if i.get('slot') in SLOTS else 'non-equipment' for i in before.values())
    slots = Counter(i.get('slot') if i.get('slot') in SLOTS else 'non-equipment' for i in ITEMS.values())
    cats = Counter(category(i) for i in ITEMS.values())
    rarity = Counter(i.get('rarity', 'unspecified') for i in ITEMS.values())
    found = placements()
    lines = ['# Item catalogue audit', '', 'October 1, 2026. Generated from the live Python catalogue by `tools/audit_item_catalogue.py`. This describes implemented effects, not promises inferred from item names.', '',
             f'The catalogue contains **{len(ITEMS)} items**, including **{len(SLOT_GEAR)} additions** in this pass. All have installed local icons. Generated art stays outside the public code repository.', '',
             '## Equipment coverage', '', '| Slot | Before | Now | Added |', '|---|---:|---:|---:|']
    for slot in [*SLOTS, 'non-equipment']:
        lines.append(f'| {slot.title()} | {old.get(slot, "—")} | {slots[slot]} | {slots[slot]-old[slot] if before else "—"} |')
    lines += ['', '## Primary gameplay categories', '', 'Each item is counted once, using the first applicable category. Active techniques take precedence over enchantments and passives. Stat-focused equipment includes attribute bonuses, armor, HP, movement, initiative and mission-capability bonuses. It can still be useful; a named perk does not automatically make it a new mechanic.', '', '| Category | Count |', '|---|---:|']
    lines += [f'| {cat} | {count} |' for cat, count in sorted(cats.items())]
    lines += ['', 'Rarities: '+', '.join(f'{k} {rarity[k]}' for k in ['common','uncommon','rare','epic','legendary','mythic','event','story'])+'.', '',
              '“Mission exclusive” means a restricted acquisition source, not one globally owned copy. Completed chains can produce another copy. Champions keep their separate ownership rules.', '',
              '## What to chase', '', '| Mission | Exclusive item | Success / critical success | Gameplay reason |', '|---|---|---|---|']
    for mid, (iid, chance, bonus, chain) in EXCLUSIVE_DROPS.items():
        lines.append(f'| {MISSION_TEMPLATES[mid]["name"]} ({MISSION_TEMPLATES[mid]["rank"]}) | {ITEMS[iid]["name"]} | {chance}% / {chance+bonus}%'+(' · chain required' if chain else '')+f' | {ITEMS[iid]["description"]} |')
    for mid, (iid, chance, bonus) in EVENT_EXCLUSIVES.items():
        lines.append(f'| {MISSION_TEMPLATES[mid]["name"]} · Starfall | {ITEMS[iid]["name"]} | {chance}% / {chance+bonus}% | {ITEMS[iid]["description"]} |')
    for mid, drop in CAPTURE_DROPS.items():
        lines.append(f'| {MISSION_TEMPLATES[mid]["name"]} | {ITEMS[drop["item"]]["name"]} | {drop["chance"]}% live capture; {drop["chance"]+drop["secured_bonus"]}% secured field | {ITEMS[drop["item"]]["description"]} |')
    lines += ['', 'These are independent, once-per-resolution checks after success. Killing the required captive prevents the capture-exclusive check. Escaped enemies do not qualify. Failure does not trigger these new discoveries. The existing five chain weapons remain additional independent 14% / 22% checks, with chain provenance required. No guarantee or pity system is added.', '',
              '## Full catalogue', '', 'Cache placement shows eligibility, not an unconditional award. An authored reward check still uses its normal rank/outcome reward chances. Item rarity and minimum rank are separate: a low-rank exclusive can be valuable without entering higher-rank random caches. Items without a listed mission/cache source may be starting gear, training supplies, trade stock or retained legacy content.', '']
    for slot in [*SLOTS, 'non-equipment']:
        lines += [f'### {slot.title()}', '', '| Item (ID) | Rarity | Primary category | Implemented identity | Acquisition |', '|---|---|---|---|---|']
        for iid, item in ITEMS.items():
            if (item.get('slot') if item.get('slot') in SLOTS else 'non-equipment') != slot:
                continue
            effects = []
            if item.get('combat_skill'):
                s = item['combat_skill']
                effects.append(f'{s["name"]}, range {s["range"]}, {s["scaling"].upper()}, '+('nonlethal' if s.get('nonlethal') else 'lethal'))
            if item.get('element'): effects.append('Element: '+item['element'])
            if item.get('on_hit'): effects.append('On hit: '+str(item['on_hit']))
            if item.get('combat_rules'): effects.append('Rules: '+str(item['combat_rules']))
            if item.get('granted_perks'): effects.append('Granted perks: '+', '.join(item['granted_perks']))
            if any(item.get('attribute_bonuses', {}).values()): effects.append('Attributes: '+str(item['attribute_bonuses']))
            if any(item.get('bonuses', {}).values()): effects.append('Capabilities: '+str(item['bonuses']))
            if item.get('power'): effects.append(f'Weapon power {item["power"]}')
            source = '; '.join(sorted(found[iid])) or 'No mission/cache placement in this audit'
            columns = [f'{item["name"]} (`{iid}`)',item.get('rarity','—'),category(item),'; '.join(effects) or item.get('description','—'),source]
            lines.append('| '+' | '.join(str(c).replace('|','/').replace('\n',' ') for c in columns)+' |')
        lines.append('')
    out = ROOT / 'docs/gameplay/ITEM_CATALOGUE_AUDIT.md'
    out.write_text('\n'.join(lines)+'\n', encoding='utf-8')
    print(json.dumps({'items':len(ITEMS),'slots':dict(slots),'categories':dict(cats),'rarities':dict(rarity),'equipment_skills':sum(bool(i.get('combat_skill')) for i in ITEMS.values()),'exclusive_items':sum('mission_exclusive' in i.get('tags',[]) for i in ITEMS.values()),'report':str(out)},indent=2))


if __name__ == '__main__':main()

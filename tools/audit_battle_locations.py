"""Document current combat-map coverage from runtime content; no save access."""
import sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from backend.content import MISSION_TEMPLATES
from backend.tactical_contracts import TACTICAL_CONTRACTS
from backend.location_maps import MISSION_LOCATIONS
from backend.location_templates import BUILDING_PLANS


def main():
    authored=[];generic={}
    for mid,spec in TACTICAL_CONTRACTS.items():
        mission=MISSION_TEMPLATES[mid]
        location=MISSION_LOCATIONS.get(mid)
        if location:
            count=len(BUILDING_PLANS.get(location,[None,None]))
            authored.append((mission['name'],mission['rank'],location,count))
        else:
            key=(mission['name'],spec['layout'])
            generic.setdefault(key,[]).append(mission['rank'])
    lines=['# Combat location coverage audit','',
           'Generated from runtime content with `.venv\\Scripts\\python.exe tools/audit_battle_locations.py`.',
           'This inventories existing tactical encounters, including combat branches of roll/story missions. It does not propose converting roll-only contracts to combat.', '',
           f'{len(authored)} contract encounter IDs use authored locations; {len(TACTICAL_CONTRACTS)-len(authored)} still use generic road/camp/ruin/court layouts. Prison rank copies are grouped below. Generic maps have seeded dressing but no named, mission-specific building plans.', '',
           '## Authored contract locations','',
           '| Mission | Rank | Setting | Named layouts |','| --- | --- | --- | --- |']
    lines.extend(f'| {name} | {rank} | {location} | {count} |' for name,rank,location,count in sorted(authored))
    lines+=['','## Generic contract locations still needing review','',
            '| Mission | Ranks | Current fallback |','| --- | --- | --- |']
    for (name,layout),ranks in sorted(generic.items()):
        ordered=' / '.join(r for r in 'EDCBAS' if r in ranks)
        lines.append(f'| {name} | {ordered} | {layout} |')
    lines+=['','## Separate authored scenarios','',
            'Goblin Warcamp, The Captive Cart, Smoke on the Hedgerow investigation ambush and Hedgerow Watch defense have separate scenario generators. They are not counted as generic contracts above. They still need a separate review of named layout coverage; existing seeded dressing and defense deployment should be preserved.', '',
            'Story-only locations such as The Bell Beneath the Mud are not standalone tactical maps just because their story names a location. Their current combat complications can route to another contract. Giving them their own battle site requires changing that encounter routing deliberately.', '',
            'See [authored locations](../design/AUTHORED_BATTLE_LOCATIONS.md) for implemented rollout and proposed next batches.']
    destination=ROOT/'docs/maps/BATTLE_LOCATION_AUDIT.md'
    destination.write_text('\n'.join(lines)+'\n',encoding='utf-8')
    print(f'{len(authored)} authored; {len(TACTICAL_CONTRACTS)-len(authored)} generic contract encounter IDs. Wrote {destination}')


if __name__=='__main__':main()

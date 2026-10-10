"""Fresh-battle balance smoke audit after the shared-stat migration."""
import csv
import argparse
from copy import deepcopy
from pathlib import Path
import statistics
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from backend import combat
from backend.battle_lab import layout_presets
from backend.combat_encounter_profiles import MISSION_IDS, D_IDS
from backend.combat_stats import ATTRIBUTE_NAMES
from backend.game import new_game


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--missions',nargs='*',choices=sorted(MISSION_IDS))
    parser.add_argument('--append',action='store_true')
    parser.add_argument('--replace',action='store_true',help='Replace selected missions in an existing report')
    args=parser.parse_args()
    rows=[]
    destination=ROOT/'docs/design/SHARED_COMBAT_STATS_AUDIT.csv'
    if args.append and destination.exists():
        with destination.open(encoding='utf-8') as stream:
            rows=list(csv.DictReader(stream))
        for row in rows:
            for field in ('rounds','opening_enemy_hp','opening_enemy_attack'):row[field]=int(row[field])
        if args.replace:
            rows=[row for row in rows if row['mission'] not in (args.missions or MISSION_IDS)]
    completed={(r['mission'],r['layout'],r['job']) for r in rows}
    for mid in sorted(args.missions or MISSION_IDS):
        presets=layout_presets(mid if mid in ('frontier_watch_defense','prison_rescue_e') else 'contract:'+mid)
        if not presets:raise ValueError(f'Missing authored layouts: {mid}')
        for preset in presets:
            for job in ('fighter','barbarian','monk','rogue','ranger','mage'):
                if (mid,preset['id'],job) in completed:continue
                state=new_game({'name':'Shared-stat audit','starting_role':job,
                                'attributes':dict.fromkeys(ATTRIBUTE_NAMES,6)})
                character=state['characters'][0]
                character['adventurer_rank']='D' if mid in D_IDS else 'E'
                ally=deepcopy(character)
                ally.update(id='ally',name='Partner',is_player=False,loyalty=100)
                state['characters'].append(ally)
                if mid=='frontier_watch_defense':
                    battle=combat.create_frontier_watch_defense_battle(state,['player','ally'],preset['seed'])
                elif mid=='prison_rescue_e':
                    battle=combat.create_prison_rescue_battle(state,['player','ally'],preset['seed'],True)
                else:
                    battle=combat.create_contract_battle(state,['player','ally'],preset['seed'],mid,True)
                enemies=combat._living(battle,'enemy')
                opening_hp=sum(u['max_hp'] for u in enemies)
                opening_attack=sum(u['attack'] for u in enemies)
                try:
                    for _ in range(120):
                        if battle['status'] not in ('active','preparing'):break
                        combat.auto_step(battle)
                    outcome=battle.get('outcome') or 'stalled';error=''
                except Exception as exc:
                    outcome='error';error=f'{type(exc).__name__}: {exc}'
                rows.append(dict(mission=mid,layout=preset['id'],job=job,rank=character['adventurer_rank'],
                                 opening_enemy_hp=opening_hp,opening_enemy_attack=opening_attack,
                                 outcome=outcome,rounds=battle['round'],error=error))
            print(f"{mid} / {preset['id']}: {len(rows)} completed",flush=True)
    with (ROOT/'docs/design/SHARED_COMBAT_STATS_AUDIT.csv').open('w',newline='',encoding='utf-8') as stream:
        writer=csv.DictWriter(stream,fieldnames=list(rows[0]));writer.writeheader();writer.writerows(rows)
    lines=['# Shared combat stats: migration smoke audit','',
           'October 9, 2026. Fresh isolated battles; no database writes, saved-battle edits or server restart.', '',
           'Two Human allies, legal all-6 allocations and actual starter equipment. Six damage-focused Jobs, every layout exposed for the audited E/D mission set. D bodies explicitly have Adventurer D; this does not promote real players. Defense uses its real preparation encounter with no defenses placed; rescue uses its actual objective encounter. Species mechanics remain authored. No radiant encounters injected.','',
           '| Mission | Wins / fights | Other completed | Stalls / errors | Mean rounds |',
           '| --- | --- | --- | --- | --- |']
    for mid in sorted(MISSION_IDS):
        group=[r for r in rows if r['mission']==mid]
        if not group:continue
        wins=sum(r['outcome'] in ('success','critical_success') for r in group)
        bad=sum(r['outcome'] in ('stalled','error') for r in group)
        lines.append(f"| {mid} | {wins}/{len(group)} | {len(group)-wins-bad} | {bad} | {statistics.mean(r['rounds'] for r in group):.1f} |")
    lines+=['',f"Total {len(rows)} trials; {sum(r['outcome']=='error' for r in rows)} errors; {sum(r['outcome']=='stalled' for r in rows)} stalls.",'',
            '[Per-fight opening totals and outcomes](SHARED_COMBAT_STATS_AUDIT.csv).','',
            'Auto-play is a smoke check, not proof of human difficulty. Setup/support Jobs, other player races, optimized loadouts, progression UI and high-rank bosses are not represented. Objective/rescue/defense outcomes reflect current auto-play limitations as well as combat strength; avoid altering kits simply to improve this score. Manual map playtests remain necessary. Earlier trial reports retain their pre-migration data and must not be read as current-runtime results.','']
    (ROOT/'docs/design/SHARED_COMBAT_STATS_AUDIT.md').write_text('\n'.join(lines),encoding='utf-8')


if __name__=='__main__':main()

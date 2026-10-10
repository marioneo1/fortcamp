"""Small repeatable martial smoke sample; not a substitute for manual balance."""
import sys
from pathlib import Path
from collections import Counter
from copy import deepcopy

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from backend import combat
from backend.battle_lab import layout_presets
from backend.d_rank_locations import LOCATIONS
from backend.game import new_game


def main():
    outcomes=Counter()
    for mid in LOCATIONS.values():
        for preset in layout_presets('contract:'+mid):
            samples=[]
            for job in ('fighter','barbarian','monk','rogue'):
                state=new_game({'name':'QA','starting_role':job})
                ally=deepcopy(state['characters'][0])
                ally.update(id='ally',name='Partner',is_player=False,loyalty=100)
                state['characters'].append(ally)
                battle=combat.create_contract_battle(state,['player','ally'],preset['seed'],mid,True)
                for _ in range(100):
                    if battle['status']!='active':break
                    combat.auto_step(battle)
                if battle['status']=='active':raise RuntimeError(f'Stalled: {mid}, {preset["id"]}, {job}')
                outcomes[battle['outcome']]+=1
                samples.append(f"{job}: {battle['outcome']} ({battle['round']} rounds)")
            print(f"{mid} / {preset['label']}: "+'; '.join(samples),flush=True)
    print(f'{sum(outcomes.values())} completed fights: {dict(outcomes)}')


if __name__=='__main__':main()

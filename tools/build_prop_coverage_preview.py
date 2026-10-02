"""Build isolated encounter previews and coverage inputs; never reads player saves."""
import json
from pathlib import Path
import subprocess
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from backend.game import new_game
from backend.combat import (create_goblin_warcamp_battle, create_captive_cart_battle,
                           create_smoke_signals_battle, create_frontier_watch_defense_battle,
                           create_contract_battle, battle_view)
from backend.tactical_contracts import TACTICAL_CONTRACTS
from backend.location_maps import MISSION_LOCATIONS

subprocess.run([sys.executable,str(ROOT/'tools/build_gear_battle_preview.py')],check=True)
state=new_game({'name':'Prop Preview'})
battles={
    'warcamp':create_goblin_warcamp_battle(state,['player'],'prop-warcamp',True),
    'captive_cart':create_captive_cart_battle(state,['player'],'prop-cart',True),
    'investigation':create_smoke_signals_battle(state,['player'],'prop-investigation',True),
    'defense':create_frontier_watch_defense_battle(state,['player'],'prop-defense'),
}
for mid in TACTICAL_CONTRACTS:
    battles[mid]=create_contract_battle(state,['player'],'prop-'+mid,mid,True)
# Keep an actual-engine preview of every authored layout, not just one lucky seed.
for mid in MISSION_LOCATIONS:
    seen=set()
    for index in range(40):
        battle=create_contract_battle(state,['player'],f'layout-{index}',mid,True)
        variant=battle['map_variation']
        if variant not in seen:
            battles[f'{mid}_v{variant}']=battle;seen.add(variant)
# Include both states of prepared objects without changing a live encounter.
battles['defense']['terrain'].extend([
    {'id':'audit_spikes','name':'Spike Trap','x':6,'y':4,'kind':'prepared_trap','sprite':'spike_trap','prepared_trap':True,'blocking':False},
    {'id':'audit_snare','name':'Spent Snare','x':6,'y':5,'kind':'rubble','original_kind':'prepared_trap','sprite':'iron_jaw_trap','prepared_trap':True,'destroyed':True,'blocking':False},
])
for battle in battles.values():
    battle['turn_order']=['player',*[uid for uid in battle['turn_order'] if uid!='player']]
    battle['turn_index']=0
views={key:battle_view(value) for key,value in battles.items()}
edge_walk=create_contract_battle(state,['player'],'layout-0','tool_shed',True)
for uid,unit in edge_walk['units'].items():unit['extracted']=uid!='player'
edge_walk['turn_order']=['player'];edge_walk['turn_index']=0
edge=next(t for t in edge_walk['terrain'] if t.get('edge_wall') and t.get('wall_edges')==['north']
          and t.get('kind')!='gate' and not any(u['x']==t['x'] and u['y']==t['y']+1 and u.get('blocking')
                                              for u in edge_walk['terrain']))
edge_walk['units']['player'].update(x=edge['x'],y=edge['y']+1)
edge_walk_view=battle_view(edge_walk)
destination=ROOT/'staging-terrain/overhead-props-v2'
destination.mkdir(parents=True,exist_ok=True)
(destination/'coverage-input.json').write_text(json.dumps(views,ensure_ascii=True),encoding='utf-8')
source=(ROOT/'staging-ui/equipment-icons-v1/battle-preview.js').read_text(encoding='utf-8')
source+='\nconst propCoverageFixture='+json.dumps({'state':state,'battles':views,'edgeWalk':edge_walk_view,'walkEdge':edge},ensure_ascii=True)+';\n'+'''
state=propCoverageFixture.state;
window.propEncounter=name=>{activeBattleMissionId='prop-'+name;selectedCombatAction='move';renderBattle(structuredClone(propCoverageFixture.battles[name]))};
window.propEdgeWalk=()=>{activeBattleMissionId='edge-walk';selectedCombatAction='move';renderBattle(structuredClone(propCoverageFixture.edgeWalk));return propCoverageFixture.walkEdge};
const propControls=document.createElement('div');propControls.style.cssText='position:fixed;bottom:12px;left:24px;z-index:999;background:#152215;border:1px solid #7c9266;padding:8px;border-radius:8px';
const propSelect=document.createElement('select');Object.keys(propCoverageFixture.battles).forEach(name=>{const option=document.createElement('option');option.value=name;option.textContent=name.replaceAll('_',' ');propSelect.append(option)});propSelect.onchange=()=>window.propEncounter(propSelect.value);propControls.append(propSelect);document.body.append(propControls);
window.propEncounter('captive_cart');window.propCoverageReady=true;
'''
(destination/'encounter-preview.js').write_text(source,encoding='utf-8')
page=(ROOT/'staging-ui/equipment-icons-v1/battle-preview.html').read_text(encoding='utf-8').replace('/staging-ui/equipment-icons-v1/battle-preview.js','/staging-terrain/overhead-props-v2/encounter-preview.js')
(destination/'encounter-preview.html').write_text(page,encoding='utf-8')
print(f'Built {len(battles)} isolated encounter previews and coverage inputs')

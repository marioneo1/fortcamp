"""Percentage DoT stack pools, decaying one stack at each target turn end."""
from copy import deepcopy
PERCENT={'burn':.02,'poison':.10,'bleed':.05}

def normalize(status):
    """Retain old layer ownership/count; ignore former per-layer expiry and attack scaling."""
    if 'layers' not in status:
        layer={k:deepcopy(status[k]) for k in ('source_id','source_name','applied_activation') if k in status}
        status['layers']=[deepcopy(layer) for _ in range(max(1,int(status.get('stacks',1))))]
    status['stacks']=len(status['layers']);status['turns']=len(status['layers']);status['expiry']='target_end'
    return status

def count(status):return len(status['layers']) if 'layers' in status else max(1,int(status.get('stacks',1)))
def base_damage(unit,sid,stacks):
    per_stack=unit['max_hp']*PERCENT[sid]
    return (max(1,per_stack) if sid=='burn' else per_stack)*stacks

def potential(unit,sid,stacks):
    # n stacks now, then n-1, ... down to one on future turn ends.
    return base_damage(unit,sid,1)*stacks*(stacks+1)/2

"""Bounded equipment rules separate from additive attribute bonuses."""
CAPS={'carry_strength':6,'throw_range':1,'breach_damage':3,'guard_heal':4,'wounded_damage':2,'boss_damage':2}
FLAGS={'water_walk','rubble_walk','opening_guard','subdue_gloves','lifeline'}

def collect_rules(equipped):
    result={'resistances':[]}
    for item in equipped:
        for key,value in item.get('combat_rules',{}).items():
            if key=='resistances':result[key]=sorted(set(result[key])|set(value))
            elif key in FLAGS:result[key]=bool(result.get(key) or value)
            elif key in CAPS:result[key]=min(CAPS[key],max(result.get(key,0),int(value)))
    return result

def equipped_skills(equipped,attribute,training,fallback=None,weapon=None):
    # One shared focus use per battle. Extra gear adds choices, not extra casts.
    found=[]
    priority=([weapon] if weapon else [])+[item for item in equipped if item is not weapon]
    seen=set()
    for item in priority:
        authored=item.get('combat_skill')
        if not authored or authored['id'] in seen:continue
        seen.add(authored['id']);entry=dict(authored)
        entry.update(attack=5+attribute(entry['scaling'])//2+int(item.get('power',2))+training,
                     source_name=item['name'])
        entry.setdefault('element', item.get('element'))
        entry.setdefault('on_hit', item.get('on_hit'))
        found.append(entry)
    if fallback and fallback['id'] not in seen:found.append(dict(fallback))
    return found

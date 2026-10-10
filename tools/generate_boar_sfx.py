"""Generate reusable boar vocal variants; retained originals prevent rebilling."""
import json
from generate_engineer_impact_sfx import generate, ROOT

PACK='boar-combat-v1'
CLIPS={
    'attack':('A real adult wild boar lunging aggressively: one short throaty guttural grunt and forceful nasal snort, energetic outward attacking effort, rough low animal voice. Not pain, no human voice, no words, no cat, no roar, no music or background.', .8),
    'hurt':('A real adult wild boar struck once: a brief rough pained grunt with a compact coarse squeal, low throaty pig timbre, dry close animal vocal. Not a cat meow, not a human, no shrill sustained squealing, no words, music or background.', .8),
    'death':('A real adult wild boar dying: one strained low guttural groan-grunt dropping in strength into a short final breath, grounded rough porcine timbre, compact dramatic finish. No human voice, no cat meow, no sustained shrill squeal, no words, music or background.', 1.3),
}

if __name__=='__main__':
    report={}
    for action,(prompt,duration) in CLIPS.items():
        for variant in range(1,4):
            name=f'boar_{action}_{variant}'
            generate(name,prompt+f' Variation {variant}: one distinct short vocal, consistent adult boar identity.',duration,PACK)
            report[name]=json.loads((ROOT/'staging-sfx'/PACK/'generation_report.json').read_text(encoding='utf-8'))
            (ROOT/'staging-sfx'/PACK/'manifest.json').write_text(json.dumps(report,indent=2),encoding='utf-8')

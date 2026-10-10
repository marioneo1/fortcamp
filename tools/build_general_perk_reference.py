"""Keep the readable quirk catalog aligned with the runtime definitions."""
from pathlib import Path
import argparse
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from backend.general_perks import DEFINITIONS, RARITY

DEST=Path(__file__).resolve().parents[1]/'docs/player-reference/GENERAL_PERKS.md'
def render():
    lines=['# General character quirks',
           'Implemented in dev, October 9, 2026. These are innate perks, not skill slots.',
           '',f'**{len(DEFINITIONS)} new quirks.** Characters get variety, not the whole list; existing characters are not rerolled.',
           '', '## Rules',
           '- No Lucky + Unlucky, opposing movement/range/evasion/accuracy traits, or conflicting resistance tiers.',
           '- Only one HP tier and one stat-redistribution profile, including existing Strong-Armed/Nimble/Bookish/Steady-Handed and random-stat traits. Naturally Gifted is a separate bonus and may coexist with those traits and Lucky/Unlucky.',
           '- Unrelated strengths and weaknesses may coexist. Existing saved traits are preserved; new rolls and trait rewards reject conflicts.',
           '- Low level and low mission rank never exclude rare perks.',
           '- Naturally Gifted: **one-in-a-million opening roll**. It gives +1 to all six attributes and does not occupy a redistribution or luck tier; duplicate copies are still blocked.',
           '- Ordinary generated recruits have a 40% chance of no additional general quirk; their existing archetype traits remain. Generic-roll tiers: 52% common, 7.5% uncommon, 0.5% rare, 0.0001% exceptional. An incompatible/empty tier adds nothing.',
           '- Audited combat NPCs retain roughly 20% completely perkless outcomes. Usually they receive their role background; 20% of remaining ordinary outcomes try a general quirk, falling back to the existing small stat profiles. The exceptional opening roll can bypass the perkless outcome.',
           '- HP/VIT-changing general traits use the rare tier on authored combat NPCs to protect ordinary map difficulty. They remain possible at E-rank. Existing background/profession rolls remain separate.',
           '', '## Catalog',
           '| Quirk | Effect | Rarity |','| --- | --- | --- |']
    lines.extend(f'| {name} | {description} | {RARITY[key].title()} |' for key,(name,description) in DEFINITIONS.items())
    lines += ['', '## Reading the numbers',
              '- Evasion is a stat: +5 does not mean five extra dodge points against every attack. Ballistic/melee/magic use different evasion weights; guaranteed hits remain guaranteed.',
              '- One-percent damage changes can round away on small hits. Damage resistance reduces the calculated hit/tick; it does not change status stacks or duration. Existing mitigation combines normally.',
              '- Sleep/Stun and other application resistance uses the strongest applicable value. DoT-damage resistance is separate and never makes Poison/Bleed/Burn application fail.',
              '- Heavy-Fisted shares its +3 budget across a multi-hit action, rather than adding +3 to each hit. It affects melee unarmed damage, not magic or Rat Form.',
              '- A battle-start random stat uses the battle seed and stays in the saved unit; refreshes do not reroll it. Permanent character attributes stay unchanged.',
              '- Ranger range quirks affect bow/crossbow weapon range, not fixed spell/technique ranges or AoE size. Movement penalties never undo real movement locks.',
              '- Enterprising gives +1 gold per participating bearer on a mission settlement with a positive gold reward; no bonus for a zero-gold mission.',
              '', 'Source: `backend/general_perks.py`. Regenerate with `tools/build_general_perk_reference.py`; `--check` detects drift.',
              'Selected profession/role perks: [Recruit perks](RECRUIT_PERKS.md).']
    return '\n'.join(lines)+'\n'

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--check',action='store_true');args=parser.parse_args()
    expected=render()
    if args.check:
        if not DEST.exists() or DEST.read_text(encoding='utf-8')!=expected:sys.exit('General perk reference is stale')
    else:DEST.write_text(expected,encoding='utf-8')

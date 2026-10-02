"""Contract briefings describe known rewards without revealing hidden drop tables."""
import re


def public_reward_preview(mission):
    briefing = ' '.join(str(mission.get(key, '')) for key in ('description', 'objective'))
    disclosed = set(mission.get('disclosed_rewards', []))
    result = []
    for entry in mission.get('reward_preview', []):
        text = str(entry)
        hidden = any(marker in text.lower() for marker in ('exclusive:', 'chain relic:', 'discovery', 'drop chance')) or '%' in text
        if hidden:
            name = re.sub(r'^(?:Live-capture exclusive:|Exclusive:|Chain relic:)\s*', '', text, flags=re.I)
            name = re.split(r'\s*[·(]', name)[0].strip()
            if name and (name in briefing or name in disclosed):
                text = name + ' (possible recovery)'
            else:
                text = 'Possible unusual equipment from live captures' if 'capture' in text.lower() else 'Possible equipment discoveries'
        if text not in result:
            result.append(text)
    return result

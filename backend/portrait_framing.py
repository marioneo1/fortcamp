"""Non-destructive circle framing, separate from portrait identity/appearance."""
import json
import math
from pathlib import Path
from urllib.parse import unquote, urlsplit

REGISTRY_PATH = Path(__file__).resolve().parents[1] / 'data' / 'portrait_framing.json'
OVERRIDES_PATH = REGISTRY_PATH.with_name('portrait_framing_overrides.json')
_cache_stamp = None
_cache = {}


def portrait_key(url):
    path = unquote(urlsplit(str(url or '')).path)
    if path.startswith('/api/portrait-pools/'):
        return path.replace('/thumb/', '/full/')
    if path.startswith('/api/champion-portraits/'):
        return path.replace('/thumb.webp', '/full.webp')
    if path.startswith('/api/portraits/'):
        return path.replace('.thumb.webp', '.webp')
    return str(url or '')


def clean_frame(frame):
    frame = frame if isinstance(frame, dict) else {}
    result = {}
    for key, default, low, high in [('x',.5,0,1),('y',.5,0,1),('size',1,.25,2.5)]:
        try:value = float(frame.get(key,default))
        except (TypeError, ValueError):value = default
        result[key] = round(max(low,min(high,value if math.isfinite(value) else default)),5)
    return result


def defaults():
    global _cache_stamp, _cache
    stamp = tuple(p.stat().st_mtime_ns if p.exists() else None for p in (REGISTRY_PATH, OVERRIDES_PATH))
    if stamp != _cache_stamp:
        try:_cache = json.loads(REGISTRY_PATH.read_text(encoding='utf-8')).get('portraits',{})
        except (OSError, ValueError):_cache = {}
        try:_cache.update(json.loads(OVERRIDES_PATH.read_text(encoding='utf-8')).get('portraits',{}))
        except (OSError, ValueError):pass
        _cache_stamp = stamp
    return _cache


def save_default(key, frame=None):
    """Atomic local art override; audits never replace hand-adjusted defaults."""
    try:data = json.loads(OVERRIDES_PATH.read_text(encoding='utf-8'))
    except FileNotFoundError:data = {'version':1,'portraits':{}}
    if frame is None:data['portraits'].pop(key,None)
    else:data['portraits'][key] = clean_frame(frame)
    OVERRIDES_PATH.parent.mkdir(parents=True,exist_ok=True)
    temporary = OVERRIDES_PATH.with_suffix('.tmp')
    temporary.write_text(json.dumps(data,indent=2)+'\n',encoding='utf-8')
    temporary.replace(OVERRIDES_PATH)
    return clean_frame(defaults().get(key,{}))


def resolve_frame(character):
    key = portrait_key(character.get('portrait_full') or character.get('portrait'))
    if character.get('portrait_frame_source') == 'manual' and character.get('portrait_frame_key') == key:
        return clean_frame(character.get('portrait_frame'))
    return clean_frame(defaults().get(key,{}))

"""Default footprints for new props. Saved battles retain authored occupancy."""
import json
from pathlib import Path

PROP_SIZES=json.loads(Path(__file__).with_name('map_prop_sizes.json').read_text())

def prop_footprint(sprite):
    return list(PROP_SIZES.get(sprite,{}).get('footprint',[1,1]))

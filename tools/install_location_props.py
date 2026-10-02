"""Extract the location-only prop pack, preserving detached details and old assets."""
import json
from pathlib import Path
from PIL import Image
from audit_catalogue_crops import components, recovered_icon

ROOT = Path(__file__).resolve().parents[1]
IDS = ['repair_workbench','iron_anvil','carpenter_tool_rack','small_coal_forge',
       'mossy_gravestone','fallen_gravestone','grave_cross','old_bone_pile',
       'carpenter_sawhorse','stacked_planks','camp_lantern','open_toolbox']


def extract(source):
    parts, labels = components(source)
    anchors = [p for p in parts if p['area'] > 10000]
    if len(anchors) != 12:
        raise ValueError('Expected twelve primary props; inspect source before installation')
    ordered, by_y = [], sorted(anchors, key=lambda p:p['center'][1])
    for row in range(3):
        ordered.extend(sorted(by_y[row*4:(row+1)*4], key=lambda p:p['center'][0]))
    # A detached bone in this sheet is larger than the older importer's small-part threshold.
    # Assign bounded detached details to their encompassing primary silhouette, never a neighbor.
    ownership = {}
    for part in parts:
        if part in anchors:
            continue
        owners = [a for a in anchors if a['box'][0]-4 <= part['center'][0] <= a['box'][2]+4
                  and a['box'][1]-4 <= part['center'][1] <= a['box'][3]+4]
        if len(owners) == 1:
            ownership[part['label']] = owners[0]['label']
    for index, label in enumerate(labels):
        if label in ownership:
            labels[index] = ownership[label]
    outputs, report = {}, []
    for ident, anchor in zip(IDS, ordered):
        l,t,r,b = anchor['box']
        if min(l,t,source.width-r,source.height-b) < 2:
            raise ValueError(f'{ident}: source touches canvas edge')
        outputs[ident] = recovered_icon(source, anchor, parts, labels, size=384, padding=32)
        report.append({'id':ident,'source_box':anchor['box'],'retained_detached_parts':
                       [label for label,owner in ownership.items() if owner==anchor['label']]})
    return outputs, report


def main():
    folder = ROOT/'staging-terrain/location-props-v1'
    source = Image.open(folder/'location_props_12.png').convert('RGBA')
    outputs, report = extract(source)
    registry_path = ROOT/'frontend/src/map-prop-art.json'
    registry = json.loads(registry_path.read_text(encoding='utf-8'))
    destination = ROOT/'frontend/public/assets/combat-terrain/props/location-v1'
    destination.mkdir(parents=True,exist_ok=True)
    for ident, image in outputs.items():
        image.save(destination/f'{ident}.png',optimize=True)
        registry[ident] = f'props/location-v1/{ident}.png'
    registry_path.write_text(json.dumps(registry,indent=2)+'\n',encoding='utf-8')
    (folder/'extraction.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print(f'Installed {len(outputs)} location props; older sprites preserved')


if __name__ == '__main__':
    main()

"""Install only structures from their separate atlas, keeping disconnected gate leaves."""
import json
from pathlib import Path
from PIL import Image
from audit_catalogue_crops import components, recovered_icon

ROOT=Path(__file__).resolve().parents[1]
IDS=['shed_wall_straight','shed_wall_corner','shed_door_closed','shed_door_open',
     'yard_gate_closed','yard_gate_open','shed_wall_broken','cemetery_wall_corner']


def main():
    folder=ROOT/'staging-terrain/location-structures-v1'
    image=Image.open(folder/'location_structures_8.png').convert('RGBA')
    parts,labels=components(image)
    groups=[[] for _ in IDS]
    for part in parts:
        if part['area']<20:continue
        x,y=part['center'];column=min(3,int(x*4/image.width));row=min(1,int(y*2/image.height))
        groups[row*4+column].append(part)
    registry_path=ROOT/'frontend/src/map-prop-art.json'
    registry=json.loads(registry_path.read_text(encoding='utf-8'))
    output,report={},[]
    for ident,group in zip(IDS,groups):
        if not group:raise ValueError(f'{ident}: empty grid cell')
        anchor=max(group,key=lambda p:p['area']).copy()
        anchor['box']=[min(p['box'][0] for p in group),min(p['box'][1] for p in group),
                       max(p['box'][2] for p in group),max(p['box'][3] for p in group)]
        l,t,r,b=anchor['box']
        if min(l,t,image.width-r,image.height-b)<2:raise ValueError(f'{ident}: touches source border')
        owned={p['label'] for p in group}
        for index,label in enumerate(labels):
            if label in owned:labels[index]=anchor['label']
        output[ident]=recovered_icon(image,anchor,parts,labels,size=384,padding=32)
        report.append({'id':ident,'source_box':anchor['box'],'components':len(group)})
    destination=ROOT/'frontend/public/assets/combat-terrain/structures/location-v1'
    destination.mkdir(parents=True,exist_ok=True)
    for ident,sprite in output.items():
        sprite.save(destination/f'{ident}.png',optimize=True)
        if not registry.get('structure:'+ident,'').startswith('structures/building-v'):
            registry['structure:'+ident]=f'structures/location-v1/{ident}.png'
    registry_path.write_text(json.dumps(registry,indent=2)+'\n',encoding='utf-8')
    (folder/'extraction.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print(f'Installed {len(output)} structure sprites, including complete open gate pairs')


if __name__=='__main__':main()

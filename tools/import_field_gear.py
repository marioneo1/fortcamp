"""Import the approved 5x4 field equipment sheet using silhouette-safe extraction."""
from pathlib import Path
import json
import sys
from PIL import Image

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from tools.audit_catalogue_crops import source_icons,recovered_icon


def main():
    source=Path(sys.argv[1])
    manifest=json.loads((ROOT/'docs/art/FIELD_GEAR_V1_MANIFEST.json').read_text())
    image=Image.open(source).convert('RGBA')
    parts,components,labels=source_icons(image,manifest['columns'],manifest['rows'],len(manifest['items']))
    out=ROOT/'frontend/public/assets/catalogue/items'
    targets=[out/row['file'] for row in manifest['items']]
    if any(p.exists() for p in targets):raise SystemExit('Refusing to replace existing item art')
    icons=[recovered_icon(image,part,components,labels) for part in parts]
    out.mkdir(parents=True,exist_ok=True)
    preview=Image.new('RGBA',(5*192,4*192),(30,31,27,255))
    for row,icon,target in zip(manifest['items'],icons,targets):
        icon.save(target)
        preview.alpha_composite(icon,(row['cell']%5*192,row['cell']//5*192))
    preview.convert('RGB').save(source.parent/'installed-preview.jpg',quality=92)
    (source.parent/'import-report.json').write_text(json.dumps({'source':str(source), 'count':len(icons),
        'size':192,'silhouette_boxes':[p['box'] for p in parts]},indent=2))
    print(f'Installed {len(icons)} icons; no old icons replaced.')


if __name__=='__main__':main()

"""Install the six-piece candidate at one unchanged pixel scale for dev review."""
import json
from PIL import Image, ImageChops, ImageFilter
from install_building_toolset import ROOT
from audit_catalogue_crops import components

def main(raw_only=False):
    if not raw_only:
        from fit_boxed_wall_ports import main as fit
        return fit()
    source = ROOT / 'staging-terrain/building-toolset-v9-boxed-reference'
    image = Image.open(source / 'limestone_boxed_source.png').convert('RGBA')
    parts, labels = components(image, threshold=220)
    parts = sorted([p for p in parts if p['area'] > 1000], key=lambda p:p['center'][1])
    if len(parts) != 6: raise ValueError('Expected six complete wall silhouettes')
    parts = sorted(parts[:3],key=lambda p:p['center'][0])+sorted(parts[3:],key=lambda p:p['center'][0])
    names = ['wall','half','vertical','corner','junction','cross']
    # Authored top-band intersection centers, in original sheet pixels.
    anchors = [(281,270),(772,270),(1268,270),(340,676),(770,676),(1268,711)]
    dest = ROOT / 'frontend/public/assets/combat-terrain/structures/building-v9-boxed'
    dest.mkdir(parents=True,exist_ok=True)
    registry_path = ROOT / 'frontend/src/map-prop-art.json'
    registry = json.loads(registry_path.read_text())
    report=[]
    for name,part,(ax,ay) in zip(names,parts,anchors):
        # Retain actual pixels and a two-pixel antialiased silhouette fringe;
        # reject the broad generated background halo, not masonry geometry.
        mask=Image.frombytes('L',image.size,bytes(255 if label==part['label'] else 0 for label in labels))
        mask=mask.filter(ImageFilter.MaxFilter(5))
        cut=image.copy();cut.putalpha(ImageChops.multiply(image.getchannel('A'),mask))
        box=(ax-320,ay-320,ax+320,ay+320)
        sprite=cut.crop(box)
        filename=f'limestone_boxed_{name}.png'
        sprite.save(dest/filename,optimize=True)
        registry['structure:limestone_boxed_'+name]='structures/building-v9-boxed/'+filename
        report.append({'piece':name,'source_bounds':part['box'],'anchor':[ax,ay],'canvas':640,'scale':1})
    registry_path.write_text(json.dumps(registry,indent=2)+'\n')
    for file in ['backend/building_art_geometry.json','frontend/src/building-art-geometry.json']:
        path=ROOT/file;geometry=json.loads(path.read_text())
        geometry['limestone_boxed']={'native_pieces':True,'plan_view':True,'join_offset':0,
                                    'wall_half_thickness':.12}
        path.write_text(json.dumps(geometry,indent=2)+'\n')
    (source/'installed.json').write_text(json.dumps(report,indent=2)+'\n')
    print('Installed six candidate sprites at unchanged shared scale; original assets preserved.')

if __name__=='__main__':main()

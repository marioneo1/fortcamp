"""Fit authored junction arm ends to boundary ports, retaining their painted centres.

Uses crop-only texture sections from the same six-piece generation. No warping,
foreign material, centre patches, or overlapping straight bands at a junction.
"""
import json
from PIL import Image
from install_building_toolset import ROOT

SIZE=1024
C=SIZE//2
UNIT=397
OFFSET=.38
DEST=ROOT/'frontend/public/assets/combat-terrain/structures/building-v9-boxed'

def main():
    # Always rebuild the original exports first; repeated fitting cannot compound.
    from install_boxed_wall_trial import main as recover
    recover(raw_only=True)
    art={name:Image.open(DEST/f'limestone_boxed_{name}.png').convert('RGBA')
         for name in ['wall','half','vertical','corner','junction','cross']}
    straight=art['wall'];vertical=art['vertical']
    report=[]
    def arm(canvas,direction,start,end):
        # Texture strips are aligned by their existing top-band centre. Each
        # destination interval is disjoint from the retained authored centre.
        donor=straight if direction in ('left','right') else vertical
        length=abs(end-start)
        horizontal=direction in ('left','right')
        strip=donor.crop((180,280,460,382) if horizontal else (270,165,374,445))
        cursor=0
        while cursor<length:
            amount=min(280,length-cursor)
            cut=strip.crop((0,0,amount,strip.height) if horizontal else (0,0,strip.width,amount))
            position=(C+min(start,end)+cursor,C-40) if horizontal else (C-50,C+min(start,end)+cursor)
            canvas.alpha_composite(cut,position)
            cursor+=amount
    def build(name,left=0,right=0,up=0,down=0):
        canvas=Image.new('RGBA',(SIZE,SIZE))
        original=art['junction' if name=='edge_junction' else name]
        # The full original junction occupies the middle; outer arms are cropped
        # at 90px, then continued with uncapped same-atlas material sections.
        original=original.crop((230,230,410,410))
        canvas.alpha_composite(original,(C-90,C-90))
        for direction,value in [('left',left),('right',right),('up',up),('down',down)]:
            if value:
                end=round(value*UNIT)
                if direction in ('left','up'):arm(canvas,direction,-end,-90)
                else:arm(canvas,direction,90,end)
        canvas.save(DEST/f'limestone_boxed_{name}.png',optimize=True)
        report.append({'piece':name,'port_lengths':[left,right,up,down],
                       'centre_retained_px':180,'texture_resized':False})
    # Straight bands share the same boundary-to-boundary distance. Their source
    # top/side cross-section is preserved; only uncapped interior strips tile.
    for name,horizontal,length in [('wall',True,UNIT),('half',True,round(UNIT/2)),('vertical',False,UNIT)]:
        canvas=Image.new('RGBA',(SIZE,SIZE));a=-(length//2);b=a+length
        arm(canvas,'right' if horizontal else 'down',a,b)
        canvas.save(DEST/f'limestone_boxed_{name}.png',optimize=True)
    build('corner',left=.5+OFFSET,down=.5+OFFSET)
    build('junction',left=.5,right=.5,down=.5)
    build('edge_junction',left=.5,right=.5,down=.5+OFFSET)
    build('cross',left=.5,right=.5,up=.5,down=.5)
    registry_path=ROOT/'frontend/src/map-prop-art.json'
    registry=json.loads(registry_path.read_text())
    registry['structure:limestone_boxed_edge_junction']='structures/building-v9-boxed/limestone_boxed_edge_junction.png'
    registry_path.write_text(json.dumps(registry,indent=2)+'\n')
    for file in ['backend/building_art_geometry.json','frontend/src/building-art-geometry.json']:
        path=ROOT/file;data=json.loads(path.read_text())
        data['limestone_boxed'].update(join_offset=OFFSET,wall_half_thickness=.12)
        path.write_text(json.dumps(data,indent=2)+'\n')
    (ROOT/'staging-terrain/building-toolset-v9-boxed-reference/port-fit.json').write_text(json.dumps(report,indent=2)+'\n')
    print('Fitted complete authored junctions to perimeter and divider ports without texture scaling.')

if __name__=='__main__':main()

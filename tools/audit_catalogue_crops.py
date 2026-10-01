"""Measure separate silhouettes on original icon sheets before repairing grid cuts."""
import argparse
import hashlib
import json
import shutil
from array import array
from collections import deque
from pathlib import Path
from datetime import datetime
from PIL import Image, ImageFilter, ImageDraw

ROOT=Path(__file__).resolve().parents[1]

def source_icons(image,columns,rows,expected_count=None):
    parts,labels=components(image)
    large=[p for p in parts if p['area']>1500]
    expected_count=columns*rows if expected_count is None else expected_count
    if len(large)!=expected_count:
        raise ValueError(f'Expected {expected_count} separate silhouettes, found {len(large)}. Inspect the sheet manually.')
    ordered=[];by_y=sorted(large,key=lambda p:p['center'][1])
    for y in range(rows):ordered.extend(sorted(by_y[y*columns:(y+1)*columns],key=lambda p:p['center'][0]))
    return ordered,parts,labels

def recovered_icon(image,part,parts,labels):
    # Take a generous source region, but retain only this silhouette and its nearby
    # detached details. Masking removes neighbors rather than clipping the icon.
    width,height=image.size;l,t,r,b=part['box'];pad=6
    box=(max(0,l-pad),max(0,t-pad),min(width,r+pad),min(height,b+pad))
    owned={part['label']}
    for small in parts:
        x,y=small['center']
        if small['area']<=1500 and l-4<=x<=r+4 and t-4<=y<=b+4:owned.add(small['label'])
    mask=Image.new('L',(box[2]-box[0],box[3]-box[1]));pixels=bytearray(mask.width*mask.height)
    for y in range(box[1],box[3]):
        for x in range(box[0],box[2]):
            if labels[y*width+x] in owned:pixels[(y-box[1])*mask.width+x-box[0]]=255
    mask.frombytes(bytes(pixels));mask=mask.filter(ImageFilter.MaxFilter(7))
    tile=image.crop(box);alpha=tile.getchannel('A');alpha.frombytes(bytes(value if keep else 0 for value,keep in zip(alpha.tobytes(),mask.tobytes())));tile.putalpha(alpha)
    tile=tile.crop(tile.getbbox());tile.thumbnail((180,180),Image.Resampling.LANCZOS)
    result=Image.new('RGBA',(192,192));result.alpha_composite(tile,((192-tile.width)//2,(192-tile.height)//2))
    return result

def audit_sheet(source,entries,columns,rows,apply=False,backup=None):
    image=Image.open(source).convert('RGBA');ordered,parts,labels=source_icons(image,columns,rows)
    repairs=[]
    for entry in entries:
        i=entry['cell'];x,y=i%columns,i//columns
        box=(round(x*image.width/columns),round(y*image.height/rows),round((x+1)*image.width/columns),round((y+1)*image.height/rows))
        part=ordered[i];l,t,r,b=part['box']
        clipped=max(box[0]-l,box[1]-t,r-box[2],b-box[3],0)
        foreign=0
        for other in ordered:
            if other is part:continue
            ol,ot,orr,ob=other['box']
            if ol>=box[2] or orr<=box[0] or ot>=box[3] or ob<=box[1]:continue
            for yy in range(max(ot,box[1]),min(ob,box[3])):
                foreign+=sum(labels[yy*image.width+xx]==other['label'] for xx in range(max(ol,box[0]),min(orr,box[2])))
        if clipped<=2 and foreign<30:continue
        kind=source.name.split('_batch_')[0];target=ROOT/'frontend/public/assets/catalogue'/kind/entry['file']
        record={'id':entry['id'],'file':str(target.relative_to(ROOT)),'source':str(source.relative_to(ROOT)),'cell':i,'old_box':box,'silhouette_box':part['box'],'clipped_pixels':clipped,'neighbor_pixels':foreign,'before_sha256':hashlib.sha256(target.read_bytes()).hexdigest()}
        if apply:
            saved=backup/kind/entry['file'];saved.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(target,saved)
            recovered_icon(image,part,parts,labels).save(target)
            record['after_sha256']=hashlib.sha256(target.read_bytes()).hexdigest()
        repairs.append(record)
    return repairs

def components(image,threshold=40):
    width,height=image.size;alpha=image.getchannel('A').tobytes()
    labels=array('i',[-1])*len(alpha);found=[]
    for seed,value in enumerate(alpha):
        if value<threshold or labels[seed]!=-1:continue
        label=len(found);labels[seed]=label;queue=deque([seed]);area=0;sx=sy=0
        left=right=seed%width;top=bottom=seed//width
        while queue:
            index=queue.popleft();x=index%width;y=index//width;area+=1;sx+=x;sy+=y
            left=min(left,x);right=max(right,x);top=min(top,y);bottom=max(bottom,y)
            for neighbor in ((index-1 if x else -1),(index+1 if x+1<width else -1),index-width,index+width):
                if 0<=neighbor<len(alpha) and labels[neighbor]==-1 and alpha[neighbor]>=threshold:
                    labels[neighbor]=label;queue.append(neighbor)
        found.append({'label':label,'area':area,'box':[left,top,right+1,bottom+1],'center':[sx/area,sy/area]})
    return found,labels

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--apply',action='store_true');args=parser.parse_args()
    destination=ROOT/'data/catalogue-crop-audit';destination.mkdir(parents=True,exist_ok=True)
    backup=destination/'backups'/datetime.now().strftime('%Y%m%d-%H%M%S')
    manifest=json.loads((ROOT/'docs/art/equipment_icon_manifest.json').read_text());repairs=[]
    for kind in ('items','races'):
        columns,rows=manifest['layouts'][kind]
        for batch in sorted({e['batch'] for e in manifest[kind]}):
            source=ROOT/'staging-ui/equipment-icons-v1'/f'{kind}_batch_{batch:03d}.png'
            entries=[e for e in manifest[kind] if e['batch']==batch]
            repaired=audit_sheet(source,entries,columns,rows,args.apply,backup);repairs.extend(repaired)
            print(source.name,len(repaired),'faulty crops',', '.join(e['id'] for e in repaired))
    (destination/('repairs.json' if args.apply else 'audit.json')).write_text(json.dumps({'applied':args.apply,'backup':str(backup) if args.apply else None,'repairs':repairs},indent=2))
    print('Total:',len(repairs),'replacements' if args.apply else 'candidates; review before --apply')

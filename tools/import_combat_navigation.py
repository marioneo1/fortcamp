"""Crop the six painted navigation sprites and derive proportional native cursors."""
import argparse
import json
import shutil
from collections import deque
from pathlib import Path
from PIL import Image
ROOT=Path(__file__).resolve().parents[1]
NAMES=['door_open','door_close','retreat','pan','interact','hazard']
def subject_bounds(cell):
    # Ignore isolated spill from a neighbouring atlas cell while keeping substantial
    # detached parts of this icon (for example the broken hazard triangle).
    alpha=cell.getchannel('A');w,h=cell.size;pixels=alpha.load();visited=set();parts=[]
    for y in range(h):
        for x in range(w):
            if pixels[x,y]<48 or (x,y) in visited:continue
            queue=deque([(x,y)]);visited.add((x,y));size=0;left=right=x;top=bottom=y
            while queue:
                px,py=queue.popleft();size+=1;left=min(left,px);right=max(right,px);top=min(top,py);bottom=max(bottom,py)
                for nx,ny in ((px-1,py),(px+1,py),(px,py-1),(px,py+1)):
                    if 0<=nx<w and 0<=ny<h and (nx,ny) not in visited and pixels[nx,ny]>=48:
                        visited.add((nx,ny));queue.append((nx,ny))
            parts.append((size,(left,top,right+1,bottom+1)))
    if not parts:return None
    cutoff=max(size for size,_ in parts)*.02
    boxes=[box for size,box in parts if size>=cutoff]
    return min(b[0] for b in boxes),min(b[1] for b in boxes),max(b[2] for b in boxes),max(b[3] for b in boxes)

def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('atlas',type=Path);args=parser.parse_args()
    staging=ROOT/'staging-ui/combat-navigation-v1';destination=ROOT/'frontend/public/assets/combat-navigation-v1'
    staging.mkdir(parents=True,exist_ok=True);destination.mkdir(parents=True,exist_ok=True)
    if args.atlas.resolve()!=(staging/'atlas.png').resolve():shutil.copy2(args.atlas,staging/'atlas.png')
    atlas=Image.open(args.atlas).convert('RGBA');records=[]
    for index,name in enumerate(NAMES):
        col,row=index%3,index//3
        bounds=(round(col*atlas.width/3),round(row*atlas.height/2),round((col+1)*atlas.width/3),round((row+1)*atlas.height/2))
        cell=atlas.crop(bounds);box=subject_bounds(cell)
        if not box:raise ValueError('Empty cell '+name)
        crop=cell.crop(box)
        for size,suffix in [(256,''),(40,'_cursor')]:
            art=crop.copy();art.thumbnail((size-6,size-6),Image.Resampling.LANCZOS)
            square=Image.new('RGBA',(size,size));square.alpha_composite(art,((size-art.width)//2,(size-art.height)//2));square.save(destination/f'{name}{suffix}.png')
        records.append({'name':name,'cell':bounds,'alpha_bounds':box})
    (staging/'crop_manifest.json').write_text(json.dumps(records,indent=2));print(destination)
if __name__=='__main__':main()

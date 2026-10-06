"""Reproducibly split the square 4x4 martial icon/effect atlases."""
import json
from pathlib import Path
from PIL import Image

ROOT=Path(__file__).resolve().parents[1]
NAMES=['brace','second-wind','victory-strike','bloodfury','reckless-blow','skullbreaker','groundbreaker','bloodied-strength',
       'too-angry-to-fall','bloodthirst','unstoppable','fury','reckless-exposure','brace-defense','fury-ready','fury-spent']
FAMILIES=['protection','restoration','groundbreaker','force']


def main():
    stage=ROOT/'staging-ui/martial-jobs-v1'
    output=ROOT/'frontend/public/assets/martial-jobs-v1';output.mkdir(parents=True,exist_ok=True)
    report={}
    for filename in ('icons-atlas.png','effects-atlas.png'):
        im=Image.open(stage/filename)
        if im.width!=im.height:raise ValueError('Expected a square 4x4 atlas')
        if filename.startswith('effects') and im.mode!='RGBA':raise ValueError('Effect atlas needs real alpha')
        for index in range(16):
            col,row=index%4,index//4
            bounds=(round(col*im.width/4),round(row*im.height/4),round((col+1)*im.width/4),round((row+1)*im.height/4))
            cell=im.crop(bounds)
            if filename.startswith('icons'):
                name=NAMES[index];size=128
            else:
                name=f'{FAMILIES[row]}-{col+1}';size=256
                # Remove tiny peripheral fragments belonging to adjacent frames.
                alpha=cell.getchannel('A');w,h=cell.size;pixels=list(alpha.getdata());seen=set()
                for y in range(h):
                    for x in range(w):
                        at=y*w+x
                        if at in seen or pixels[at]<24:continue
                        queue=[at];seen.add(at);component=[]
                        while queue:
                            point=queue.pop();component.append(point);px,py=point%w,point//w
                            for nx,ny in ((px-1,py),(px+1,py),(px,py-1),(px,py+1)):
                                nxt=ny*w+nx
                                if 0<=nx<w and 0<=ny<h and nxt not in seen and pixels[nxt]>=24:
                                    seen.add(nxt);queue.append(nxt)
                        if len(component)<20:
                            for point in component:pixels[point]=0
                for y in range(h):
                    for x in range(w):
                        at=y*w+x
                        edge=min(x,y,w-1-x,h-1-y)
                        pixels[at]=round(pixels[at]*min(1,edge/4)) if pixels[at]>=24 else 0
                alpha.putdata(pixels);cell.putalpha(alpha)
            cell.resize((size,size),Image.Resampling.LANCZOS).save(output/(name+'.png'))
            report[name]={'source':filename,'bounds':bounds,'output_size':size}
    (stage/'manifest.json').write_text(json.dumps(report,indent=2))
    print(f'Imported {len(report)} martial assets')


if __name__=='__main__':main()

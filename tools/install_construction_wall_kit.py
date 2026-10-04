"""Install a 3x3 native construction atlas; does not change existing combat art."""
import argparse
import json
import re
from collections import deque
from pathlib import Path
from PIL import Image

ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/'staging-terrain/construction-plain-wood-v1'
DEST=ROOT/'frontend/public/assets/combat-terrain/construction/plain-wood-v1'
NAMES=['horizontal_plain','vertical_plain','horizontal_one_post','vertical_one_post',
       'horizontal_both_posts','vertical_both_posts','corner','gate_horizontal','gate_vertical']


def remove_neighbor_slivers(cell):
    """Remove small disconnected edge fragments leaking in from a neighboring cell."""
    width,height=cell.size;mask=cell.getchannel('A').point(lambda p:255 if p>=96 else 0).tobytes()
    seen=bytearray(len(mask));components=[]
    for start,alpha in enumerate(mask):
        if not alpha or seen[start]:continue
        queue=deque([start]);seen[start]=1;pixels=[];edge=False
        while queue:
            pos=queue.popleft();pixels.append(pos);x=pos%width;y=pos//width
            edge|=x in (0,width-1) or y in (0,height-1)
            for next_pos,valid in ((pos-1,x>0),(pos+1,x<width-1),(pos-width,y>0),(pos+width,y<height-1)):
                if valid and mask[next_pos] and not seen[next_pos]:seen[next_pos]=1;queue.append(next_pos)
        components.append((pixels,edge))
    largest=max((len(p) for p,_ in components),default=0);removed=[]
    result=cell.copy()
    for pixels,edge in components:
        if edge and len(pixels)<largest*.1:
            xs=[p%width for p in pixels];ys=[p//width for p in pixels]
            # Include the antialiasing halo around this separate fragment.
            bounds=(max(0,min(xs)-2),max(0,min(ys)-2),min(width,max(xs)+3),min(height,max(ys)+3))
            result.paste((0,0,0,0),bounds);removed.append(bounds)
    return result,removed


def thickness(image, horizontal):
    mask=image.getchannel('A').point(lambda p:255 if p>=160 else 0)
    counts=[sum(mask.getpixel((x,y))>0 for x in range(image.width)) for y in range(image.height)] if horizontal else [sum(mask.getpixel((x,y))>0 for y in range(image.height)) for x in range(image.width)]
    return max(1,sum(n>=max(counts)*.8 for n in counts))


def fit_axis(image, length, horizontal, first, last):
    """Fit only the middle grain band; preserve authored ends/posts/joint dimensions."""
    old=image.width if horizontal else image.height
    first=min(first,old//3);last=min(last,old//3)
    result=Image.new('RGBA',(length,image.height) if horizontal else (image.width,length))
    bounds=[(0,first,0,first),(first,old-last,first,length-last),(old-last,old,length-last,length)]
    for a,b,c,d in bounds:
        crop=image.crop((a,0,b,image.height) if horizontal else (0,a,image.width,b))
        crop=crop.resize((d-c,image.height) if horizontal else (image.width,d-c),Image.Resampling.LANCZOS)
        result.alpha_composite(crop,(c,0) if horizontal else (0,c))
    return result


def main():
    global SOURCE,DEST
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--kit',default='plain_wood_v1')
    parser.add_argument('--name',default='Plain wood - painted test kit')
    parser.add_argument('--atlas',type=Path,default=SOURCE/'plain-wood-atlas.png')
    args=parser.parse_args()
    if not re.fullmatch(r'[a-z][a-z0-9_]{1,60}',args.kit):parser.error('Kit ID must use lowercase letters, digits and underscores')
    SOURCE=args.atlas.resolve().parent
    slug=args.kit.replace('_','-');DEST=ROOT/'frontend/public/assets/combat-terrain/construction'/slug
    DEST.mkdir(parents=True,exist_ok=True);(SOURCE/'original-cells').mkdir(exist_ok=True)
    atlas=Image.open(args.atlas).convert('RGBA')
    if atlas.width!=atlas.height:raise ValueError('Construction atlases must be square 3x3 grids')
    report=[];sources={}
    padding=48 if args.kit=='plain_wood_v1' else 80
    canvas_size=416+padding*2;middle=canvas_size//2
    for i,name in enumerate(NAMES):
        col=i%3;row=i//3
        bounds=[round(col*atlas.width/3),round(row*atlas.height/3),round((col+1)*atlas.width/3),round((row+1)*atlas.height/3)]
        cell=atlas.crop(bounds);cell.save(SOURCE/'original-cells'/f'{name}.png')
        cell,removed=remove_neighbor_slivers(cell)
        box=cell.getchannel('A').point(lambda p:255 if p>=96 else 0).getbbox()
        if not box:raise ValueError(f'Missing silhouette: {name}')
        image=cell.crop(box);raw_size=image.size
        horizontal=name.startswith('horizontal') or name=='gate_horizontal'
        if name=='corner':
            tx=thickness(image,False);ty=thickness(image,True)
            image=image.resize((round(image.width*64/tx),round(image.height*64/ty)),Image.Resampling.LANCZOS)
            image=fit_axis(image,448,True,96,64);image=fit_axis(image,448,False,96,64)
            position=(padding-32,padding-32);origin=[padding,padding]
        else:
            scale=64/thickness(image,horizontal)
            image=image.resize((round(image.width*scale),round(image.height*scale)),Image.Resampling.LANCZOS)
            # Post centers, rather than outer silhouette tips, are the logical connection ports.
            first_post=name in {'horizontal_one_post','vertical_one_post','horizontal_both_posts','vertical_both_posts','gate_horizontal','gate_vertical'}
            last_post=name in {'horizontal_both_posts','vertical_both_posts','gate_horizontal','gate_vertical'}
            cross=image.height if horizontal else image.width
            radius=cross//2 if first_post or last_post else 0
            length=416+radius*int(first_post)+radius*int(last_post)
            image=fit_axis(image,length,horizontal,max(64,radius*2) if first_post else 64,max(64,radius*2) if last_post else 64)
            position=(padding-radius*int(first_post),middle-image.height//2) if horizontal else (middle-image.width//2,padding-radius*int(first_post))
            origin=[padding,middle] if horizontal else [middle,padding]
        canvas=Image.new('RGBA',(canvas_size,canvas_size));canvas.alpha_composite(image,position)
        if position[0]<0 or position[1]<0 or position[0]+image.width>canvas_size or position[1]+image.height>canvas_size:
            raise ValueError(f'Normalized piece clips its cell: {name}, {position}, {image.size}')
        canvas.save(DEST/f'{name}.png')
        sources[name]={'file':f'construction/{slug}/{name}.png','origin':origin,'span':416,'size':canvas_size}
        report.append({'piece':name,'relative_cell_bounds':bounds,'removed_neighbor_fragments':removed,'silhouette_bounds':box,'raw_size':raw_size,'normalized_bounds':[*position,*image.size]})
    manifest_path=ROOT/'frontend/src/construction-wall-art.json'
    manifest=json.loads(manifest_path.read_text()) if manifest_path.exists() else {}
    manifest[args.kit]={'name':args.name,'sources':sources}
    (ROOT/'frontend/src/construction-wall-art.json').write_text(json.dumps(manifest,indent=2)+'\n')
    (SOURCE/'installation.json').write_text(json.dumps({'source':args.atlas.name,'kit':args.kit,'atlas_size':atlas.size,'pieces':report,'normalization':'Native horizontal/vertical sources; middle-band fitting keeps endcaps and corner joint intact. No 90-degree image rotations.'},indent=2)+'\n')
    print(f'Installed {len(sources)} originals into {DEST}')
    print(f'Crop/normalization report: {SOURCE / "installation.json"}')


if __name__=='__main__':main()

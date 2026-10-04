"""Install the isolated 3x3 plain-wood construction trial; does not change combat art."""
import json
from pathlib import Path
from PIL import Image

ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/'staging-terrain/construction-plain-wood-v1'
DEST=ROOT/'frontend/public/assets/combat-terrain/construction/plain-wood-v1'
NAMES=['horizontal_plain','vertical_plain','horizontal_one_post','vertical_one_post',
       'horizontal_both_posts','vertical_both_posts','corner','gate_horizontal','gate_vertical']


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
    DEST.mkdir(parents=True,exist_ok=True);(SOURCE/'original-cells').mkdir(exist_ok=True)
    atlas=Image.open(SOURCE/'plain-wood-atlas.png').convert('RGBA')
    report=[];sources={}
    for i,name in enumerate(NAMES):
        col=i%3;row=i//3
        bounds=[round(col*atlas.width/3),round(row*atlas.height/3),round((col+1)*atlas.width/3),round((row+1)*atlas.height/3)]
        cell=atlas.crop(bounds);cell.save(SOURCE/'original-cells'/f'{name}.png')
        box=cell.getchannel('A').point(lambda p:255 if p>=96 else 0).getbbox()
        if not box:raise ValueError(f'Missing silhouette: {name}')
        image=cell.crop(box);raw_size=image.size
        horizontal=name.startswith('horizontal') or name=='gate_horizontal'
        if name=='corner':
            tx=thickness(image,False);ty=thickness(image,True)
            image=image.resize((round(image.width*64/tx),round(image.height*64/ty)),Image.Resampling.LANCZOS)
            image=fit_axis(image,448,True,96,64);image=fit_axis(image,448,False,96,64)
            position=(16,16);origin=[48,48]
        else:
            scale=64/thickness(image,horizontal)
            image=image.resize((round(image.width*scale),round(image.height*scale)),Image.Resampling.LANCZOS)
            # Post centers, rather than outer silhouette tips, are the logical connection ports.
            first_post=name in {'horizontal_one_post','vertical_one_post','horizontal_both_posts','vertical_both_posts','gate_horizontal'}
            last_post=name in {'horizontal_both_posts','vertical_both_posts','gate_horizontal'}
            cross=image.height if horizontal else image.width
            radius=cross//2 if first_post or last_post else 0
            length=416+radius*int(first_post)+radius*int(last_post)
            image=fit_axis(image,length,horizontal,max(64,radius*2) if first_post else 64,max(64,radius*2) if last_post else 64)
            position=(48-radius*int(first_post),256-image.height//2) if horizontal else (256-image.width//2,48-radius*int(first_post))
            origin=[48,256] if horizontal else [256,48]
        canvas=Image.new('RGBA',(512,512));canvas.alpha_composite(image,position)
        if position[0]<0 or position[1]<0 or position[0]+image.width>512 or position[1]+image.height>512:
            raise ValueError(f'Normalized piece clips its cell: {name}, {position}, {image.size}')
        canvas.save(DEST/f'{name}.png')
        sources[name]={'file':f'construction/plain-wood-v1/{name}.png','origin':origin,'span':416,'size':512}
        report.append({'piece':name,'relative_cell_bounds':bounds,'silhouette_bounds':box,'raw_size':raw_size,'normalized_bounds':[*position,*image.size]})
    manifest={'plain_wood_v1':{'name':'Plain wood - painted test kit','sources':sources}}
    (ROOT/'frontend/src/construction-wall-art.json').write_text(json.dumps(manifest,indent=2)+'\n')
    (SOURCE/'installation.json').write_text(json.dumps({'source':'plain-wood-atlas.png','atlas_size':atlas.size,'pieces':report,'normalization':'Native horizontal/vertical sources; middle-band fitting keeps endcaps and corner joint intact. No 90-degree image rotations.'},indent=2)+'\n')
    print(f'Installed {len(sources)} originals into {DEST}')
    print(json.dumps(report,indent=2))


if __name__=='__main__':main()

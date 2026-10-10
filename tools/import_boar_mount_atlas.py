"""Slice the approved transparent 5x4 sheet; no regeneration or raster editing."""
from pathlib import Path
from PIL import Image

ROOT=Path(__file__).resolve().parents[1]
NAMES=['idle_n','idle_ne','idle_e','idle_se','idle_s','idle_sw','idle_w','idle_nw',
       'walk_n_1','walk_n_2','walk_e_1','walk_e_2','walk_s_1','walk_s_2','walk_w_1',
       'walk_w_2','dead','unsaddled_n','mount_icon','dismount_icon']

# The generated subjects cross nominal grid boundaries. Import the complete
# approved silhouettes rather than clipping tusks or including neighboring feet.
SUBJECT_BOUNDS={'idle_n':(66,0,237,293),'idle_e':(535,72,867,281),'dead':(311,843,637,1099)}

def main():
    source=Image.open(ROOT/'staging-art/boar-mount-v1/atlas.png').convert('RGBA')
    destination=ROOT/'frontend/public/assets/boar-mount-v1'
    destination.mkdir(parents=True,exist_ok=True)
    for index,name in enumerate(NAMES):
        column,row=index%5,index//5
        bounds=(round(column*source.width/5),round(row*source.height/4),
                round((column+1)*source.width/5),round((row+1)*source.height/4))
        source.crop(SUBJECT_BOUNDS.get(name,bounds)).save(destination/(name+'.png'))

if __name__=='__main__':main()

"""Split the equal 4x4 overhead ground atlas; do not modify older terrain.

Run from dev with .venv/Scripts/python.exe tools/install_environment_ground.py.
The tiny inset excludes generated cell seams. Coordinates use actual dimensions.
"""
import json
from pathlib import Path
from PIL import Image

ROOT=Path(__file__).resolve().parents[1]
IDS=['garden_soil','garden_worn_soil','garden_furrows','garden_irrigation',
     'herbs_broadleaf','herbs_violet','herbs_sage','herbs_white',
     'practice_earth','practice_scuffs','practice_straw','practice_grass',
     'garden_stepping_stones','practice_footprints','garden_weeds','garden_leaf_litter']

def main():
    folder=ROOT/'staging-terrain/environment-ground-v1'
    source=Image.open(folder/'environment_ground_16.png').convert('RGB')
    destination=ROOT/'frontend/public/assets/combat-terrain/environment-ground-v1'
    destination.mkdir(parents=True,exist_ok=True)
    records=[]
    for i,name in enumerate(IDS):
        col,row=i%4,i//4
        box=[round(col*source.width/4)+3,round(row*source.height/4)+3,
             round((col+1)*source.width/4)-3,round((row+1)*source.height/4)-3]
        source.crop(box).resize((256,256),Image.Resampling.LANCZOS).save(destination/f'{name}.png',optimize=True)
        records.append({'id':name,'source_box':box,'output':[256,256]})
    (folder/'extraction.json').write_text(json.dumps(records,indent=2)+'\n')
    (ROOT/'frontend/src/environment-ground-art.json').write_text(json.dumps({name:f'environment-ground-v1/{name}.png' for name in IDS},indent=2)+'\n')
    print('Installed 16 ground-only textures; previous terrain preserved.')

if __name__=='__main__':main()

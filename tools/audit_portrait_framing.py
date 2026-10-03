"""Local face-centred circle defaults and review sheets; full images stay intact.

Optional audit dependencies live in data/portrait_audit/python_packages. The
anime cascade is nagadomi/lbpcascade_animeface (retained locally, not vendored).
No detector is required by the running game.
"""
import json
import sys
from pathlib import Path
from statistics import median

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'data/portrait_audit/python_packages'))
import cv2
from PIL import Image, ImageDraw, ImageOps

OUT = ROOT/'data/portrait_audit/framing'


def circle(image, frame, size=100):
    w,h = image.size
    diameter = frame['size']*min(w,h)
    cx,cy = frame['x']*w,frame['y']*h
    crop = image.transform((size,size),Image.Transform.EXTENT,
                          (cx-diameter/2,cy-diameter/2,cx+diameter/2,cy+diameter/2),
                          Image.Resampling.BICUBIC,fillcolor=(23,27,25))
    mask = Image.new('L',(size,size));ImageDraw.Draw(mask).ellipse((0,0,size-1,size-1),fill=255)
    result = Image.new('RGB',(size,size),(23,27,25));result.paste(crop,(0,0),mask)
    return result


def main():
    OUT.mkdir(parents=True,exist_ok=True)
    detectors = [('anime',cv2.CascadeClassifier(str(ROOT/'data/portrait_audit/models/lbpcascade_animeface.xml'))),
                 ('human',cv2.CascadeClassifier(cv2.data.haarcascades+'haarcascade_frontalface_default.xml'))]
    eyes = cv2.CascadeClassifier(cv2.data.haarcascades+'haarcascade_eye.xml')
    records, groups = {}, []
    inputs = []
    for pool in sorted((ROOT/'data/portrait_pools').iterdir()):
        if not pool.is_dir():continue
        inputs.append((pool.name,[(f,'/api/portrait-pools/'+pool.name+'/full/'+f.name)
                                  for f in sorted((pool/'full').glob('*.webp'))]))
    champions = [(f,'/api/champion-portraits/'+f.relative_to(ROOT/'data/champion_portraits').as_posix())
                 for f in sorted((ROOT/'data/champion_portraits').glob('*/**/full.webp'))]
    for i in range(0,len(champions),20):inputs.append((f'champions_{i//20+1:02}',champions[i:i+20]))
    for name,files in inputs:
        group = []
        for path,key in files:
            source = cv2.imread(str(path));h,w = source.shape[:2]
            grey = cv2.equalizeHist(cv2.cvtColor(cv2.resize(source,(384,384)),cv2.COLOR_BGR2GRAY))
            candidates = []
            for method,detector in detectors:
                for x,y,fw,fh in detector.detectMultiScale(grey,1.08,5,minSize=(48,48)):
                    cx,cy = (x+fw/2)/384,(y+fh/2)/384
                    if method=='human' and not len(eyes.detectMultiScale(grey[y:y+int(fh*.65),x:x+fw],1.1,4,minSize=(12,12))):continue
                    max_y = .38 if name.startswith('centaur') else .55
                    if .15<cx<.85 and .10<cy<max_y and .12<fw/384<.65:
                        score = fw*fh*(1-abs(cx-.5))
                        candidates.append((score,method,[int(x),int(y),int(fw),int(fh)]))
            if candidates:
                _,method,(x,y,fw,fh) = max(candidates)
                frame = {'x':round((x+fw/2)/384,4),'y':round((y+fh*.40)/384,4),
                         'size':round(min(1.3,max(.65,max(fw,fh)/384*2.2)),4)}
                record = {'frame':frame,'method':method,'face':[x,y,fw,fh],
                          'review':'detector estimate; hair and horns need visual review'}
            else:
                record = {'frame':None,'method':'fallback','review':'no reliable face; manual framing available'}
            records[key] = record; group.append((path,key))
        reliable = [records[key]['frame'] for _,key in group if records[key]['frame']]
        fallback = {'x':.5,'y':.34,'size':1.0}
        if len(reliable)>=3:
            # The sheet composition offers a cautious fallback, never a claim
            # that a detector recognized a beast's face.
            fallback = {k:round(median(f[k] for f in reliable),4) for k in fallback}
            fallback['size'] = max(.9,fallback['size'])
        if name.startswith('centaur'):fallback = {'x':.5,'y':.23,'size':.60}
        for _,key in group:
            if records[key]['frame'] is None:records[key]['frame']=dict(fallback)
        groups.append((name,group))
        print(name,len(group),len(reliable),flush=True)
    frames = {key:record['frame'] for key,record in records.items()}
    target = ROOT/'data/portrait_framing.json'
    if target.exists():(OUT/'previous_defaults.json').write_bytes(target.read_bytes())
    target.write_text(json.dumps({'version':1,'portraits':frames},indent=2)+'\n',encoding='utf-8')
    (OUT/'audit.json').write_text(json.dumps(records,indent=2)+'\n',encoding='utf-8')
    for start in range(0,len(groups),5):
        subset=groups[start:start+5]
        sheet=Image.new('RGB',(1000,len(subset)*250),(23,27,25));draw=ImageDraw.Draw(sheet)
        for row,(name,group) in enumerate(subset):
            draw.text((5,row*250+3),name,fill='white')
            for index,(path,key) in enumerate(group):
                x,y=index%10*100,row*250+23+index//10*110
                with Image.open(path) as image:sheet.paste(circle(image.convert('RGB'),frames[key]),(x,y))
                draw.text((x+3,y+99),f'{index+1} {records[key]["method"]}',fill='white')
        sheet.save(OUT/f'review_{start//5+1:02}.jpg',quality=92)
    summary={'portraits':len(records),'detected':sum(r['method']!='fallback' for r in records.values()),
             'fallback':sum(r['method']=='fallback' for r in records.values()),'review_sheets':(len(groups)+4)//5}
    (OUT/'summary.json').write_text(json.dumps(summary,indent=2)+'\n')
    print(summary)


if __name__=='__main__':main()

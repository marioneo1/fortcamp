"""Import named Mureka uploads, preserving originals and avoiding byte-identical playlist duplicates.

No API calls. Rerunning reuses processed files unless --reprocess is supplied.
"""
import argparse
import hashlib
import json
from pathlib import Path
import generate_music_candidates as processing

ROOT=processing.ROOT.resolve()
PACK='mureka-import-v1'
SOURCES=ROOT/'staging-music'/PACK/'originals'
FINAL=ROOT/'frontend/public/assets/music'/PACK
UPLOADS=[
    ('Boss 1.mp3','boss_1','Boss I','boss'),('Boss 2.mp3','boss_2','Boss II','boss'),
    ('Defense 1.mp3','defense_1','Defense I','defense'),('Defense 2.mp3','defense_2','Defense II','defense'),
    ('Investigate 1.mp3','investigation_1','Investigation I','investigation'),
    ('Investigate 2.mp3','investigation_2','Investigation II','investigation'),
    ('Undead 1.mp3','undead_1','Undead I','undead'),('Undead 2.mp3','undead_2','Undead II','undead'),
]


REGIONAL_UPLOADS=[
    (filename+suffix+'.mp3',identifier+'_'+str(index),name+' '+str(index),identifier)
    for filename,identifier,name in [('Green Warhost','goblin_warhost','The Green Warhost'),('The Ashen Procession','ashen_procession','The Ashen Procession'),('Arcane Convergence','arcane_convergence','Arcane Convergence'),('The Great Beast Tide','great_beast_tide','The Great Beast Tide'),('Starfall Omen','starfall_omen','Starfall Omen')]
    for index,suffix in [(1,''),(2,' (1)')]
]


def main():
    global PACK,SOURCES,FINAL,UPLOADS
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--reprocess',action='store_true');parser.add_argument('--pack',choices=['encounters','regions'],default='encounters');args=parser.parse_args()
    if args.pack=='regions':
        PACK='regional-events-v1';SOURCES=ROOT/'staging-music'/PACK/'originals';FINAL=ROOT/'frontend/public/assets/music'/PACK;UPLOADS=REGIONAL_UPLOADS
    SOURCES.mkdir(parents=True,exist_ok=True);FINAL.mkdir(parents=True,exist_ok=True)
    processing.FINAL=FINAL
    report_path=ROOT/'staging-music'/PACK/'import_report.json'
    report=json.loads(report_path.read_text(encoding='utf-8')) if report_path.exists() else {}
    seen={};tracks=[];duplicates=[]
    for filename,identifier,name,context in UPLOADS:
        incoming=ROOT/'staging-music'/filename;original=SOURCES/filename
        # Verify resolved absolute paths before moving anything on Windows.
        incoming.resolve().relative_to(ROOT);original.resolve().relative_to(ROOT)
        if incoming.exists():
            if original.exists():raise SystemExit(f'Original already exists: {filename}. No overwrite performed.')
            incoming.rename(original)
        if not original.exists():raise SystemExit(f'Missing upload or archived original: {filename}')
        digest=hashlib.sha256(original.read_bytes()).hexdigest()
        if digest in seen:
            duplicate={'filename':filename,'sha256':digest,'duplicate_of':seen[digest]};duplicates.append(duplicate)
            report[identifier]=duplicate;processing.write_json(report_path,report)
            print(f'{filename}: exact duplicate of {seen[digest]}; both originals retained.',flush=True)
            continue
        seen[digest]=identifier
        candidate={'id':identifier,'name':name,'context':context,'description':f'User-supplied Mureka {context} theme.','source_filename':filename,'source_sha256':digest}
        old=report.get(identifier,{})
        if args.reprocess or not (FINAL/(identifier+'.mp3')).exists() or not (FINAL/(identifier+'_loop_preview.mp3')).exists() or old.get('source_sha256') != digest or not old.get('technical_check'):
            print('Processing '+filename,flush=True)
            candidate['technical_check']=processing.process(original,candidate)
        else:candidate['technical_check']=old['technical_check']
        report[identifier]=candidate;tracks.append(candidate);processing.write_json(report_path,report)
    manifest={'pack':PACK,'source':'user uploads from Mureka website','tracks':tracks,'duplicates':duplicates}
    processing.write_json(FINAL/'manifest.json',manifest)
    print(f'Installed {len(tracks)} unique tracks; preserved {len(UPLOADS)} originals. No API requests made.',flush=True)


if __name__=='__main__':main()

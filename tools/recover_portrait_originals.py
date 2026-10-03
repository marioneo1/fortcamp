"""Recover uncropped pool cells without changing existing square portrait IDs."""
import json
from pathlib import Path
from PIL import Image
from portrait_import_core import ROOT, POOL_ROOT, read_manifest, normalized_sheet, pixel_digest
from portrait_grid import detect_grid_bounds


def main():
    recovered=0;missing=[]
    entries=list(read_manifest()['imports'])
    tracked={entry['pool'] for entry in entries}
    for pool in sorted(POOL_ROOT.iterdir()):
        if not pool.is_dir() or pool.name in tracked:continue
        names=sorted(p.name for p in (pool/'full').glob('*.webp'))
        source=ROOT/'portraits'/(pool.name+'.png')
        if len(names)==20 and source.is_file():
            entries.append({'pool':pool.name,'source_path':str(source),'source_name':source.name,
                            'pixel_sha256':pixel_digest(source),'files':names,'columns':5,'rows':4,'inset':.025})
    for entry in entries:
        source=Path(entry.get('source_path',''))
        if not source.is_file():
            candidates=[ROOT/'portraits'/entry['source_name'],ROOT/'staging-portraits'/entry['source_name']]
            source=next((p for p in candidates if p.is_file()),source)
        if not source.is_file() or pixel_digest(source)!=entry['pixel_sha256']:
            missing.append(entry['pool']);continue
        sheet=normalized_sheet(source);columns=entry.get('columns',5);rows=entry.get('rows',4)
        bounds=entry.get('grid_bounds') or {}
        if 'x' in bounds and 'y' in bounds:x,y=bounds['x'],bounds['y']
        else:x,y,_=detect_grid_bounds(sheet,columns,rows)
        destination=POOL_ROOT/entry['pool']/'original';destination.mkdir(exist_ok=True)
        inset=entry.get('inset',.025)
        for index,name in enumerate(entry['files']):
            target=destination/name
            if target.exists():continue
            row,column=divmod(index,columns);left,right=x[column:column+2];top,bottom=y[row:row+2]
            dx,dy=(right-left)*inset,(bottom-top)*inset
            cell=sheet.crop((round(left+dx),round(top+dy),round(right-dx),round(bottom-dy)))
            cell.thumbnail((1200,1200),Image.Resampling.LANCZOS)
            cell.save(target,'WEBP',quality=90,method=0);recovered+=1
    report={'recovered':recovered,'source_unavailable_or_changed':missing}
    output=ROOT/'data/portrait_audit/original_recovery.json';output.write_text(json.dumps(report,indent=2))
    print(json.dumps(report))


if __name__=='__main__':main()

"""Build an immutable local friend-trial release from committed code."""
import json
import shutil
import sqlite3
import subprocess
import zipfile
import io
from datetime import datetime
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
def main():
    if subprocess.check_output(['git','status','--porcelain','--untracked-files=no'],cwd=ROOT).strip():
        raise SystemExit('Commit source changes before updating the trial release. Running friends are not affected.')
    subprocess.run(['npm.cmd','--prefix','frontend','run','build'],cwd=ROOT,check=True)
    commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
    release=ROOT/'.fortcamp-releases'/f'{datetime.now():%Y%m%d-%H%M%S}-{commit[:8]}'
    release.mkdir(parents=True,exist_ok=False)
    archive=subprocess.check_output(['git','archive','--format=zip','HEAD','backend'],cwd=ROOT)
    with zipfile.ZipFile(io.BytesIO(archive)) as z:
        for member in z.infolist():
            target=(release/member.filename).resolve()
            if not target.is_relative_to(release.resolve()):raise ValueError('Invalid archive path')
        z.extractall(release)
    shutil.copytree(ROOT/'frontend'/'dist',release/'frontend'/'dist')
    for name in ('portrait_pools','champion_portraits'):
        source=ROOT/'data'/name
        if source.exists():shutil.copytree(source,release/'data'/name)
    uploads=ROOT/'data'/'stable_portraits'
    if not uploads.exists() and (ROOT/'data'/'portraits').exists():shutil.copytree(ROOT/'data'/'portraits',uploads)
    # The trial save lives outside versioned releases and is never overwritten.
    trial=ROOT/'data'/'fortcamp-stable.db'
    if not trial.exists() and (ROOT/'data'/'fortcamp.db').exists():
        with sqlite3.connect(ROOT/'data'/'fortcamp.db') as source,sqlite3.connect(trial) as target:source.backup(target)
    info={'commit':commit,'release':str(release.relative_to(ROOT)),'created_at':datetime.now().isoformat()}
    (release/'release.json').write_text(json.dumps(info,indent=2))
    pointer=ROOT/'.fortcamp-releases'/'current.json';temp=pointer.with_suffix('.tmp')
    temp.write_text(json.dumps(info,indent=2));temp.replace(pointer)
    print('Trial release ready:',release)
    print('Restart run_stable_windows.bat when no one is in a battle. Existing progress is preserved.')
if __name__=='__main__':main()

"""Create an independent, versioned release clone from committed development code."""
import argparse
import json
import re
import shutil
import sqlite3
import subprocess
from datetime import datetime
from pathlib import Path
from dotenv import set_key

ROOT=Path(__file__).resolve().parents[1]

def release_paths(parent,version):
    if not re.fullmatch(r'[0-9]+\.[0-9]+\.[0-9]+(?:-[A-Za-z0-9]+(?:\.[A-Za-z0-9]+)*)?',version):raise ValueError('Use a version such as 0.3.1-trial.2')
    parent=Path(parent).resolve()
    return parent/f'fortcamp-release-{version}',parent/'fortcamp-release-data'

def git(*args):return subprocess.check_output(['git',*args],cwd=ROOT,text=True).strip()

def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--version',required=True);parser.add_argument('--parent',type=Path)
    args=parser.parse_args()
    if (ROOT/'.fortcamp-release.json').exists():raise SystemExit('Create new releases from the development folder, not a release copy.')
    parent=args.parent or next((p for p in ROOT.parents if p.name.lower()=='fortcamp'),ROOT.parent)
    target,data=release_paths(parent,args.version)
    if target.exists():raise SystemExit(f'That release folder already exists; nothing was overwritten: {target}')
    if git('status','--porcelain'):raise SystemExit('Commit all source changes before creating a release. Untracked secrets/media are ignored by Git.')
    commit=git('rev-parse','HEAD');tag='v'+args.version
    if git('tag','--list',tag):raise SystemExit('That version tag already exists. Choose a new version.')
    remote=git('remote','get-url','origin')
    subprocess.run(['npm.cmd','--prefix','frontend','run','build'],cwd=ROOT,check=True)
    # Fast-forward only: never force-push or overwrite an older version tag.
    subprocess.run(['git','push','origin',f'{commit}:refs/heads/release'],cwd=ROOT,check=True)
    subprocess.run(['git','clone','--branch','release',remote,str(target)],check=True)
    actual=subprocess.check_output(['git','rev-parse','HEAD'],cwd=target,text=True).strip()
    if actual!=commit:raise SystemExit('Remote release advanced during creation; folder retained for inspection, no tag created.')
    # Independently installed packages; the release never uses the dev virtualenv.
    dev_python=ROOT/'.venv'/'Scripts'/'python.exe'
    subprocess.run([str(dev_python),'-m','venv',str(target/'.venv')],check=True)
    release_python=target/'.venv'/'Scripts'/'python.exe'
    subprocess.run([str(release_python),'-m','pip','install','-r',str(target/'requirements.lock.txt')],check=True)
    # Keep frontend tools and tests independent of the development installation too.
    subprocess.run(['npm.cmd','--prefix','frontend','ci'],cwd=target,check=True)
    shutil.copytree(ROOT/'frontend'/'dist',target/'frontend'/'dist')
    shutil.copytree(ROOT/'frontend'/'public'/'assets',target/'frontend'/'public'/'assets')
    for name in ('portrait_pools','champion_portraits'):
        source=ROOT/'data'/name
        if source.exists():shutil.copytree(source,target/'data'/name)
    shutil.copy2(ROOT/'.env',target/'.env')
    values={'DATABASE_URL':f'sqlite+aiosqlite:///{(data/"fortcamp.db").as_posix()}','DEV_BYPASS_AUTH':'false','GAME_DEBUG_MODE':'false','MISSION_TIME_SCALE':'1.0','BOT_ENABLED':'true','DISCORD_TEST_GUILD_ID':'','FORTCAMP_UPLOAD_ROOT':str(data/'portraits')}
    for name,value in values.items():set_key(str(target/'.env'),name,value,quote_mode='always')
    data.mkdir(parents=True,exist_ok=True)
    save=data/'fortcamp.db'
    if not save.exists():
        source=ROOT/'data'/'fortcamp-stable.db'
        if not source.exists():source=ROOT/'data'/'fortcamp.db'
        if source.exists():
            with sqlite3.connect(source) as src,sqlite3.connect(save) as dest:src.backup(dest)
    if not (data/'portraits').exists():
        uploads=ROOT/'data'/'stable_portraits'
        if not uploads.exists():uploads=ROOT/'data'/'portraits'
        if uploads.exists():shutil.copytree(uploads,data/'portraits')
        else:(data/'portraits').mkdir()
    info={'version':args.version,'commit':commit,'branch':'release','runtime_data':str(data),'created_at':datetime.now().isoformat()}
    (target/'.fortcamp-release.json').write_text(json.dumps(info,indent=2))
    subprocess.run(['git','-c','user.name=Fortcamp Workspace','-c','user.email=workspace@fortcamp.invalid','tag','-a',tag,commit,'-m',f'Fortcamp {args.version} friend trial'],cwd=ROOT,check=True)
    subprocess.run(['git','push','origin',f'refs/tags/{tag}'],cwd=ROOT,check=True)
    subprocess.run(['git','fetch','origin','--tags'],cwd=target,check=True)
    (ROOT/'.fortcamp-release-destination.json').write_text(json.dumps({'folder':str(target),'runtime_data':str(data),'version':args.version},indent=2))
    print(f'Release copy ready: {target}')
    print(f'Production save/portraits: {data}')
    print('Stop the old game host; keep Cloudflare running. Start run_release_windows.bat in the new folder.')

if __name__=='__main__':main()

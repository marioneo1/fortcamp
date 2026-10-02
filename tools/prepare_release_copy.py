"""Create an independent, versioned release clone from committed development code."""
import argparse
import json
import re
import shutil
import sqlite3
import subprocess
import socket
from contextlib import contextmanager, closing
from datetime import datetime
from pathlib import Path
from dotenv import set_key, dotenv_values

ROOT=Path(__file__).resolve().parents[1]

def release_paths(parent,version):
    if not re.fullmatch(r'[0-9]+\.[0-9]+\.[0-9]+(?:-[A-Za-z0-9]+(?:\.[A-Za-z0-9]+)*)?',version):raise ValueError('Use a version such as 0.3.1-trial.2')
    parent=Path(parent).resolve()
    return parent/f'fortcamp-release-{version}',parent/'fortcamp-release-data'

def git(*args):return subprocess.check_output(['git',*args],cwd=ROOT,text=True).strip()

def release_env_source(parent):
    """Never carry development bot credentials into a new production copy."""
    parent=Path(parent).resolve()
    explicit=ROOT/'.env.release'
    if explicit.is_file():return explicit
    prod=parent/'fortcamp-prod'
    if (prod/'.fortcamp-release.json').is_file() and (prod/'.env').is_file():return prod/'.env'
    pointer=ROOT/'.fortcamp-release-destination.json'
    if pointer.is_file():
        previous=Path(json.loads(pointer.read_text())['folder']).resolve()
        if previous.is_relative_to(parent) and (previous/'.fortcamp-release.json').is_file() and (previous/'.env').is_file():return previous/'.env'
    candidates=[p for p in parent.glob('fortcamp-release-*') if (p/'.fortcamp-release.json').is_file() and (p/'.env').is_file()]
    if candidates:
        latest=max(candidates,key=lambda p:(p/'.fortcamp-release.json').stat().st_mtime)
        return latest/'.env'
    raise SystemExit('Create a private .env.release containing your production credentials first. The builder will not copy alpha/dev credentials into production.')

@contextmanager
def production_destination(target,data,production_env):
    """Archive the previous stopped production copy and restore it if preparation fails."""
    target=target.resolve();parent=target.parent.resolve();data=data.resolve()
    if target.name!='fortcamp-prod' or data.parent!=parent or target==ROOT.resolve():
        raise ValueError('Invalid production destination')
    with socket.socket() as sock:
        if sock.connect_ex(('127.0.0.1',5173))==0:
            raise SystemExit('Stop the production control window with Ctrl+C before updating. The running server was left alone.')
    stamp=datetime.now().strftime('%Y%m%d-%H%M%S-%f')
    save=data/'fortcamp.db'
    if save.is_file():
        backup_dir=data/'backups';backup_dir.mkdir(parents=True,exist_ok=True)
        with closing(sqlite3.connect(save)) as source,closing(sqlite3.connect(backup_dir/f'before-prod-update-{stamp}.db')) as dest:
            source.backup(dest)
    archive=None
    if target.exists():
        if not (target/'.fortcamp-release.json').is_file():raise ValueError('The production folder is not a prepared Fortcamp release; nothing was replaced')
        archive=parent/'fortcamp-backups'/f'prod-{stamp}'
        archive.parent.mkdir(exist_ok=True)
        target.rename(archive)
        if production_env.resolve().is_relative_to(target):production_env=archive/production_env.relative_to(target)
    try:
        yield production_env
    except BaseException:
        if target.exists():
            failed=parent/'fortcamp-backups'/f'failed-prod-{stamp}'
            failed.parent.mkdir(exist_ok=True);target.rename(failed)
        if archive:archive.rename(target)
        raise


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--version');parser.add_argument('--parent',type=Path);parser.add_argument('--prod',action='store_true',help='Update the fixed fortcamp-prod folder, keeping a rollback copy and the production save')
    args=parser.parse_args()
    if (ROOT/'.fortcamp-release.json').exists():raise SystemExit('Create new releases from the development folder, not a release copy.')
    if not args.version:
        if not args.prod:parser.error('--version is required for versioned release copies')
        base=json.loads((ROOT/'frontend'/'package.json').read_text())['version']
        args.version=f"{base}-prod.{datetime.now().strftime('%Y%m%d.%H%M%S')}"
    parent=args.parent or next((p for p in ROOT.parents if p.name.lower()=='fortcamp'),ROOT.parent)
    target,data=release_paths(parent,args.version)
    production_env=release_env_source(parent)
    if args.prod:
        target=Path(parent).resolve()/'fortcamp-prod'
        if git('status','--porcelain'):raise SystemExit('Commit tested source changes before updating production.')
        with production_destination(target,data,production_env) as source:
            build_copy(args,target,data,source)
    else:build_copy(args,target,data,production_env)


def build_copy(args,target,data,production_env):
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
    shutil.copy2(production_env,target/'.env')
    values={'DATABASE_URL':f'sqlite+aiosqlite:///{(data/"fortcamp.db").as_posix()}','DEV_BYPASS_AUTH':'false','GAME_DEBUG_MODE':'false','MISSION_TIME_SCALE':'1.0','BOT_ENABLED':'true','DISCORD_TEST_GUILD_ID':'','FORTCAMP_UPLOAD_ROOT':str(data/'portraits'),'FORTCAMP_PROFILE':'release','FORTCAMP_WEB_ORIGIN':dotenv_values(production_env).get('FORTCAMP_RELEASE_WEB_ORIGIN') or 'https://play.fortcampgame.fyi'}
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
    # Only release copies receive a release launcher; keep alpha's entry points unambiguous.
    launcher='run_prod_windows.bat' if args.prod else 'run_release_windows.bat'
    profile='prod' if args.prod else 'release'
    (target/launcher).write_text(f'@echo off\ncd /d "%~dp0"\ntitle Fortcamp Production\n.venv\\Scripts\\python.exe tools\\run_profile.py {profile}\nif errorlevel 1 pause\n')
    subprocess.run(['git','-c','user.name=Fortcamp Workspace','-c','user.email=workspace@fortcamp.invalid','tag','-a',tag,commit,'-m',f'Fortcamp {args.version} friend trial'],cwd=ROOT,check=True)
    subprocess.run(['git','push','origin',f'refs/tags/{tag}'],cwd=ROOT,check=True)
    subprocess.run(['git','fetch','origin','--tags'],cwd=target,check=True)
    (ROOT/'.fortcamp-release-destination.json').write_text(json.dumps({'folder':str(target),'runtime_data':str(data),'version':args.version},indent=2))
    print(f'Release copy ready: {target}')
    print(f'Production save/portraits: {data}')
    print(f'Keep Cloudflare running. Start {launcher} in the production folder.')

if __name__=='__main__':main()

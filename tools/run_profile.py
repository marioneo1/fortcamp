"""Own and stop only the processes launched for this stable/dev session."""
import argparse
import json
import os
import signal
import socket
import subprocess
import time
from urllib.request import urlopen
from pathlib import Path
from dotenv import dotenv_values

ROOT=Path(__file__).resolve().parents[1]

def conflicting_application(profile,env):
    if profile not in {'dev-discord','release','stable'}:return False
    other_port=5173 if profile=='dev-discord' else 8001
    app_id=env.get('DISCORD_CLIENT_ID') or dotenv_values(ROOT/'.env').get('DISCORD_CLIENT_ID')
    if not app_id:return False
    try:
        with urlopen(f'http://127.0.0.1:{other_port}/api/config',timeout=1) as response:
            other=json.load(response)
        return other.get('discord_client_id')==app_id and not other.get('dev_bypass_auth',True)
    except (OSError,ValueError):return False
def profile_config(profile):
    env=os.environ.copy()
    public_config=dotenv_values(ROOT/'.env')
    save_profile='dev' if profile=='dev-discord' else profile
    is_release=profile in {'release','stable'}
    origin_key='FORTCAMP_RELEASE_WEB_ORIGIN' if is_release else 'FORTCAMP_DEV_WEB_ORIGIN'
    env.update(FORTCAMP_PROFILE='release' if is_release else 'dev',FORTCAMP_WEB_ORIGIN=env.get(origin_key) or public_config.get(origin_key) or ('https://play.fortcampgame.fyi' if is_release else 'https://dev.fortcampgame.fyi'))
    env.update(FORTCAMP_ENV_FILE=str(ROOT/'.env'),DATABASE_URL=f'sqlite+aiosqlite:///{(ROOT/"data"/f"fortcamp-{save_profile}.db").as_posix()}',FORTCAMP_UPLOAD_ROOT=str(ROOT/'data'/f'{save_profile}_portraits'))
    if profile=='release' or profile=='stable' and (ROOT/'.fortcamp-release.json').exists():
        marker=ROOT/'.fortcamp-release.json'
        if not marker.is_file():raise SystemExit('Run the release launcher from a prepared sibling release folder.')
        info=json.loads(marker.read_text())
        data=Path(info['runtime_data']).resolve()
        if not data.is_relative_to(ROOT.parent.resolve()):raise ValueError('Release data must stay inside the Fortcamp parent directory')
        env.update(DATABASE_URL=f'sqlite+aiosqlite:///{(data/"fortcamp.db").as_posix()}',FORTCAMP_UPLOAD_ROOT=str(data/'portraits'),DEV_BYPASS_AUTH='false',GAME_DEBUG_MODE='false',MISSION_TIME_SCALE='1.0',BOT_ENABLED='true',DISCORD_TEST_GUILD_ID='')
        return env,ROOT,[5173]
    if profile=='stable':
        env.update(DEV_BYPASS_AUTH='false',GAME_DEBUG_MODE='false',MISSION_TIME_SCALE='1.0',BOT_ENABLED='true',DISCORD_TEST_GUILD_ID='')
        pointer=ROOT/'.fortcamp-releases'/'current.json'
        if not pointer.exists():raise SystemExit('Prepare a sibling release with create_release_windows.bat and launch it from that folder.')
        cwd=(ROOT/json.loads(pointer.read_text())['release']).resolve()
        if not cwd.is_relative_to((ROOT/'.fortcamp-releases').resolve()):raise ValueError('Invalid release location')
        return env,cwd,[5173]
    env.update(DEV_BYPASS_AUTH='true',GAME_DEBUG_MODE='true',MISSION_TIME_SCALE='0.05',BOT_ENABLED='false',FORTCAMP_API_TARGET='http://127.0.0.1:8001')
    if profile=='dev-discord':
        env.update(DEV_BYPASS_AUTH='false',BOT_ENABLED='true',DISCORD_TEST_GUILD_ID='')
        return env,ROOT,[8001,5174]
    return env,ROOT,[8001,5174]

def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('profile',choices=['stable','release','dev','dev-discord'])
    args=parser.parse_args();env,cwd,ports=profile_config(args.profile)
    conflict_message='Dev and release cannot run Discord bots using the same application. Create a separate Discord dev application and put its client ID, secret and bot token in alpha .env. Keep the release credentials in its own .env.'
    if conflicting_application(args.profile,env):raise SystemExit(conflict_message)
    if args.profile=='release':
        info=json.loads((ROOT/'.fortcamp-release.json').read_text())
        commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
        dirty=subprocess.check_output(['git','status','--porcelain','--untracked-files=no'],cwd=ROOT,text=True).strip()
        if commit!=info['commit'] or dirty:raise SystemExit('Release source changed. Develop in the dev folder and prepare a new release there so code and built assets match.')
        if not (ROOT/'frontend'/'dist'/'index.html').is_file():raise SystemExit('Built release frontend is missing. Prepare the release again from dev.')
    for port in ports:
        with socket.socket() as sock:
            if sock.connect_ex(('127.0.0.1',port))==0:raise SystemExit(f'Port {port} is already in use. Close the older Fortcamp runner first; it has not been killed.')
    commands=[[str(ROOT/'.venv'/'Scripts'/'python.exe'),'-m','uvicorn','backend.main:app','--host','127.0.0.1','--port',str(ports[0])]]
    if args.profile in ('dev','dev-discord'):
        commands[0].append('--reload')
        commands.append(['cmd','/c','npm.cmd','--prefix','frontend','run','dev','--','--port',str(ports[-1])])
    if args.profile=='dev-discord':
        print('Discord development: dev.fortcampgame.fyi -> port 5174, with real Discord login and DEV saves. Use your dev application credentials in alpha .env; keep Cloudflare running.',flush=True)
    print(f'{args.profile.upper()}: http://127.0.0.1:{ports[-1]} | separate {args.profile} save | Ctrl+C to stop this session',flush=True)
    children=[]
    try:
        for command in commands:children.append(subprocess.Popen(command,cwd=cwd,env=env,creationflags=subprocess.CREATE_NEW_PROCESS_GROUP))
        next_conflict_check=time.monotonic()+5
        while all(child.poll() is None for child in children):
            time.sleep(.25)
            if time.monotonic()>=next_conflict_check:
                if conflicting_application(args.profile,env):raise SystemExit(conflict_message)
                next_conflict_check=time.monotonic()+5
    except KeyboardInterrupt:pass
    finally:
        for child in children:
            if child.poll() is None:
                try:child.send_signal(signal.CTRL_BREAK_EVENT)
                except OSError:child.terminate()
        for child in children:
            try:child.wait(timeout=8)
            except subprocess.TimeoutExpired:
                subprocess.run(['taskkill','/PID',str(child.pid),'/T','/F'],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
if __name__=='__main__':main()

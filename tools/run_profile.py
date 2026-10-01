"""Own and stop only the processes launched for this stable/dev session."""
import argparse
import json
import os
import signal
import socket
import subprocess
import time
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
def profile_config(profile):
    env=os.environ.copy()
    env.update(FORTCAMP_ENV_FILE=str(ROOT/'.env'),DATABASE_URL=f'sqlite+aiosqlite:///{(ROOT/"data"/f"fortcamp-{profile}.db").as_posix()}',FORTCAMP_UPLOAD_ROOT=str(ROOT/'data'/f'{profile}_portraits'))
    if profile=='stable':
        env.update(DEV_BYPASS_AUTH='false',GAME_DEBUG_MODE='false',MISSION_TIME_SCALE='1.0',BOT_ENABLED='true',DISCORD_TEST_GUILD_ID='')
        pointer=ROOT/'.fortcamp-releases'/'current.json'
        if not pointer.exists():raise SystemExit('Run update_stable_windows.bat first.')
        cwd=(ROOT/json.loads(pointer.read_text())['release']).resolve()
        if not cwd.is_relative_to((ROOT/'.fortcamp-releases').resolve()):raise ValueError('Invalid release location')
        return env,cwd,[5173]
    env.update(DEV_BYPASS_AUTH='true',GAME_DEBUG_MODE='true',MISSION_TIME_SCALE='0.05',BOT_ENABLED='false',FORTCAMP_API_TARGET='http://127.0.0.1:8001')
    return env,ROOT,[8001,5174]

def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('profile',choices=['stable','dev'])
    args=parser.parse_args();env,cwd,ports=profile_config(args.profile)
    for port in ports:
        with socket.socket() as sock:
            if sock.connect_ex(('127.0.0.1',port))==0:raise SystemExit(f'Port {port} is already in use. Close the older Fortcamp runner first; it has not been killed.')
    commands=[[str(ROOT/'.venv'/'Scripts'/'python.exe'),'-m','uvicorn','backend.main:app','--host','127.0.0.1','--port',str(ports[0])]]
    if args.profile=='dev':
        commands[0].append('--reload')
        commands.append(['cmd','/c','npm.cmd','--prefix','frontend','run','dev','--','--port','5174'])
    print(f'{args.profile.upper()}: http://127.0.0.1:{ports[-1]} | separate {args.profile} save | Ctrl+C to stop this session',flush=True)
    children=[]
    try:
        for command in commands:children.append(subprocess.Popen(command,cwd=cwd,env=env,creationflags=subprocess.CREATE_NEW_PROCESS_GROUP))
        while all(child.poll() is None for child in children):time.sleep(.25)
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

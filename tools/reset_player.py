"""Reset one local SQLite player, with a consistent backup and no shared-board wipe."""
import argparse
import sqlite3
from datetime import datetime
from pathlib import Path
from dotenv import dotenv_values

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--guild',required=True);parser.add_argument('--user',required=True)
    parser.add_argument('--database',type=Path)
    parser.add_argument('--keep-registration',action='store_true',help='Keep Discord registration so the player need not register again.')
    args=parser.parse_args()
    root=Path(__file__).resolve().parents[1]
    url=dotenv_values(root/'.env').get('DATABASE_URL','sqlite+aiosqlite:///./data/fortcamp.db')
    if not args.database and not url.startswith('sqlite+aiosqlite:///'):parser.error('Use --database with a local SQLite save.')
    path=args.database or root/url.split('///',1)[1]
    if not path.is_file():parser.error('Save database does not exist.')
    backup=path.parent/'backups'/f'{path.stem}-before-player-reset-{datetime.now():%Y%m%d-%H%M%S-%f}.sqlite'
    backup.parent.mkdir(parents=True,exist_ok=True)
    with sqlite3.connect(path,timeout=30) as conn:
        player=conn.execute('select display_name from player_states where guild_id=? and user_id=?',(args.guild,args.user)).fetchone()
        if not player:parser.error('That player has no save; nothing changed.')
        with sqlite3.connect(backup) as target:conn.backup(target)
        conn.execute('BEGIN IMMEDIATE')
        if conn.execute("select 1 from sqlite_master where name='mission_result_notices'").fetchone():
            conn.execute('delete from mission_result_notices where mission_id in (select id from mission_instances where guild_id=? and claimed_by_user_id=?)',(args.guild,args.user))
        missions=conn.execute('delete from mission_instances where guild_id=? and claimed_by_user_id=?',(args.guild,args.user)).rowcount
        conn.execute('delete from player_states where guild_id=? and user_id=?',(args.guild,args.user))
        if not args.keep_registration and conn.execute("select 1 from sqlite_master where name='player_registrations'").fetchone():
            conn.execute('delete from player_registrations where guild_id=? and user_id=?',(args.guild,args.user))
        conn.commit()
    print(f'Reset {player[0]} and {missions} owned contracts. Shared contracts and other players preserved.')
    print(f'Backup: {backup}')
if __name__=='__main__':main()

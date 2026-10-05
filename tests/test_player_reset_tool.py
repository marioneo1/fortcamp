import sqlite3
import subprocess
import sys
import tempfile
import unittest
from contextlib import closing
from pathlib import Path


class PlayerResetToolTests(unittest.TestCase):
    def test_reset_keeps_registration_and_other_players_and_removes_owned_notices(self):
        with tempfile.TemporaryDirectory() as tmp:
            path=Path(tmp)/'dev.db'
            with closing(sqlite3.connect(path)) as conn:
                conn.executescript('''
                    create table player_states(guild_id text,user_id text,display_name text);
                    create table player_registrations(guild_id text,user_id text);
                    create table mission_instances(id text,guild_id text,claimed_by_user_id text);
                    create table mission_result_notices(mission_id text);
                    insert into player_states values ('g','me','Me'),('g','friend','Friend');
                    insert into player_registrations values ('g','me'),('g','friend');
                    insert into mission_instances values ('owned','g','me'),('public','g',null),('other','g','friend');
                    insert into mission_result_notices values ('owned'),('other');
                ''')
                conn.commit()
            subprocess.run([sys.executable,'tools/reset_player.py','--database',str(path),
                            '--guild','g','--user','me','--keep-registration'],check=True,capture_output=True)
            with closing(sqlite3.connect(path)) as conn:
                self.assertEqual(conn.execute('select user_id from player_states').fetchall(),[('friend',)])
                self.assertEqual(conn.execute('select count(*) from player_registrations').fetchone()[0],2)
                self.assertEqual(conn.execute('select id from mission_instances').fetchall(),[('public',),('other',)])
                self.assertEqual(conn.execute('select mission_id from mission_result_notices').fetchall(),[('other',)])
            backup=next((path.parent/'backups').glob('*.sqlite'))
            with closing(sqlite3.connect(backup)) as conn:self.assertEqual(conn.execute('select count(*) from player_states').fetchone()[0],2)


if __name__=='__main__':unittest.main()

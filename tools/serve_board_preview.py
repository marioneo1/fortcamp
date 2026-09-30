"""Compatibility command for the local Vite board preview; does not start the game."""
import subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
if __name__=='__main__':
    try:subprocess.run(['node',str(ROOT/'tools/serve_board_preview.mjs')],cwd=ROOT,check=True)
    except KeyboardInterrupt:pass

"""Rebuild the authored Effekseer fire trial with the portable 1.70e editor."""
import argparse
import shutil
import subprocess
import urllib.request
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RELEASE = 'https://github.com/effekseer/Effekseer/releases/download/170e/Effekseer170eWin.zip'

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--editor', type=Path, help='Existing Effekseer 1.70e executable; otherwise use the local portable copy')
    args = parser.parse_args()
    work = ROOT / 'staging-ui/effekseer-fire-trial'
    work.mkdir(parents=True, exist_ok=True)
    editor = args.editor or work / 'editor/Tool/Effekseer.exe'
    texture = work / 'editor/Sample/01_Pierre01/Texture/Fire.png'
    if not editor.exists() or not texture.exists():
        archive = work / 'Effekseer170eWin.zip'
        if not archive.exists():
            print('Downloading the official portable Effekseer 1.70e editor (about 32 MB).')
            urllib.request.urlretrieve(RELEASE, archive)
        target = (work / 'editor').resolve()
        with zipfile.ZipFile(archive) as files:
            if any(not (target / name).resolve().is_relative_to(target) for name in files.namelist()):
                raise ValueError('Archive contains a path outside the editor folder')
            files.extractall(target)
    if not editor.exists():
        raise FileNotFoundError(editor)
    shutil.copy2(ROOT / 'docs/art/effekseer/campfire.efkproj', work / 'campfire.efkproj')
    (work / 'Texture').mkdir(exist_ok=True)
    shutil.copy2(texture, work / 'Texture/Fire.png')
    destination = ROOT / 'frontend/public/assets/effekseer/campfire-v1'
    (destination / 'Texture').mkdir(parents=True, exist_ok=True)
    shutil.copy2(texture, destination / 'Texture/Fire.png')
    subprocess.run([str(editor.resolve()), '-cui', '-in', str(work / 'campfire.efkproj'), '-e', str(destination / 'campfire.efk')], check=True, creationflags=subprocess.CREATE_NO_WINDOW)
    print(f'Built {destination / "campfire.efk"}; original source and texture remain intact.')

if __name__ == '__main__':
    main()

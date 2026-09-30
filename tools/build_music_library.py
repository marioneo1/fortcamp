"""Build the local and hosted seven-track listening library without generation or paid requests."""
import html
import json
from pathlib import Path
from generate_music_candidates import CANDIDATES, LOCATION_CANDIDATES, ROOT


def main():
    cards=[]
    for pack,candidates in [('guild-board-candidates-v1',CANDIDATES),('location-themes-v1',LOCATION_CANDIDATES)]:
        for candidate in candidates:
            identifier=candidate['id']
            source=ROOT/'staging-music'/pack/(identifier+'.mp3')
            if not source.exists():raise SystemExit(f'Missing listening copy: {source}')
            cards.append(f'''<article><small>{'GUILD BOARD - APPROVED' if identifier[:2]<'05' else 'NEW LOCATION THEME'}</small><h2>{html.escape(candidate['name'])}</h2><p>{html.escape(candidate['description'])}</p><audio controls preload="none" src="{pack}/{identifier}.mp3"></audio><label><input type="checkbox" data-repeat> Repeat</label><a href="{pack}/{identifier}.mp3" download>Download track</a><details><summary>Loop trial</summary><audio controls loop preload="none" src="{pack}/{identifier}_loop_preview.mp3"></audio></details></article>''')
    page='''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Fortcamp Music Library</title><style>:root{color-scheme:dark}body{background:#131a13;color:#ebeade;font:15px system-ui;margin:0;padding:24px}main{max-width:1080px;margin:auto}h1{margin-bottom:8px}p{color:#b9c3b2;line-height:1.6}.grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:18px;margin-top:25px}article{background:#202920;border:1px solid #475440;border-radius:15px;padding:22px}small,a{color:#d7b66a}h2{margin:10px 0}audio{width:100%;margin:12px 0}label{display:block;margin-bottom:15px}details{border-top:1px solid #475440;padding-top:15px;margin-top:18px}summary{cursor:pointer}input{accent-color:#d7b66a}button{padding:8px 12px;background:#384432;color:inherit;border:1px solid #647051;border-radius:8px;margin-left:20px;cursor:pointer}@media(max-width:700px){.grid{grid-template-columns:1fr}}</style><main><small>FORTCAMP SOUNDTRACK</small><h1>Music library</h1><p>Four approved guild tracks and three new location themes. All have gentle three-second endings. Originals remain preserved. One preview plays at a time.</p><label>Preview volume <input id="volume" type="range" min="0" max="100" value="55"><button id="stop">Stop all</button></label><div class="grid">'''+''.join(cards)+'''</div></main><script>const tracks=[...document.querySelectorAll('audio')],slider=document.querySelector('#volume');const volume=()=>tracks.forEach(a=>a.volume=Number(slider.value)/100);volume();slider.oninput=volume;tracks.forEach(a=>a.addEventListener('play',()=>tracks.forEach(other=>{if(other!==a)other.pause()})));document.querySelector('#stop').onclick=()=>tracks.forEach(a=>a.pause());document.querySelectorAll('[data-repeat]').forEach(box=>box.onchange=()=>box.closest('article').querySelector('audio').loop=box.checked);</script></html>'''
    for destination in [ROOT/'staging-music/LISTEN.html',ROOT/'frontend/public/assets/music/LISTEN.html']:
        destination.write_text(page,encoding='utf-8')
    print('Built seven-track music library; no API requests made.')


if __name__=='__main__':main()

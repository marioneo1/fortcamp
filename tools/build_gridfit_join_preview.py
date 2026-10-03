"""Write a standalone renderer trial; no active art, maps or saves are changed."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEST = ROOT / 'staging-terrain/building-toolset-v6-gridfit'
DEST.mkdir(parents=True, exist_ok=True)
(DEST / 'junction-preview.html').write_text('''<!doctype html><html lang="en"><meta charset="utf-8">
<title>Painted wall junction trial</title><style>
body{background:#172018;color:#eadfc8;font:16px system-ui;margin:24px;max-width:1600px}
h1{font-size:24px}button,select{font:inherit;padding:8px;background:#303c2c;color:inherit;border:1px solid #847855;border-radius:6px}
.controls{display:flex;gap:12px;align-items:center;flex-wrap:wrap;margin:16px 0}canvas{width:100%;height:auto;border:1px solid #736b50;border-radius:8px}a{color:#e1c785}
</style><h1>Corner, T and +: fixed-unit assembly</h1>
<p>One full span = 256px. Half span = 128px. Every top band = 48px thick. Painted side depth = 36px. All shapes use the same generated material without stretching.</p>
<div class="controls"><label>Turn <select id="rotation"><option value="0">0 degrees</option><option value="1">90 degrees</option><option value="2">180 degrees</option><option value="3">270 degrees</option></select></label><label>Surface <select id="variant"><option value="1">Clean</option><option value="2">Aged</option><option value="3">Cracked</option><option value="4">Moss</option></select></label><label><input type="checkbox" id="grid" checked> Show grid</label><button id="download">Save this preview</button></div>
<canvas id="preview" width="1536" height="1120"></canvas>
<p>This is a staging comparison, not the combat renderer. Top surfaces join before the shaded sides are drawn, so a T or + does not have a dark face painted through its center. The original materials remain active.</p>
<script src="junction-preview.js"></script></html>''', encoding='utf-8')
(DEST / 'junction-preview.js').write_text('''
const load=src=>new Promise((resolve,reject)=>{const im=new Image();im.onload=()=>resolve(im);im.onerror=()=>reject(Error(src));im.src=src});
const surface=(w,h)=>{const c=document.createElement('canvas');c.width=w;c.height=h;return c};
const shapes={Corner:[[-128,-24,128,48],[-24,0,48,128]],T:[[-128,-24,256,48],[-24,0,48,128]],'+':[[-128,-24,256,48],[-24,-128,48,256]]};
function rotateRect([x,y,w,h],turn){for(let n=0;n<turn;n++)[x,y,w,h]=[-y-h,x,h,w];return [x,y,w,h]}
let walls,floor,latest;
function renderPart(name,turn,variant){
 const size=512,cx=256,cy=256,rects=shapes[name].map(r=>rotateRect(r,turn));
 const mask=surface(size,size),mc=mask.getContext('2d');
 for(const [x,y,w,h] of rects)mc.fillRect(cx+x,cy+y,w,h);
 const wall=walls[variant-1];
 // The camera's side projection stays down, even when the logical join rotates.
 // Extrude the UNION, avoiding internal side faces underneath connected arms.
 const sideMask=surface(size,size),sm=sideMask.getContext('2d');
 sm.drawImage(mask,0,36);sm.globalCompositeOperation='destination-out';sm.drawImage(mask,0,0);
 const sideTexture=surface(256,36);sideTexture.getContext('2d').drawImage(wall,0,48,256,36,0,0,256,36);
 const out=surface(size,size),ctx=out.getContext('2d');
 ctx.fillStyle=ctx.createPattern(sideTexture,'repeat');ctx.fillRect(0,0,size,size);
 ctx.globalCompositeOperation='destination-in';ctx.drawImage(sideMask,0,0);ctx.globalCompositeOperation='source-over';
 for(const [x,y,w,h] of rects){
  ctx.save();ctx.beginPath();ctx.rect(cx+x,cy+y,w,h);ctx.clip();
  if(w>=h)ctx.drawImage(wall,0,0,w,48,cx+x,cy+y,w,48);
  else{ctx.translate(cx+x+w,cy+y);ctx.rotate(Math.PI/2);ctx.drawImage(wall,0,0,h,48,0,0,h,48)}
  ctx.restore();
 }
 // Matching 48px top patch conceals the crossing texture seam, never a column.
 ctx.save();ctx.beginPath();
 for(const [x,y,w,h] of rects)ctx.rect(cx+x,cy+y,w,h);
 ctx.clip();ctx.drawImage(wall,104,0,48,48,cx-24,cy-24,48,48);ctx.restore();
 return {image:out,rects};
}
function draw(){
 const turn=Number(document.querySelector('#rotation').value),variant=Number(document.querySelector('#variant').value),grid=document.querySelector('#grid').checked;
 const c=document.querySelector('#preview'),ctx=c.getContext('2d');ctx.fillStyle='#273329';ctx.fillRect(0,0,c.width,c.height);
 ctx.fillStyle='#eadfc8';ctx.font='bold 22px system-ui';ctx.fillText('Enlarged joins - one 256px construction unit',24,36);
 latest=[];
 for(const [i,name] of ['Corner','T','+'].entries()){
  const rendered=renderPart(name,turn,variant);latest.push(rendered);
  for(const [row,y] of [[0,64],[1,592]]){
   const x=i*512;
   ctx.save();ctx.beginPath();ctx.rect(x,y,512,512);ctx.clip();
   if(row)for(let fy=0;fy<512;fy+=256)for(let fx=0;fx<512;fx+=256)ctx.drawImage(floor,x+fx,y+fy);
   if(grid){ctx.strokeStyle=row?'rgba(234,223,200,.25)':'#455044';ctx.lineWidth=1;for(const p of [128,384]){ctx.beginPath();ctx.moveTo(x+p,y);ctx.lineTo(x+p,y+512);ctx.moveTo(x,y+p);ctx.lineTo(x+512,y+p);ctx.stroke()}}
   ctx.drawImage(rendered.image,x,y);
   ctx.restore();ctx.fillStyle='#eadfc8';ctx.font='bold 20px system-ui';ctx.fillText(name+(row?' on actual map paving':''),x+24,y+30);
  }
 }
 window.gridfitReady=true;window.gridfitGeometry=latest.map(r=>r.rects);
}
Promise.all([Promise.all([1,2,3,4].map(i=>load(`sprites/limestone_full_0${i}.png`))),load('../../frontend/public/assets/combat-terrain/bridge-v1/smithy_cobbles.png')]).then(([w,f])=>{walls=w;floor=f;draw()}).catch(e=>{document.body.append('Preview failed: '+e.message)});
for(const id of ['rotation','variant','grid'])document.querySelector('#'+id).onchange=draw;
document.querySelector('#download').onclick=()=>{const a=document.createElement('a');a.download='painted-junction-comparison.png';a.href=document.querySelector('#preview').toDataURL('image/png');a.click()};
''', encoding='utf-8')
print(DEST / 'junction-preview.html')

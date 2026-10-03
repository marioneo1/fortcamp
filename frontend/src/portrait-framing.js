import './portrait-framing.css';

export function normalizeFrame(frame={}){
  const clamp=(value,fallback,lo,hi)=>Number.isFinite(Number(value))?Math.max(lo,Math.min(hi,Number(value))):fallback;
  return {x:clamp(frame.x,.5,0,1),y:clamp(frame.y,.5,0,1),size:clamp(frame.size,1,.25,2.5)};
}

// The source image keeps its aspect ratio; only the containing circle clips it.
export function frameGeometry(frame,width,height){
  const f=normalizeFrame(frame),diameter=Math.min(width,height)*f.size;
  return {width:width/diameter*100,height:height/diameter*100,
    left:50-f.x*width/diameter*100,top:50-f.y*height/diameter*100};
}

export function framedImage(src,frame,esc,classes='',attributes=''){
  const f=normalizeFrame(frame);
  return `<span class="portrait-crop ${classes}" ${attributes}><img class="portrait-framed-image" src="${esc(src)}" alt="" data-face-x="${f.x}" data-face-y="${f.y}" data-face-size="${f.size}"></span>`;
}

function positionImage(image){
  if(!image.naturalWidth)return;
  const g=frameGeometry({x:image.dataset.faceX,y:image.dataset.faceY,size:image.dataset.faceSize},image.naturalWidth,image.naturalHeight);
  for(const key of ['width','height','left','top'])image.style.setProperty(key,g[key]+'%','important');
}
document.addEventListener('load',event=>{if(event.target.matches?.('.portrait-framed-image'))positionImage(event.target)},true);
document.addEventListener('error',event=>{const image=event.target;if(image.matches?.('.portrait-framed-image')){image.parentElement.classList.add('portrait-unavailable');image.parentElement.title='Portrait could not be loaded'}},true);

export function openPortraitFraming({character,src,onSave,onReset,onError}){
  const dialog=document.createElement('dialog');dialog.className='portrait-framing-dialog';
  dialog.innerHTML=`<header><div><small>PORTRAIT FRAMING</small><h2>Adjust character icon</h2></div><button type="button" data-close aria-label="Close">×</button></header><p>Drag the circle onto the face. A larger circle includes more hair and headroom.</p><div class="portrait-framing-workspace"><canvas data-editor width="420" height="420" aria-label="Drag to position the portrait circle"></canvas><aside><canvas data-preview width="180" height="180" aria-label="Battle icon preview"></canvas><b>Battle icon preview</b><small>The full photo stays intact. The icon frame keeps its current size.</small></aside></div><div class="portrait-framing-controls"><label>Horizontal position<input type="range" data-axis="x" min="0" max="1" step=".005"></label><label>Vertical position<input type="range" data-axis="y" min="0" max="1" step=".005"></label><label>Circle size<input type="range" data-axis="size" min=".25" max="2.5" step=".01"></label></div><p data-error class="portrait-framing-error" role="status"></p><footer><button type="button" data-reset>Use recommended framing</button><div><button type="button" data-close>Cancel</button><button type="button" data-save class="primary">Save framing</button></div></footer>`;
  document.body.append(dialog);dialog.showModal();
  let frame=normalizeFrame(character.portrait_frame),ready=false,busy=false;
  const image=new Image(),editor=dialog.querySelector('[data-editor]'),preview=dialog.querySelector('[data-preview]');
  const bounds=()=>{const scale=Math.min(editor.width/image.naturalWidth,editor.height/image.naturalHeight);return {w:image.naturalWidth*scale,h:image.naturalHeight*scale,x:(editor.width-image.naturalWidth*scale)/2,y:(editor.height-image.naturalHeight*scale)/2}};
  function draw(){
    dialog.querySelectorAll('[data-axis]').forEach(input=>input.value=frame[input.dataset.axis]);
    if(!ready)return;
    const b=bounds(),cx=b.x+frame.x*b.w,cy=b.y+frame.y*b.h,r=frame.size*Math.min(b.w,b.h)/2;
    const ctx=editor.getContext('2d');ctx.fillStyle='#171b19';ctx.fillRect(0,0,420,420);ctx.drawImage(image,b.x,b.y,b.w,b.h);
    ctx.save();ctx.fillStyle='#08100dcc';ctx.beginPath();ctx.rect(0,0,420,420);ctx.arc(cx,cy,r,0,Math.PI*2,true);ctx.fill('evenodd');ctx.restore();
    ctx.strokeStyle='#e3c787';ctx.lineWidth=2;ctx.beginPath();ctx.arc(cx,cy,r,0,Math.PI*2);ctx.stroke();
    ctx.beginPath();ctx.moveTo(cx-8,cy);ctx.lineTo(cx+8,cy);ctx.moveTo(cx,cy-8);ctx.lineTo(cx,cy+8);ctx.stroke();
    const p=preview.getContext('2d');p.clearRect(0,0,180,180);p.save();p.beginPath();p.arc(90,90,89,0,Math.PI*2);p.clip();p.fillStyle='#171b19';p.fillRect(0,0,180,180);
    const g=frameGeometry(frame,image.naturalWidth,image.naturalHeight);p.drawImage(image,g.left*1.8,g.top*1.8,g.width*1.8,g.height*1.8);p.restore();
    p.strokeStyle='#c9ad70';p.lineWidth=2;p.beginPath();p.arc(90,90,89,0,Math.PI*2);p.stroke();
  }
  image.onload=()=>{ready=true;draw()};image.onerror=()=>dialog.querySelector('[data-error]').textContent='The photo could not be loaded.';image.src=src;
  const close=()=>{if(!busy){dialog.close();dialog.remove()}};
  dialog.querySelectorAll('[data-close]').forEach(button=>button.onclick=close);
  dialog.addEventListener('cancel',event=>{event.preventDefault();close()});
  dialog.onclick=event=>{if(event.target===dialog){const r=dialog.getBoundingClientRect();if(event.clientX<r.left||event.clientX>r.right||event.clientY<r.top||event.clientY>r.bottom)close()}};
  dialog.querySelectorAll('[data-axis]').forEach(input=>input.oninput=()=>{frame[input.dataset.axis]=Number(input.value);draw()});
  function point(event){if(!ready||busy)return;const rect=editor.getBoundingClientRect(),b=bounds();frame.x=Math.max(0,Math.min(1,((event.clientX-rect.left)*420/rect.width-b.x)/b.w));frame.y=Math.max(0,Math.min(1,((event.clientY-rect.top)*420/rect.height-b.y)/b.h));draw()}
  editor.onpointerdown=event=>{editor.setPointerCapture(event.pointerId);point(event)};editor.onpointermove=event=>{if(editor.hasPointerCapture(event.pointerId))point(event)};
  editor.onpointerup=event=>{if(editor.hasPointerCapture(event.pointerId))editor.releasePointerCapture(event.pointerId)};
  editor.onwheel=event=>{event.preventDefault();if(!busy){frame.size=Math.max(.25,Math.min(2.5,frame.size+event.deltaY*.001));draw()}};
  async function save(reset){if(busy||!ready)return;busy=true;dialog.querySelectorAll('button,input').forEach(e=>e.disabled=true);try{await(reset?onReset():onSave(frame));busy=false;close()}catch(error){busy=false;dialog.querySelectorAll('button,input').forEach(e=>e.disabled=false);dialog.querySelector('[data-error]').textContent=error.message;onError?.(error)}}
  dialog.querySelector('[data-save]').onclick=()=>save(false);dialog.querySelector('[data-reset]').onclick=()=>save(true);draw();
}

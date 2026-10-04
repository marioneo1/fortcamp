import './construction-ui.css';
import {anchors,wallArms,snapAnchor,validPlacement,rotatePlacement} from './construction-geometry.js';
import {constructionSVG} from './construction-render.js';
import {confirmAction} from './confirmation-ui.js';

export async function openConstruction({api,esc,definitions,onSave,onError}){
 let data;try{data=await api('/api/construction')}catch(e){onError(e.message);return}
 let plan=structuredClone(data.plan),revision=data.plan.revision,saved=JSON.stringify(plan),selected='',mode='ground',rotation=0,zoom=1,query='',ghost=null,busy=false;
 const size=data.size,cat=data.catalogue,undo=[],redo=[];
 const brush={ground:cat.ground.grass_short?'grass_short':Object.keys(cat.ground)[0],props:cat.props.crate_closed?'crate_closed':Object.keys(cat.props)[0],shape:'straight',anchor:'snap',material:'timber',posts:'auto',w:1,h:1,offset_x:0,offset_y:0,blocking:false,open:false,broken:false};
 const dialog=document.createElement('dialog');dialog.className='construction-dialog';
 dialog.innerHTML=`<header><div><div class="eyebrow">YOUR SETTLEMENT · CONSTRUCTION</div><h2>Make this camp your own</h2><small>Ground, movable props and snapping walls. Decorations are free in this first pass; they do not grant loot, production or defense bonuses.</small></div><button data-close aria-label="Close construction">×</button></header>
 <nav class="construction-tools">${[['ground','Floors & terrain'],['props','Props'],['walls','Walls'],['select','Select / move'],['erase','Erase']].map(([id,label])=>`<button data-tool="${id}">${label}</button>`).join('')}<span></span><button data-undo>Undo</button><button data-redo>Redo</button></nav>
 <div class="construction-workspace"><aside class="construction-library"><label>Find an asset<input data-search type="search" placeholder="Grass, cage, bed…"></label><div data-palette></div></aside>
 <section class="construction-map"><div class="construction-camera"><b>${size.w} × ${size.h} cells</b><button data-zoom="-.25" aria-label="Zoom out">−</button><button data-zoom="0">100%</button><button data-zoom=".25" aria-label="Zoom in">+</button><small>R rotate · Ctrl+Z undo · Ctrl+Shift+Z redo</small></div><div class="construction-scroll"><svg data-map viewBox="0 0 ${size.w} ${size.h}" xmlns="http://www.w3.org/2000/svg" aria-label="Camp construction grid"></svg></div><p data-help></p></section>
 <aside class="construction-inspector"><h3 data-inspector-heading>Placement</h3><div data-inspector></div><p class="construction-error" role="alert" data-error></p></aside></div>
 <footer><small data-status>Nothing saved until you choose Save camp.</small><div><button data-export>Export layout</button><button data-close>Close</button><button data-save class="primary">Save camp</button></div></footer>`;
 document.body.append(dialog);dialog.showModal();const find=s=>dialog.querySelector(s),svg=find('[data-map]');
 const selectedObject=()=>{for(const layer of ['props','walls']){const item=plan[layer].find(i=>i.id===selected);if(item)return {item,layer}}return null};
 const remember=()=>{undo.push(structuredClone(plan));if(undo.length>60)undo.shift();redo.length=0};
 function renderMap(){svg.style.width=`${size.w*64*zoom}px`;svg.style.height=`${size.h*64*zoom}px`;svg.innerHTML=constructionSVG(plan,size,cat,{selected,ghost,facilities:data.buildings,definitions});find('[data-save]').disabled=busy;find('[data-undo]').disabled=!undo.length;find('[data-redo]').disabled=!redo.length;find('[data-status]').textContent=JSON.stringify(plan)===saved?'Camp layout saved.':'Unsaved changes · Save camp to keep this layout.'}
 function palette(){
  dialog.querySelectorAll('[data-tool]').forEach(b=>b.classList.toggle('active',b.dataset.tool===mode));
  const entries=mode==='walls'?Object.keys(wallArms).map(id=>[id,{name:{straight:'Full wall',half:'Half wall',corner:'Corner',tee:'T junction',cross:'+ junction',gate:'Gate'}[id]}]):Object.entries(cat[mode]||{});
  find('[data-palette]').innerHTML=entries.filter(([,item])=>item.name.toLowerCase().includes(query)).map(([id,item])=>`<button data-asset="${esc(id)}" class="${(mode==='walls'?brush.shape:brush[mode])===id?'active':''}">${item.file?`<img src="/assets/combat-terrain/${esc(item.file)}" alt="" loading="lazy">`:`<span class="wall-palette-shape">${{straight:'━',half:'╸',corner:'┏',tee:'┳',cross:'╋',gate:'▥'}[id]}</span>`}<small>${esc(item.name)}</small></button>`).join('')||'<p>Select a placed object to adjust it, or choose a construction layer.</p>';
  find('[data-help]').textContent={ground:'Click and drag to paint cells. R rotates your terrain brush.',props:'Click to place. Select / move lets you drag an object to another cell. Adjust its position inside the cell in Placement.',walls:'Snap follows the closest cell edge or center. Connections meet on the same grid points. R rotates the piece. Automatic posts appear only at exposed ends.',select:'Click an object to select it. Drag objects to move them; use Placement for precise offsets. Click empty ground to deselect.',erase:'Click an object to remove it; click empty ground to remove its painted floor. Undo restores the edit.'}[mode];
  find('[data-palette]').querySelectorAll('[data-asset]').forEach(b=>b.onclick=()=>{if(mode==='walls')brush.shape=b.dataset.asset;else{brush[mode]=b.dataset.asset;if(mode==='props'){[brush.w,brush.h]=cat.props[brush.props].footprint;if(rotation%180)[brush.w,brush.h]=[brush.h,brush.w]}}selected='';palette();inspector();renderMap()});
 }
 function inspector(){
  const selection=selectedObject(),item=selection?.item||brush,layer=selection?.layer||mode;
  find('[data-inspector-heading]').textContent=selection?'Selected object':'Placement';
  const select=(key,label,options,value)=>`<label>${label}<select data-field="${key}">${options.map(([id,name])=>`<option value="${id}" ${String(value)===id?'selected':''}>${name}</option>`).join('')}</select></label>`;
  const range=(key,label,value)=>`<label>${label}<input data-field="${key}" type="range" min="-.45" max=".45" step=".025" value="${value||0}"><small data-range-value="${key}">${Math.round((value||0)*100)}% of a cell</small></label>`;
  const check=(key,label)=>`<label class="construction-check"><input data-field="${key}" type="checkbox" ${item[key]?'checked':''}>${label}</label>`;
  let html=`<p>${selection?esc(selection.layer==='props'?cat.props[item.asset]?.name||'Prop':item.shape+' wall'):'Current brush'} · ${selection?item.rotation:rotation}°</p><button data-rotate>Rotate [R]</button>`;
  if(layer==='props')html+=select('w','Footprint width',[1,2,3,4].map(v=>[String(v),`${v} cell${v===1?'':'s'}`]),String(item.w))+select('h','Footprint height',[1,2,3,4].map(v=>[String(v),`${v} cell${v===1?'':'s'}`]),String(item.h))+range('offset_x','Position left / right',item.offset_x)+range('offset_y','Position up / down',item.offset_y)+check('blocking','Reserve this footprint')+'<small>Reserved footprints keep future facilities out. Offsets move the artwork, not the reserved cells.</small>';
  if(layer==='walls')html+=select('anchor','Position',[...(!selection?[['snap','Snap to pointer']]:[]),...Object.keys(anchors).map(v=>[v,v==='center'?'Center':{north:'Top edge',east:'Right edge',south:'Bottom edge',west:'Left edge'}[v]])],item.anchor)+select('material','Material',cat.wall_materials.map(v=>[v,v]),item.material)+select('posts','End posts',[['auto','Automatic exposed ends'],['none','No posts'],['both','Posts on piece ends']],item.posts)+check('broken','Broken variation')+(item.shape==='gate'?check('open','Gate open'):'');
  if(selection)html+=`<label>Cell X<input data-field="x" type="number" min="0" max="${size.w-1}" value="${item.x}"></label><label>Cell Y<input data-field="y" type="number" min="0" max="${size.h-1}" value="${item.y}"></label><button data-delete>Remove object</button>`;
  find('[data-inspector]').innerHTML=html;
  find('[data-rotate]').onclick=rotate;
  find('[data-inspector]').querySelectorAll('[data-field]').forEach(input=>{let rangeEditing=false;input.addEventListener('change',()=>{if(input.type==='range')rangeEditing=false});input.addEventListener(input.type==='range'?'input':'change',()=>{
   const key=input.dataset.field,value=input.type==='checkbox'?input.checked:['w','h','x','y','offset_x','offset_y'].includes(key)?Number(input.value):input.value;
   if(selection){const next={...item,[key]:value};if(!validPlacement(next,layer,size)){find('[data-error]').textContent='That piece extends outside the camp.';inspector();return}if(input.type!=='range'||!rangeEditing)remember();rangeEditing=input.type==='range';Object.assign(item,next)}else brush[key]=value;
   find('[data-error]').textContent='';const label=find(`[data-range-value="${key}"]`);if(label)label.textContent=`${Math.round(value*100)}% of a cell`;renderMap();
  })});
  if(selection)find('[data-delete]').onclick=()=>{remember();plan[selection.layer]=plan[selection.layer].filter(p=>p.id!==selected);selected='';renderMap();inspector()};
 }
 function rotate(){const selection=selectedObject();if(selection){const next=rotatePlacement(selection.item,selection.layer);if(!validPlacement(next,selection.layer,size)){find('[data-error]').textContent='Rotation extends outside the camp.';return}remember();Object.assign(selection.item,next)}else{rotation=(rotation+90)%360;if(mode==='props')[brush.w,brush.h]=[brush.h,brush.w]}renderMap();inspector()}
 function coords(e){const r=svg.getBoundingClientRect();return {px:(e.clientX-r.left)*size.w/r.width,py:(e.clientY-r.top)*size.h/r.height}}
 function makeGhost(e){const {px,py}=coords(e),x=Math.floor(px),y=Math.floor(py);if(x<0||y<0||x>=size.w||y>=size.h)return null;
  if(mode==='ground')return {layer:'ground',x,y};
  if(mode==='props')return {layer:'props',item:{id:'preview',asset:brush.props,x,y,rotation,w:brush.w,h:brush.h,offset_x:brush.offset_x,offset_y:brush.offset_y,blocking:brush.blocking}};
  if(mode==='walls')return {layer:'walls',item:{id:'preview',x,y,rotation,shape:brush.shape,anchor:brush.anchor==='snap'?snapAnchor(px,py).anchor:brush.anchor,material:brush.material,posts:brush.posts,open:brush.open,broken:brush.broken}};
  return null;
 }
 let gesture=null;
 function paintBetween(a,b){if(!b)return;const steps=Math.max(Math.abs(b.x-a.x),Math.abs(b.y-a.y),1);for(let i=0;i<=steps;i++)paint({layer:'ground',x:Math.round(a.x+(b.x-a.x)*i/steps),y:Math.round(a.y+(b.y-a.y)*i/steps)})}
 function paint(g){if(!g)return;if(g.layer==='ground')plan.ground[`${g.x},${g.y}`]={asset:brush.ground,rotation};else if(validPlacement(g.item,g.layer,size)){
   const next={...g.item,id:crypto.randomUUID()};
   if(g.layer==='walls'){const existing=plan.walls.find(w=>w.x===next.x&&w.y===next.y&&w.anchor===next.anchor&&w.rotation===next.rotation&&w.shape===next.shape);if(existing)next.id=existing.id;plan.walls=plan.walls.filter(w=>w.id!==next.id)}
   plan[g.layer].push(next);
  }else find('[data-error]').textContent='That piece extends outside the camp. Rotate it or choose another position.';
 }
 svg.onpointerdown=e=>{
  if(e.button!==0||busy)return;e.preventDefault();svg.setPointerCapture(e.pointerId);const target=e.target.closest('[data-construction-id]'),{px,py}=coords(e);
  if(mode==='select'){selected=target?.dataset.constructionId||'';const s=selectedObject();gesture=s?{kind:'drag',layer:s.layer,before:structuredClone(plan),start:[px,py],origin:[s.item.x,s.item.y],id:selected}:null;inspector()}
  else if(mode==='erase'){remember();if(target){const layer=target.dataset.constructionLayer;plan[layer]=plan[layer].filter(p=>p.id!==target.dataset.constructionId)}else delete plan.ground[`${Math.floor(px)},${Math.floor(py)}`];selected=''}
  else{remember();ghost=makeGhost(e);paint(ghost);gesture=mode==='ground'?{kind:'paint',last:ghost}:null}
  renderMap();
 };
 svg.onpointermove=e=>{
  if(gesture?.kind==='paint'){const next=makeGhost(e);if(next){paintBetween(gesture.last,next);gesture.last=next}}
  else if(gesture?.kind==='drag'){const {px,py}=coords(e),p=plan[gesture.layer].find(p=>p.id===gesture.id),next={...p,x:gesture.origin[0]+Math.round(px-gesture.start[0]),y:gesture.origin[1]+Math.round(py-gesture.start[1])};if(validPlacement(next,gesture.layer,size))Object.assign(p,next)}
  else ghost=makeGhost(e);
  renderMap();
 };
 svg.onpointerup=()=>{if(gesture?.kind==='drag'&&JSON.stringify(gesture.before)!==JSON.stringify(plan)){undo.push(gesture.before);redo.length=0}gesture=null;renderMap();inspector()};
 svg.onpointercancel=()=>{gesture=null};svg.onpointerleave=()=>{if(!gesture){ghost=null;renderMap()}};
 function history(direction){const from=direction==='undo'?undo:redo,to=direction==='undo'?redo:undo;if(!from.length)return;to.push(structuredClone(plan));plan=from.pop();selected='';ghost=null;renderMap();inspector()}
 find('[data-undo]').onclick=()=>history('undo');find('[data-redo]').onclick=()=>history('redo');
 dialog.querySelectorAll('[data-tool]').forEach(b=>b.onclick=()=>{mode=b.dataset.tool;if(mode!=='select')selected='';ghost=null;query='';find('[data-search]').value='';palette();inspector();renderMap()});
 find('[data-search]').oninput=e=>{query=e.target.value.toLowerCase();palette()};
 dialog.querySelectorAll('[data-zoom]').forEach(b=>b.onclick=()=>{zoom=b.dataset.zoom==='0'?1:Math.max(.5,Math.min(2,zoom+Number(b.dataset.zoom)));find('[data-zoom="0"]').textContent=`${Math.round(zoom*100)}%`;renderMap()});
 dialog.onkeydown=e=>{if(e.target.matches('input,select,textarea'))return;if(e.key.toLowerCase()==='r'){e.preventDefault();rotate()}if((e.ctrlKey||e.metaKey)&&e.key.toLowerCase()==='z'){e.preventDefault();history(e.shiftKey?'redo':'undo')}};
 const close=async()=>{if(busy)return;if(JSON.stringify(plan)!==saved&&!await confirmAction({title:'Discard construction changes?',message:'Your last saved camp layout will remain.',confirmLabel:'Discard changes',danger:true}))return;dialog.close();dialog.remove()};
 dialog.querySelectorAll('[data-close]').forEach(b=>b.onclick=close);dialog.oncancel=e=>{e.preventDefault();close()};
 find('[data-save]').onclick=async()=>{if(busy)return;busy=true;renderMap();try{const result=await api('/api/construction',{method:'PUT',body:JSON.stringify({revision,plan})});plan=result.plan;revision=plan.revision;saved=JSON.stringify(plan);find('[data-error]').textContent='';onSave(result.state)}catch(e){find('[data-error]').textContent=e.message}finally{busy=false;renderMap()}};
 find('[data-export]').onclick=()=>{const blob=new Blob([JSON.stringify({format:'fortcamp-construction',size,plan},null,2)],{type:'application/json'}),url=URL.createObjectURL(blob),a=document.createElement('a');a.href=url;a.download='fortcamp-camp-layout.json';a.click();setTimeout(()=>URL.revokeObjectURL(url),1000)};
 palette();inspector();renderMap();
}

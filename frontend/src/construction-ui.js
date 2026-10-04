import './construction-ui.css';
import {anchors,defaultWallAnchor,wallPieces,availableWallPieces,wallLibraryPiece,wallLibraryEntries,placementError,rotatePlacement,nudgePlacement,newPlan} from './construction-geometry.js';
import {constructionSVG} from './construction-render.js';
import {confirmAction} from './confirmation-ui.js';
import {snapWall,rotateSnappedWall} from './construction-snapping.js';
import {wheelZoom} from './battle-camera.js';
import {rectangleCells,wallRun,wallRunError} from './construction-strokes.js';
import {wallSegments} from './construction-geometry.js';

export async function openConstruction({api,esc,definitions,onSave,onError,debugLab=false}){
 let data;try{data=await api(debugLab?'/api/debug/construction/wall-kits':'/api/construction')}catch(e){onError(e.message);return}
 let plan=structuredClone(data.plan),revision=data.plan.revision,saved=JSON.stringify(plan),selected='',mode=debugLab?'walls':'ground',rotation=0,zoom=debugLab?.5:1,query='',ghost=null,busy=false;
 const size=data.size,cat=data.catalogue,undo=[],redo=[];let wallKit=debugLab&&data.kits?.plain_wood_v1?'plain_wood_v1':'placeholder';
 let snapping=true,snapLock=null;try{snapping=localStorage.getItem('fortcamp.construction.snapping')!=='off'}catch{}
 const brush={ground:cat.ground.grass_short?'grass_short':Object.keys(cat.ground)[0],props:cat.props.crate_closed?'crate_closed':Object.keys(cat.props)[0],piece:'horizontal_plain',shape:'straight',anchor:'north',material:'timber',posts:'none',w:1,h:1,offset_x:0,offset_y:0,blocking:false,open:false,broken:false};
 const dialog=document.createElement('dialog');dialog.className='construction-dialog';
 dialog.innerHTML=`<header><div><div class="eyebrow">YOUR SETTLEMENT · CONSTRUCTION</div><h2>${debugLab?'Wall Kit Lab':'Make this camp your own'}</h2><small>${debugLab?'DEBUG ONLY - Temporary layout. Changes here never alter your camp or player save.':'Ground, movable props and snapping walls. Decorations are free in this first pass; they do not grant loot, production or defense bonuses.'}</small></div><button data-close aria-label="Close construction">×</button></header>
 <nav class="construction-tools">${[['ground','Floors & terrain [F]'],['props','Props [P]'],['walls','Walls [W]'],['select','Select / move [V]'],['erase','Remove [Del]']].map(([id,label])=>`<button data-tool="${id}">${label}</button>`).join('')}<button data-snap aria-pressed="${snapping}">Snapping [S]: ${snapping?'On':'Off'}</button><span></span><button data-undo>Undo</button><button data-redo>Redo</button></nav>
 <div class="construction-workspace"><aside class="construction-library"><label>Find an asset<input data-search type="search" placeholder="Grass, cage, bed…"></label><div data-palette></div></aside>
 <section class="construction-map"><div class="construction-camera"><b>${size.w} × ${size.h} cells</b>${debugLab?`<label class="construction-kit-picker">DEBUG WALL KIT<select data-wall-kit>${Object.entries(data.kits).map(([id,kit])=>`<option value="${esc(id)}" ${id===wallKit?'selected':''}>${esc(kit.name)}</option>`).join('')}</select></label>`:''}<button data-zoom="-.25" aria-label="Zoom out">−</button><button data-zoom="0">100%</button><button data-zoom=".25" aria-label="Zoom in">+</button><small>Wheel zoom | Shift+wheel scroll | R rotate | S snapping | Arrows position | Home center | Ctrl+Z undo</small><span data-snap-state role="status"></span></div><div class="construction-scroll"><svg data-map viewBox="0 0 ${size.w} ${size.h}" xmlns="http://www.w3.org/2000/svg" tabindex="0" aria-label="Camp construction grid"></svg></div><p data-help></p></section>
 <aside class="construction-inspector"><h3 data-inspector-heading>Placement</h3><div data-inspector></div><p class="construction-error" role="alert" data-error></p></aside></div>
 <footer><small data-status>Nothing saved until you choose Save camp.</small><div><button data-export>Export layout</button><button data-close>Close</button><button data-save class="primary">Save camp</button></div></footer>`;
 document.body.append(dialog);dialog.showModal();const find=s=>dialog.querySelector(s),svg=find('[data-map]');

 const scroll=find('.construction-scroll');
 svg.innerHTML='<g data-scene></g><g data-preview pointer-events="none"></g>';
 const scene=svg.querySelector('[data-scene]'),preview=svg.querySelector('[data-preview]');
 let gesture=null,lastPointer=null,previewFrame=0,previewKey='',hiddenKey='',removeHover=null;
 const selectedObject=()=>{for(const layer of ['props','walls']){const item=plan[layer].find(i=>i.id===selected);if(item)return {item,layer}}return null};
 const showPlacementError=error=>{const label=find('[data-error]');if(label.textContent!==error)label.textContent=error};
 const remember=()=>{undo.push(structuredClone(plan));if(undo.length>60)undo.shift();redo.length=0};
 function renderMap(){
  svg.style.width=`${size.w*64*zoom}px`;svg.style.height=`${size.h*64*zoom}px`;
  scene.innerHTML=constructionSVG(plan,size,cat,{selected,facilities:data.buildings,definitions,wallKit});hiddenKey='';previewKey='';
  refreshStatus();
  drawPreview();
 }
 function refreshStatus(){
  find('[data-save]').disabled=busy||!!gesture||debugLab;find('[data-undo]').disabled=!undo.length||!!gesture;find('[data-redo]').disabled=!redo.length||!!gesture;
  find('[data-status]').textContent=debugLab?'Debug layout only - nothing here is saved to your camp.':JSON.stringify(plan)===saved?'Camp layout saved.':'Unsaved changes - Save camp to keep this layout.';
 }
 function renderObject(item,layer){
  if(layer==='walls'&&!item.piece){renderMap();return} // Legacy automatic posts depend on neighbors.
  const old=Array.from(scene.querySelectorAll('[data-construction-id]')).find(el=>el.dataset.constructionId===item.id);
  if(!old){renderMap();return}
  old.outerHTML=constructionSVG({...newPlan(),[layer]:[item]},size,cat,{selected,grid:false,background:false,wallKit});refreshStatus();
 }
 // Pointer movement never rebuilds the ground, facilities or placed-object DOM.
 function drawPreview(){
  previewFrame=0;const hide=JSON.stringify([gesture?.kind==='move'?gesture.id:'',...(gesture?.removed||[]),removeHover?.item?.id]);
  if(hide!==hiddenKey){hiddenKey=hide;scene.querySelectorAll('[data-construction-id]').forEach(el=>{el.style.visibility=gesture?.kind==='move'&&el.dataset.constructionId===gesture.id?'hidden':'';el.classList.toggle('construction-remove-pending',!!gesture?.removed?.has(el.dataset.constructionId));el.classList.toggle('construction-remove-hover',removeHover?.item?.id===el.dataset.constructionId)})}
  const label=find('[data-snap-state]');let message=ghost?.snapped?'Connected — R keeps the join':snapping&&mode==='walls'?'Snapping on — drag near a wall end':'';
  if(gesture?.kind==='paint')message=`${Object.keys(gesture.tiles).length} floors — release inside to place; outside to cancel`;
  if(gesture?.kind==='wall-run')message=`${ghost?.items?.length||0} wall pieces — release inside to place; outside to cancel`;
  if(mode==='erase')message=gesture?gesture.removeFloor?`${gesture.ground.size} floors marked for removal`:`${gesture.removed.size} objects marked for removal`:removeHover?.layer==='ground'?'Remove floor — drag a rectangle':removeHover?.item?`Remove ${removeHover.layer==='walls'?'wall':cat.props[removeHover.item.asset]?.name||'prop'} — hold Shift for floors`:'Remove props/walls — hold Shift to remove floors';
  if(label.textContent!==message)label.textContent=message;
  const key=JSON.stringify([ghost,gesture?.tiles,[...(gesture?.ground||[])],[...(gesture?.removed||[])],removeHover]);if(key===previewKey)return;previewKey=key;
  if(gesture?.kind==='paint')preview.innerHTML=`<g data-floor-fill opacity=".85">${constructionSVG({ground:gesture.tiles,props:[],walls:[]},size,cat,{grid:false,background:false})}${Object.keys(gesture.tiles).map(key=>{const [x,y]=key.split(',');return `<rect data-floor-preview x="${x}" y="${y}" width="1" height="1" fill="#eadc8b" fill-opacity=".1" stroke="#ffe5a1" stroke-width=".025"/>`}).join('')}</g>`;
  else if(gesture?.kind==='wall-run')preview.innerHTML=ghost?.items?.length?`<g data-wall-run opacity=".7">${constructionSVG({...newPlan(),walls:ghost.items},size,cat,{grid:false,background:false,wallKit,selected:ghost.item.id})}${ghost.error?ghost.items.flatMap(w=>wallSegments(w)).map(([a,b])=>`<path d="M${a.join(' ')} L${b.join(' ')}" fill="none" stroke="#ff7c6a" stroke-width=".07"/>`).join(''):''}</g>`:'';
  else if(mode==='erase')preview.innerHTML=removalPreview();
  else if(ghost)preview.innerHTML=constructionSVG(newPlan(),size,cat,{ghost,grid:false,background:false,wallKit})+(ghost.snapped?ghost.contacts.map(([x,y])=>`<circle data-snap-port cx="${x}" cy="${y}" r=".085" fill="#b8ffe0" stroke="#183c30" stroke-width=".025"/>`).join(''):'');
  else preview.innerHTML='';
 }
 function removalPreview(){
  const cells=gesture?.removeFloor?[...gesture.ground]:removeHover?.layer==='ground'?[`${removeHover.x},${removeHover.y}`]:[];
  let html=cells.map(key=>{const [x,y]=key.split(',');return `<rect data-remove-floor x="${x}" y="${y}" width="1" height="1" fill="#f16556" fill-opacity=".28" stroke="#ffc1a1" stroke-width=".045" stroke-dasharray=".12 .04"/>`}).join('');
  if(removeHover?.item){
   const {item,layer}=removeHover,points=layer==='walls'?wallSegments(item).flat():[[item.x+(item.offset_x||0),item.y+(item.offset_y||0)],[item.x+item.w+(item.offset_x||0),item.y+item.h+(item.offset_y||0)]];
   const minX=Math.min(...points.map(p=>p[0])),maxX=Math.max(...points.map(p=>p[0])),minY=Math.min(...points.map(p=>p[1])),maxY=Math.max(...points.map(p=>p[1])),cx=(minX+maxX)/2,cy=(minY+maxY)/2;
   html+=`<g data-remove-object transform="translate(${cx} ${cy}) scale(1.1) translate(${-cx} ${-cy})">${constructionSVG({...newPlan(),[layer]:[item]},size,cat,{grid:false,background:false,wallKit})}<rect x="${minX-.12}" y="${minY-.12}" width="${maxX-minX+.24}" height="${maxY-minY+.24}" fill="#f1775c" fill-opacity=".14" stroke="#ffc1a1" stroke-width=".035" stroke-dasharray=".1 .035"/></g>`;
  }
  return html;
 }
 function schedulePreview(){if(!previewFrame)previewFrame=requestAnimationFrame(drawPreview)}
 function chooseAsset(id){
  if(mode==='walls'){brush.piece=id;brush.shape=wallPieces[id].shape;brush.anchor=defaultWallAnchor(id);rotation=0}
  else{brush[mode]=id;if(mode==='props'){[brush.w,brush.h]=cat.props[id].footprint;if(rotation%180)[brush.w,brush.h]=[brush.h,brush.w]}}
  selected='';find('[data-palette]').querySelectorAll('[data-asset]').forEach(b=>b.classList.toggle('active',b.dataset.asset===id));inspector();
 }
 function palette(){
  dialog.querySelectorAll('[data-tool]').forEach(b=>b.classList.toggle('active',b.dataset.tool===mode));
  const entries=mode==='walls'?wallLibraryEntries():Object.entries(cat[mode]||{});
  find('[data-palette]').innerHTML=entries.filter(([,item])=>item.name.toLowerCase().includes(query)).map(([id,item])=>`<button draggable="false" data-asset="${esc(id)}" class="${(mode==='walls'?wallLibraryPiece(brush.piece):brush[mode])===id?'active':''}">${item.file?`<img draggable="false" src="/assets/combat-terrain/${esc(item.file)}" alt="" loading="lazy">`:`<svg class="wall-palette-preview" viewBox="-.15 -.15 1.3 1.3" aria-hidden="true">${constructionSVG({ground:{},props:[],walls:[{id:'palette',x:0,y:0,rotation:0,piece:id,shape:item.shape,anchor:'center',material:brush.material,posts:'none'}]},{w:1,h:1},cat,{grid:false,background:false,wallKit})}</svg>`}<small>${esc(item.name)}</small></button>`).join('')||(mode==='erase'?'<p>Hover a prop or wall to check the removal target.<br><br>Hold <b>Shift</b> for floors.</p>':'<p>Select a placed object to adjust it, or choose a construction layer.</p>');
  find('[data-help]').textContent={ground:'Drag from one corner to the opposite corner to preview a filled rectangle. Release inside to place; outside cancels.',props:'Drag an asset into the map, or drag on the map with your brush. Arrows adjust its position; Shift gives finer steps. Drop outside to cancel.',walls:'Drag to extend a single row or column. Corners start the run, followed by matching plain walls. R rotates the preview; S toggles snapping. Release inside to place; outside cancels.',select:'Drag a placed object to move it. R rotates, arrows adjust its position. Dropping outside cancels the move. Click empty ground to deselect.',erase:'Remove [Del] targets props/walls only. Hold Shift before dragging to remove a rectangle of floors. Highlights show the exact layer being removed. Release inside to confirm; outside cancels.'}[mode];
  find('[data-palette]').querySelectorAll('[data-asset]').forEach(b=>{
   b.onclick=e=>{if(e.detail===0)chooseAsset(b.dataset.asset)};
   b.onpointerdown=e=>{if(e.button!==0||busy)return;e.preventDefault();cancelGesture();chooseAsset(b.dataset.asset);begin(e,'place');};
  });
 }
 function refreshWallThumbnails(){if(mode!=='walls')return;find('[data-palette]').querySelectorAll('[data-asset]').forEach(b=>{const id=b.dataset.asset;b.querySelector('svg').innerHTML=constructionSVG({ground:{},props:[],walls:[{id:'palette',x:0,y:0,rotation:0,piece:id,shape:wallPieces[id].shape,anchor:'center',material:brush.material,posts:'none'}]},{w:1,h:1},cat,{grid:false,background:false,wallKit})})}
 function inspector(){
  const selection=selectedObject(),item=gesture?.item||selection?.item||brush,layer=gesture?.layer||selection?.layer||mode;
  if(mode==='erase'){
   find('[data-inspector-heading]').textContent='Remove layers';
   find('[data-inspector]').innerHTML='<div class="construction-remove-guide"><strong>Props & walls</strong><p>Drag over objects to mark them. Their floors stay in place.</p><strong>Floors <kbd>Shift</kbd></strong><p>Hold Shift before dragging a rectangle. Props and walls stay in place.</p><small>Release inside to remove. Drop outside to cancel. Undo restores the entire drag.</small></div>';return;
  }
  find('[data-inspector-heading]').textContent=selection?'Selected object':'Placement';
  const select=(key,label,options,value)=>`<label>${label}<select data-field="${key}">${options.map(([id,name])=>`<option value="${id}" ${String(value)===id?'selected':''}>${esc(name)}</option>`).join('')}</select></label>`;
  const range=(key,label,value)=>`<label>${label}<input data-field="${key}" type="range" min="-.45" max=".45" step=".01" value="${value||0}"><small data-range-value="${key}">${Math.round((value||0)*100)}% of a cell</small></label>`;
  const check=(key,label)=>`<label class="construction-check"><input data-field="${key}" type="checkbox" ${item[key]?'checked':''}>${label}</label>`;
  let html=`<p data-piece-label>${esc(layer==='props'?cat.props[item.asset||brush.props]?.name||'Prop':layer==='walls'?wallPieces[item.piece]?.name||'Legacy wall':'Terrain')} | <span data-angle>${layer==='walls'&&item.piece?'native facing':selection?item.rotation:rotation+' deg'}</span></p><button data-rotate>Rotate [R]</button><button data-center>Center [Home]</button><small>Arrows position | Shift+Arrows fine | Home center</small>`;
  if(layer==='props')html+=select('w','Footprint width',[1,2,3,4].map(v=>[String(v),`${v} cell${v===1?'':'s'}`]),String(item.w))+select('h','Footprint height',[1,2,3,4].map(v=>[String(v),`${v} cell${v===1?'':'s'}`]),String(item.h))+range('offset_x','Position left / right',item.offset_x)+range('offset_y','Position up / down',item.offset_y)+check('blocking','Reserve this footprint')+'<small>Offsets move the artwork, not the reserved cells.</small>';
  if(layer==='walls')html+=select('piece','Wall asset',wallLibraryEntries().map(([id,p])=>[id,p.name]),wallLibraryPiece(item.piece))+select('anchor','Position',Object.keys(anchors).map(v=>[v,v==='center'?'Center':{north:'Top edge',east:'Right edge',south:'Bottom edge',west:'Left edge'}[v]]),item.anchor)+select('material','Material',cat.wall_materials.map(v=>[v,v]),item.material)+(wallKit==='placeholder'?check('broken','Broken variation')+check('open','Gate open (gates only)'):'<small>This painted trial contains intact walls and closed gates.</small>');
  if(selection)html+=`<label>Cell X<input data-field="x" type="number" min="0" max="${size.w-1}" value="${item.x}"></label><label>Cell Y<input data-field="y" type="number" min="0" max="${size.h-1}" value="${item.y}"></label><button data-delete>Remove object</button>`;
  find('[data-inspector]').innerHTML=html;find('[data-rotate]').onclick=rotate;find('[data-center]').onclick=()=>transform((item,layer)=>['props','walls'].includes(layer)?nudgePlacement(item,layer,'Home'):item);find('[data-center]').disabled=!['props','walls'].includes(layer);
  if(layer==='walls'&&wallKit!=='placeholder')find('[data-field=material]').disabled=true;
  if(layer==='walls'&&['tee','cross'].includes(item.shape)){find('[data-rotate]').disabled=true;const field=find('[data-field=piece]');field.insertAdjacentHTML('afterbegin',`<option value="${esc(item.piece||'')}" selected disabled>Retired junction (saved placement)</option>`);}
  find('[data-inspector]').querySelectorAll('[data-field]').forEach(input=>{let rangeEditing=false;input.addEventListener('change',()=>{if(input.type==='range')rangeEditing=false});input.addEventListener(input.type==='range'?'input':'change',()=>{
   showPlacementError('');const key=input.dataset.field,value=input.type==='checkbox'?input.checked:['w','h','x','y','offset_x','offset_y'].includes(key)?Number(input.value):input.value;
   let next={...item,[key]:value};if(key==='piece')next={...next,anchor:defaultWallAnchor(value),rotation:0,shape:wallPieces[value].shape,posts:'none'};
   if(selection&&!gesture){const error=placementError(next,layer,size,plan);if(error){find('[data-error]').textContent=error;syncInspector();return}if(input.type!=='range'||!rangeEditing)remember();rangeEditing=input.type==='range';Object.assign(selection.item,next);if(['x','y','w','h'].includes(key))renderMap();else renderObject(selection.item,layer)}
   else{Object.assign(gesture?.item||brush,next);if(key==='piece')rotation=0;updatePointer(lastPointer);schedulePreview()}
   syncInspector();if(key==='material')refreshWallThumbnails();
  })});
  if(selection)find('[data-delete]').onclick=()=>{remember();plan[selection.layer]=plan[selection.layer].filter(p=>p.id!==selected);selected='';renderMap();inspector()};
 }
 // Keep focus and native controls alive when using hotkeys; do not replace inspector DOM.
 function syncInspector(){
  const selection=selectedObject(),item=gesture?.item||selection?.item||brush,layer=gesture?.layer||selection?.layer||mode;
  find('[data-inspector]').querySelectorAll('[data-field]').forEach(input=>{const value=item[input.dataset.field];if(input.type==='checkbox')input.checked=!!value;else if(value!==undefined)input.value=input.dataset.field==='piece'?wallLibraryPiece(value):value});
  for(const key of ['offset_x','offset_y']){const label=find(`[data-range-value="${key}"]`);if(label)label.textContent=`${Math.round((item[key]||0)*100)}% of a cell`}
  const label=find('[data-piece-label]');if(layer==='walls'&&item.piece&&label)label.textContent=`${wallPieces[item.piece].name} | native facing`;else if(find('[data-angle]'))find('[data-angle]').textContent=`${selection?item.rotation:rotation} deg`;
  if(mode==='walls')find('[data-palette]').querySelectorAll('[data-asset]').forEach(b=>b.classList.toggle('active',b.dataset.asset===wallLibraryPiece(brush.piece)));
 }
 function transform(fn){
  const s=selectedObject(),layer=gesture?.layer||s?.layer||mode;
  if(!['ground','props','walls'].includes(layer))return;
  const source=gesture?.seed||gesture?.item||s?.item||{...brush,rotation},next=fn(source,layer);showPlacementError('');
  if(s&&!gesture){const error=placementError(next,layer,size,plan);if(error){find('[data-error]').textContent=error;return}remember();Object.assign(s.item,next);renderObject(s.item,layer)}
  else if(gesture?.kind==='wall-run'){gesture.seed=next;updatePointer(lastPointer);schedulePreview()}
  else if(gesture?.kind==='move'){gesture.item=next;updatePointer(lastPointer);schedulePreview()}
  else{Object.assign(brush,next);rotation=next.rotation;updatePointer(lastPointer);schedulePreview()}
  syncInspector();
 }
 function rotate(){
  const selection=selectedObject(),layer=gesture?.layer||selection?.layer||mode,current=ghost?.item||gesture?.item||selection?.item;
  if(snapping&&layer==='walls'&&current){
   const result=rotateSnappedWall(current,plan,size);
   if(result.blocked){showPlacementError('No other rotation fits this connection. Turn snapping off [S] to rotate freely.');return}
   if(gesture?.kind==='move'){
    gesture.item=result.item;gesture.origin=[result.item.x,result.item.y];const {px,py}=coords(lastPointer);gesture.start=[px,py];
   }else if(!selection)Object.assign(brush,result.item);
   snapLock=result.snapped&&lastPointer?{x:lastPointer.clientX,y:lastPointer.clientY,contacts:result.contacts,item:result.item}:null;
   transform(()=>result.item);return;
  }
  transform((item,layer)=>rotatePlacement(item,layer));
 }
 function coords(e){const r=svg.getBoundingClientRect();return {px:(e.clientX-r.left)*size.w/r.width,py:(e.clientY-r.top)*size.h/r.height}}
 function inside(e){if(!e)return false;const r=scroll.getBoundingClientRect(),{px,py}=coords(e);return e.clientX>r.left&&e.clientX<r.right&&e.clientY>r.top&&e.clientY<r.bottom&&px>=0&&py>=0&&px<size.w&&py<size.h}
 function makeGhost(e){
  if(!inside(e))return null;const {px,py}=coords(e),x=Math.floor(px),y=Math.floor(py);
  if(mode==='ground')return {layer:'ground',x,y};
  if(mode==='props')return {layer:'props',item:{id:'preview',asset:brush.props,x,y,rotation,w:brush.w,h:brush.h,offset_x:brush.offset_x,offset_y:brush.offset_y,blocking:brush.blocking}};
  if(mode==='walls')return {layer:'walls',item:{id:'preview',x,y,rotation:0,piece:brush.piece,shape:wallPieces[brush.piece].shape,anchor:brush.anchor,material:brush.material,posts:'none',open:brush.open,broken:brush.broken}};
  return null;
 }
 function cellAt(e){const {px,py}=coords(e);return {x:Math.floor(px),y:Math.floor(py)}}
 function removalTarget(e,floor){
  if(!inside(e))return null;
  if(floor)return {layer:'ground',...cellAt(e)};
  const element=document.elementFromPoint(e.clientX,e.clientY)?.closest('[data-construction-id]');
  if(!element||!scene.contains(element))return null;
  for(const layer of ['props','walls']){const item=plan[layer].find(i=>i.id===element.dataset.constructionId);if(item)return {layer,item}}
  return null;
 }
 function updatePointer(e){
  if(!e)return;lastPointer=e;
  if(snapLock&&Math.hypot(e.clientX-snapLock.x,e.clientY-snapLock.y)>2)snapLock=null;
  if(gesture?.kind==='place'&&gesture.layer==='walls'&&inside(e)){
   const placement=makeGhost(e);if(snapping)Object.assign(placement,snapWall(placement.item,plan,size));
   gesture.kind='wall-run';gesture.seed={...placement.item};gesture.startCell=cellAt(e);
  }
  if(gesture?.kind==='move'){
   if(!inside(e)){ghost=null;return}const {px,py}=coords(e);let item={...gesture.item,x:gesture.origin[0]+Math.round(px-gesture.start[0]),y:gesture.origin[1]+Math.round(py-gesture.start[1])};
   const snap=snapping&&gesture.layer==='walls'?snapWall(item,plan,size,{requiredContacts:snapLock?.contacts||[],allowRotate:!snapLock&&item.shape==='corner'}):null;if(snap?.snapped)item=snap.item;
   const error=placementError(item,gesture.layer,size,plan);showPlacementError(error);ghost=error?null:{layer:gesture.layer,item,...snap};
  }else if(gesture?.kind==='paint'){
   ghost=null;gesture.tiles={};if(!inside(e))return;
   gesture.startCell??=cellAt(e);
   for(const {x,y} of rectangleCells(gesture.startCell,cellAt(e)))gesture.tiles[`${x},${y}`]={asset:brush.ground,rotation};
  }else if(gesture?.kind==='wall-run'){
   ghost=null;if(!inside(e))return;
   const end=cellAt(e),items=wallRun(gesture.seed,end.x-gesture.startCell.x,end.y-gesture.startCell.y),error=wallRunError(items,plan,size);
   showPlacementError(error);ghost={layer:'walls',item:gesture.seed,items,error};
  }else if(mode==='erase'){
   ghost=null;removeHover=removalTarget(e,gesture?.removeFloor??e.shiftKey);
   if(gesture?.kind==='erase'){
    if(gesture.removeFloor){gesture.ground.clear();if(inside(e))for(const {x,y} of rectangleCells(gesture.startCell,cellAt(e)))gesture.ground.add(`${x},${y}`)}
    else if(removeHover?.item)gesture.removed.add(removeHover.item.id);
   }
  }else{
   ghost=makeGhost(e);if(ghost?.layer==='walls'&&snapping){if(snapLock)ghost.item={...ghost.item,x:snapLock.item.x,y:snapLock.item.y,piece:snapLock.item.piece,anchor:snapLock.item.anchor};const snap=snapWall(ghost.item,plan,size,{requiredContacts:snapLock?.contacts||[],allowRotate:!snapLock&&ghost.item.shape==='corner'});ghost={...ghost,...snap};}if(ghost?.item){const error=placementError(ghost.item,ghost.layer,size,plan);showPlacementError(error);if(error)ghost=null;}
  }
 }
 function begin(e,kind,initial=null){
  svg.focus({preventScroll:true});svg.setPointerCapture(e.pointerId);gesture={kind,pointerId:e.pointerId,layer:mode,tiles:{},startCell:inside(e)?cellAt(e):null};
  if(mode==='ground')gesture.kind='paint';
  if(mode==='walls'&&inside(e)){
   // Keep the exact hovered/rotated preview; do not snap again on pointerdown.
   const placement=initial||makeGhost(e);
   if(!initial&&placement&&snapping)Object.assign(placement,snapWall(placement.item,plan,size));
   if(placement?.item){gesture.kind='wall-run';gesture.seed={...placement.item};gesture.startCell=cellAt(e)}
  }
  updatePointer(e);find('[data-save]').disabled=true;find('[data-undo]').disabled=true;find('[data-redo]').disabled=true;schedulePreview();
 }
 function cancelGesture(){gesture=null;ghost=null;snapLock=null;removeHover=null;if(previewFrame){cancelAnimationFrame(previewFrame);previewFrame=0}drawPreview();find('[data-save]').disabled=busy||debugLab;find('[data-undo]').disabled=!undo.length;find('[data-redo]').disabled=!redo.length}
 svg.onpointerdown=e=>{
  if(e.button!==0||busy)return;e.preventDefault();svg.focus({preventScroll:true});const initial=mode==='walls'&&ghost?.layer==='walls'&&lastPointer&&Math.hypot(e.clientX-lastPointer.clientX,e.clientY-lastPointer.clientY)<=2?structuredClone(ghost):null;cancelGesture();const target=e.target.closest('[data-construction-id]');
  svg.setPointerCapture(e.pointerId);
  if(mode==='select'){
   selected=target?.dataset.constructionId||'';const s=selectedObject();renderMap();inspector();if(!s)return;
   const {px,py}=coords(e);gesture={kind:'move',pointerId:e.pointerId,layer:s.layer,item:{...s.item},start:[px,py],origin:[s.item.x,s.item.y],id:selected};updatePointer(e);schedulePreview();find('[data-save]').disabled=true;
  }else if(mode==='erase'){gesture={kind:'erase',pointerId:e.pointerId,removed:new Set(),ground:new Set(),removeFloor:e.shiftKey,startCell:cellAt(e)};updatePointer(e);schedulePreview();find('[data-save]').disabled=true}
  else begin(e,'place',initial);
 };
 const pointerMove=e=>{if(gesture&&e.pointerId!==gesture.pointerId)return;if(!gesture&&!svg.contains(e.target))return;updatePointer(e);schedulePreview()};
 const pointerUp=e=>{
  if(!gesture||e.pointerId!==gesture.pointerId)return;updatePointer(e);const g=gesture,valid=inside(e)&&(['paint','erase'].includes(g.kind)||g.kind==='wall-run'&&ghost?.items?.length&&!ghost.error||['move','place'].includes(g.kind)&&!!ghost),next=valid?structuredClone(plan):plan;
  if(valid){
   if(g.kind==='paint')Object.assign(next.ground,g.tiles);
   else if(g.kind==='wall-run')next.walls.push(...ghost.items.map(({invalidConnection,...item})=>({...item,id:crypto.randomUUID()})));
   else if(g.kind==='erase'){for(const layer of ['props','walls'])next[layer]=next[layer].filter(p=>!g.removed.has(p.id));for(const key of g.ground)delete next.ground[key]}
   else if(g.kind==='move')Object.assign(next[g.layer].find(p=>p.id===g.id),ghost.item);
   else if(ghost?.item){const item={...ghost.item,id:crypto.randomUUID()};next[ghost.layer].push(item)}
   if(JSON.stringify(plan)!==JSON.stringify(next)){remember();plan=next}
  }
  cancelGesture();renderMap();inspector();find('[data-status]').textContent=valid?find('[data-status]').textContent:'Drop cancelled - no changes placed.';
 };
 const pointerCancel=e=>{if(gesture?.pointerId===e.pointerId)cancelGesture()};
 window.addEventListener('blur',cancelGesture);window.addEventListener('pointermove',pointerMove);window.addEventListener('pointerup',pointerUp);window.addEventListener('pointercancel',pointerCancel);
 svg.onpointerleave=()=>{if(!gesture){ghost=null;removeHover=null;snapLock=null;schedulePreview()}};
 function history(direction){if(gesture)cancelGesture();const from=direction==='undo'?undo:redo,to=direction==='undo'?redo:undo;if(!from.length)return;to.push(structuredClone(plan));plan=from.pop();selected='';ghost=null;renderMap();inspector()}
 find('[data-undo]').onclick=()=>history('undo');find('[data-redo]').onclick=()=>history('redo');
 function setTool(next){cancelGesture();mode=next;if(mode!=='select')selected='';query='';find('[data-search]').value='';showPlacementError('');palette();inspector();renderMap();if(svg.matches(':hover')){updatePointer(lastPointer);schedulePreview()}}
 dialog.querySelectorAll('[data-tool]').forEach(b=>b.onclick=()=>setTool(b.dataset.tool));
 find('[data-snap]').onclick=()=>{snapping=!snapping;snapLock=null;try{localStorage.setItem('fortcamp.construction.snapping',snapping?'on':'off')}catch{}find('[data-snap]').textContent=`Snapping [S]: ${snapping?'On':'Off'}`;find('[data-snap]').setAttribute('aria-pressed',String(snapping));updatePointer(lastPointer);schedulePreview()};
 find('[data-search]').oninput=e=>{query=e.target.value.toLowerCase();palette()};
 function setZoom(next,point){
  const before=svg.getBoundingClientRect(),px=point?.clientX??scroll.getBoundingClientRect().left+scroll.clientWidth/2,py=point?.clientY??scroll.getBoundingClientRect().top+scroll.clientHeight/2,fx=(px-before.left)/before.width,fy=(py-before.top)/before.height;
  zoom=Math.max(.25,Math.min(3,next));find('[data-zoom="0"]').textContent=`${Math.round(zoom*100)}%`;svg.style.width=`${size.w*64*zoom}px`;svg.style.height=`${size.h*64*zoom}px`;
  const after=svg.getBoundingClientRect();scroll.scrollLeft+=after.left+fx*after.width-px;scroll.scrollTop+=after.top+fy*after.height-py;updatePointer(lastPointer);schedulePreview();
 }
 dialog.querySelectorAll('[data-zoom]').forEach(b=>b.onclick=()=>setZoom(b.dataset.zoom==='0'?1:zoom+Number(b.dataset.zoom)));
 scroll.addEventListener('wheel',e=>{if(e.shiftKey||e.ctrlKey||e.metaKey||!e.deltaY)return;e.preventDefault();setZoom(wheelZoom(zoom,e),e)},{passive:false});
 dialog.onkeydown=e=>{
  if(e.target.matches('textarea,input:not([type=range]):not([type=checkbox])')||e.target.isContentEditable)return;
  if(e.key==='Shift'&&mode==='erase'&&!gesture&&lastPointer){updatePointer({clientX:lastPointer.clientX,clientY:lastPointer.clientY,shiftKey:true});schedulePreview();return}
  if(!e.ctrlKey&&!e.metaKey&&!e.altKey){const tool={Delete:'erase',f:'ground',p:'props',w:'walls',v:'select'}[e.key.length===1?e.key.toLowerCase():e.key];if(tool){e.preventDefault();e.stopPropagation();setTool(tool);return}if(e.key.toLowerCase()==='s'){e.preventDefault();e.stopPropagation();find('[data-snap]').click();return}}
  if(e.key==='Escape'&&gesture){e.preventDefault();e.stopPropagation();cancelGesture();return}
  if((e.ctrlKey||e.metaKey)&&e.key.toLowerCase()==='z'){e.preventDefault();e.stopPropagation();history(e.shiftKey?'redo':'undo');return}
  if(!e.ctrlKey&&!e.metaKey&&!e.altKey&&e.key.toLowerCase()==='r'){e.preventDefault();e.stopPropagation();rotate()}
  if(['ArrowLeft','ArrowRight','ArrowUp','ArrowDown','Home'].includes(e.key)){e.preventDefault();e.stopPropagation();transform((item,layer)=>['props','walls'].includes(layer)?nudgePlacement(item,layer,e.key,e.shiftKey):item)}
 };
 dialog.onkeyup=e=>{if(e.key==='Shift'&&mode==='erase'&&!gesture&&lastPointer){updatePointer({clientX:lastPointer.clientX,clientY:lastPointer.clientY,shiftKey:false});schedulePreview()}};
 const close=async()=>{if(busy)return;cancelGesture();if(!debugLab&&JSON.stringify(plan)!==saved&&!await confirmAction({title:'Discard construction changes?',message:'Your last saved camp layout will remain.',confirmLabel:'Discard changes',danger:true}))return;window.removeEventListener('blur',cancelGesture);window.removeEventListener('pointermove',pointerMove);window.removeEventListener('pointerup',pointerUp);window.removeEventListener('pointercancel',pointerCancel);dialog.close();dialog.remove()};
 dialog.querySelectorAll('[data-close]').forEach(b=>b.onclick=close);dialog.oncancel=e=>{e.preventDefault();if(gesture)cancelGesture();else close()};
 find('[data-save]').onclick=async()=>{if(busy||gesture||debugLab)return;busy=true;renderMap();try{const result=await api('/api/construction',{method:'PUT',body:JSON.stringify({revision,plan})});plan=result.plan;revision=plan.revision;saved=JSON.stringify(plan);find('[data-error]').textContent='';onSave(result.state)}catch(e){find('[data-error]').textContent=e.message}finally{busy=false;renderMap()}};
 find('[data-export]').onclick=()=>{const blob=new Blob([JSON.stringify({format:'fortcamp-construction',size,plan},null,2)],{type:'application/json'}),url=URL.createObjectURL(blob),a=document.createElement('a');a.href=url;a.download='fortcamp-camp-layout.json';a.click();setTimeout(()=>URL.revokeObjectURL(url),1000)};
 if(debugLab){find('[data-save]').textContent='Preview only';find('[data-wall-kit]').onchange=e=>{cancelGesture();wallKit=e.target.value;if(wallKit!=='placeholder')for(const w of plan.walls){w.open=false;w.broken=false}palette();inspector();renderMap()}}
 find('[data-zoom="0"]').textContent=`${Math.round(zoom*100)}%`;palette();inspector();renderMap();
}

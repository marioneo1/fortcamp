import {framedImage,openPortraitFraming} from './portrait-framing.js';
import './portrait-lab.css';

export function filterPortraits(rows,{query='',kind='',group=''}={}){
  const words=query.toLowerCase().trim().split(/\s+/).filter(Boolean);
  return rows.filter(r=>(!kind||r.kind===kind)&&(!group||r.group===group)&&words.every(w=>`${r.name} ${r.group} ${r.variant||''}`.toLowerCase().includes(w)));
}

export async function openPortraitLab({api,src,esc,onSaved,onError}){
  const dialog=document.createElement('dialog');dialog.className='portrait-lab';
  dialog.setAttribute('aria-label','Portrait Lab');
  dialog.innerHTML=`<header><div><small>DEVELOPMENT ART LIBRARY</small><h2>Portrait Lab</h2></div><button data-close aria-label="Close Portrait Lab">×</button></header><p>Review every generic and Champion portrait. Adjusting a frame changes its default icon for characters using this image. Individual character overrides stay intact; the original photo is preserved.</p><div class="portrait-lab-filters"><label>Search<input data-query placeholder="Race, Champion, or image name…"></label><label>Collection<select data-kind><option value="">All portraits</option><option>Generic</option><option>Champion</option></select></label><label>Image set<select data-group><option value="">All sets</option></select></label></div><div data-grid class="portrait-lab-grid" aria-live="polite">Loading portraits…</div><footer><button data-prev>← Previous</button><span data-count></span><button data-next>Next →</button></footer>`;
  document.body.append(dialog);dialog.showModal();
  const find=s=>dialog.querySelector(s),filters={query:'',kind:'',group:''};let rows=[],page=0;const pageSize=60;
  const close=()=>{dialog.close();dialog.remove()};find('[data-close]').onclick=close;
  dialog.oncancel=event=>{event.preventDefault();close()};
  dialog.onclick=event=>{if(event.target===dialog){const b=dialog.getBoundingClientRect();if(event.clientX<b.left||event.clientX>b.right||event.clientY<b.top||event.clientY>b.bottom)close()}};
  function render(){
    const filtered=filterPortraits(rows,filters),pages=Math.max(1,Math.ceil(filtered.length/pageSize));page=Math.min(page,pages-1);
    find('[data-count]').textContent=`${filtered.length} portraits · Page ${page+1} of ${pages}`;
    find('[data-prev]').disabled=!page;find('[data-next]').disabled=page+1>=pages;
    find('[data-grid]').innerHTML=filtered.slice(page*pageSize,(page+1)*pageSize).map(r=>`<button class="portrait-lab-card" data-key="${esc(r.key)}">${framedImage(src(r.thumbnail),r.portrait_frame,esc,'portrait-lab-face','')}<b>${esc(r.name.replaceAll('_',' '))}</b><small>${esc((r.kind==='Champion'?r.variant:r.group).replaceAll('_',' '))}</small><span>Adjust framing</span></button>`).join('')||'<p>No portraits match these filters.</p>';
    find('[data-grid]').scrollTop=0;
    find('[data-grid]').querySelectorAll('[data-key]').forEach(button=>button.onclick=()=>{
      const row=rows.find(r=>r.key===button.dataset.key);
      const save=async payload=>{const result=await api('/api/debug/portrait-lab/frame',{method:'POST',body:JSON.stringify({key:row.key,...payload})});row.portrait_frame=result.portrait_frame;render();await onSaved?.()};
      openPortraitFraming({character:row,src:src(row.full||row.key),onSave:save,onReset:()=>save({reset:true}),onError});
    });
  }
  for(const key of ['query','kind','group'])find('[data-'+key+']').addEventListener(key==='query'?'input':'change',event=>{filters[key]=event.target.value;page=0;render()});
  find('[data-prev]').onclick=()=>{page--;render()};find('[data-next]').onclick=()=>{page++;render()};
  try{
    rows=(await api('/api/debug/portrait-lab')).portraits;
    if(!dialog.isConnected)return;
    find('[data-group]').innerHTML='<option value="">All sets</option>'+[...new Set(rows.map(r=>r.group))].sort().map(g=>`<option value="${esc(g)}">${esc(g.replaceAll('_',' '))}</option>`).join('');render();
  }catch(error){find('[data-grid]').textContent=error.message;onError?.(error)}
}

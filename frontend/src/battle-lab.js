import './battle-lab.css';

const escape = value => String(value ?? '').replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const title = value => value.replaceAll('_', ' ').replace(/\b\w/g, c => c.toUpperCase());
export function filterLabMissions(missions, {query='', rank='', source=''}={}) {
  const words=query.toLowerCase().trim().split(/\s+/).filter(Boolean);
  return missions.filter(m => (!rank || m.rank===rank) && (!source || m.source===source) &&
    words.every(word => `${m.name} ${m.description} ${m.source} ${m.form} ${m.faction}`.toLowerCase().includes(word)));
}

export function createBattleLab({api, onStart, onError}) {
  let data=null, selection=null, variantId=null, filters={query:'', rank:'', source:''}, request=null, busy=false;
  const dialog=document.createElement('dialog');
  dialog.className='battle-lab';dialog.setAttribute('aria-label','Battle Lab');document.body.append(dialog);
  dialog.innerHTML=`<header class="lab-header"><div><span class="eyebrow">DEVELOPMENT SANDBOX</span><h2>Battle Lab</h2><p>Try any battlefield and its real approach outcomes.</p></div><button data-lab-close aria-label="Close Battle Lab">×</button></header>
    <div class="lab-notice">Isolated test · No rewards, injuries, prisoners, or changes to your save. Tests expire after an hour or when the server restarts.</div>
    <div class="lab-filters"><label>Search missions<input data-lab-query placeholder="Name, faction, or mission type…"></label><label>Rank<select data-lab-rank><option value="">All ranks</option>${[...'EDCBAS'].map(r=>`<option>${r}</option>`).join('')}</select></label><label>Source<select data-lab-source><option value="">All sources</option></select></label></div>
    <div class="lab-workspace"><nav class="lab-list" aria-label="Battle missions"></nav><section class="lab-details"></section></div><footer class="lab-footer"><small>Select a mission</small><button class="primary" data-lab-start>Start Test Battle</button></footer>`;
  const find=s=>dialog.querySelector(s);
  find('[data-lab-close]').onclick=()=>dialog.close();
  dialog.onclick=event=>{if(event.target===dialog){const box=dialog.getBoundingClientRect();if(event.clientX<box.left||event.clientX>box.right||event.clientY<box.top||event.clientY>box.bottom)dialog.close()}};
  for(const [key, selector] of [['query','[data-lab-query]'],['rank','[data-lab-rank]'],['source','[data-lab-source]']]){
    find(selector).addEventListener(key==='query'?'input':'change',event=>{filters[key]=event.target.value;renderList()});
  }
  function renderList(){
    const missions=filterLabMissions(data?.missions||[],filters);
    find('.lab-list').innerHTML=`<small>${missions.length} battle missions</small>${missions.map(m=>`<button data-lab-mission="${escape(m.id)}" class="lab-mission ${m.id===selection?'selected':''}" aria-pressed="${m.id===selection}"><span class="lab-rank">${escape(m.rank)}</span><span><b>${escape(m.name)}</b><small>${escape(m.source)}</small><small>${escape(title(m.form))}</small></span></button>`).join('')||'<p>No missions match these filters.</p>'}`;
    find('.lab-list').querySelectorAll('[data-lab-mission]').forEach(button=>button.onclick=()=>{selection=button.dataset.labMission;variantId=null;renderList();renderDetails()});
  }
  function renderDetails(){
    const mission=data?.missions.find(m=>m.id===selection);
    if(!mission){find('.lab-details').innerHTML='<div class="lab-empty">Select a mission to inspect its battlefield and approaches.</div>';return}
    const groups=[...new Set(mission.variants.map(v=>`${v.node}|||${v.label}`))];
    const selected=mission.variants.find(v=>v.id===variantId)||mission.variants[0];variantId=selected.id;
    find('.lab-details').innerHTML=`<div class="lab-title"><span class="lab-rank large">${escape(mission.rank)}</span><div><span class="eyebrow">${escape(title(mission.form))}</span><h3>${escape(mission.name)}</h3><p>${escape(mission.source)}${mission.faction?` · ${escape(title(mission.faction))}`:''}</p></div></div><p class="lab-description">${escape(mission.description)}</p>${mission.follows?.length?`<p class="lab-hint">Follow-up from: ${escape(mission.follows.join(", "))}</p>`:""}
      <div class="lab-settings"><label>Approach<select data-lab-approach>${groups.map(g=>{const [node,label]=g.split('|||');return `<option value="${escape(g)}" ${g===`${selected.node}|||${selected.label}`?'selected':''}>${escape(node)} · ${escape(label)}</option>`}).join('')}</select></label><label>Force roll outcome<select data-lab-outcome></select></label></div>
      <div class="lab-approach-help"></div><div class="lab-encounter"></div>
      <label class="lab-layout" hidden>Map layout<select data-lab-layout></select></label>
      <div class="lab-seed"><label>Generation seed<input data-lab-seed maxlength="100" value="${escape(request?.seed||'battle-test-1')}"></label><button data-lab-new-seed>New seed</button></div><small class="lab-hint">Choose a named layout to fill its repeatable seed, or enter your own. Keep the seed to repeat the map, enemies, and names.</small>
      <fieldset class="lab-party"><legend>Test party · Choose up to 4</legend><p>Copies of your roster with their current stats and equipment. Busy characters can be tested too.</p>${data.characters.map(c=>`<label class="lab-character"><input type="checkbox" data-lab-character="${escape(c.id)}" ${(request?.party_ids||[data.characters[0]?.id]).includes(c.id)?'checked':''}>${c.portrait?`<img src="${escape(c.portrait)}" alt="">`:'<span class="lab-face">◇</span>'}<span><b>${escape(c.name)}</b><small>${escape(c.race)} · ${escape(title(c.status))}</small></span></label>`).join('')||'<p>A temporary starter character will be used.</p>'}</fieldset>
      <label class="lab-helper"><input data-lab-helper type="checkbox" ${request?.add_helper===false?'':'checked'}>Add a temporary companion if testing solo</label><div class="lab-error" role="alert"></div>`;
    find('.lab-footer small').textContent=`${mission.rank} Rank · ${mission.name}`;
    const updateOutcomes=()=>{
      const group=find('[data-lab-approach]').value;
      const [node,label]=group.split('|||');
      const variants=mission.variants.filter(v=>v.node===node&&v.label===label);
      find('[data-lab-outcome]').innerHTML=variants.map(v=>`<option value="${escape(v.id)}" ${v.id===variantId?'selected':''}>${v.outcome==='direct'?'Normal deployment':escape(title(v.outcome))}</option>`).join('');
      variantId=find('[data-lab-outcome]').value;
      find('[data-lab-outcome]').disabled=variants.length===1;
      updateDescription();
    };
    const updateDescription=()=>{
      variantId=find('[data-lab-outcome]').value;
      const v=mission.variants.find(v=>v.id===variantId);
      find('.lab-approach-help').textContent=v.description+(v.requires?' The lab bypasses the training requirement.':'');
      find('.lab-encounter').innerHTML=`<b>Encounter</b> ${escape(v.encounter_id)}${v.transition.boss?' · Stronger commander':''}${v.transition.setup?` · ${escape(title(v.transition.setup))}`:''}`;
      const presets=v.layout_presets||[],layout=find('[data-lab-layout]'),seed=find('[data-lab-seed]');
      find('.lab-layout').hidden=!presets.length;
      layout.innerHTML='<option value="">Custom / random seed</option>'+presets.map(p=>`<option value="${escape(p.seed)}">${escape(p.label)} · ${escape(p.seed)}</option>`).join('');
      layout.value=presets.some(p=>p.seed===seed.value)?seed.value:'';
      layout.onchange=()=>{if(layout.value)seed.value=layout.value};
      seed.oninput=()=>{layout.value=presets.some(p=>p.seed===seed.value)?seed.value:''};
    };
    find('[data-lab-approach]').onchange=updateOutcomes;
    find('[data-lab-outcome]').onchange=updateDescription;updateOutcomes();
    find('[data-lab-new-seed]').onclick=()=>{find('[data-lab-seed]').value=`test-${Date.now().toString(36)}`;find('[data-lab-layout]').value=''};
    const partyInputs=[...dialog.querySelectorAll('[data-lab-character]')];
    const updateParty=()=>{const full=partyInputs.filter(i=>i.checked).length>=4;partyInputs.forEach(i=>i.disabled=full&&!i.checked)};
    partyInputs.forEach(i=>i.onchange=updateParty);updateParty();
    find('[data-lab-start]').onclick=async()=>{
      if(busy)return;busy=true;find('[data-lab-start]').disabled=true;
      const next={mission_id:mission.id,variant_id:variantId,seed:find('[data-lab-seed]').value.trim(),party_ids:partyInputs.filter(i=>i.checked).map(i=>i.dataset.labCharacter),add_helper:find('[data-lab-helper]').checked};
      if(data.characters.length&&!next.party_ids.length){find('.lab-error').textContent='Choose at least one character.';busy=false;find('[data-lab-start]').disabled=false;return}
      try{const result=await api('/api/debug/battle-lab',{method:'POST',body:JSON.stringify(next)});request=next;dialog.close();onStart(result)}catch(error){find('.lab-error').textContent=error.message}finally{busy=false;find('[data-lab-start]').disabled=false}
    };
  }
  return {
    async open(){try{data=await api('/api/debug/battle-lab');if(!selection)selection=data.missions.find(m=>m.id==='goblin_warcamp')?.id||data.missions[0]?.id;find('[data-lab-source]').innerHTML='<option value="">All sources</option>'+[...new Set(data.missions.map(m=>m.source))].sort().map(s=>`<option>${escape(s)}</option>`).join('');find('[data-lab-source]').value=filters.source;renderList();renderDetails();dialog.showModal();find('.lab-mission.selected')?.scrollIntoView({block:'nearest'})}catch(error){onError(error.message)}},
    async restart(){if(busy||!request)return;busy=true;try{onStart(await api('/api/debug/battle-lab',{method:'POST',body:JSON.stringify(request)}))}catch(error){onError(error.message)}finally{busy=false}},
  };
}

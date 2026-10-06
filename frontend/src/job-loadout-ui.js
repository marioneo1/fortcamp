import './job-loadout-ui.css';
import {skillIconMarkup} from './ability-icons.js';
import {loadoutSelection,jobSkillRows} from './job-loadout-rules.js';

const drafts=new Map();
const escape=value=>String(value??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));

export function mountJobLoadout(root,{character,catalog,onSave,onError,scope=''}){
  if(['champion','celestial'].includes(character.source_kind)||character.temporary_mercenary){
    root.innerHTML='<p>Authored character kits will appear here when available. Equipment techniques remain available in battle.</p>';return;
  }
  if(!catalog){root.innerHTML='<p>Skill catalogue unavailable.</p>';return;}
  const editable=character.status==='idle'&&!character.assignment;
  const key=`${scope}:${character.id}`,capacity=catalog.capacity;
  let draft=drafts.get(key);
  if(!draft||draft.saved!==JSON.stringify([character.job_id,character.equipped_skills])){
    draft={saved:JSON.stringify([character.job_id,character.equipped_skills]),job:character.job_id||'',ids:[...(character.equipped_skills||[])],query:'',busy:false};drafts.set(key,draft);
  }
  const render=()=>{
    const job=catalog.jobs[draft.job],known=character.job_id?(character.learned_skills||[]):job?.starter_skills||[];
    const rows=jobSkillRows(job,known,character.job_id?character.job_practice||0:0);
    const skills=rows.map(row=>({...catalog.skills[row.id],...row})).filter(s=>s.name);
    root.innerHTML=`<header class="loadout-header"><div><small>COMBAT JOB</small><h3>${escape(job?.name||'Choose a Job')}</h3><p>${escape(job?.description||'Choose a combat toolbox for this character. Work proficiencies remain separate.')}</p></div><strong>${draft.ids.length} / ${capacity}<small>skills equipped</small></strong></header>
      ${!character.job_id?`<label>Job<select data-job-choice ${!editable?'disabled':''}><option value="">Choose a Job</option>${Object.entries(catalog.jobs).map(([id,j])=>`<option value="${escape(id)}" ${draft.job===id?'selected':''}>${escape(j.name)}</option>`).join('')}</select></label><p class="muted">Your Job choice is permanent for now. Preview the starter skills below before saving. Equipment is unchanged.</p>`:''}
      <p>Actives and passives share five slots. Basic actions, racial traits and equipment abilities use no slots.</p>
      <div class="loadout-slots">${Array.from({length:capacity},(_,i)=>{const s=catalog.skills[draft.ids[i]];return `<button data-slot-id="${escape(s?.id||'')}" ${!editable||!s?'disabled':''}><small>${i+1} · ${s?s.type:'Empty'}</small>${s?skillIconMarkup(s,escape):''}${escape(s?.name||'Free slot')}</button>`}).join('')}</div>
      ${character.job_migration_note?`<p class="job-migration-note">${escape(character.job_migration_note)}</p>`:''}<h4>Job skills</h4><p>${character.job_id?`${character.job_practice||0} successful contracts with this Job. `:''}${job?`Unlocks at ${[...new Set(job.unlocks.map(u=>u.contracts))].join(', ')} successes. `:''}Newly learned skills wait here for you to equip.</p><input data-skill-search type="search" placeholder="Find a Job skill" value="${escape(draft.query)}">
      <div class="loadout-catalogue">${skills.filter(s=>(s.name+' '+s.description).toLowerCase().includes(draft.query.toLowerCase())).map(s=>{const selected=draft.ids.includes(s.id);return `<button class="loadout-skill ${selected?'selected':''}" data-skill-id="${escape(s.id)}" aria-pressed="${selected}" ${!editable||!s.learned||!selected&&draft.ids.length>=capacity?'disabled':''}>${skillIconMarkup(s,escape)}<small>${escape(s.type)}${s.cost?` · ${s.cost.cooldown} turn cooldown`:''} · ${selected?'Equipped':s.learned?'Learned':`Unlocks in ${s.remaining} successes`}</small><b>${escape(s.name)}</b><span>${escape(s.description)}</span></button>`}).join('')||'<p class="muted">Choose a Job to preview its starter skills.</p>'}</div>
      <footer class="loadout-footer"><span>${editable?'Changes apply to future expeditions.':'Unassign this character and wait until they are idle to change skills.'}</span><button data-loadout-reset ${draft.busy?'disabled':''}>Discard changes</button><button class="primary" data-loadout-save ${!editable||!draft.job||draft.busy?'disabled':''}>${draft.busy?'Saving…':'Save loadout'}</button></footer>
      `;
    root.querySelector('[data-job-choice]')?.addEventListener('change',event=>{draft.job=event.target.value;draft.ids=[...(catalog.jobs[draft.job]?.starter_skills||[])];render()});
    root.querySelectorAll('[data-skill-id],[data-slot-id]').forEach(button=>button.onclick=()=>{draft.ids=loadoutSelection(draft.ids,button.dataset.skillId||button.dataset.slotId,capacity);render()});
    root.querySelector('[data-skill-search]').oninput=event=>{const pos=event.target.selectionStart;draft.query=event.target.value;render();const input=root.querySelector('[data-skill-search]');input.focus();input.setSelectionRange(pos,pos)};
    root.querySelector('[data-loadout-reset]').onclick=()=>{drafts.delete(key);mountJobLoadout(root,{character,catalog,onSave,onError,scope})};
    root.querySelector('[data-loadout-save]').onclick=async()=>{draft.busy=true;render();try{await onSave({skill_ids:draft.ids,job_id:character.job_id?null:draft.job});drafts.delete(key)}catch(error){draft.busy=false;render();onError(error)}};
  };render();
}

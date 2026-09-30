import {mountDecisionScene} from './mission-scene-ui.js';
import {createAudioMixer,mountAudioSettings,audioCategory} from './audio-settings.js';
import {raceEffects,perkModifiers} from './character-effects.js';
import {rosterPage} from './roster-tools.js';
﻿import {mountMissionPlanner} from './mission-claim-ui.js';
import {matchesMission,equipmentEditable} from './mission-planner.js';
import { DiscordSDK } from "@discord/embedded-app-sdk";
import "./styles.css?v=20260930u";

const $ = s => document.querySelector(s);
const $$ = s => [...document.querySelectorAll(s)];
const attributeNames = ["str","dex","agi","vit","int","luk"];
const creatorAttributes = Object.fromEntries(attributeNames.map(k=>[k,4]));
let creatorAttributePoints = 12;
let sessionToken = null, devHeaders = {}, identity = null, appConfig = null, content = null, state = null, pool = null, privateContracts = [], activeMissions = [];
let buildMode = null, moveModeBuildingId = null, selectedBuildingId = null, selectedCharacterId = null, selectedMission = null, pollTimer = null, clockTimer = null;
let dynamicReady = false, audioCtx = null;
let dynamicRefreshPromise = null, lastDeadlineRefresh = 0;
const DEFAULT_BATTLE_ZOOM=.5;
let activeBattleMissionId = null, activeBattleView = null, selectedCombatAction = 'move', contextMenuOpen = false, tileActionMenu = null, retreatAllArmed = false, battleZoom = DEFAULT_BATTLE_ZOOM, battlePan = {left:0,top:0}, combatRequestPending = false;
let selectedPreparation = {mode:'defense',id:null};
const rankBoardOpen={};
const rosterCollectionOpen={champions:false,celestials:false,prisoners:false};
const appearanceEditorOpen={};
const appearanceDrafts={};
const rosterFilters={query:'',status:'',race:'',kind:'',sort:'name',page:0};
let rosterDetailTab='overview',rosterNeedsRefresh=false;
let missionPlanner=null,analysisSequence=0;
const missionFilters={query:'',rank:'',form:'',available:true,sort:'shortest'};
let missionClaimPending=false;
let audioStorage;try{audioStorage=window.localStorage}catch{}
const audioMixer=createAudioMixer(audioStorage);
let closeAudioSettings=null;

const esc=(v='')=>String(v).replace(/[&<>'"]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;',"'":'&#39;','"':'&quot;'}[c]));
const title=(s='')=>s.replaceAll('_',' ').replace(/\b\w/g,m=>m.toUpperCase());
const initials=(name='?')=>name.split(/\s+/).map(x=>x[0]).join('').slice(0,2).toUpperCase();
function portraitSrc(url=''){
  try{
    const parsed=new URL(url);
    if(/^encrypted-tbn\d+\.gstatic\.com$/i.test(parsed.hostname))return `/api/portrait-proxy?url=${encodeURIComponent(url)}`;
  }catch{}
  return url;
}
function toast(msg){const el=$('#toast');el.textContent=msg;el.classList.add('show');setTimeout(()=>el.classList.remove('show'),2600)}
function fmtDuration(s){s=Math.max(0,Math.floor(s));if(s<60)return `${s}s`;if(s<3600)return `${Math.floor(s/60)}m`;if(s<86400)return `${Math.floor(s/3600)}h ${Math.floor((s%3600)/60)}m`;return `${Math.floor(s/86400)}d ${Math.floor((s%86400)/3600)}h`}
function countdown(ts){return fmtDuration(Math.max(0,Math.ceil(Number(ts)-Date.now()/1000)))}
function characterStatus(c){return c.status==='incapacitated'?`Recovering in ${c.recovery_location||'camp'} · ${countdown(c.recovers_at||0)}`:title(c.status)}
function debugEnabled(){return !!(appConfig?.debug_mode && (identity?.guild_admin || appConfig?.dev_bypass_auth))}
async function launchDebugBattle(button,endpoint,label){
  button.disabled=true;toast(`Preparing ${label}…`);
  try{
    const data=await rawApi(endpoint,{method:'POST',body:'{}'});
    await refreshDynamic();
    if(!data?.mission?.id)throw new Error('The backend did not return a battle mission');
    await openBattle(data.mission.id);
    toast(`${label} ready`);
  }catch(error){
    console.error(`Debug battle launch failed: ${label}`,error);
    const restartHint=/not found/i.test(error.message)?' Restart Fortcamp once to load the new backend route.':'';
    toast(`Could not start ${label}: ${error.message}.${restartHint}`);
  }finally{button.disabled=false}
}

function ensureAudio(){
  if(!audioCtx){
    const AC=window.AudioContext||window.webkitAudioContext;
    if(AC)audioCtx=new AC();
  }
  if(audioCtx?.state==='suspended')audioCtx.resume().catch(()=>{});
  return audioCtx;
}
window.addEventListener('pointerdown',()=>ensureAudio(),{once:true});

const sfxFiles={ui_click:'ui_click.wav',ui_confirm:'ui_confirm.wav',ui_cancel:'ui_cancel.wav',melee_swing:'melee_swing.wav',melee_hit_light:'melee_hit_light.wav',melee_hit_heavy:'melee_hit_heavy.wav',subdue_hit:'subdue_hit.wav',unit_death:'unit_death.wav',unit_unconscious:'unit_unconscious.wav',guard:'guard.wav',mission_success:'mission_success_v3.wav',mission_failure:'mission_failure_v3.wav',mission_critical_success:'mission_critical_success_v3.wav',mission_critical_failure:'mission_critical_failure_v3.wav'};
for(const name of ['step_earth','step_stone','step_water','bow_release','arrow_hit','magic_cast','magic_hit','attack_miss','shield_block','throw_release','throw_hit','structure_hit','structure_break','cage_open','pickup','payload_drop','extraction','objective_interact'])sfxFiles[name]=`${name}.wav`;
const unavailableSfx=new Set();
function playSfx(name,volume=.5,delay=0,fallback=null){
  const run=()=>{
    if(!sfxFiles[name]||unavailableSfx.has(name)){fallback?.();return}
    if(audioMixer.volume(audioCategory(name),volume)===0)return;
    const audio=new Audio(`/assets/sfx/${sfxFiles[name]}?v=20260930-actions-v1`);audio.preload='auto';
    const release=audioMixer.track(audio,audioCategory(name),volume);
    audio.play().catch(error=>{release();if(error.name!=='NotAllowedError'){unavailableSfx.add(name);fallback?.()}});
  };
  if(delay>0)setTimeout(run,delay);else run();
}
document.addEventListener('pointerdown',event=>{const button=event.target.closest?.('button');if(button&&!button.disabled)playSfx(button.matches('.modal-close,#portrait-lightbox-close,#cancel-build')?'ui_cancel':'ui_click',.16)},true);

function playProceduralOutcomeSound(outcome){
  const level=audioMixer.volume('ui');if(!level)return;
  const ctx=ensureAudio(); if(!ctx)return;
  const patterns={
    critical_failure:[[196,.00,.18,'sawtooth'],[147,.16,.26,'sawtooth'],[98,.34,.42,'triangle']],
    failure:[[220,.00,.14,'triangle'],[174,.18,.22,'triangle']],
    success:[[392,.00,.12,'sine'],[494,.12,.12,'sine'],[587,.24,.24,'sine']],
    critical_success:[[523,.00,.10,'sine'],[659,.09,.10,'sine'],[784,.18,.10,'sine'],[1047,.27,.28,'triangle']],
  };
  const now=ctx.currentTime+.03;
  for(const [freq,offset,dur,type] of patterns[outcome]||patterns.success){
    const osc=ctx.createOscillator(),gain=ctx.createGain();
    osc.type=type;osc.frequency.value=freq;gain.gain.setValueAtTime(0.0001,now+offset);gain.gain.exponentialRampToValueAtTime(.075*level,now+offset+.018);gain.gain.exponentialRampToValueAtTime(0.0001,now+offset+dur);osc.connect(gain);gain.connect(ctx.destination);osc.start(now+offset);osc.stop(now+offset+dur+.03);
  }
}
function playOutcomeSound(outcome,delay=0){
  const cue={critical_success:'mission_critical_success',success:'mission_success',failure:'mission_failure',critical_failure:'mission_critical_failure'}[outcome]||'mission_success';
  playSfx(cue,.5,delay,()=>playProceduralOutcomeSound(outcome));
}

function playWalkingSounds(battle,unit,points,duration,delay=0){
  if(['flying','fly'].includes(unit?.movement_type)||points.length<2)return;
  const stride=Math.max(1,Math.ceil((points.length-1)/4));
  for(let i=1;i<points.length;i+=stride){
    const point=points[i],material=battle.ground_tiles?.find(tile=>tile.x===point.x&&tile.y===point.y)?.material||'grass';
    const cue=/water/.test(material)?'step_water':/stone|brick|cobble|dungeon|prison_floor/.test(material)?'step_stone':'step_earth';
    playSfx(cue,.16,delay+Math.round((i-.5)/(points.length-1)*duration));
  }
}
function playBattleSounds(battle,events=battle?.animation_events||[]){
  if(!battle)return 0;
  let delay=0;
  for(const event of events){
    if(event.type==='sound'){
      for(const cue of event.cues||[])playSfx(cue.name,cue.name==='shield_block'?.35:.4,delay+(cue.offset||0));
      delay+=event.duration||0;
    }else if(event.type==='melee_attack'){
      playSfx('melee_swing',.42,delay+45);
      playSfx(event.hit?(event.target_condition==='unconscious'?'subdue_hit':'melee_hit_light'):'attack_miss',.5,delay+185);
      if(event.hit&&event.target_condition==='dead')playSfx('unit_death',.4,delay+330);
      else if(event.hit&&event.target_condition==='unconscious')playSfx('unit_unconscious',.4,delay+315);
      delay+=490;
    }else if(event.type==='movement'){
      const points=event.points||[],duration=Math.max(220,Math.min(850,Math.max(1,points.length-1)*155));
      playWalkingSounds(battle,battle.units?.[event.unit_id],points,duration,delay);
      delay+=duration+70;
    }
  }
  return delay;
}

async function rawApi(path, options={}){
  const headers={'Content-Type':'application/json',...devHeaders,...(options.headers||{})};
  if(sessionToken) headers.Authorization=`Bearer ${sessionToken}`;
  const res=await fetch(path,{...options,headers}); let data={}; try{data=await res.json()}catch{}
  if(!res.ok) throw new Error(data.detail||`Request failed: ${res.status}`); return data;
}

async function setupIdentity(){
  const cfg=await rawApi('/api/config'); appConfig=cfg;
  const params=new URLSearchParams(location.search);
  const embedded=params.has('frame_id') && params.has('instance_id');
  if(embedded){
    if(!cfg.discord_client_id) throw new Error('DISCORD_CLIENT_ID is not configured on the backend.');
    const sdk=new DiscordSDK(cfg.discord_client_id); await sdk.ready();
    if(!sdk.guildId) throw new Error('Launch Fortcamp from inside a Discord server, not a DM.');
    const sessionKey=`fortcamp-session:${cfg.discord_client_id}:${sdk.guildId}`;
    const cachedSession=localStorage.getItem(sessionKey);
    if(cachedSession){
      sessionToken=cachedSession;
      try{
        const existing=await rawApi('/api/state');
        identity=existing.identity;
        return;
      }catch{
        localStorage.removeItem(sessionKey);
        sessionToken=null;
      }
    }
    const {code}=await sdk.commands.authorize({client_id:cfg.discord_client_id,response_type:'code',state:'',prompt:'none',scope:['identify','guilds']});
    const token=await rawApi('/api/discord/token',{method:'POST',body:JSON.stringify({code})});
    const auth=await sdk.commands.authenticate({access_token:token.access_token});
    if(!auth) throw new Error('Discord authentication failed.');
    const gameSession=await rawApi('/api/discord/session',{method:'POST',body:JSON.stringify({access_token:token.access_token,guild_id:sdk.guildId})});
    sessionToken=gameSession.session_token; identity=gameSession.identity;
    localStorage.setItem(sessionKey,sessionToken);
  } else {
    if(!cfg.dev_bypass_auth) throw new Error('This build requires launching from Discord.');
    devHeaders={
      'X-Dev-Guild':params.get('guild_id')||'local-guild',
      'X-Dev-User':params.get('user_id')||'local-user',
      'X-Dev-Name':params.get('name')||'Local Tester'
    };
    identity={guild_id:devHeaders['X-Dev-Guild'],user_id:devHeaders['X-Dev-User'],display_name:devHeaders['X-Dev-Name'],guild_admin:true};
  }
}

function renderCreatorStats(){
  $('#attribute-points-left').textContent=`${creatorAttributePoints} points remaining`;
  $('#creator-attributes').innerHTML=attributeNames.map(k=>`<div class="creator-stat"><span>${k.toUpperCase()}</span><button data-attribute="${k}" data-delta="-1">−</button><b>${creatorAttributes[k]}</b><button data-attribute="${k}" data-delta="1">+</button></div>`).join('');
  $$('[data-attribute]').forEach(btn=>btn.onclick=()=>{const k=btn.dataset.attribute,d=Number(btn.dataset.delta);if(d>0&&(creatorAttributePoints<=0||creatorAttributes[k]>=10))return;if(d<0&&creatorAttributes[k]<=1)return;creatorAttributes[k]+=d;creatorAttributePoints-=d;renderCreatorStats()});
}

async function init(){
  try{
    await setupIdentity(); content=await rawApi('/api/content');
    $('#loading').classList.add('hidden'); $('#identity-label').textContent=`${identity.display_name} · server ${identity.guild_id}${debugEnabled()?' · DEBUG':''}`;
    const data=await rawApi('/api/state');
    if(data.exists){state=data.state;showGame()}else{$('#creator').classList.remove('hidden');renderCreatorStats()}
  }catch(e){$('#loading-text').textContent=e.message;console.error(e)}
}

$('#create-game').onclick=async()=>{
  const starter=$('#cc-perk').value;
  try{const data=await rawApi('/api/new-game',{method:'POST',body:JSON.stringify({character:{name:$('#cc-name').value.trim()||'Wanderer',race:$('#cc-race').value.trim()||'Human',series:$('#cc-series').value.trim()||'Player',specialty:$('#cc-specialty').value,traits:[$('#cc-trait').value],portrait:$('#cc-portrait').value.trim(),perks:{[starter]:'basic'},attributes:creatorAttributes}})});state=data.state;$('#creator').classList.add('hidden');showGame()}catch(e){toast(e.message)}
};

function updateLiveCountdowns(){
  const now=Date.now()/1000;
  $$('[data-countdown-end]').forEach(element=>{const remaining=Math.max(0,Math.ceil(Number(element.dataset.countdownEnd)-now));element.textContent=`${fmtDuration(remaining)}${element.dataset.countdownSuffix||''}`});
  if(pool?.next_refresh)$('#pool-countdown').textContent=countdown(pool.next_refresh);
  const due=activeMissions.some(m=>m.status==='claimed'&&Number(m.completes_at||Infinity)<=now);
  if(due&&Date.now()-lastDeadlineRefresh>600){lastDeadlineRefresh=Date.now();refreshDynamic()}
}
function showGame(){ $('#game').classList.remove('hidden'); refreshAll(); if(!pollTimer)pollTimer=setInterval(refreshDynamic,5000);if(!clockTimer)clockTimer=setInterval(updateLiveCountdowns,250); }
async function refreshAll(){renderResources();renderBase();renderRoster();await refreshDynamic()}
function refreshDynamic(){
  if(dynamicRefreshPromise)return dynamicRefreshPromise;
  dynamicRefreshPromise=(async()=>{try{
    const previous=new Map(activeMissions.map(m=>[m.id,m.status]));
    const [p,pc,a]=await Promise.all([rawApi('/api/missions/pool'),rawApi('/api/private-contracts'),rawApi('/api/missions/active')]);
    const s=await rawApi('/api/state');
    pool=p;
    privateContracts=pc.missions||[];
    const incoming=a.missions;
    if(dynamicReady){
      const complications=incoming.filter(m=>m.status==='battle'&&previous.get(m.id)==='claimed');if(complications.length)toast(`${complications[0].name}: the expedition turned into a fight. Resume it from Your missions.`);
      const completed=incoming.filter(m=>m.status==='completed'&&['claimed','battle'].includes(previous.get(m.id))&&m.result);
      if(completed.length){
        const newest=completed[0];
        playOutcomeSound(newest.result.outcome);
        toast(`${newest.name}: ${title(newest.result.outcome)}`);
        if($('#mission-modal').classList.contains('hidden'))showResult(newest.result);
      }
    }
    const stateChanged=!!(s.exists&&JSON.stringify(s.state)!==JSON.stringify(state));
    activeMissions=incoming;dynamicReady=true;if(s.exists)state=s.state;renderResources();renderMissions();renderPrivateContracts();renderActive();updateLiveCountdowns();
    if(stateChanged)rosterNeedsRefresh=true;
    if(rosterNeedsRefresh&&!document.querySelector('#tab-roster input:focus, #tab-roster textarea:focus, #tab-roster select:focus'))renderRoster();
    if(stateChanged&&!document.querySelector('#tab-base select:focus'))renderBase();
    if(stateChanged&&$('.mission-planner')&&!$('#mission-modal').classList.contains('hidden'))missionPlanner?.refresh(state.characters);
  }catch(e){console.warn(e.message)}})().finally(()=>{dynamicRefreshPromise=null});
  return dynamicRefreshPromise;
}

$$('.tabs button').forEach(btn=>btn.onclick=()=>{$$('.tabs button').forEach(x=>x.classList.remove('active'));btn.classList.add('active');$$('.tab-panel').forEach(x=>x.classList.add('hidden'));$(`#tab-${btn.dataset.tab}`).classList.remove('hidden')});

function renderResources(){if(!state)return;$('#resources').innerHTML=Object.entries(state.resources).map(([k,v])=>`<div class="resource"><b>${v}</b><span>${title(k)}</span></div>`).join('')}
function portraitHTML(c,small=false,viewable=false){const cls=`portrait ${small?'smallp':''} ${c.status!=='idle'?'deployed':''} ${viewable?'viewable':''}`;if(c.portrait){const full=portraitSrc(c.portrait),thumb=portraitSrc(c.portrait_thumbnail||c.portrait);return `<img class="${cls}" draggable="${c.status==='idle'}" data-char="${c.id}" src="${esc(thumb)}" ${viewable?`data-portrait-view="${esc(full)}" data-portrait-name="${esc(c.name)}"`:''} title="${esc(c.name)}" onerror="this.outerHTML='<div class=&quot;${cls}&quot; title=&quot;Portrait could not be loaded&quot;>${initials(c.name)}</div>'">`}return `<div class="${cls}" draggable="${c.status==='idle'}" data-char="${c.id}">${initials(c.name)}</div>`}

function renderMissions(){
  if(!pool)return;$('#pool-countdown').textContent=countdown(pool.next_refresh);$('#mission-rank-label').textContent=`${pool.rank}-RANK`;$('#pool-player-count').textContent=`Pool scaled for ${pool.registered_players} registered player${pool.registered_players===1?'':'s'}`;
  const eventBanner=$('#mission-event-banner'),event=pool.event||{id:'general'};
  document.body.classList.remove('theme-goblin','theme-undead','theme-arcane','theme-beast','theme-starfall');
  if(event.id!=='general')document.body.classList.add(`theme-${event.theme}`);
  if(event.id==='general'){eventBanner.className='event-banner hidden';eventBanner.innerHTML=''}else{eventBanner.className=`event-banner event-${event.theme||'general'}`;eventBanner.innerHTML=`<div class="eyebrow">REGIONAL EVENT</div><h2>${esc(event.name)}</h2><p>${esc(event.splash)}</p>`}
  const debugBox=$('#debug-pool-controls');debugBox.classList.toggle('hidden',!debugEnabled());
  if(debugEnabled()&&!$('#debug-pool-event').options.length){$('#debug-pool-event').innerHTML=Object.entries(content.mission_events).map(([id,e])=>`<option value="${id}">${esc(e.name)}</option>`).join('');$('#debug-force-refresh').onclick=async()=>{const btn=$('#debug-force-refresh');btn.disabled=true;try{const d=await rawApi('/api/debug/missions/refresh',{method:'POST',body:JSON.stringify({event_id:$('#debug-pool-event').value})});toast(`Forced ${d.event.name}`);await refreshDynamic()}catch(err){toast(err.message)}finally{btn.disabled=false}};$('#debug-goblin-battle').onclick=()=>launchDebugBattle($('#debug-goblin-battle'),'/api/debug/battles/goblin-warcamp','Goblin Warcamp battle')}
  if(debugEnabled()&&!$('#debug-captive-cart').onclick)$('#debug-captive-cart').onclick=()=>launchDebugBattle($('#debug-captive-cart'),'/api/debug/battles/captive-cart','Captive Cart battle');
  if(debugEnabled()&&!$('#debug-smoke-signals').onclick)$('#debug-smoke-signals').onclick=()=>launchDebugBattle($('#debug-smoke-signals'),'/api/debug/battles/smoke-signals','Investigation Ambush');
  const ranks=content.mission_ranks||['E','D','C','B','A','S'],viewerIndex=ranks.indexOf(pool.rank);
  const rankFilter=$('#board-rank'),formFilter=$('#board-form');
  if(rankFilter.options.length===1)rankFilter.insertAdjacentHTML('beforeend',ranks.map(rank=>`<option value="${rank}">${rank} rank</option>`).join(''));
  const forms=[...new Set(pool.missions.filter(m=>!m.locked).map(m=>m.mission_form).filter(Boolean))].sort();
  for(const form of forms)if(![...formFilter.options].some(option=>option.value===form))formFilter.insertAdjacentHTML('beforeend',`<option value="${esc(form)}">${esc(title(form))}</option>`);
  $('#board-search').oninput=e=>{missionFilters.query=e.target.value;renderMissions()};
  rankFilter.onchange=e=>{missionFilters.rank=e.target.value;renderMissions()};formFilter.onchange=e=>{missionFilters.form=e.target.value;renderMissions()};
  $('#board-sort').onchange=e=>{missionFilters.sort=e.target.value;renderMissions()};$('#board-available').onchange=e=>{missionFilters.available=e.target.checked;renderMissions()};
  $('#board-reset').onclick=()=>{Object.assign(missionFilters,{query:'',rank:'',form:'',available:true,sort:'shortest'});$('#board-search').value='';rankFilter.value='';formFilter.value='';$('#board-sort').value='shortest';$('#board-available').checked=true;renderMissions()};
  const matching=pool.missions.filter(m=>!m.locked&&matchesMission(m,missionFilters));
  $('#board-match-count').textContent=`${matching.length} visible contract${matching.length===1?'':'s'}`;
  $('#mission-grid').className='rank-boards';
  $('#mission-grid').innerHTML='<div class="mission-guidance"><b>Contract encounters</b><span>Combat is identified when the guild expects it. Other contracts can still become dangerous because of choices, failed rolls, or discoveries.</span></div>'+ranks.map((rank,index)=>{
    const unlocked=index<=viewerIndex;
    if(missionFilters.rank&&missionFilters.rank!==rank)return '';
    const entries=pool.missions.filter(m=>m.rank===rank&&(m.locked||matchesMission(m,missionFilters))),available=entries.filter(m=>m.status==='available').length;
    if((missionFilters.query||missionFilters.form)&&(!unlocked||!entries.length))return '';
    const open=rankBoardOpen[rank]??unlocked;
    const stacks=[...entries.filter(m=>!m.locked).reduce((groups,m)=>{const key=m.template_id||m.id;if(!groups.has(key))groups.set(key,[]);groups.get(key).push(m);return groups},new Map()).values()];
    stacks.sort((a,b)=>missionFilters.sort==='name'?a[0].name.localeCompare(b[0].name):a[0].duration_seconds-b[0].duration_seconds||a[0].name.localeCompare(b[0].name));
    const cards=unlocked?stacks.map(stack=>{const openCopies=stack.filter(m=>m.status==='available'),m=openCopies[0]||stack[0],claimed=stack.length-openCopies.length,count=openCopies.length;return `<article class="mission rank-${m.rank.toLowerCase()} ${m.chain?'chain-mission':''} ${m.world_trigger?'world-trigger-mission':''} ${count?'':'claimed'}" data-mission="${m.id}"><div class="mission-top"><span class="difficulty">${m.chain?`PRIVATE CHAIN · ${m.chain.step}/${m.chain.total}`:m.world_trigger?'WORLD CONSEQUENCE':`${title(m.stat)} proficiency · DC ${m.difficulty}`}</span><span class="duration">${fmtDuration(m.duration_seconds)}</span></div><h3>${esc(m.name)}${count>1?` <span class="mission-stack">×${count}</span>`:''}</h3><div class="mission-form">${esc(title(m.mission_form||'operation'))}</div><p>${esc(m.description)}</p>${m.story_thread?.name?`<small class="story-thread">${esc(m.story_thread.name)}</small>`:''}<div class="chips"><span>${m.party_size} character${m.party_size===1?'':'s'}</span>${(m.roles||[]).map(r=>`<span>${esc(r.label)} · ${r.metric==='constitution'?'CON':r.metric.toUpperCase()} ${r.recommended} rec.</span>`).join('')}${m.reward_preview.map(x=>`<span>${esc(x)}</span>`).join('')}</div>${m.world_trigger?`<div class="world-consequence">Caused by ${esc(m.world_trigger.source_mission)} · uncovered by ${esc(m.world_trigger.triggered_by)}</div>`:''}${m.chain?`<div class="chain-deadline">Claim within ${countdown(m.chain.claim_by)} · visible only to you</div>`:''}${m.requirements.length?`<div class="requirements">Requires: ${m.requirements.map(esc).join(' · ')}</div>`:''}<div class="mission-status">${count?`<b>${count} AVAILABLE</b>${claimed?` · ${claimed} claimed`:''}`:`${claimed} claimed`}</div></article>`}).join(''):`<div class="locked-rank-copy"><b>${available} ${rank}-Rank mission${available===1?'':'s'} available</b><span>Upgrade Guild Hall visibility to reveal this board.</span></div>`;
    return `<details class="rank-board rank-${rank.toLowerCase()} ${unlocked?'':'rank-board-locked'}" data-rank-board="${rank}" ${open?'open':''}><summary><span class="rank-badge">${rank}</span><strong>${rank}-Rank Board</strong><span>${available} available</span><i>${unlocked?'':'LOCKED'}</i></summary><div class="rank-mission-grid">${cards||'<p class="muted">No contracts of this rank appeared this refresh.</p>'}</div></details>`;
  }).join('')+(!matching.length?'<div class="board-empty"><b>No revealed contracts match.</b><span>Try another search or reset your filters. Locked boards reveal only their available counts.</span></div>':'');
  $$('[data-rank-board]').forEach(board=>board.ontoggle=()=>rankBoardOpen[board.dataset.rankBoard]=board.open);
  $$('.mission[data-mission]').forEach(el=>el.onclick=()=>openMission(pool.missions.find(m=>m.id===el.dataset.mission)));
}
function renderPrivateContracts(){
  const grid=$('#private-contract-grid'),debug=$('#private-debug-controls');
  if(!grid)return;
  const privateTab=$('[data-tab="private"]');if(privateTab)privateTab.textContent=`Private Contracts${privateContracts.length?` (${privateContracts.length})`:''}`;
  debug?.classList.toggle('hidden',!debugEnabled());
  const debugButton=$('#debug-hedgerow-watch');
  if(debugEnabled()&&debugButton&&!debugButton.onclick)debugButton.onclick=async()=>{
    debugButton.disabled=true;
    try{await rawApi('/api/debug/private-contracts/hedgerow-watch',{method:'POST',body:'{}'});toast('Defense contract added');await refreshDynamic()}
    catch(error){toast(error.message)}finally{debugButton.disabled=false}
  };
  if(!privateContracts.length){
    grid.innerHTML='<div class="private-empty"><div class="eyebrow">NO OPEN LEADS</div><h3>Your contacts have no private work waiting.</h3><p>Investigations, faction trust, rescued characters, and story consequences can place contracts here. They are visible only to you and expire if ignored.</p></div>';
    return;
  }
  grid.innerHTML=privateContracts.map(m=>`<article class="mission private-contract rank-${m.rank.toLowerCase()}" data-private-mission="${m.id}"><div class="mission-top"><span class="difficulty">${esc(m.private_source||'Earned follow-up')}</span><span class="duration" data-countdown-end="${m.expires_at}" data-countdown-suffix=" to claim">${countdown(m.expires_at)} to claim</span></div><h3>${esc(m.name)}</h3><div class="mission-form">${esc(title(m.mission_form||'operation'))} · ${esc(title(m.resolution_mode||'roll'))}</div><p>${esc(m.description)}</p><div class="chips"><span>${m.party_size} character${m.party_size===1?'':'s'}</span>${(m.reward_preview||[]).map(x=>`<span>${esc(x)}</span>`).join('')}</div><div class="chain-deadline">Personal contract · disappears when its claim window ends</div></article>`).join('');
  $$('[data-private-mission]').forEach(card=>card.onclick=()=>openMission(privateContracts.find(m=>m.id===card.dataset.privateMission)));
}
function renderActive(){
  const running=activeMissions.filter(m=>['claimed','battle','decision'].includes(m.status));const recent=activeMissions.filter(m=>m.status==='completed').slice(0,3);
  const debug=debugEnabled();
  $('#active-missions').innerHTML=(running.length||recent.length)?`<div class="active-title">Your missions${debug?' · DEBUG ENABLED':''}</div>${running.map(m=>m.status==='decision'?`<button class="active-card" data-resume-scene="${m.id}"><div class="active-main"><b>${esc(m.name)}</b><span>Decision waiting · Continue story</span></div></button>`:m.status==='battle'?`<button class="active-card battle-active" data-resume-battle="${m.id}"><div class="active-main"><b>${esc(m.name)}</b><span>Tactical battle in progress · Resume</span></div></button>`:`<div class="active-card mission-running"><div class="active-main"><b>${esc(m.name)}</b><span data-countdown-end="${m.completes_at}" data-countdown-suffix=" remaining">${countdown(m.completes_at)} remaining</span></div>${debug?`<div class="debug-complete"><small>Debug resolution</small><button class="debug-resolve-natural" data-debug-resolve-now="${m.id}">Resolve Now · Real Roll</button><button data-debug="critical_failure" data-debug-mission="${m.id}">Critical Failure</button><button data-debug="failure" data-debug-mission="${m.id}">Failure</button><button data-debug="success" data-debug-mission="${m.id}">Success</button><button data-debug="critical_success" data-debug-mission="${m.id}" ${m.critical_success_available?'':'disabled'}>Critical Success</button></div>`:''}</div>`).join('')}${recent.map(m=>`<button class="active-card result-card" data-result="${m.id}"><b>${esc(m.name)}</b><span>${title(m.result?.outcome||'completed')}${m.result?.debug_forced?' · DEBUG':''}</span></button>`).join('')}`:'';
  $$('[data-resume-scene]').forEach(el=>el.onclick=()=>openDecision(el.dataset.resumeScene));
  $$('[data-resume-battle]').forEach(el=>el.onclick=()=>openBattle(el.dataset.resumeBattle));
  $$('[data-result]').forEach(el=>el.onclick=()=>showResult(activeMissions.find(m=>m.id===el.dataset.result)?.result));
  $$('[data-debug-mission]').forEach(btn=>btn.onclick=async e=>{e.stopPropagation();await debugCompleteMission(btn.dataset.debugMission,btn.dataset.debug)});
  $$('[data-debug-resolve-now]').forEach(btn=>btn.onclick=async e=>{e.stopPropagation();btn.disabled=true;try{const data=await rawApi(`/api/debug/missions/${btn.dataset.debugResolveNow}/resolve-now`,{method:'POST',body:'{}'});if(data.mission.status==='battle'){toast('The investigation turned into a fight');await openBattle(data.mission.id);await refreshDynamic();return}const local=activeMissions.find(m=>m.id===btn.dataset.debugResolveNow);if(local){local.status='completed';local.result=data.result}playOutcomeSound(data.result.outcome);toast(`Resolved: ${title(data.result.outcome)}`);showResult(data.result);await refreshDynamic()}catch(error){toast(error.message)}finally{btn.disabled=false}});
}

function currentMissionSelection(){return missionPlanner?.selection()||{party_ids:[],role_assignments:null,bodyguard_ids:[]}}

async function debugCompleteMission(missionId,outcome,selection={party_ids:[],role_assignments:null}){
  try{
    const data=await rawApi(`/api/debug/missions/${missionId}/complete`,{method:'POST',body:JSON.stringify({outcome,...selection})});
    const local=activeMissions.find(m=>m.id===missionId);if(local){local.status='completed';local.result=data.result}
    playOutcomeSound(data.result.outcome);toast(`DEBUG: ${title(data.result.outcome)}`);showResult(data.result);await refreshDynamic();
  }catch(e){toast(e.message)}
}

function perkLevel(c,track){return c.perks?.[track]||'none'}
function perkRank(c,track){return (content.perk_levels||['none','basic','skilled','expert','master']).indexOf(perkLevel(c,track))}
function effectiveAttribute(c,attribute){let n=c.attributes?.[attribute]??5;Object.values(c.equipment||{}).forEach(id=>{const item=itemByInstance(id);if(item)n+=item.attribute_bonuses?.[attribute]||0});Object.entries(content.perk_tracks||{}).forEach(([track,d])=>{if(d.attribute_bonus===attribute&&perkRank(c,track)>=1)n++});return n+(perkModifiers(c,Object.values(c.equipment||{}).map(itemByInstance),content.standalone_perks,'attributes')[attribute]||0)}
function combatMetrics(c){
  const weapon=itemByInstance(c.equipment?.weapon),scaling=weapon?.weapon_scaling||'str';
  return {constitution:effectiveAttribute(c,'vit'),dps:effectiveAttribute(c,scaling)+(weapon?.power||0)+Math.floor(effectiveStat(c,'combat')/2),dps_attribute:scaling,weapon:weapon?.name||'Unarmed'};
}
function roleMetricLabel(metric){return metric==='constitution'?'CON':metric.toUpperCase()}
function roleScoreText(c,role){const metrics=combatMetrics(c),score=metrics[role.metric]||0;return role.metric==='dps'?`${score} DPS · ${metrics.dps_attribute.toUpperCase()} · ${metrics.weapon}`:`${score} CON`}
function syncRoleOptions(){
  const selects=$$('[data-role-select]'),chosen=selects.map(x=>x.value).filter(Boolean);
  selects.forEach(select=>[...select.options].forEach(option=>{if(option.value)option.disabled=option.value!==select.value&&chosen.includes(option.value)}));
}
function syncBodyguardSelection(){
  const selected=currentMissionSelection(),primary=new Set(selected.party_ids),guards=$$('#mission-detail input[data-bodyguard]');
  guards.forEach(input=>{if(primary.has(input.value))input.checked=false;input.disabled=primary.has(input.value)});
  const count=$('[data-bodyguard-count]');if(count)count.textContent=`${guards.filter(input=>input.checked).length}/${selectedMission?.bodyguard_slots||0}`;
}
function syncMissionPartyCapacity(){
  if(!selectedMission||selectedMission.roles?.length)return;
  const inputs=$$('#mission-detail input[data-mission-party]'),checked=inputs.filter(input=>input.checked),full=checked.length>=selectedMission.party_size;
  inputs.forEach(input=>{
    const option=input.closest('.party-option'),unavailable=option?.classList.contains('disabled');
    input.disabled=!!unavailable||full&&!input.checked;
    option?.classList.toggle('capacity-locked',full&&!input.checked&&!unavailable);
  });
}

async function openMission(m){
  selectedMission=m;missionPlanner=null;analysisSequence++;$('#mission-modal').classList.remove('hidden');
  if(m.status!=='available'){$('#mission-detail').innerHTML=`<div class="eyebrow">${title(m.status)}</div><h2>${esc(m.name)}</h2><p>${m.claimed_by_name?`Claimed by ${esc(m.claimed_by_name)}.`:'No longer available.'}</p>`;return}
  missionPlanner=mountMissionPlanner($('#mission-detail'),m,state.characters,{
    esc,title,portrait:c=>portraitHTML(c,true),metrics:combatMetrics,rating:effectiveStat,
    statLabel:content.perk_tracks?.[m.stat]?.name||title(m.stat),debug:debugEnabled(),
    onChange:updateAnalysis,onClaimDebug:(outcome,selection)=>debugCompleteMission(m.id,outcome,selection)
  });
  const debugCrit=$('[data-debug-available="critical_success"]');if(debugCrit&&m.has_special_critical)debugCrit.disabled=true;
  await updateAnalysis();
}

async function updateAnalysis(){
  const requestId=++analysisSequence,missionId=selectedMission?.id;
  const selection=currentMissionSelection(),btn=$('#claim-mission'),roleMode=!!selectedMission.roles?.length;
  if(!btn||!$('#odds'))return;btn.disabled=true;
  if(selection.party_ids.length!==selectedMission.party_size){$('#odds').innerHTML=roleMode?'Assign one unique character to every role.':`Select ${selectedMission.party_size-selection.party_ids.length} more character(s).`;btn.disabled=true;return}
  try{const {analysis}=await rawApi(`/api/missions/${selectedMission.id}/analysis`,{method:'POST',body:JSON.stringify(selection)});
    if(requestId!==analysisSequence||selectedMission?.id!==missionId||!$('#odds'))return;
    const p=analysis.probabilities,roles=(analysis.roles||[]).map(r=>`<div class="role-result ${r.meets_recommendation?'met':'below'}"><b>${esc(r.label)} · ${r.metric==='constitution'?'CON':r.metric.toUpperCase()} ${r.score}</b><span>Recommended ${r.recommended}${r.metric==='dps'?` · ${String(r.dps_attribute||'str').toUpperCase()} · ${esc(r.weapon||'Unarmed')}`:''}</span></div>`).join('');
    $('#odds').innerHTML=selectedMission.has_decisions?`<div class="tactical-readiness"><b>Choose how this contract unfolds.</b><span>Each decision shows its check, risks and odds. Choices can change rewards, reveal a lead or start a fight.</span></div>${roles?`<div class="role-results">${roles}</div>`:''}${analysis.requirements.length?`<div class="req-checks">${analysis.requirements.map(r=>`<span class="${r.met?'met':'unmet'}">${r.met?'✓':'✕'} ${esc(r.label)}</span>`).join('')}</div>`:''}`:selectedMission.combat_encounter?`<div class="tactical-readiness"><b>Lineup ready for tactical deployment.</b><span>Mission rolls do not decide this outcome. Positioning, objectives, combat actions, and safe extraction determine the result.</span>${selectedMission.combat_critical_condition?`<small><b>Critical Success:</b> ${esc(selectedMission.combat_critical_condition)}</small>`:''}</div>${roles?`<div class="role-results">${roles}</div>`:''}${analysis.requirements.length?`<div class="req-checks">${analysis.requirements.map(r=>`<span class="${r.met?'met':'unmet'}">${r.met?'✓':'✕'} ${esc(r.label)}</span>`).join('')}</div>`:''}`:`<div class="odds-grid"><div class="bad"><b>${p.critical_failure}%</b><span>Critical Failure</span></div><div><b>${p.failure}%</b><span>Failure</span></div><div class="good"><b>${p.success}%</b><span>Success</span></div><div class="crit"><b>${p.critical_success}%</b><span>Critical Success</span></div></div>${roles?`<div class="role-results">${roles}</div>`:''}${analysis.requirements.length?`<div class="req-checks">${analysis.requirements.map(r=>`<span class="${r.met?'met':'unmet'}">${r.met?'✓':'✕'} ${esc(r.label)}</span>`).join('')}</div>`:''}${analysis.secret_event_possible?'<div class="secret-event-hint"><b>Something unusual resonates with this lineup.</b><br>This party has a chance to trigger a secret event.</div>':''}${analysis.critical_path_active?'<div class="critical-path">A special critical-success path is active for this team.</div>':!analysis.critical_success_available?'<div class="critical-locked">Critical Success is locked until this mission’s special criterion is met.</div>':''}`;
    const debugCrit=$('[data-debug-available="critical_success"]');if(debugCrit)debugCrit.disabled=!analysis.critical_success_available;
    btn.disabled=!analysis.claimable||missionClaimPending;btn.onclick=()=>claimMission(selection);
  }catch(e){if(requestId!==analysisSequence||selectedMission?.id!==missionId||!$('#odds'))return;$('#odds').textContent=e.message;btn.disabled=true}
}
async function claimMission(selection){if(missionClaimPending)return;missionClaimPending=true;const button=$('#claim-mission');if(button)button.disabled=true;try{const data=await rawApi(`/api/missions/${selectedMission.id}/claim`,{method:'POST',body:JSON.stringify(selection)});playSfx('ui_confirm',.25);toast(data.mission.status==='decision'?'Contract started · choose your approach':data.mission.status==='battle'?'Battle started':'Mission claimed');if(data.mission.status==='decision'){await openDecision(data.mission.id,data.mission,data.decision)}else if(data.mission.status==='battle'){await openBattle(data.mission.id)}else{$('#mission-modal').classList.add('hidden')}await refreshDynamic()}catch(e){toast(e.message);await refreshDynamic()}finally{missionClaimPending=false;if($('.mission-planner'))await updateAnalysis()}}

async function openDecision(missionId,mission,initialDecision){
  missionPlanner=null;analysisSequence++;activeBattleView=null;
  const data=initialDecision?{decision:initialDecision}:await rawApi(`/api/missions/${missionId}/decision`);
  const current=mission||activeMissions.find(m=>m.id===missionId)||selectedMission;
  $('#mission-modal').classList.remove('hidden');
  const draw=scene=>{mountDecisionScene($('#mission-detail'),current,scene,{esc,title,onChoose:async payload=>{
    const response=await rawApi(`/api/missions/${missionId}/decision`,{method:'POST',body:JSON.stringify(payload)});
    playSfx('ui_confirm',.25);
    if(response.decision)draw(response.decision);
    else if(response.mission.status==='battle')await openBattle(missionId);
    else if(response.result){const local=activeMissions.find(m=>m.id===missionId);if(local){local.status='completed';local.result=response.result}playOutcomeSound(response.result.outcome);showResult(response.result)}
    await refreshDynamic();
  }});const card=$('#mission-modal .modal-card');card.scrollTop=0;$('#mission-detail').querySelector('[data-scene-choice]:not(:disabled)')?.focus({preventScroll:true})};
  draw(data.decision);
}

async function openBattle(missionId){
  try{activeBattleMissionId=missionId;activeBattleView=null;selectedCombatAction='move';selectedPreparation={mode:'defense',id:null};contextMenuOpen=false;tileActionMenu=null;retreatAllArmed=false;battleZoom=DEFAULT_BATTLE_ZOOM;battlePan={left:0,top:0};const data=await rawApi(`/api/missions/${missionId}/battle`);$('#mission-modal').classList.remove('hidden');renderBattle(data.battle)}catch(e){toast(e.message)}
}
const paintedTerrainSpriteByKind={palisade:'structure:palisade_straight',cookfire:'campfire_lit',watchtower:'structure:wooden_watch_platform',wagon:'wooden_handcart',pit:'terrain:pit_deep_earthen'};
const paintedObjectSprites={
  prisoner_pen:{default:'structure:wooden_rescue_cage_closed',opened:'structure:wooden_rescue_cage_open'},
  iron_rescue_cage:{default:'structure:iron_rescue_cage_closed',opened:'structure:iron_rescue_cage_open'},
  wooden_rescue_cage:{default:'structure:wooden_rescue_cage_closed',opened:'structure:wooden_rescue_cage_open'},
  prisoner_stocks:{default:'structure:prisoner_stocks_closed',opened:'structure:prisoner_stocks_open'},
  stone_sarcophagus:{default:'structure:stone_sarcophagus_closed',opened:'structure:stone_sarcophagus_open'},
  ritual_altar:{default:'structure:ritual_altar_dormant',active:'structure:ritual_altar_active'},
  supply_crate:{default:'crate_closed',opened:'crate_open'},
  military_supply_coffer:{default:'military_supply_coffer_closed',opened:'military_supply_coffer_open'},
  treasure_chest_bronze:{default:'treasure_chest_bronze_closed',opened:'treasure_chest_bronze_open'},
  treasure_chest_silver:{default:'treasure_chest_silver_closed',opened:'treasure_chest_silver_open'},
  treasure_chest_gold:{default:'treasure_chest_gold_closed',opened:'treasure_chest_gold_open'},
  ancient_reliquary:{default:'ancient_reliquary_closed',opened:'ancient_reliquary_open'},
  arcane_crystal:{default:'arcane_crystal_intact',broken:'arcane_crystal_shattered',destroyed:'arcane_crystal_shattered'},
  floor_lever:{default:'floor_lever_off',active:'floor_lever_on',opened:'floor_lever_on'},
  loose_stone:{default:'scattered_stones'},
};
function paintedObjectSprite(object){const set=paintedObjectSprites[object.id];return object.sprite||set?.[object.state]||set?.default||''}
function paintedPropStyle(sprite){if(!sprite)return'';const terrain=sprite.startsWith('terrain:'),structure=sprite.startsWith('structure:'),id=terrain?sprite.slice(8):structure?sprite.slice(10):sprite,folder=terrain?'mega-terrain-tiles':structure?'structures':'props';return /^[a-z0-9_]+$/.test(id)?`--battle-prop:url('/assets/combat-terrain/${folder}/${id}.png');`:''}
function mapAssetLayout(item){const footprint=Array.isArray(item.footprint)?item.footprint:[1,1],baseWidth=Math.max(1,Number(footprint[0])||1),baseHeight=Math.max(1,Number(footprint[1])||1),rotation=((Number(item.rotation)||0)%360+360)%360,turned=rotation===90||rotation===270,width=turned?baseHeight:baseWidth,height=turned?baseWidth:baseHeight,multi=baseWidth>1||baseHeight>1||rotation!==0;return{className:multi?'multi-cell-asset':'',style:`grid-column:${item.x+1}/span ${width};grid-row:${item.y+1}/span ${height};--asset-width:${baseWidth/width*100}%;--asset-height:${baseHeight/height*100}%;--asset-rotation:${rotation}deg`}}
function terrainVariant(mapId,material,x,y){const choices={grass:[0,0,0,0,0,1,1,2],dirt:[0,0,0,0,0,0,1],mud:[0,0,0,1],stone:[0,0,0,0,1],water:[0,0,0,1],timber:[0]}[material]||[0],patchX=Math.floor(x/2),patchY=Math.floor(y/2),key=`${mapId||'map'}:${material}:${patchX}:${patchY}`;let hash=2166136261;for(let i=0;i<key.length;i++){hash^=key.charCodeAt(i);hash=Math.imul(hash,16777619)}return choices[(hash>>>0)%choices.length]}
function combatActionArt(name){return `<span class="combat-action-art action-${name}" aria-hidden="true"></span>`}
function battleToken(unit,current,battle){
  const face=unit.portrait?`<img src="${esc(portraitSrc(unit.portrait))}" alt="">`:`<span>${initials(unit.name)}</span>`;
  const boss=unit.boss||unit.kind==='chieftain';
  const height=battle.elevation?.find(tile=>tile.x===unit.x&&tile.y===unit.y)?.height||0,preview=battle.attack_previews?.[unit.id]?.[selectedCombatAction];
  const accuracy=preview?` · ${preview.chance}% accuracy${preview.damage_bonus?` · +${preview.damage_bonus} height damage`:''}`:'';
  const statuses=(unit.statuses||[]).map(status=>{const d=battle.status_definitions?.[status.id]||{name:title(status.id),icon:'•',description:'Status effect'};return `<span class="status-icon" tabindex="0">${esc(d.icon)}<span class="status-tooltip"><b>${esc(d.name)}</b><small>${esc(d.description)}</small>${status.duration!=null?`<em>${status.duration} activation${status.duration===1?'':'s'} remaining</em>`:''}</span></span>`}).join('');
  const condition=unit.condition||(!unit.alive?'dead':'active'),bodyLabel=condition==='unconscious'?'UNCONSCIOUS':condition==='dead'?'CORPSE':'';
  const throwTarget=(battle.throw_profile?.target_ids||[]).includes(unit.id);
  const targeting=['attack','subdue','skill','throw'].includes(selectedCombatAction)&&unit.team==='enemy',validTarget=selectedCombatAction==='throw'?throwTarget:!!preview;
  const occupiedAbove=condition!=='active'&&Object.values(battle.units||{}).some(other=>other.id!==unit.id&&other.x===unit.x&&other.y===unit.y&&other.alive&&other.conscious!==false&&!other.extracted&&!other.carried_by);
  return `<button class="battle-token ${unit.team} ${current?'current':''} ${boss?'boss':''} ${throwTarget?'throw-target':''} ${targeting?(validTarget?'valid-target':'invalid-target'):''} ${unit.extracted?'extracted':''} ${unit.carried_by?'carried':''} ${occupiedAbove?'body-under-unit':''} ${condition}" data-battle-unit="${unit.id}" style="grid-column:${unit.x+1};grid-row:${unit.y+1}" title="${esc(unit.name)} · ${unit.hp}/${unit.max_hp} HP · ${title(condition)} · elevation ${height}${boss?' · BOSS':''}${targeting?validTarget?' · valid target':' · out of range or line of sight':''}${throwTarget?` · ${battle.throw_profile.damage} throw damage`:''}${accuracy}">${boss?'<strong class="boss-label">BOSS</strong>':''}${height?`<strong class="height-badge">▲${height}</strong>`:''}${face}${condition==='active'?`<i><b>${unit.hp}</b><small>HP</small></i>`:''}${bodyLabel?`<em class="body-label">${condition==='dead'?'† CORPSE':'ZZZ · UNCONSCIOUS'}</em>`:''}${statuses?`<span class="status-row">${statuses}</span>`:''}</button>`;
}

function tileActionsForBattle(b,x,y){
  const current=b.units?.[b.current_unit_id],actions=[];
  if(!current)return actions;
  const units=Object.values(b.units||{}).filter(unit=>unit.x===x&&unit.y===y&&!unit.extracted&&!unit.carried_by);
  const livingEnemy=units.find(unit=>unit.team==='enemy'&&unit.alive&&unit.conscious!==false);
  const body=units.find(unit=>unit.conscious===false&&['unconscious','dead'].includes(unit.condition));
  if(livingEnemy){
    const previews=b.attack_previews?.[livingEnemy.id]||{};
    if(previews.attack)actions.push({label:`Attack ${livingEnemy.name}`,detail:`${previews.attack.chance}% accuracy`,command:{action:'attack',target_id:livingEnemy.id},icon:'⚔'});
    if(previews.subdue)actions.push({label:`Subdue ${livingEnemy.name}`,detail:`${previews.subdue.chance}% accuracy`,command:{action:'subdue',target_id:livingEnemy.id},icon:'◇'});
    if(previews.skill&&current.special)actions.push({label:`${current.special.name}: ${livingEnemy.name}`,detail:`${previews.skill.chance}% accuracy`,command:{action:'skill',target_id:livingEnemy.id},icon:'✦'});
    if((b.throw_profile?.target_ids||[]).includes(livingEnemy.id))actions.push({label:`Throw ${b.throw_profile.payload_name}`,detail:`${b.throw_profile.damage} impact damage`,command:{action:'throw',target_id:livingEnemy.id},icon:'➶'});
  }
  if(body){
    const carry=(b.context_actions||[]).find(entry=>entry.command?.action==='carry'&&entry.command?.target_id===body.id);
    if(carry){
      actions.push({label:`Carry ${body.name}`,detail:`${title(body.condition)} · ${carry.cost}`,command:carry.command,icon:'↥'});
      actions.push({label:`Pick Up to Throw`,detail:`Carry ${body.name}, then choose a target`,command:carry.command,nextMode:'throw',icon:'➶'});
    }
  }
  const occupied=units.some(unit=>unit.alive&&unit.conscious!==false);
  if(!occupied&&(b.reachable||[]).some(point=>point.x===x&&point.y===y))actions.unshift({label:'Move Here',detail:`Tile ${x+1},${y+1}`,command:{action:'move',x,y},icon:'➜'});
  return actions;
}

function animateBattleMovement(previous,battle,durationFloor=260){
  const animationEvents=[...(battle.animation_events||[])];
  battle.animation_events=[];
  if(!previous||previous.encounter_id!==battle.encounter_id)return;
  const field=$('.battlefield');if(!field)return;
  const cellWidth=field.getBoundingClientRect().width/battle.width,cellHeight=field.getBoundingClientRect().height/battle.height;
  if(animationEvents.length){
    playBattleSounds(battle,animationEvents);
    let delay=0;
    animationEvents.forEach(event=>{
      if(event.type==='sound'){delay+=event.duration||0;return}
      if(event.type==='melee_attack'){
        const attacker=battle.units?.[event.attacker_id],target=battle.units?.[event.target_id];
        const attackerToken=field.querySelector(`[data-battle-unit="${CSS.escape(event.attacker_id)}"]`),targetToken=field.querySelector(`[data-battle-unit="${CSS.escape(event.target_id)}"]`);
        if(!attacker||!target||!attackerToken||!targetToken)return;
        const dx=Math.sign(target.x-attacker.x)*cellWidth*.42,dy=Math.sign(target.y-attacker.y)*cellHeight*.42;
        const attackerScale=attacker.id===battle.current_unit_id?1.15:1,targetScale=target.id===battle.current_unit_id?1.15:1;
        attackerToken.classList.add('is-attacking');
        const lunge=attackerToken.animate([
          {transform:`translate(0,0) scale(${attackerScale})`,offset:0},
          {transform:`translate(${dx*.18}px,${dy*.18}px) scale(${attackerScale*.98})`,offset:.28},
          {transform:`translate(${dx}px,${dy}px) scale(${attackerScale*1.08})`,offset:.52},
          {transform:`translate(0,0) scale(${attackerScale})`,offset:1},
        ],{duration:420,delay,easing:'cubic-bezier(.2,.8,.25,1)',fill:'both'});
        const finishAttack=()=>attackerToken.classList.remove('is-attacking');
        lunge.addEventListener('finish',finishAttack,{once:true});lunge.addEventListener('cancel',finishAttack,{once:true});
        if(event.hit){
          targetToken.classList.add('is-hit');
          const impactX=Math.sign(target.x-attacker.x)*cellWidth*.12,impactY=Math.sign(target.y-attacker.y)*cellHeight*.12;
          const impact=targetToken.animate([
            {transform:`translate(0,0) scale(${targetScale})`,filter:'brightness(1)',offset:0},
            {transform:`translate(${impactX}px,${impactY}px) scale(${targetScale*.94})`,filter:'brightness(1.8) saturate(.6)',offset:.28},
            {transform:`translate(${-impactX*.25}px,${-impactY*.25}px) scale(${targetScale})`,filter:'brightness(.8)',offset:.55},
            {transform:`translate(0,0) scale(${targetScale})`,filter:'brightness(1)',offset:1},
          ],{duration:300,delay:delay+185,easing:'ease-out',fill:'both'});
          const finishImpact=()=>targetToken.classList.remove('is-hit');
          impact.addEventListener('finish',finishImpact,{once:true});impact.addEventListener('cancel',finishImpact,{once:true});
        }
        delay+=490;
        return;
      }
      const unit=battle.units?.[event.unit_id],points=event.points||[];
      const token=field.querySelector(`[data-battle-unit="${CSS.escape(event.unit_id)}"]`);
      if(!unit||!token||!points.length)return;
      const baseScale=unit.id===battle.current_unit_id?1.15:1;
      const frames=[];
      if(points.length===1){
        frames.push({transform:`translate(0,0) scale(${baseScale})`,opacity:1,offset:0});
      }else for(let index=0;index<points.length-1;index++){
        const from=points[index],to=points[index+1],start=index/(points.length-1),middle=(index+.5)/(points.length-1);
        frames.push({transform:`translate(${(from.x-unit.x)*cellWidth}px, ${(from.y-unit.y)*cellHeight}px) scale(${baseScale}) rotate(${index%2?-2:2}deg)`,opacity:1,offset:start});
        frames.push({transform:`translate(${((from.x+to.x)/2-unit.x)*cellWidth}px, ${((from.y+to.y)/2-unit.y)*cellHeight-5}px) scale(${baseScale*1.025}) rotate(${index%2?2:-2}deg)`,opacity:1,offset:middle});
      }
      frames.push({transform:`translate(0,0) scale(${baseScale}) rotate(0deg)`,opacity:event.extracted?0:1,offset:1});
      token.classList.remove('extracted');
      token.classList.add('is-walking');
      const duration=Math.max(220,Math.min(850,Math.max(1,points.length-1)*155));
      const animation=token.animate(frames,{duration,delay,easing:'ease-in-out',fill:'both'});
      const finishWalking=()=>{token.classList.remove('is-walking');if(event.extracted)token.classList.add('extracted')};
      animation.addEventListener('finish',finishWalking,{once:true});
      animation.addEventListener('cancel',finishWalking,{once:true});
      delay+=duration+70;
    });
    return;
  }
  Object.values(battle.units||{}).forEach(unit=>{
    const before=previous.units?.[unit.id];
    if(!before||before.x===unit.x&&before.y===unit.y)return;
    const token=field.querySelector(`[data-battle-unit="${CSS.escape(unit.id)}"]`);if(!token)return;
    let points=[{x:before.x,y:before.y},{x:unit.x,y:unit.y}];
    if(unit.id===battle.current_unit_id&&battle.movement_path?.length){
      const fullPath=battle.movement_path.map(point=>({x:point.x,y:point.y}));
      const previousIndex=fullPath.findIndex(point=>point.x===before.x&&point.y===before.y);
      points=previousIndex>=0?[{x:before.x,y:before.y},...fullPath.slice(previousIndex+1)]:[{x:before.x,y:before.y},{x:unit.x,y:unit.y}];
    }
    if(points.length<2||points.at(-1).x!==unit.x||points.at(-1).y!==unit.y)points.push({x:unit.x,y:unit.y});
    const baseScale=unit.id===battle.current_unit_id?1.15:1;
    const frames=[];
    for(let index=0;index<points.length-1;index++){
      const from=points[index],to=points[index+1],start=index/(points.length-1),middle=(index+.5)/(points.length-1);
      frames.push({transform:`translate(${(from.x-unit.x)*cellWidth}px, ${(from.y-unit.y)*cellHeight}px) scale(${baseScale}) rotate(${index%2?-2:2}deg)`,offset:start});
      frames.push({transform:`translate(${((from.x+to.x)/2-unit.x)*cellWidth}px, ${((from.y+to.y)/2-unit.y)*cellHeight-5}px) scale(${baseScale*1.025}) rotate(${index%2?2:-2}deg)`,offset:middle});
    }
    frames.push({transform:`translate(0px, 0px) scale(${baseScale}) rotate(0deg)`,offset:1});
    token.classList.add('is-walking');
    const duration=Math.max(durationFloor,Math.min(950,(points.length-1)*190));
    playWalkingSounds(battle,unit,points,duration);
    const animation=token.animate(frames,{duration,easing:'ease-in-out'});
    const finishWalking=()=>token.classList.remove('is-walking');
    animation.addEventListener('finish',finishWalking,{once:true});
    animation.addEventListener('cancel',finishWalking,{once:true});
  });
}
function renderBattlePreparation(b){
  const previousBattle=activeBattleView;
  activeBattleView=b;
  const prep=b.preparation||{},prepZone=new Set((prep.zone||[]).map(p=>`${p.x},${p.y}`)),deploymentZone=new Set((prep.deployment_zone||[]).map(p=>`${p.x},${p.y}`));
  const ground=new Map((b.ground_tiles||[]).map(tile=>[`${tile.x},${tile.y}`,tile.material])),groundMaterials=b.ground_materials||{};
  let cells='';
  for(let y=0;y<b.height;y++)for(let x=0;x<b.width;x++){
    const key=`${x},${y}`,material=ground.get(key)||'grass',info=groundMaterials[material]||{name:title(material)};
    cells+=`<button class="battle-cell ground-${material} tile-variant-${terrainVariant(b.map_id,material,x,y)} ${prepZone.has(key)?'preparation-zone':''} ${deploymentZone.has(key)?'deployment-zone':''}" data-battle-cell="${x},${y}" style="grid-column:${x+1};grid-row:${y+1};--gx:${x};--gy:${y}" title="${esc(info.name)}${prepZone.has(key)?' · defense placement zone':''}${deploymentZone.has(key)?' · deployment zone':''}"></button>`;
  }
  const elevations=(b.elevation||[]).map(tile=>`<div class="battle-elevation" style="grid-column:${tile.x+1};grid-row:${tile.y+1};--height:${tile.height}" title="${title(tile.kind||'elevation')} · height ${tile.height}"><span>▲${tile.height}</span></div>`).join('');
  const decorations=(b.decorations||[]).map(item=>{const layout=mapAssetLayout(item);return `<div class="battle-decoration has-prop-art ${layout.className}" style="${layout.style};${paintedPropStyle(item.sprite)}" title="${esc(item.name||title(item.sprite))}"></div>`}).join('');
  const placedIds=new Set((prep.placements||[]).map(row=>row.id));
  const terrain=(b.terrain||[]).map(t=>{const layout=mapAssetLayout(t),sprite=t.sprite||paintedTerrainSpriteByKind[t.kind],placed=placedIds.has(t.id);return `<button class="battle-terrain ${t.kind} ${sprite?'has-prop-art':''} ${layout.className} ${sprite?.startsWith('structure:')?'prop-structure':''} ${placed?'prepared-defense':''}" ${placed?`data-prep-remove="${esc(t.id)}"`: 'disabled'} style="${layout.style};${paintedPropStyle(sprite)}" title="${esc(t.name||title(t.kind))}${placed?' · click to remove and refund':''}">${t.hp?`<span class="terrain-hp">${t.hp}/${t.max_hp}</span>`:''}</button>`}).join('');
  const units=Object.values(b.units).map(u=>battleToken(u,false,b)).join('');
  const party=Object.values(b.units).filter(u=>u.team==='player'&&!u.defense_objective);
  const options=(prep.available||[]).map(option=>{const used=(prep.placements||[]).filter(row=>row.type===option.id).length,disabled=prep.remaining<option.cost||used>=option.limit;return `<button class="prep-option ${selectedPreparation.mode==='defense'&&selectedPreparation.id===option.id?'active':''}" data-prep-defense="${esc(option.id)}" ${disabled?'disabled':''} title="${esc(option.description)}"><b>${esc(option.name)}</b><span>${option.cost} points · ${used}/${option.limit}</span><small>${esc(option.description)}</small></button>`}).join('');
  const deployButtons=party.map(unit=>`<button class="prep-unit ${selectedPreparation.mode==='deploy'&&selectedPreparation.id===unit.id?'active':''}" data-prep-unit="${unit.id}"><b>${esc(unit.name)}</b><span>Position ${unit.x+1},${unit.y+1}</span></button>`).join('');
  const bonus=[];if(prep.race_bonus)bonus.push(`+${prep.race_bonus} race`);if(prep.gear_bonus)bonus.push(`+${prep.gear_bonus} equipment`);
  $('#mission-detail').innerHTML=`<div class="battle-header preparation-header"><div><div class="eyebrow">DEFENSE PREPARATION</div><h2>${esc(b.name)}</h2><p>Choose a defense, then click a blue tile. Choose a character, then click a gold deployment tile. Placed defenses can be removed for a full refund until battle begins.</p></div><div class="prep-budget"><b>${prep.remaining}</b><span>of ${prep.budget} points left</span><small>${prep.base_budget} base${bonus.length?` · ${bonus.join(' · ')}`:''}</small></div></div><div class="battle-layout"><div class="battle-viewport" id="battle-viewport"><div class="battlefield preparing terrain-style-custom-painted theme-${b.theme||'wilds'}" style="--battle-w:${b.width};--battle-h:${b.height};--battle-scale-width:${battleZoom*100}%;--battle-scale-min:${Math.round(b.width*72*battleZoom)}px">${cells}${elevations}${decorations}${terrain}${units}</div></div><aside class="battle-sidebar prep-sidebar"><div class="battle-camera"><b>Map view</b><button data-battle-zoom="out">−</button><button data-battle-zoom="reset">${Math.round(battleZoom*100)}%</button><button data-battle-zoom="in">+</button></div><section><h3>Field defenses</h3><div class="prep-options">${options}</div></section><section><h3>Deploy party</h3><div class="prep-units">${deployButtons}</div></section><button id="start-defense" class="primary big">Start Defense</button><div class="prep-legend"><span><i class="prep-swatch"></i>Defense zone</span><span><i class="deploy-swatch"></i>Deployment zone</span></div><div class="battle-log">${(b.log||[]).slice().reverse().map(line=>`<p>${esc(line)}</p>`).join('')}</div></aside></div>`;
  $$('[data-prep-defense]').forEach(button=>button.onclick=()=>{selectedPreparation={mode:'defense',id:button.dataset.prepDefense};renderBattlePreparation(b)});
  $$('[data-prep-unit]').forEach(button=>button.onclick=()=>{selectedPreparation={mode:'deploy',id:button.dataset.prepUnit};renderBattlePreparation(b)});
  $$('[data-battle-unit]').forEach(token=>{const unit=b.units[token.dataset.battleUnit];if(unit?.team==='player'&&!unit.defense_objective)token.onclick=e=>{e.stopPropagation();selectedPreparation={mode:'deploy',id:unit.id};renderBattlePreparation(b)}});
  $$('[data-battle-cell]').forEach(cell=>cell.onclick=()=>{if(combatRequestPending)return;const [x,y]=cell.dataset.battleCell.split(',').map(Number),key=`${x},${y}`;if(selectedPreparation.mode==='defense'&&selectedPreparation.id&&prepZone.has(key))sendCombat({action:'place_defense',placement_id:selectedPreparation.id,x,y});else if(selectedPreparation.mode==='deploy'&&selectedPreparation.id&&deploymentZone.has(key)){const optimistic=structuredClone(b),unit=optimistic.units[selectedPreparation.id];if(unit){unit.x=x;unit.y=y;renderBattlePreparation(optimistic)}sendCombat({action:'deploy_unit',target_id:selectedPreparation.id,x,y})}});
  $$('[data-prep-remove]').forEach(button=>button.onclick=e=>{e.stopPropagation();sendCombat({action:'remove_defense',target_id:button.dataset.prepRemove})});
  $('#start-defense').onclick=()=>sendCombat({action:'start_battle'});
  $$('[data-battle-zoom]').forEach(button=>button.onclick=()=>{battleZoom=button.dataset.battleZoom==='reset'?DEFAULT_BATTLE_ZOOM:Math.max(.5,Math.min(1.75,battleZoom+(button.dataset.battleZoom==='in'?.25:-.25)));renderBattlePreparation(b)});
  requestAnimationFrame(()=>animateBattleMovement(previousBattle,b,140));
}
function renderBattle(b){
  if(b.status==='preparing'){renderBattlePreparation(b);return}
  const previousBattle=activeBattleView;
  const previousViewport=$('#battle-viewport');
  if(previousViewport)battlePan={left:previousViewport.scrollLeft,top:previousViewport.scrollTop};
  activeBattleView=b;
  const current=b.units[b.current_unit_id];
  if(['interact','carry'].includes(selectedCombatAction))selectedCombatAction='move';
  if(current&&!current.special&&selectedCombatAction==='skill')selectedCombatAction='move';
  if(!b.throw_profile&&selectedCombatAction==='throw')selectedCombatAction='move';
  const reachable=new Set((b.reachable||[]).map(p=>`${p.x},${p.y}`));
  const contextActions=b.context_actions||[],terrainTargets=new Set(b.terrain_targets||[]);
  const throwTargets=new Set(b.throw_profile?.target_ids||[]);
  if(!contextActions.length)contextMenuOpen=false;
  const pathSteps=new Map((b.movement_path||[]).map((p,index)=>[`${p.x},${p.y}`,p.cost??index+1])),origin=b.movement_origin?`${b.movement_origin.x},${b.movement_origin.y}`:'',extraction=new Set((b.extraction?.tiles||[]).map(p=>`${p.x},${p.y}`)),enemyExtraction=new Set((b.enemy_extraction?.tiles||[]).map(p=>`${p.x},${p.y}`)),voidTiles=new Set((b.void_tiles||[]).map(p=>`${p.x},${p.y}`));
  const ground=new Map((b.ground_tiles||[]).map(tile=>[`${tile.x},${tile.y}`,tile.material])),groundMaterials=b.ground_materials||{};
  const tileActions=tileActionMenu?tileActionsForBattle(b,tileActionMenu.x,tileActionMenu.y):[];
  if(tileActionMenu&&!tileActions.length)tileActionMenu=null;
  const materialAt=(x,y)=>ground.get(`${x},${y}`)||'grass';
  let cells='';for(let y=0;y<b.height;y++)for(let x=0;x<b.width;x++){const key=`${x},${y}`,step=pathSteps.get(key),exit=extraction.has(key),enemyExit=enemyExtraction.has(key),holdingExit=exit&&current?.x===x&&current?.y===y&&!current?.exit_ready,voidTile=voidTiles.has(key),flyableVoid=voidTile&&reachable.has(key),material=materialAt(x,y),materialInfo=groundMaterials[material]||{name:title(material),movement_cost:1,description:''},edges=[['n',x,y-1],['e',x+1,y],['s',x,y+1],['w',x-1,y]].filter(([,nx,ny])=>nx<0||ny<0||nx>=b.width||ny>=b.height||materialAt(nx,ny)!==material).map(([side])=>`edge-${side}`).join(' '),variant=terrainVariant(b.map_id,material,x,y);const contextualTitle=voidTile?(flyableVoid?'Fly across void':'Impassable void'):(exit||enemyExit)?`Exit · ${holdingExit?'hold until next activation':esc(exit?b.extraction.name:b.enemy_extraction.name)}`:reachable.has(key)?'Move here':'';cells+=`<button class="battle-cell ground-${material} tile-variant-${variant} ${edges} ${voidTile?'void-tile':''} ${reachable.has(key)?'reachable':''} ${step?'movement-path':''} ${key===origin?'movement-origin':''} ${exit?'extraction-tile':''} ${enemyExit?'enemy-extraction-tile':''}" data-battle-cell="${x},${y}" style="grid-column:${x+1};grid-row:${y+1};--gx:${x};--gy:${y}" title="${esc(materialInfo.name)} · ${materialInfo.movement_cost||1} movement${materialInfo.description?` · ${esc(materialInfo.description)}`:''}${contextualTitle?` · ${contextualTitle}`:''}" ${voidTile&&!flyableVoid?'disabled':''}>${voidTile?`<span class="void-marker">${flyableVoid?'FLY':'VOID'}</span>`:step?`<span>${step}</span>`:(exit||enemyExit&&b.battle_won)?`<span class="exit-marker">${holdingExit?'HOLD':'EXIT'}</span>`:''}</button>`}
  const elevations=(b.elevation||[]).map(tile=>`<div class="battle-elevation ${tile.impassable?'impassable':''}" style="grid-column:${tile.x+1};grid-row:${tile.y+1};--height:${tile.height}" title="${title(tile.kind||'elevation')} · height ${tile.height}${tile.impassable?' · impassable':''}"><span>▲${tile.height}</span></div>`).join('');
  const decorations=(b.decorations||[]).map(item=>{const layout=mapAssetLayout(item);return `<div class="battle-decoration has-prop-art ${layout.className}" style="${layout.style};${paintedPropStyle(item.sprite)}" title="${esc(item.name||title(item.sprite))}"></div>`}).join('');
  const terrain=(b.terrain||[]).map(t=>{const destructible=t.destructible&&!t.destroyed,target=terrainTargets.has(t.id),details=destructible?` · ${t.hp}/${t.max_hp} HP · Armor ${t.armor||0}${target?' · in attack range':''}`:t.kind==='shallow_water'?' · costs 2 movement · extinguishes Burn':t.kind==='pit'?' · impassable without flight':t.destroyed?` · spent or destroyed · costs ${t.destroyed_movement_cost||1} movement`:'',originalKind=t.original_kind||t.kind,sprite=t.destroyed?(t.destroyed_sprite||(originalKind==='palisade'?'structure:palisade_breached':'structure:wall_rubble')):(t.sprite||paintedTerrainSpriteByKind[t.kind]),layout=mapAssetLayout(t);return `<div class="battle-terrain ${t.kind} ${sprite?'has-prop-art':''} ${layout.className} ${['palisade','watchtower','wagon','tent','barricade','platform'].includes(originalKind)?'prop-structure':''} ${destructible?'destructible':''} ${t.destroyed?'destroyed':''} ${target?'attack-target':''}" ${destructible?`data-battle-terrain="${esc(t.id)}"`:''} style="${layout.style};${paintedPropStyle(sprite)}" title="${esc(t.name||title(t.kind))}${details}">${destructible?`<span class="terrain-hp">${t.hp}/${t.max_hp}</span>`:t.kind==='pit'?'<span class="terrain-mark">↧</span>':''}</div>`}).join('');
  const objects=Object.values(b.objects||{}).map(o=>{const sprite=paintedObjectSprite(o),layout=mapAssetLayout(o);return `<button class="battle-object ${o.state} ${o.portable?'portable':''} ${sprite?'has-prop-art':''} ${layout.className} ${sprite.startsWith('structure:')?'prop-structure':''}" data-battle-object="${o.id}" style="${layout.style};${paintedPropStyle(sprite)}" title="${esc(o.name)} · ${title(o.state)}${o.portable?` · weight ${o.weight}`:''}"><span>${o.icon||(o.id==='alarm_horn'?'📯':'🔒')}</span></button>`}).join('');
  const units=Object.values(b.units).map(u=>battleToken(u,u.id===b.current_unit_id,b)).join('');
  const bodyMarkers=Object.values(b.units||{}).filter(body=>body.conscious===false&&!body.extracted&&!body.carried_by&&Object.values(b.units||{}).some(unit=>unit.id!==body.id&&unit.x===body.x&&unit.y===body.y&&unit.alive&&unit.conscious!==false&&!unit.extracted&&!unit.carried_by)).map(body=>`<div class="stacked-body-marker ${body.condition==='dead'?'dead':'unconscious'}" style="grid-column:${body.x+1};grid-row:${body.y+1}" title="${esc(body.name)} · ${title(body.condition||'unconscious')}">${body.condition==='dead'?'† CORPSE':'ZZZ · UNCONSCIOUS'}</div>`).join('');
  const tileMenu=tileActionMenu?`<div class="tile-action-menu ${tileActionMenu.x>=b.width/2?'opens-left':''} ${tileActionMenu.y>=b.height/2?'opens-up':''}" style="left:${(tileActionMenu.x+.55)/b.width*100}%;top:${(tileActionMenu.y+.52)/b.height*100}%"><b>Tile ${tileActionMenu.x+1},${tileActionMenu.y+1}</b>${tileActions.map((action,index)=>`<button data-tile-action="${index}"><i>${action.icon}</i><span><strong>${esc(action.label)}</strong><small>${esc(action.detail)}</small></span></button>`).join('')}</div>`:'';
  const order=[...b.turn_order.slice(b.turn_index),...b.turn_order.slice(0,b.turn_index)].map(id=>b.units[id]).filter(u=>u?.alive&&u.conscious!==false&&!u.extracted&&!u.carried_by).slice(0,10);
  const turnOrder=order.map((u,index)=>`<div class="turn-chip ${u.id===b.current_unit_id?'current':''} ${u.team} ${u.boss||u.kind==='chieftain'?'boss':''}" title="${esc(u.name)}"><span>${u.boss||u.kind==='chieftain'?'♛ ':''}${index+1}</span>${u.portrait?`<img src="${esc(portraitSrc(u.portrait))}" alt="">`:`<b>${initials(u.name)}</b>`}<small>${esc(u.name)}</small></div>`).join('');
  const objectives=(b.objectives||[]).map(o=>`<li class="${o.complete?'complete':''}">${o.complete?'✓':'○'} ${esc(o.name)}${o.required?' · required':' · optional'}</li>`).join('');
  const special=current?.special;
  const throwProfile=b.throw_profile;
  const contextPanel=contextMenuOpen?`<div class="context-action-menu"><div><b>Context Actions</b><small>Available from ${esc(current?.name||'the current position')}</small></div>${contextActions.map((entry,index)=>`<button data-context-action="${index}" title="${esc(entry.description)}"><kbd>${esc(entry.hotkey||'I')}</kbd><span><b>${esc(entry.label)}</b><small>${esc(entry.target)} · ${esc(entry.cost)}</small><em>${esc(entry.description)}</em></span></button>`).join('')}</div>`:'';
  const skillButton=special?`<button data-combat-mode="skill" data-description="${esc(special.description)}" title="${esc(special.description)}" class="${selectedCombatAction==='skill'?'active':''}" ${current?.acted||current?.special_used?'disabled':''}>${combatActionArt('skill')}<span><kbd>S</kbd> ${esc(special.name)}</span></button>`:'';
  const currentActor=current?`<div class="active-unit-card"><div class="active-unit-portrait">${current.portrait?`<img src="${esc(portraitSrc(current.portrait))}" alt="">`:`<span>${initials(current.name)}</span>`}</div><div><small>ACTING NOW</small><b>${esc(current.name)}</b><span>${esc(current.weapon||'Unarmed')}${throwProfile?` · Carrying ${esc(throwProfile.payload_name)}`:''}</span><i><em style="width:${Math.max(0,Math.min(100,current.hp/current.max_hp*100))}%"></em></i><small>${current.hp}/${current.max_hp} HP</small></div></div>`:`<p>${title(b.outcome||b.status)}</p>`;
  const victoryPrompt=b.decision_pending?`<section class="victory-decision"><div><div class="eyebrow">PRIMARY OBJECTIVE SECURED</div><h3>${esc(b.victory_title||'Victory is secured.')}</h3><p>${esc(b.victory_description||'Withdraw now or continue pursuing optional objectives.')}</p></div><div><button data-combat-action="claim_victory" class="claim-victory">${esc(b.claim_victory_label||'Complete Mission')}</button><button data-combat-action="continue_pursuit">Continue for Optional Objectives</button></div></section>`:b.battle_won?`<section class="victory-decision compact"><div><b>Primary objective remains secured.</b><span>${b.battlefield_secured?'No organized enemy resistance remains.':'Optional objectives remain available.'} You may finish whenever you are ready.</span></div><button data-combat-action="claim_victory" class="claim-victory">${esc(b.claim_victory_label||'Complete Mission')}</button></section>`:'';
  const usedMaterials=[...new Set((b.ground_tiles||[]).map(tile=>tile.material))].map(material=>{const info=groundMaterials[material]||{name:title(material),description:''};return `<span title="${esc(info.description||'')}"><i class="ground-swatch ground-${material}"></i>${esc(info.name)}</span>`}).join('');
  const mapLegend=`<div class="battle-map-legend"><b>Terrain</b><div>${usedMaterials}<span title="Higher terrain affects movement and physical accuracy"><i class="legend-height">▲</i>Elevation</span><span title="Guild extraction region"><i class="legend-exit">↙</i>Exit</span></div></div>`;
  const actionHelp={move:`Choose any green tile. Path numbers show cumulative movement cost.${throwProfile?` Carrying ${throwProfile.payload_name} applies a ${current?.carried_payload_penalty||0}-point movement penalty from STR versus weight.`:''} Shallow water and rubble cost 2. Uphill movement costs 2 per level and a single step can climb at most 2 levels.`,attack:'Attack an enemy or destructible wall, gate, palisade, or similar terrain within weapon range. Destroyed obstacles open their tile.',subdue:'Make a reduced-damage adjacent attack intended to knock the target unconscious. Requires an unarmed or blunt-capable weapon.',throw:throwProfile?`Throw ${throwProfile.payload_name} at an enemy. STR ${throwProfile.strength} against weight ${throwProfile.weight} gives range ${throwProfile.range} and ${throwProfile.damage} base impact before armor. The payload lands beside the target.`:'Pick up a portable object or carry an unconscious body before throwing.',skill:`${special?.description||'No combat skill is equipped.'} This commits movement and ends the activation.`,context:'Show actions available from the current tile, including objectives, portable objects, bodies, carried units, and extraction handoff.',carry:'Select an adjacent unconscious unit or corpse. The movement penalty is calculated from the carrier’s STR and the target’s weight.',drop:'Put the carried payload into the first safe adjacent tile.',extract_body:'After holding an EXIT for one activation, hand the carried body or prisoner over for free. The carrier may then leave or continue fighting.',interact:'Use an adjacent objective or pick up a portable battlefield object.',guard:'End this activation in a defensive stance. The next incoming hit deals half damage.',end_turn:'End this activation without attacking or gaining Guard.',leave:`Leave through ${b.extraction?.name||'the exit'}. End one activation on an EXIT tile first; Leave becomes available on that character’s next activation.`,retreat_all:'Order every guild fighter to path toward the nearest exit, hold there for one turn, and then leave automatically. Before securing the required objective this concedes the mission; afterward it preserves the victory.'};
  $('#mission-detail').innerHTML=`<div class="battle-header"><div><div class="eyebrow">TACTICAL BATTLE · ROUND ${b.round}</div><h2>${esc(b.name)}</h2>${currentActor}</div><div class="battle-objectives"><b>Objectives</b><ul>${objectives}</ul></div></div>${victoryPrompt}<div class="turn-order"><b>Turn order</b><div>${turnOrder}</div></div><div class="battle-layout"><div class="battle-viewport" id="battle-viewport"><div class="battlefield terrain-style-custom-painted theme-${b.theme||'wilds'} mode-${selectedCombatAction} ${contextMenuOpen?'context-open':''}" style="--battle-w:${b.width};--battle-h:${b.height};--battle-scale-width:${battleZoom*100}%;--battle-scale-min:${Math.round(b.width*72*battleZoom)}px">${cells}${elevations}${decorations}${terrain}${objects}${units}${bodyMarkers}${tileMenu}</div></div><aside class="battle-sidebar"><div class="battle-camera"><b>Map view</b><button data-battle-zoom="out" title="Zoom out">−</button><button data-battle-zoom="reset" title="Reset zoom">${Math.round(battleZoom*100)}%</button><button data-battle-zoom="in" title="Zoom in">+</button><small>Middle-click to auto-scroll · wheel to scroll</small></div>${mapLegend}<div class="combat-actions ${!current?'combat-locked':''}"><button data-combat-mode="move" data-description="${esc(actionHelp.move)}" title="${esc(actionHelp.move)}" class="${selectedCombatAction==='move'?'active':''}">${combatActionArt('move')}<span><kbd>M</kbd> Move</span></button><button data-combat-mode="attack" data-description="${esc(actionHelp.attack)}" title="${esc(actionHelp.attack)}" class="${selectedCombatAction==='attack'?'active':''}" ${current?.acted?'disabled':''}>${combatActionArt('attack')}<span><kbd>A</kbd> Attack</span></button><button data-combat-mode="subdue" data-description="${esc(actionHelp.subdue)}" title="${esc(actionHelp.subdue)}" class="${selectedCombatAction==='subdue'?'active':''}" ${b.can_subdue?'':'disabled'}>${combatActionArt('subdue')}<span><kbd>N</kbd> Subdue</span></button><button data-combat-mode="throw" data-description="${esc(actionHelp.throw)}" title="${esc(actionHelp.throw)}" class="${selectedCombatAction==='throw'?'active':''}" ${throwProfile&&!current?.acted?'':'disabled'}>${combatActionArt('throw')}<span><kbd>T</kbd> Throw</span></button>${skillButton}<button data-combat-action="guard" data-description="${esc(actionHelp.guard)}" title="${esc(actionHelp.guard)}" ${current?.acted?'disabled':''}>${combatActionArt('guard')}<span><kbd>G</kbd> Guard</span></button><button data-context-toggle data-description="${esc(actionHelp.context)}" title="${esc(actionHelp.context)}" class="${contextMenuOpen?'active':''}" ${contextActions.length?'':'disabled'}>${combatActionArt('interact')}<span><kbd>I</kbd> Actions <span class="action-count">${contextActions.length}</span></span></button><button data-combat-action="end_turn" data-description="${esc(actionHelp.end_turn)}" title="${esc(actionHelp.end_turn)}"><span><kbd>Space</kbd> End Turn</span></button><button data-combat-action="leave" data-description="${esc(actionHelp.leave)}" title="${esc(actionHelp.leave)}" class="leave-map" ${b.can_extract?'':'disabled'}>${combatActionArt('exit')}<span>Leave Map</span></button><button data-combat-action="retreat_all" data-description="${esc(actionHelp.retreat_all)}" title="${esc(actionHelp.retreat_all)}" class="retreat-all ${retreatAllArmed?'armed':''}">${combatActionArt('exit')}<span><kbd>R</kbd> ${retreatAllArmed?'Confirm Retreat All':'Retreat All'}</span></button></div><small class="combat-hotkey-note">Keyboard: M Move · A Attack · N Subdue · T Throw · S Skill · I Actions · G Guard · Space End Turn</small>${contextPanel}<div id="combat-action-help" class="combat-action-help">${esc(actionHelp[selectedCombatAction]||actionHelp.move)}</div><div class="auto-controls"><select id="battle-tactic"><option value="balanced">Balanced</option><option value="objective">Seek Objectives</option><option value="defensive">Defensive</option></select><button id="auto-step">Auto One Turn</button><button id="auto-resolve">Auto Resolve Battle</button></div><div class="battle-log">${(b.log||[]).slice().reverse().map(line=>`<p>${esc(line)}</p>`).join('')}</div></aside></div>`;
  $$('[data-combat-mode]').forEach(btn=>btn.onclick=()=>{retreatAllArmed=false;contextMenuOpen=false;tileActionMenu=null;selectedCombatAction=btn.dataset.combatMode;renderBattle(b)});
  $$('[data-battle-zoom]').forEach(button=>button.onclick=()=>{battleZoom=button.dataset.battleZoom==='reset'?DEFAULT_BATTLE_ZOOM:Math.max(.5,Math.min(1.75,battleZoom+(button.dataset.battleZoom==='in'?.25:-.25)));renderBattle(b)});
  const viewport=$('#battle-viewport');
  if(viewport){viewport.scrollLeft=battlePan.left;viewport.scrollTop=battlePan.top;viewport.addEventListener('scroll',()=>{battlePan={left:viewport.scrollLeft,top:viewport.scrollTop}},{passive:true})}
  $('[data-context-toggle]')?.addEventListener('click',()=>{retreatAllArmed=false;contextMenuOpen=!contextMenuOpen;renderBattle(b)});
  $$('[data-context-action]').forEach(btn=>btn.onclick=()=>{const entry=contextActions[Number(btn.dataset.contextAction)];if(!entry)return;contextMenuOpen=false;retreatAllArmed=false;sendCombat(entry.command)});
  $$('[data-tile-action]').forEach(button=>button.onclick=e=>{e.stopPropagation();const entry=tileActions[Number(button.dataset.tileAction)];if(!entry)return;tileActionMenu=null;sendCombat(entry.command,entry.nextMode)});
  $$('.combat-actions button').forEach(btn=>{btn.onmouseenter=()=>{$('#combat-action-help').textContent=btn.dataset.description||''};btn.onmouseleave=()=>{$('#combat-action-help').textContent=retreatAllArmed?'Warning: Retreat All automatically withdraws the entire party and cannot be cancelled once confirmed.':actionHelp[selectedCombatAction]||actionHelp.move}});
  $$('[data-combat-action]').forEach(btn=>btn.onclick=()=>{const action=btn.dataset.combatAction;if(action==='retreat_all'){if(!retreatAllArmed){retreatAllArmed=true;contextMenuOpen=false;renderBattle(b);$('#combat-action-help').textContent='Warning: Retreat All automatically withdraws the entire party and cannot be cancelled once confirmed. Click again or press R again to confirm.';return}retreatAllArmed=false}else{retreatAllArmed=false;contextMenuOpen=false}sendCombat({action})});
  $$('[data-battle-cell]').forEach(cell=>cell.onclick=()=>{const [x,y]=cell.dataset.battleCell.split(',').map(Number),actions=tileActionsForBattle(b,x,y),ambiguous=actions.length>1||Object.values(b.units||{}).some(unit=>unit.x===x&&unit.y===y&&unit.conscious===false&&!unit.extracted&&!unit.carried_by);retreatAllArmed=false;contextMenuOpen=false;if(ambiguous){tileActionMenu={x,y};renderBattle(b);return}tileActionMenu=null;if(actions.length===1){sendCombat(actions[0].command,actions[0].nextMode);return}renderBattle(b)});
  $$('[data-battle-unit]').forEach(token=>token.onclick=e=>{e.stopPropagation();const target=b.units[token.dataset.battleUnit];if(target.team==='enemy'&&target.conscious!==false&&['attack','skill','subdue'].includes(selectedCombatAction)&&b.attack_previews?.[target.id]?.[selectedCombatAction]){tileActionMenu=null;retreatAllArmed=false;sendCombat({action:selectedCombatAction,target_id:target.id});return}if(target.team==='enemy'&&target.conscious!==false&&selectedCombatAction==='throw'&&throwTargets.has(target.id)){tileActionMenu=null;retreatAllArmed=false;sendCombat({action:'throw',target_id:target.id});return}const actions=tileActionsForBattle(b,target.x,target.y);if(actions.length){contextMenuOpen=false;tileActionMenu={x:target.x,y:target.y};renderBattle(b);return}tileActionMenu=null;if(contextMenuOpen){const entry=contextActions.find(item=>item.command?.target_id===target.id);if(entry){contextMenuOpen=false;sendCombat(entry.command)}}});
  $$('[data-battle-object]').forEach(object=>object.onclick=e=>{e.stopPropagation();const target=b.objects?.[object.dataset.battleObject],tile=target?`${target.x},${target.y}`:'';if(selectedCombatAction==='move'&&target&&!target.blocking&&reachable.has(tile)){tileActionMenu=null;retreatAllArmed=false;sendCombat({action:'move',x:target.x,y:target.y});return}if(contextMenuOpen){const entry=contextActions.find(item=>item.command?.target_id===object.dataset.battleObject);if(entry){contextMenuOpen=false;tileActionMenu=null;retreatAllArmed=false;sendCombat(entry.command);return}}const actions=target?tileActionsForBattle(b,target.x,target.y):[];tileActionMenu=actions.length?{x:target.x,y:target.y}:null;renderBattle(b)});
  $$('[data-battle-terrain]').forEach(tile=>tile.onclick=e=>{e.stopPropagation();if(selectedCombatAction==='attack'&&terrainTargets.has(tile.dataset.battleTerrain)){contextMenuOpen=false;tileActionMenu=null;retreatAllArmed=false;sendCombat({action:'attack',target_id:tile.dataset.battleTerrain});return}const target=b.terrain?.find(entry=>entry.id===tile.dataset.battleTerrain),actions=target?tileActionsForBattle(b,target.x,target.y):[];tileActionMenu=actions.length?{x:target.x,y:target.y}:null;renderBattle(b)});
  $('#auto-step').onclick=()=>{retreatAllArmed=false;sendCombatAuto(false)};$('#auto-resolve').onclick=()=>{retreatAllArmed=false;sendCombatAuto(true)};
  requestAnimationFrame(()=>animateBattleMovement(previousBattle,b));
}
document.addEventListener('keydown',event=>{
  const tag=event.target?.tagName?.toLowerCase();
  if(event.repeat||event.ctrlKey||event.metaKey||event.altKey||['input','textarea','select'].includes(tag)||event.target?.isContentEditable)return;
  if(!activeBattleView||!$('.battlefield')||$('#mission-modal')?.classList.contains('hidden'))return;
  const key=event.code==='Space'?'space':event.key.toLowerCase();
  if(key==='escape'&&retreatAllArmed){event.preventDefault();retreatAllArmed=false;renderBattle(activeBattleView);return}
  if(!activeBattleView.current_unit_id&&key!=='r')return;
  if(['c','d','p','x'].includes(key)){
    const contextual=$$('[data-context-action]').find(button=>(activeBattleView.context_actions?.[Number(button.dataset.contextAction)]?.hotkey||'').toLowerCase()===key);
    if(contextual){event.preventDefault();contextual.click()}else if(activeBattleView.context_actions?.some(entry=>(entry.hotkey||'').toLowerCase()===key)){contextMenuOpen=true;renderBattle(activeBattleView)}
    return;
  }
  const hotkeys={m:'[data-combat-mode="move"]',a:'[data-combat-mode="attack"]',n:'[data-combat-mode="subdue"]',t:'[data-combat-mode="throw"]',s:'[data-combat-mode="skill"]',i:'[data-context-toggle]',g:'[data-combat-action="guard"]',space:'[data-combat-action="end_turn"]',r:'[data-combat-action="retreat_all"]'};
  const button=hotkeys[key]?$(hotkeys[key]):null;
  if(!button||button.disabled)return;
  event.preventDefault();button.click();
});
async function sendCombat(command,nextMode=null){
  if(combatRequestPending)return;
  combatRequestPending=true;
  try{
    const data=await rawApi(`/api/missions/${activeBattleMissionId}/battle/command`,{method:'POST',body:JSON.stringify(command)});
    tileActionMenu=null;
    if(nextMode)selectedCombatAction=nextMode;
    if(data.result){const local=activeMissions.find(m=>m.id===activeBattleMissionId);if(local){local.status='completed';local.result=data.result}const soundDuration=playBattleSounds(data.battle);activeBattleView=null;retreatAllArmed=false;playOutcomeSound(data.result.outcome,soundDuration);showResult(data.result);await refreshDynamic();return}
    const optimisticDeployment=command.action==='deploy_unit'&&activeBattleView?.status==='preparing'&&activeBattleView.units?.[command.target_id]?.x===command.x&&activeBattleView.units?.[command.target_id]?.y===command.y;
    if(optimisticDeployment){
      activeBattleView=data.battle;
      const log=$('.battle-log');if(log)log.innerHTML=(data.battle.log||[]).slice().reverse().map(line=>`<p>${esc(line)}</p>`).join('');
      return;
    }
    renderBattle(data.battle);
  }catch(e){
    toast(e.message);
    if(activeBattleMissionId)try{const fresh=await rawApi(`/api/missions/${activeBattleMissionId}/battle`);renderBattle(fresh.battle)}catch{}
  }finally{combatRequestPending=false}
}
async function sendCombatAuto(resolveAll){if(combatRequestPending)return;combatRequestPending=true;try{const tactic=$('#battle-tactic')?.value||'balanced',data=await rawApi(`/api/missions/${activeBattleMissionId}/battle/auto`,{method:'POST',body:JSON.stringify({tactic,resolve_all:resolveAll})});tileActionMenu=null;if(data.result){const local=activeMissions.find(m=>m.id===activeBattleMissionId);if(local){local.status='completed';local.result=data.result}const soundDuration=resolveAll?0:playBattleSounds(data.battle);activeBattleView=null;retreatAllArmed=false;playOutcomeSound(data.result.outcome,soundDuration);showResult(data.result);await refreshDynamic()}else renderBattle(data.battle)}catch(e){toast(e.message)}finally{combatRequestPending=false}}
$('#mission-close').onclick=()=>{retreatAllArmed=false;tileActionMenu=null;activeBattleView=null;$('#mission-modal').classList.add('hidden')};
$('#sound-settings-open').onclick=()=>{closeAudioSettings?.();closeAudioSettings=mountAudioSettings($('#sound-settings-content'),audioMixer,name=>playSfx(name,name.startsWith('mission_')?.5:name.startsWith('ui_')?.16:.5));$('#sound-settings-modal').showModal()};
$('#sound-settings-close').onclick=()=>$('#sound-settings-modal').close();
$('#sound-settings-modal').addEventListener('close',()=>{closeAudioSettings?.();closeAudioSettings=null});
$('#sound-settings-modal').addEventListener('click',event=>{if(event.target===$('#sound-settings-modal')){const rect=event.target.getBoundingClientRect();if(event.clientX<rect.left||event.clientX>rect.right||event.clientY<rect.top||event.clientY>rect.bottom)event.target.close()}});
function closePortraitViewer(){$('#portrait-lightbox').classList.add('hidden');$('#portrait-lightbox-image').src=''}
document.addEventListener('click',event=>{const portrait=event.target.closest?.('[data-portrait-view]');if(!portrait)return;event.preventDefault();event.stopPropagation();$('#portrait-lightbox-image').src=portrait.dataset.portraitView;$('#portrait-lightbox-image').alt=portrait.dataset.portraitName;$('#portrait-lightbox-name').textContent=portrait.dataset.portraitName;$('#portrait-lightbox').classList.remove('hidden')},true);
$('#portrait-lightbox-close').onclick=closePortraitViewer;$('#portrait-lightbox').onclick=event=>{if(event.target===$('#portrait-lightbox'))closePortraitViewer()};document.addEventListener('keydown',event=>{if(event.key==='Escape')closePortraitViewer()});
function showResult(r){
  if(!r)return;
  missionPlanner=null;analysisSequence++;activeBattleView=null;
  const rw=r.rewards||{},bits=[];
  if(rw.gold)bits.push(`+${rw.gold} Gold`);
  Object.entries(rw.materials||{}).forEach(([k,v])=>bits.push(`+${v} ${title(k)}`));
  (rw.items||[]).forEach(x=>{const item=content.items[x];bits.push(item?`${item.name} · ${title(item.rarity||'common')}${item.granted_perks?.length?` · grants ${item.granted_perks.map(p=>content.standalone_perks?.[p]?.name||title(p)).join(', ')}`:''}`:x)});
  (rw.blueprints||[]).forEach(x=>bits.push(`${content.buildings[x]?.name||x} blueprint`));
  (rw.recruits||[]).forEach(x=>bits.push(`${x.kind==='champion'?'Champion':x.kind==='celestial'?'Unique Celestial':'Recruit'}: ${x.name}${x.race?` · ${x.race}`:''}`));
  (rw.prisoners||[]).forEach(x=>bits.push(`Prisoner secured: ${x.name} · ${x.race} · ${x.holding==='prison_cell'?'Prison Cell':'temporary stockade'}`));
  (rw.perks||[]).forEach(x=>bits.push(x.standalone?`${x.character} gained perk: ${title(x.standalone)}`:`${x.character} gained ${title(x.level)} ${title(x.track)}`));
  (rw.transformations||[]).forEach(x=>bits.push(`${x.character} transformed: ${x.from} → ${x.to}`));
  (rw.world_flags||[]).forEach(x=>bits.push(`World outcome: ${x.name}`));
  (rw.injuries||[]).forEach(x=>bits.push(`${x.name} incapacitated · ${x.location} · ${countdown(x.recovers_at)} recovery`));
  const rolls=(rw.loot_rolls||[]).map(x=>`<div class="loot-roll ${x.item||x.recruit||x.champion?'won':'missed'}"><b>${esc(title(x.source))}</b><span>Rolled ${x.roll}${x.range?`/${x.range}`:''} · needed ${x.chance} or lower${x.item?` · ${esc(content.items[x.item]?.name||x.item)}${x.rarity?` (${title(x.rarity)})`:''}`:x.champion?` · Champion: ${esc(x.champion.name)}`:x.recruit?` · ${esc(x.recruit.race)} recruit: ${esc(x.recruit.name)}`:x.fallback_gold?` · +${x.fallback_gold} Gold`:x.possible_item?` · no ${esc(content.items[x.possible_item]?.name||x.possible_item)} recovered`:' · no reward'}</span></div>`).join('');
  const story=(r.story?.length?r.story:[`The expedition returned from ${r.mission}. The details of this older mission were not recorded in the new narrative format.`]);
  const roles=(r.roles||[]).filter(x=>x.character).map(x=>`<div><b>${esc(x.label)}:</b> ${esc(x.character)} · ${x.metric==='constitution'?'CON':String(x.metric).toUpperCase()} ${x.score}</div>`).join('');
  const primaryTarget=r.battle_report?.primary_target,enemyOutcome=r.battle_report?.enemy_outcome||{},enemyCounts=[enemyOutcome.killed?.length?`${enemyOutcome.killed.length} killed`:'',enemyOutcome.captured?.length?`${enemyOutcome.captured.length} captured`:'',enemyOutcome.subdued_unsecured?.length?`${enemyOutcome.subdued_unsecured.length} subdued but left`:'',enemyOutcome.fled?.length?`${enemyOutcome.fled.length} escaped`:'',enemyOutcome.remaining?.length?`${enemyOutcome.remaining.length} left in the field`:''].filter(Boolean).join(' · ');
  const battleReport=r.battle_report?`<div class="battle-result"><div class="outcome ${r.outcome}">${title(r.outcome)}</div><b>Tactical report</b><span>${r.battle_report.rounds} rounds · ${r.battle_report.actions} player actions${r.battle_report.reinforcements_spawned?' · enemy reinforcements arrived':''}</span>${primaryTarget?`<small><b>Primary target:</b> ${esc(primaryTarget.name)} · ${esc(title(primaryTarget.resolution))}</small>`:''}${enemyCounts?`<small><b>Enemy outcome:</b> ${esc(enemyCounts)}</small>`:''}${r.battle_report.objectives?.length?`<small>${r.battle_report.objectives.map(esc).join(' · ')}</small>`:''}${r.battle_report.battlefield_secured?'<small>✓ Battlefield secured and recoverable bodies gathered automatically</small>':''}${r.battle_report.rescued?.length?`<small>Rescued: ${r.battle_report.rescued.map(esc).join(', ')}</small>`:''}${r.battle_report.captured?.length?`<small>Captured alive: ${r.battle_report.captured.map(esc).join(', ')}</small>`:''}${r.battle_report.recovered_objects?.length?`<small>Recovered: ${r.battle_report.recovered_objects.map(esc).join(', ')}</small>`:''}${r.battle_report.corpse_loot?.length?`<small>Recovered from ${r.battle_report.corpse_loot.length} ${r.battle_report.corpse_loot.length===1?'body':'bodies'}: ${r.battle_report.corpse_loot.map(x=>`${esc(x.name)}${x.gold?` · ${x.gold} gold`:''}${x.item?` · ${esc(content.items[x.item]?.name||x.item)}${x.rarity?` (${title(x.rarity)})`:''}`:''}`).join(' | ')}</small>`:''}${r.battle_report.recap?.length?`<div class="combat-recap"><b>Combat recap</b>${r.battle_report.recap.map(line=>`<small>${esc(line)}</small>`).join('')}</div>`:''}</div>`:'';
  const resolutionRoll=r.battle_report?'':r.scene_history?`<div class="outcome ${r.outcome}">${title(r.outcome)}</div>`:`<div class="result-roll"><div class="d20">${r.die}</div><div><div class="outcome ${r.outcome}">${title(r.outcome)}</div><small>Total ${r.total} vs DC ${r.difficulty}</small></div></div>`;
  const sceneRolls=r.scene_history?`<details class="scene-history"><summary>Decision rolls</summary>${r.scene_history.map(h=>`<p><b>${esc(h.choice)}</b><small>${title(h.outcome)}${h.die?` · ${esc(h.lead||'Party')} · d20 ${h.die} → ${h.total} vs ${h.difficulty}`:' · no roll'}</small></p>`).join('')}</details>`:'';
  $('#mission-modal').classList.remove('hidden');
  $('#mission-detail').innerHTML=`<div class="eyebrow">MISSION AFTERMATH${r.debug_forced?' · DEBUG FORCED':''}</div><h2>${esc(r.mission)}</h2><div class="aftermath-heading"><span class="outcome ${r.outcome}">${title(r.outcome)}</span><small>The choices, consequences, and rewards of this expedition.</small></div><div class="aftermath-layout"><section class="aftermath-story"><div class="mission-story">${story.map(p=>`<p>${esc(p)}</p>`).join('')}</div>${r.special_events?.length?`<div class="special-event"><b>Special event</b><br>${r.special_events.map(esc).join('<br>')}</div>`:''}${r.board_followups?.length?`<div class="world-consequence"><b>New leads</b><br>${r.board_followups.map(x=>esc(x.name)).join('<br>')}</div>`:''}${r.chain_unlocked?.length?`<div class="chain-unlocked"><b>Follow-ups ready in Private Contracts</b><br>${r.chain_unlocked.map(x=>`<button class="private-followup-link" data-open-followup="${esc(x.mission_id)}">${esc(x.name)} → <small>${countdown(x.expires_at)} to claim</small></button>`).join('')}</div>`:''}</section><aside class="aftermath-rewards"><h3>Recovered & earned</h3><div class="reward-list">${bits.length?bits.map(x=>`<div>${esc(x)}</div>`).join(''):'<div>No rewards recovered.</div>'}</div></aside></div><details class="aftermath-details"><summary>Checks & expedition details</summary>${resolutionRoll}${sceneRolls}${roles?`<div class="role-aftermath">${roles}</div>`:''}${battleReport}</details>${rolls?`<details class="aftermath-details"><summary>Loot chances & rolls</summary><div class="loot-rolls">${rolls}</div></details>`:''}`;
  $('#mission-modal .modal-card').scrollTop=0;
  $$('[data-open-followup]').forEach(button=>button.onclick=async()=>{button.disabled=true;await refreshDynamic();const mission=privateContracts.find(m=>m.id===button.dataset.openFollowup);if(mission)openMission(mission);else{toast('This contract is already claimed or has expired');button.disabled=false}});
}

function placementType(){
  if(buildMode)return buildMode;
  if(moveModeBuildingId)return state.buildings.find(b=>b.id===moveModeBuildingId)?.type||null;
  return null;
}
function placementValid(type,x,y,ignoreId=null){
  const d=content.buildings[type];if(!d)return false;
  if(x<0||y<0||x+d.w>content.grid.w||y+d.h>content.grid.h)return false;
  return !state.buildings.some(b=>{if(ignoreId&&b.id===ignoreId)return false;const bd=content.buildings[b.type];return !(x+d.w<=b.x||b.x+bd.w<=x||y+d.h<=b.y||b.y+bd.h<=y)});
}
function updatePlacementGhost(x,y){
  const ghost=$('#placement-ghost'),type=placementType();if(!ghost||!type)return;
  const d=content.buildings[type],ignore=moveModeBuildingId||null,valid=placementValid(type,x,y,ignore);
  ghost.className=`placement-ghost ${valid?'valid':'invalid'}`;ghost.style.gridColumn=`${x+1}/span ${d.w}`;ghost.style.gridRow=`${y+1}/span ${d.h}`;ghost.innerHTML=`<b>${esc(d.name)}</b><small>${d.w} × ${d.h}</small>`;
}
function stopPlacement(){buildMode=null;moveModeBuildingId=null;$('#cancel-build').classList.add('hidden');$('#build-mode-label').textContent='';renderBaseGrid()}
function renderBlueprints(){
  const root=$('#blueprints');
  const placed=new Set(state.buildings.map(b=>b.type)),available=state.learned_blueprints.filter(id=>!placed.has(id));
  if(!available.length){root.innerHTML='<p class="muted small">All learned buildings are already placed.</p>';return}
  root.innerHTML=available.map(id=>{const b=content.buildings[id],cost=Object.entries(b.cost||{}).map(([k,v])=>`${v} ${k}`).join(' · '),aff=Object.entries(b.cost||{}).every(([k,v])=>(state.resources[k]||0)>=v);return `<div class="blueprint"><strong>${esc(b.name)}</strong><small>${esc(b.description)}</small><span><b>${b.w} × ${b.h}</b> footprint · ${cost||'Free'}</span><button data-build="${id}" ${aff?'':'disabled'}>Place ${b.w}×${b.h}</button></div>`}).join('');
  $$('[data-build]').forEach(b=>b.onclick=()=>{buildMode=b.dataset.build;moveModeBuildingId=null;const d=content.buildings[buildMode];$('#build-mode-label').textContent=`placing ${d.name} (${d.w}×${d.h})`;$('#cancel-build').classList.remove('hidden');renderBaseGrid()})
}
function renderSelectedBuilding(){
  const root=$('#selected-building');const b=state.buildings.find(x=>x.id===selectedBuildingId);
  if(!b){root.classList.add('hidden');root.innerHTML='';return}
  const d=content.buildings[b.type],ranks=content.mission_ranks||['E','D','C','B','A','S'],current=state.mission_rank||'E',next=ranks[ranks.indexOf(current)+1],upgrade=next&&content.guild_hall_upgrades?.[next],canUpgrade=upgrade&&Object.entries(upgrade).every(([k,v])=>(state.resources[k]||0)>=v),cost=upgrade?Object.entries(upgrade).map(([k,v])=>`${v} ${k}`).join(' · '):'';
  const tracks=Object.entries(content.perk_tracks||{}).filter(([,definition])=>definition.facility===b.type);
  const idle=state.characters.filter(c=>c.status==='idle');
  const supplies=Object.values(content.perk_training_items||{}).map(id=>`${content.items[id].name} ×${state.inventory.filter(item=>item.item_id===id).length}`).join(' · ');
  const training=tracks.length?`<div class="training-panel"><div class="eyebrow">PERK TRAINING</div>${tracks.map(([track,definition])=>{const currentLevels=idle.map(c=>perkLevel(c,track)),allMaster=idle.length&&currentLevels.every(level=>level==='master');return `<div class="training-row"><b>${esc(definition.name)}</b><select data-trainee="${track}">${idle.map(c=>`<option value="${c.id}">${esc(c.name)} · ${title(perkLevel(c,track))}</option>`).join('')}</select><button data-train="${track}" ${!idle.length||allMaster?'disabled':''}>Train next tier</button></div>`}).join('')}<small>Basic is free. Skilled uses a Training Manual, Expert a Specialist Tome, and Master a Mastery Codex.</small><small>${esc(supplies)}</small></div>`:'';
  const wardenId=(b.assigned||[])[0]||'',warden=state.characters.find(c=>c.id===wardenId);
  const wardenPanel=b.type==='prison_cell'?`<div class="warden-panel"><div class="eyebrow">WARDEN</div><b>${warden?esc(warden.name):'No warden assigned'}</b><small>Warden mechanics will be added later. This assignment reserves the facility worker slot.</small><select id="warden-select"><option value="">— No warden —</option>${idle.map(c=>`<option value="${c.id}" ${c.id===wardenId?'selected':''}>${esc(c.name)}</option>`).join('')}</select><button id="assign-warden">Save Warden</button></div>`:'';
  root.classList.remove('hidden');root.innerHTML=`<div class="eyebrow">SELECTED BUILDING</div><strong>${esc(d.name)}</strong><small>${d.w} × ${d.h} footprint · position ${b.x+1},${b.y+1}</small>${b.type==='guild_hall'?`<div class="guild-rank"><span>Mission visibility</span><b>${current}-Rank</b>${next?`<small>Next: ${next}-Rank · ${cost}</small><button id="upgrade-guild-hall" ${canUpgrade?'':'disabled'}>Unlock ${next}-Rank Missions</button>`:'<small>Maximum rank reached</small>'}</div>`:''}${wardenPanel}${training}<button id="move-building">Move</button>`;
  $('#move-building').onclick=()=>{moveModeBuildingId=b.id;buildMode=null;$('#build-mode-label').textContent=`moving ${d.name} (${d.w}×${d.h})`;$('#cancel-build').classList.remove('hidden');renderBaseGrid()};
  if($('#upgrade-guild-hall'))$('#upgrade-guild-hall').onclick=async()=>{try{const data=await rawApi('/api/guild-hall/upgrade',{method:'POST',body:'{}'});state=data.state;toast(`${data.rank}-Rank missions unlocked`);renderResources();renderBase();await refreshDynamic()}catch(e){toast(e.message)}};
  if($('#assign-warden'))$('#assign-warden').onclick=async()=>{const selected=$('#warden-select').value;try{if(wardenId&&wardenId!==selected){const removed=await rawApi('/api/assign',{method:'POST',body:JSON.stringify({character_id:wardenId,building_id:null})});state=removed.state}if(selected){const assigned=await rawApi('/api/assign',{method:'POST',body:JSON.stringify({character_id:selected,building_id:b.id})});state=assigned.state}toast(selected?'Warden assigned':'Warden removed');renderBase();renderRoster()}catch(e){toast(e.message)}};
  $$('[data-train]').forEach(button=>button.onclick=async()=>{const track=button.dataset.train,charId=$(`[data-trainee="${track}"]`).value;try{const data=await rawApi('/api/train-perk',{method:'POST',body:JSON.stringify({character_id:charId,track})});state=data.state;toast(`${title(data.training.level)} ${content.perk_tracks[track].name} trained`);renderBase();renderRoster();renderMissions()}catch(e){toast(e.message)}});
}
function renderBase(){if(!state||!content)return;renderBlueprints();renderSelectedBuilding();const idle=state.characters.filter(c=>!c.assignment&&c.status==='idle');$('#idle-zone').innerHTML=idle.length?idle.map(c=>portraitHTML(c)).join(''):'<span class="muted small">No idle unassigned characters.</span>';renderBaseGrid();bindDrag()}
function renderBaseGrid(){
  const grid=$('#base-grid');if(!grid||!state)return;const placing=!!placementType();let html='';
  for(let y=0;y<content.grid.h;y++)for(let x=0;x<content.grid.w;x++)html+=`<div class="grid-cell ${placing?'build-target':''}" data-x="${x}" data-y="${y}" style="grid-column:${x+1};grid-row:${y+1}"></div>`;
  html+=state.buildings.map(b=>{const d=content.buildings[b.type],chars=(b.assigned||[]).map(id=>state.characters.find(c=>c.id===id)).filter(Boolean);return `<div class="building ${b.type} ${b.id===selectedBuildingId?'selected':''}" data-building="${b.id}" style="grid-column:${b.x+1}/span ${d.w};grid-row:${b.y+1}/span ${d.h}"><b>${esc(d.name)}</b><small>${d.w}×${d.h} · ${d.workers?`${chars.length}/${d.workers} assigned`:d.beds?`${d.beds} beds`:'Facility'}</small><div class="assigned">${chars.map(c=>portraitHTML(c,true)).join('')}</div></div>`}).join('');
  if(placing)html+='<div id="placement-ghost" class="placement-ghost hidden"></div>';grid.innerHTML=html;
  $$('.grid-cell').forEach(cell=>{
    cell.onmouseenter=()=>{if(placementType())updatePlacementGhost(Number(cell.dataset.x),Number(cell.dataset.y))};
    cell.onclick=async()=>{const type=placementType();if(!type){selectedBuildingId=null;renderSelectedBuilding();renderBaseGrid();return}const x=Number(cell.dataset.x),y=Number(cell.dataset.y);if(!placementValid(type,x,y,moveModeBuildingId||null))return toast('That footprint does not fit there');try{let d;if(moveModeBuildingId)d=await rawApi('/api/move-building',{method:'POST',body:JSON.stringify({building_id:moveModeBuildingId,x,y})});else d=await rawApi('/api/build',{method:'POST',body:JSON.stringify({blueprint_id:buildMode,x,y})});state=d.state;selectedBuildingId=d.building?.id||selectedBuildingId;stopPlacement();renderBase();renderResources();if(d.building?.type==='guild_hall')await refreshDynamic()}catch(e){toast(e.message)}};
  });
  $$('.building').forEach(el=>{
    el.onclick=e=>{if(e.target.closest('.portrait'))return;if(placementType())return;selectedBuildingId=el.dataset.building;renderBase()};
    el.ondragover=e=>e.preventDefault();
    el.ondrop=async e=>{e.preventDefault();const id=e.dataTransfer.getData('text/character');if(!id)return;try{const d=await rawApi('/api/assign',{method:'POST',body:JSON.stringify({character_id:id,building_id:el.dataset.building})});state=d.state;renderBase();renderRoster()}catch(err){toast(err.message)}}
  });bindDrag();
}
function bindDrag(){$$('[data-char][draggable="true"]').forEach(el=>el.ondragstart=e=>e.dataTransfer.setData('text/character',el.dataset.char))}
$('#idle-zone').ondragover=e=>e.preventDefault();$('#idle-zone').ondrop=async e=>{e.preventDefault();const id=e.dataTransfer.getData('text/character');if(!id)return;try{const d=await rawApi('/api/assign',{method:'POST',body:JSON.stringify({character_id:id,building_id:null})});state=d.state;renderBase();renderRoster()}catch(err){toast(err.message)}};
$('#cancel-build').onclick=()=>stopPlacement();
document.addEventListener('click',event=>{
  if(!selectedBuildingId||placementType()||event.target.closest('.building')||event.target.closest('#selected-building'))return;
  selectedBuildingId=null;renderSelectedBuilding();renderBaseGrid();
});

function itemByInstance(id){const inst=state.inventory.find(i=>i.instance_id===id);return inst?content.items[inst.item_id]:null}
function equippedPerks(c){const found=new Map();(c.traits||[]).forEach(p=>found.set(p,null));Object.values(c.equipment||{}).forEach(id=>{const item=itemByInstance(id);(item?.granted_perks||[]).forEach(p=>{if(!found.has(p))found.set(p,item.name)})});return [...found.entries()]}
function itemEffectText(item){const parts=[];Object.entries(item.bonuses||{}).forEach(([k,v])=>parts.push(`+${v} ${title(k)}`));Object.entries(item.attribute_bonuses||{}).forEach(([k,v])=>parts.push(`+${v} ${k.toUpperCase()}`));if(item.power)parts.push(`${item.power} power`);if(item.granted_perks?.length)parts.push(`Grants ${item.granted_perks.map(p=>content.standalone_perks?.[p]?.name||title(p)).join(', ')}`);return parts.join(' · ')||item.description||'No direct stat effect'}
function effectiveStat(c,stat){const track=stat==='cooking'?'alchemy':stat,d=content.perk_tracks?.[track]||content.perk_tracks?.survival,attrs=(d?.attributes||['vit','agi']).map(a=>c.attributes?.[a]??5);let n=Math.floor(attrs.reduce((a,b)=>a+b,0)/attrs.length)+perkRank(c,track);Object.values(c.equipment||{}).forEach(id=>{const item=itemByInstance(id);if(item)n+=item.bonuses?.[stat]||item.bonuses?.[track]||0});return n+(perkModifiers(c,Object.values(c.equipment||{}).map(itemByInstance),content.standalone_perks,'capabilities')[track]||0)}
function renderRoster(){
  if(!state)return;
  rosterNeedsRefresh=false;
  if(!selectedCharacterId||!state.characters.some(c=>c.id===selectedCharacterId))selectedCharacterId=state.characters[0]?.id;
  const catalog=Object.entries(content.champions||{}),ownedChampionIds=new Set(state.characters.filter(c=>c.source_kind==='champion').map(c=>c.source_id));
  const celestialCatalog=Object.entries(content.celestials||{}),ownedCelestialIds=new Set(state.characters.filter(c=>c.source_kind==='celestial').map(c=>String(c.source_id||'').replace('celestial:','')));
  const prisoners=state.prisoners||[];
  const prisonCapacity=state.buildings.filter(b=>b.type==='prison_cell').reduce((sum,b)=>sum+(content.buildings[b.type]?.cells||0),0),securedPrisoners=prisoners.filter(p=>p.holding==='prison_cell'),stockadePrisoners=prisoners.filter(p=>p.holding==='temporary_stockade'),prisonFull=securedPrisoners.length>=prisonCapacity;
  const collection=`<details class="champion-collection" data-roster-collection="champions" ${rosterCollectionOpen.champions?'open':''}><summary><b>Champion Collection</b><span>${ownedChampionIds.size} / ${catalog.length}</span></summary><div class="champion-catalog">${catalog.sort((a,b)=>(content.mission_ranks||[]).indexOf(b[1].rank)-(content.mission_ranks||[]).indexOf(a[1].rank)||a[1].name.localeCompare(b[1].name)).map(([id,d])=>`<div class="champion-entry ${ownedChampionIds.has(id)?'owned':'locked'}"><b>${ownedChampionIds.has(id)?'◆':'◇'} ${esc(d.name)}</b><span>${esc(d.series)}</span><small>${esc(d.rank)}-Rank · ${esc(d.specialty)}</small></div>`).join('')}</div></details>`;
  const celestialCollection=`<details class="champion-collection celestial-collection" data-roster-collection="celestials" ${rosterCollectionOpen.celestials?'open':''}><summary><b>Limited Celestials</b><span>${ownedCelestialIds.size} / ${celestialCatalog.length}</span></summary><div class="champion-catalog">${celestialCatalog.map(([id,d])=>`<div class="champion-entry ${ownedCelestialIds.has(id)?'owned':'locked'}"><b>${ownedCelestialIds.has(id)?'✦':'◇'} ${esc(d.name)}</b><span>${esc(d.pantheon)} Pantheon</span><small>Unique · ${esc(d.specialty)}</small></div>`).join('')}</div></details>`;
  const prisonerCollection=`<details class="champion-collection prisoner-collection" data-roster-collection="prisoners" ${rosterCollectionOpen.prisoners?'open':''}><summary><b>Prisoners</b><span>${securedPrisoners.length}/${prisonCapacity} cells · ${stockadePrisoners.length} stockade</span></summary><div class="prison-summary"><b>${securedPrisoners.length} secured · ${Math.max(0,prisonCapacity-securedPrisoners.length)} open cells</b><small>Each prisoner has one hour of total stockade time. Securing them pauses the remaining time; later swaps resume it.</small></div><div class="champion-catalog">${prisoners.length?prisoners.map(p=>{const inStockade=p.holding==='temporary_stockade',remaining=inStockade?Math.max(0,(p.stockade_expires_at||0)-Math.floor(Date.now()/1000)):(p.stockade_remaining_seconds??3600),swapOptions=securedPrisoners.filter(other=>other.id!==p.id).map(other=>`<option value="${other.id}">${esc(other.name)}</option>`).join('');return `<div class="prisoner-entry ${inStockade?'stockade':''}">${portraitHTML(p,true,true)}<div class="prisoner-info"><b>${esc(p.name)}</b><span>${esc(p.race)} · ${p.boss?'Priority captive':'Prisoner'} · ${p.sale_value??8} gold</span><small>${inStockade?`Temporary stockade · removed in ${fmtDuration(remaining)}`:`Secured in Prison Cell${p.stockade_remaining_seconds!=null?` · ${fmtDuration(remaining)} stockade time saved`:''}`}</small><div class="prisoner-actions">${inStockade&&prisonCapacity?`${prisonFull?`<select data-prisoner-swap="${p.id}">${swapOptions}</select>`:''}<button data-prisoner-action="secure" data-prisoner-id="${p.id}" ${prisonFull&&!swapOptions?'disabled':''}>${prisonFull?'Swap into cell':'Secure'}</button>`:!inStockade?`<button data-prisoner-action="stockade" data-prisoner-id="${p.id}">Move to stockade</button>`:''}<button class="danger" data-prisoner-action="sell" data-prisoner-id="${p.id}">Sell · ${p.sale_value??8}g</button></div></div></div>`}).join(''):'<p class="muted small">Captured mission characters will appear here.</p>'}</div></details>`;
  if(!$('#roster-toolbar')){
    $('#roster-list').insertAdjacentHTML('beforebegin',`<div id="roster-toolbar" class="roster-toolbar"><h2>Your roster <small>${state.characters.length} characters</small></h2><input id="roster-search" type="search" placeholder="Search name, race, series or perk" aria-label="Search roster"><div class="roster-filters"><select data-roster-filter="status" aria-label="Availability"><option value="">All statuses</option><option value="idle">Available</option><option value="incapacitated">Recovering</option><option value="mission">On mission</option></select><select data-roster-filter="race" aria-label="Race"><option value="">All races</option></select><select data-roster-filter="kind" aria-label="Character type"><option value="">All characters</option><option value="generic">Recruits</option><option value="champion">Champions</option><option value="celestial">Celestials</option></select><select data-roster-filter="sort" aria-label="Sort roster"><option value="name">Name A–Z</option><option value="con">Highest CON</option><option value="dps">Highest DPS</option></select></div><div id="roster-page-controls" class="roster-page-controls"></div></div>`);
    $('#roster-search').value=rosterFilters.query;
    $('#roster-search').oninput=e=>{rosterFilters.query=e.target.value;rosterFilters.page=0;$('#roster-list').scrollTop=0;renderRoster()};
    $$('[data-roster-filter]').forEach(el=>el.onchange=()=>{rosterFilters[el.dataset.rosterFilter]=el.value;rosterFilters.page=0;$('#roster-list').scrollTop=0;renderRoster()});
  }
  const raceSelect=$('[data-roster-filter="race"]'),races=[...new Set(state.characters.map(c=>c.race))].sort();
  if(document.activeElement!==raceSelect){raceSelect.innerHTML='<option value="">All races</option>'+races.map(r=>`<option value="${esc(r)}">${esc(r)}</option>`).join('');raceSelect.value=rosterFilters.race}
  $('#roster-toolbar h2 small').textContent=`${state.characters.length} characters`;
  const page=rosterPage(state.characters,rosterFilters,combatMetrics);rosterFilters.page=page.page;
  $('#roster-page-controls').innerHTML=`<span>${page.total} matching · page ${page.page+1}/${page.pages}</span><button data-roster-page="-1" ${page.page===0?'disabled':''} aria-label="Previous page">←</button><button data-roster-page="1" ${page.page+1===page.pages?'disabled':''} aria-label="Next page">→</button>`;
  $$('[data-roster-page]').forEach(el=>el.onclick=()=>{rosterFilters.page+=Number(el.dataset.rosterPage);$('#roster-list').scrollTop=0;renderRoster()});
  if(!$('#roster-collections'))$('.roster-layout').insertAdjacentHTML('afterend','<div id="roster-collections" class="roster-collections"></div>');
  $('#roster-collections').innerHTML=prisonerCollection+celestialCollection+collection;
  $('#roster-list').innerHTML=page.rows.map(c=>`<div class="roster-card ${c.id===selectedCharacterId?'active':''}" data-roster="${c.id}">${portraitHTML(c,true,true)}<div><b>${esc(c.name)}</b><small>${c.source_kind==='champion'?'CHAMPION · ':c.source_kind==='celestial'?'CELESTIAL · ':''}${esc(c.specialty)} · ${esc(characterStatus(c))}</small></div></div>`).join('');
  if(!page.rows.length)$('#roster-list').innerHTML='<p class="muted">No characters match. Change the search or filters.</p>';
  $$('[data-roster-collection]').forEach(details=>details.ontoggle=()=>{rosterCollectionOpen[details.dataset.rosterCollection]=details.open});
  $$('[data-prisoner-action]').forEach(button=>button.onclick=async event=>{event.stopPropagation();const action=button.dataset.prisonerAction,id=button.dataset.prisonerId,prisoner=prisoners.find(p=>p.id===id);if(action==='sell'&&!confirm(`Sell ${prisoner?.name||'this prisoner'} for ${prisoner?.sale_value??8} gold?`))return;const swapId=action==='secure'?document.querySelector(`[data-prisoner-swap="${CSS.escape(id)}"]`)?.value||null:null;try{const data=await rawApi(`/api/prisoners/${encodeURIComponent(id)}/action`,{method:'POST',body:JSON.stringify({action,swap_prisoner_id:swapId})});state=data.state;toast(action==='sell'?`${data.result.name} sold for ${data.result.gold} gold`:action==='secure'?'Prisoner secured':'Prisoner moved to stockade');renderResources();renderRoster();renderBase()}catch(e){toast(e.message)}});
  $$('[data-roster]').forEach(el=>el.onclick=()=>{selectedCharacterId=el.dataset.roster;renderRoster()});
  const c=state.characters.find(x=>x.id===selectedCharacterId);if(!c)return;const metrics=combatMetrics(c);
  const appearance=appearanceDrafts[c.id]||c.appearance||{},raceFamilies=content.races?.[c.race]?.families||[];
  const appearanceOpen=appearanceEditorOpen[c.id]??Object.values(appearance).some(Boolean);
  const appearanceEditor=`<details class="appearance-editor" data-appearance-editor="${c.id}" ${appearanceOpen?'open':''}><summary><b>Appearance</b><span>${c.appearance_source==='portrait'?'Filled from portrait tags':c.appearance_source==='manual'?'Custom description':'Add visible details for story scenes'}</span></summary><div class="appearance-grid"><label>Hair color<input id="appearance-hair-color" value="${esc(appearance.hair_color||'')}" maxlength="48"></label><label>Hair length<input id="appearance-hair-length" value="${esc(appearance.hair_length||'')}" maxlength="48"></label><label>Eye color<input id="appearance-eye-color" value="${esc(appearance.eye_color||'')}" maxlength="48"></label><label>Skin / surface<input id="appearance-skin-tone" value="${esc(appearance.skin_tone||'')}" maxlength="64"></label><label>Build<input id="appearance-build" value="${esc(appearance.build||'')}" maxlength="64"></label><label class="wide">Distinctive features<textarea id="appearance-distinctive-features" maxlength="240">${esc(appearance.distinctive_features||'')}</textarea></label><label class="wide">Natural description used in event prose<textarea id="appearance-summary" maxlength="360" placeholder="A compact visual description; leave blank to assemble one from the fields above.">${esc(appearance.summary||'')}</textarea></label></div><div class="appearance-actions"><button id="save-character-appearance" class="primary">Save Appearance</button>${c.portrait_metadata_available?'<button id="fill-appearance-tags">Fill from portrait tags</button>':''}</div><small>Uploaded override portraits use the description you enter here. Tagged pool portraits can restore their saved fields.</small></details>`;
  const tiered=Object.entries(content.perk_tracks||{}).filter(([track])=>perkRank(c,track)>0).map(([track,d])=>`<div class="perk-card tier-${perkLevel(c,track)}" tabindex="0"><span>${esc(d.name)}</span><b>${title(perkLevel(c,track))}</b><small>+1 ${d.attribute_bonus.toUpperCase()} · rating ${effectiveStat(c,track)}</small><div class="perk-tooltip"><p>${esc(d.description||'A trained proficiency.')}</p><strong>Effect</strong><span>+1 ${d.attribute_bonus.toUpperCase()}. ${title(perkLevel(c,track))} adds +${perkRank(c,track)} to ${esc(d.name)} mission capability before equipment.</span></div></div>`).join('');
  const standalone=equippedPerks(c).map(([p,item])=>{const racial=Object.entries(content.races||{}).find(([name])=>name.toLowerCase().replaceAll('-','_').replaceAll(' ','_')===p);const d= racial?{name:racial[0],description:racial[1].gameplay.summary,effect:raceEffects(racial[1].gameplay).join('. ')}:content.standalone_perks?.[p]||{name:title(p),description:'A unique characteristic, background, or mission-earned perk.',effect:'Can unlock matching mission conditions and special paths.'};return `<span class="perk-pill" tabindex="0">${esc(d.name)}${item?' ◇':''}<span class="perk-tooltip"><span class="tooltip-description">${esc(d.description)}</span><strong>Effect</strong><span>${esc(d.effect)}${item?` Granted by ${esc(item)} while equipped.`:''}</span></span></span>`}).join('');
  $('#character-detail').innerHTML=`<div class="char-head">${portraitHTML(c,false,true)}<div><div class="eyebrow">${title(c.source_kind||'character')}</div><h2>${esc(c.name)}</h2><div class="tags"><span>${esc(c.race)}</span>${raceFamilies.map(f=>`<span>${esc(f)}</span>`).join('')}${c.gender?`<span>${title(c.gender)}</span>`:''}<span>${esc(c.series)}</span></div></div></div><div class="portrait-editor upload-editor"><label><span>Upload override · stored at max 1200px with a separate 192px thumbnail</span><input id="character-portrait-upload" type="file" accept="image/png,image/jpeg,image/gif,image/webp"></label></div>${c.source_kind==='generic'?`<div class="portrait-pool-control"><span>Assigned pool: ${esc(c.portrait_pool||'none')} · portrait selection locked</span></div>`:''}${c.is_player?`<div class="portrait-editor"><label><span>Portrait URL</span><input id="player-portrait-url" value="${esc(c.portrait||'')}" placeholder="https://..."></label><button id="save-player-portrait">Save Portrait URL</button></div>`:''}${appearanceEditor}<h3>Perks</h3><div class="perk-section">${tiered||'<p class="muted small">No trained proficiency perks.</p>'}</div>${standalone?`<div class="standalone-perks"><small>Standalone perks</small><div class="tags">${standalone}</div></div>`:''}<h3>Attributes</h3><div class="stat-grid attributes">${attributeNames.map(a=>`<div><span>${a.toUpperCase()}</span><b>${effectiveAttribute(c,a)}</b><small>base ${c.attributes?.[a]??5}</small></div>`).join('')}</div><div class="combat-ratings"><div><span>CON</span><b>${metrics.constitution}</b><small>VIT and perk bonuses</small></div><div><span>DPS</span><b>${metrics.dps}</b><small>${metrics.dps_attribute.toUpperCase()} · ${esc(metrics.weapon)}</small></div></div><h3>Equipment ${!equipmentEditable(c)?'<small>locked during a mission</small>':''}</h3><div class="equipment">${content.slots.map(slot=>{const options=state.inventory.filter(inst=>content.items[inst.item_id]?.slot===slot);return `<label><span>${title(slot)}</span><select data-equip="${slot}" ${!equipmentEditable(c)?'disabled':''}><option value="">— Empty —</option>${options.map(inst=>`<option value="${inst.instance_id}" ${c.equipment[slot]===inst.instance_id?'selected':''}>${esc(content.items[inst.item_id].name)}</option>`).join('')}</select></label>`}).join('')}</div>`;
  $('[data-appearance-editor]')?.addEventListener('toggle',event=>{appearanceEditorOpen[event.currentTarget.dataset.appearanceEditor]=event.currentTarget.open});
  $$('[data-equip] option[value]').forEach(option=>{const item=itemByInstance(option.value);if(item)option.textContent=`${item.name} · ${title(item.rarity||'common')}${item.granted_perks?.length?` · perk: ${item.granted_perks.map(p=>content.standalone_perks?.[p]?.name||title(p)).join(', ')}`:''}`});
  $$('[data-equip] option[value]').forEach(option=>{if(!option.value)return;const owner=state.characters.find(other=>Object.values(other.equipment||{}).includes(option.value));if(owner&&owner.id!==c.id){option.textContent+=` · ${owner.name}${equipmentEditable(owner)?'':' (on mission)'}`;option.disabled=!equipmentEditable(owner)}});
  const equippedCards=Object.entries(c.equipment||{}).map(([slot,id])=>{const item=itemByInstance(id);return item?`<div class="gear-effect rarity-${esc(item.rarity||'common')}"><b>${esc(item.name)}</b><span>${title(slot)} · ${title(item.rarity||'common')}</span><small>${esc(itemEffectText(item))}</small></div>`:''}).join('');
  if(equippedCards)$('#character-detail').insertAdjacentHTML('beforeend',`<h3>Equipped effects</h3><div class="gear-effects">${equippedCards}</div>`);
  const detail=$('#character-detail'),nodes=[...detail.children],panels={};
  for(const tab of ['overview','equipment','appearance']){const panel=document.createElement('section');panel.dataset.rosterPanel=tab;panels[tab]=panel}
  let section='overview';
  for(const node of nodes.slice(1)){
    if(node.tagName==='H3'&&node.textContent.startsWith('Equipment'))section='equipment';
    const appearanceNode=node.matches('.portrait-editor,.portrait-pool-control,.appearance-editor');
    panels[appearanceNode?'appearance':section].append(node);
  }
  const tabs=document.createElement('div');tabs.className='roster-detail-tabs';tabs.innerHTML=['overview','equipment','appearance'].map(tab=>`<button data-roster-tab="${tab}" class="${tab===rosterDetailTab?'active':''}">${title(tab)}</button>`).join('');detail.append(tabs,...Object.values(panels));
  const switchTab=tab=>{rosterDetailTab=tab;Object.entries(panels).forEach(([key,panel])=>panel.classList.toggle('hidden',key!==tab));tabs.querySelectorAll('button').forEach(button=>button.classList.toggle('active',button.dataset.rosterTab===tab))};
  tabs.querySelectorAll('button').forEach(button=>button.onclick=()=>switchTab(button.dataset.rosterTab));switchTab(rosterDetailTab);
  detail.querySelector('.char-head').insertAdjacentHTML('afterend',`<div class="roster-status-bar">${esc(characterStatus(c))} · ${esc(c.specialty||'No specialty')} ${c.is_player?'· Your character':''}</div>`);
  $$('[data-equip]').forEach(select=>{const filter=document.createElement('input');filter.type='search';filter.placeholder='Find equipment…';filter.setAttribute('aria-label',`Search ${select.dataset.equip} equipment`);select.before(filter);filter.oninput=()=>{const query=filter.value.toLowerCase();[...select.options].forEach(option=>option.hidden=!!option.value&&!option.selected&&!option.textContent.toLowerCase().includes(query))}});
  const racialProfile=content.races?.[c.race]?.gameplay;
  if(racialProfile)panels.overview.insertAdjacentHTML('afterbegin',`<div class="race-gameplay-card"><h3>${esc(c.race)} · Racial identity</h3><p>${esc(racialProfile.summary)}</p><div class="tags">${raceEffects(racialProfile).map(effect=>`<span>${esc(effect)}</span>`).join('')}</div><small>These are derived effects; base attributes do not include HP, movement or evasion modifiers.</small></div>`);
  const appearanceFields=['hair-color','hair-length','eye-color','skin-tone','build','distinctive-features','summary'];
  appearanceFields.forEach(field=>$('#appearance-'+field).oninput=()=>{appearanceDrafts[c.id]=Object.fromEntries(appearanceFields.map(key=>[key.replaceAll('-','_'),$('#appearance-'+key).value]))});
  $('#character-portrait-upload').onchange=async e=>{const file=e.target.files?.[0];if(!file)return;if(file.size>4*1024*1024){toast('Portrait must be 4 MB or smaller');return}const reader=new FileReader();reader.onload=async()=>{try{const data=await rawApi(`/api/characters/${encodeURIComponent(c.id)}/portrait-upload`,{method:'POST',body:JSON.stringify({data_url:reader.result})});state=data.state;toast('Portrait uploaded');renderRoster();renderBase()}catch(err){toast(err.message)}};reader.readAsDataURL(file)};
  $('#save-character-appearance').onclick=async()=>{const payload={hair_color:$('#appearance-hair-color').value,hair_length:$('#appearance-hair-length').value,eye_color:$('#appearance-eye-color').value,skin_tone:$('#appearance-skin-tone').value,build:$('#appearance-build').value,distinctive_features:$('#appearance-distinctive-features').value,summary:$('#appearance-summary').value};try{const d=await rawApi(`/api/characters/${encodeURIComponent(c.id)}/appearance`,{method:'POST',body:JSON.stringify(payload)});state=d.state;delete appearanceDrafts[c.id];toast('Appearance saved');renderRoster()}catch(e){toast(e.message)}};
  if($('#fill-appearance-tags'))$('#fill-appearance-tags').onclick=async()=>{try{const d=await rawApi(`/api/characters/${encodeURIComponent(c.id)}/appearance-from-portrait`,{method:'POST',body:'{}'});state=d.state;delete appearanceDrafts[c.id];toast('Appearance filled from portrait tags');renderRoster()}catch(e){toast(e.message)}};
  if(c.is_player&&$('#save-player-portrait'))$('#save-player-portrait').onclick=async()=>{try{const d=await rawApi('/api/player-character/portrait',{method:'POST',body:JSON.stringify({portrait:$('#player-portrait-url').value.trim()})});state=d.state;toast('Portrait updated');renderRoster();renderBase()}catch(e){toast(e.message)}};
  $$('[data-equip]').forEach(sel=>sel.onchange=async()=>{try{const d=await rawApi('/api/equip',{method:'POST',body:JSON.stringify({character_id:c.id,slot:sel.dataset.equip,instance_id:sel.value||null})});state=d.state;renderRoster();renderMissions()}catch(e){toast(e.message)}});
}

const portraitInput=$('#cc-portrait');
if(portraitInput){
  const updateCreatorPortraitPreview=()=>{const box=$('#cc-portrait-preview'),url=portraitInput.value.trim();if(!box)return;box.innerHTML=url?`<img src="${esc(portraitSrc(url))}" onerror="this.outerHTML='<span>Image could not be loaded from that URL.</span>'">`:'<span>Portrait preview</span>'};
  portraitInput.addEventListener('input',updateCreatorPortraitPreview);updateCreatorPortraitPreview();
}

init();



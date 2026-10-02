import {victoryMarkup} from './battle-victory-ui.js';
import {attributeHelp,attributeTotalHelp,mountHoverHelp} from './roster-help.js';
import {sizeBattleMap,bindMapWheel} from './battle-camera.js';
import {mountRelationships,mountServiceRecord} from './relationship-ui.js';
import {createCombatEffects} from './combat-effects.js';
import './combat-effects.css';
const combatEffects=createCombatEffects();
import {patchLiveHTML,captureMovingPositions,restartWalking,trackBattleAnimation} from './live-dom.js';
import {createLatestMovement} from './latest-movement.js';
import {previewMovement} from './movement-preview.js';
import {applyContractUpdate} from './contract-state.js';
import {createBoardVFX} from './board-vfx.js';
import {boardIcon,rankSeal,missionCard,eventHeader,filterChips,stableBoardHTML} from './mission-board-ui.js';
import {createAmbientPlayer,ambientContext} from './ambient-player.js';
import {createMusicPlayer,musicTransitionPolicy} from './music-player.js';
import {mountDecisionScene} from './mission-scene-ui.js';
import {createAudioMixer,mountAudioSettings,audioCategory} from './audio-settings.js';
import {raceEffects,perkModifiers} from './character-effects.js';
import {mountCharacterCreator} from './character-creator.js';
import {selectBattleSkill,skillPicker} from './equipment-skills.js';
import {authenticateWeb,activitySessionKey,mountWebAccountControls} from './web-login.js';
import './web-login.css';
import {attackCommand,nextCombatMode,approachDescription} from './combat-targeting.js';
import {mountReservation} from './mission-reservation-ui.js';
import {renderCampEconomy} from './camp-economy-ui.js';
import {rosterPage} from './roster-tools.js';
import {mountEquipmentBrowser,iconPath} from './equipment-ui.js';
import './equipment-ui.css';
import './qol.css';
﻿import {mountMissionPlanner} from './mission-claim-ui.js';
import {matchesMission,equipmentEditable} from './mission-planner.js';
import { DiscordSDK } from "@discord/embedded-app-sdk";
import "./styles.css?v=20260930u";
import "./base-ui.css";

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
let battleFit=true,battleResizeObserver;
const expandedVictory=new Set();
function changeBattleZoom(b,direction){
  const current=battleFit?($('.battlefield')?.getBoundingClientRect().width||b.width*72)/(b.width*72):battleZoom;
  battleZoom=direction==='reset'?DEFAULT_BATTLE_ZOOM:Math.max(.25,Math.min(3,current+(direction==='in'?.25:-.25)));
  battleFit=false;
}
function updateBattleCamera(b){
  battleResizeObserver?.disconnect();
  const viewport=document.querySelector('#battle-viewport');
  const update=()=>sizeBattleMap(viewport,{width:b.width,height:b.height,fit:battleFit,zoom:battleZoom});
  update();
  if(viewport)bindMapWheel(viewport,{width:b.width,height:b.height,onZoom:zoom=>{
    battleFit=false;battleZoom=zoom;
    const reset=document.querySelector('[data-battle-zoom=reset]');if(reset)reset.textContent=`${Math.round(zoom*100)}%`;
    document.querySelector('[data-battle-fit]')?.setAttribute('aria-pressed','false');
  }});
  const fitButton=document.querySelector('[data-battle-fit]');if(fitButton)fitButton.setAttribute('aria-pressed',String(battleFit));
  battleResizeObserver=new ResizeObserver(update);
  if(viewport)battleResizeObserver.observe(viewport);
}
window.addEventListener('resize',()=>{if(activeBattleView)updateBattleCamera(activeBattleView)});
let activeBattleMissionId = null, activeBattleView = null, selectedCombatAction = 'move', contextMenuOpen = false, tileActionMenu = null, retreatAllArmed = false, battleZoom = DEFAULT_BATTLE_ZOOM, battlePan = {left:0,top:0}, combatRequestPending = false;
let selectedPreparation = {mode:'defense',id:null};
const rankBoardOpen={};
const rosterCollectionOpen={champions:false,celestials:false,prisoners:false};
const appearanceEditorOpen={};
const appearanceDrafts={};
const rosterFilters={query:'',status:'',race:'',kind:'',sort:'name',page:0};
let rosterDetailTab='overview',rosterNeedsRefresh=false,baseNeedsRefresh=true;
const latestMovement=createLatestMovement();
const selectedGearSkills=new Map();
let inFlightCombatAction=null;
let missionMutationVersion=0,dynamicRefreshAgain=false;
let baseBlueprintQuery='';
let missionPlanner=null,analysisSequence=0;
const missionFilters={query:'',rank:'',form:'',available:true,sort:'shortest'};
let missionClaimPending=false,activeDecisionMission=null;
let audioStorage;try{audioStorage=window.localStorage}catch{}
const audioMixer=createAudioMixer(audioStorage);
const musicPlayer=createMusicPlayer(audioMixer);
const boardVFX=createBoardVFX();
const ambientPlayer=createAmbientPlayer(audioMixer,{context:()=>ambientContext(musicPlayer.currentContext,$('.tabs button.active')?.dataset.tab),fireContext:()=>pool?.event?.id==='goblin_warhost'&&!activeBattleView&&!$('#game').classList.contains('hidden')&&['missions','private'].includes($('.tabs button.active')?.dataset.tab)});
function syncMusic(){boardVFX.setEvent(pool?.event,!activeBattleView&&!$('#game').classList.contains('hidden')&&['missions','private'].includes($('.tabs button.active')?.dataset.tab));const request=musicTransitionPolicy($('.tabs button.active')?.dataset.tab,activeBattleView,activeDecisionMission,musicPlayer.currentContext,pool?.event);musicPlayer.setContext(request.context,{delayMs:request.delayMs})}
window.addEventListener('pointerdown',()=>{musicPlayer.unlock();ambientPlayer.unlock()});
window.addEventListener('keydown',()=>{musicPlayer.unlock();ambientPlayer.unlock()});
document.addEventListener('visibilitychange',()=>{musicPlayer.suspend(document.hidden);ambientPlayer.suspend(document.hidden);document.body.classList.toggle('page-hidden',document.hidden)});
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
    await refreshDynamic(true);
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
  if(!res.ok){const error=new Error(data.detail||`Request failed: ${res.status}`);error.status=res.status;throw error} return data;
}

async function setupIdentity(){
  const cfg=await rawApi('/api/config'); appConfig=cfg;
  const params=new URLSearchParams(location.search);
  const embedded=params.has('frame_id') && params.has('instance_id');
  if(embedded){
    if(!cfg.discord_client_id) throw new Error('DISCORD_CLIENT_ID is not configured on the backend.');
    const sdk=new DiscordSDK(cfg.discord_client_id); await sdk.ready();
    if(!sdk.guildId) throw new Error('Launch Fortcamp from inside a Discord server, not a DM.');
    const sessionKey=activitySessionKey(cfg,sdk.guildId);
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
    if(!cfg.dev_bypass_auth){
      const login=await authenticateWeb(rawApi,cfg);
      sessionToken=login.session_token;identity=login.identity;
      mountWebAccountControls(rawApi,cfg);
      return;
    }
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
    if(data.exists){state=data.state;showGame()}else{$('#creator').classList.remove('hidden');mountCharacterCreator($('#creator'),content);renderCreatorStats()}
  }catch(e){$('#loading').classList.remove('hidden');$('#loading-text').textContent=e.message;console.error(e)}
}

$('#create-game').onclick=async()=>{
  const starter=$('#cc-perk').value;
  try{const data=await rawApi('/api/new-game',{method:'POST',body:JSON.stringify({character:{name:$('#cc-name').value.trim()||'Wanderer',race:$('#cc-race').value.trim()||'Human',series:$('#cc-series').value.trim()||'Player',specialty:$('#cc-specialty').value,traits:[$('#cc-trait').value],portrait:$('#cc-portrait').value.trim(),perks:{[starter]:'basic'},attributes:creatorAttributes}})});state=data.state;$('#creator').classList.add('hidden');showGame()}catch(e){toast(e.message)}
};

function updateLiveCountdowns(){
  const now=Date.now()/1000;
  $$('[data-countdown-end]').forEach(element=>{const remaining=Math.max(0,Math.ceil(Number(element.dataset.countdownEnd)-now));element.textContent=`${fmtDuration(remaining)}${element.dataset.countdownSuffix||''}`});
  if(pool?.next_refresh)$('#pool-countdown').textContent=Number(pool.next_refresh)<=now?'Refreshing…':countdown(pool.next_refresh);
  const phase=$('[data-phase-countdown]');if(phase&&Number(phase.dataset.countdownEnd)<=now)phase.textContent='Opening…';
  const due=activeMissions.some(m=>m.status==='claimed'&&Number(m.completes_at||Infinity)<=now)||(pool?.budget?.next_phase_at&&pool.budget.next_phase_at<=now)||(pool?.next_refresh&&pool.next_refresh<=now);
  if(due&&Date.now()-lastDeadlineRefresh>600){lastDeadlineRefresh=Date.now();refreshDynamic()}
}
function showGame(){ $('#game').classList.remove('hidden');syncMusic(); refreshAll(); if(!pollTimer)pollTimer=setInterval(refreshDynamic,5000);if(!clockTimer)clockTimer=setInterval(updateLiveCountdowns,250); }
async function refreshAll(){renderResources();rosterNeedsRefresh=true;baseNeedsRefresh=true;await refreshDynamic(true)}
function refreshDynamic(force=false){
  if(dynamicRefreshPromise)return force?dynamicRefreshPromise.then(()=>refreshDynamic()):dynamicRefreshPromise;
  const version=missionMutationVersion;
  dynamicRefreshPromise=(async()=>{try{
    const previous=new Map(activeMissions.map(m=>[m.id,m.status]));
    const [p,pc,a]=await Promise.all([rawApi('/api/missions/pool'),rawApi('/api/private-contracts'),rawApi('/api/missions/active')]);
    const s=await rawApi('/api/state');
    if(version!==missionMutationVersion){dynamicRefreshAgain=true;return}
    pool=p;syncRegionalTheme();syncMusic();
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
    const uiState=value=>value&&JSON.stringify({characters:value.characters?.map(({practice,...c})=>c),buildings:value.buildings,inventory:value.inventory,prisoners:value.prisoners,rank:value.mission_rank,size:value.base_size,claims:value.claim_upgrade,blueprints:value.learned_blueprints,meals:value.meals});
    const stateChanged=!!(s.exists&&uiState(s.state)!==uiState(state));
    activeMissions=incoming;dynamicReady=true;if(s.exists)state=s.state;renderResources();
    if(stateChanged){rosterNeedsRefresh=true;baseNeedsRefresh=true}
    renderVisiblePanels();updateLiveCountdowns();
    if($('.tabs button.active')?.dataset.tab==='base')$$('[data-build]').forEach(button=>{const costs=content.buildings[button.dataset.build]?.cost||{};button.disabled=Object.entries(costs).some(([r,n])=>(state.resources[r]||0)<n)});
    if(stateChanged&&$('.mission-planner')&&!$('#mission-modal').classList.contains('hidden'))missionPlanner?.refresh(state.characters);
  }catch(e){console.warn(e.message)}})().finally(()=>{dynamicRefreshPromise=null;if(dynamicRefreshAgain){dynamicRefreshAgain=false;refreshDynamic()}});
  return dynamicRefreshPromise;
}

function syncMissionMutation(mission){
  if(!mission?.id)return;
  const next=applyContractUpdate({pool,privateContracts,activeMissions},mission);
  pool=next.pool;privateContracts=next.privateContracts;activeMissions=next.activeMissions;
  missionMutationVersion++;renderVisiblePanels();
}

$$('.tabs button').forEach(btn=>btn.onclick=()=>{$$('.tabs button').forEach(x=>x.classList.remove('active'));btn.classList.add('active');$$('.tab-panel').forEach(x=>x.classList.add('hidden'));$(`#tab-${btn.dataset.tab}`).classList.remove('hidden');syncMusic();renderVisiblePanels();syncContractNavigation()});

function renderResources(){
  if(!state)return;const root=$('#resources');
  for(const [key,value] of Object.entries(state.resources)){
    let node=root.querySelector(`[data-resource="${key}"]`);
    if(!node){node=document.createElement('div');node.className='resource';node.dataset.resource=key;const count=document.createElement('b'),label=document.createElement('span');label.textContent=title(key);node.append(count,label);root.append(node)}
    const text=String(value);if(node.firstChild.textContent!==text)node.firstChild.textContent=text;
  }
  for(const node of [...root.children])if(!(node.dataset.resource in state.resources))node.remove();
}
function renderVisiblePanels(){
  if(activeBattleView||activeDecisionMission){syncContractNavigation();return}
  const tab=$('.tabs button.active')?.dataset.tab;
  if(tab==='missions'){renderMissions();renderActive()}
  else if(tab==='private'){renderPrivateContracts();syncContractNavigation()}
  else if(tab==='roster'&&rosterNeedsRefresh&&!$('#tab-roster input:focus, #tab-roster textarea:focus, #tab-roster select:focus')){renderRoster()}
  else if(tab==='base'&&baseNeedsRefresh&&!$('#tab-base select:focus')){renderBase();baseNeedsRefresh=false}
}

function portraitHTML(c,small=false,viewable=false){const cls=`portrait ${small?'smallp':''} ${c.status!=='idle'?'deployed':''} ${viewable?'viewable':''}`;if(c.portrait){const full=portraitSrc(c.portrait),thumb=portraitSrc(c.portrait_thumbnail||c.portrait);return `<img class="${cls}" draggable="${c.status==='idle'}" data-char="${c.id}" src="${esc(thumb)}" ${viewable?`data-portrait-view="${esc(full)}" data-portrait-name="${esc(c.name)}"`:''} title="${esc(c.name)}" onerror="this.outerHTML='<div class=&quot;${cls}&quot; title=&quot;Portrait could not be loaded&quot;>${initials(c.name)}</div>'">`}return `<div class="${cls}" draggable="${c.status==='idle'}" data-char="${c.id}">${initials(c.name)}</div>`}

function syncContractNavigation(){
  const tab=$('.tabs button.active')?.dataset.tab,privateCount=privateContracts.length,expeditions=activeMissions.filter(m=>['claimed','battle','decision'].includes(m.status)).length;
  $$('[data-contract-nav]').forEach(nav=>{
    if(!nav.children.length){nav.innerHTML=`<button type="button" data-contract-view="missions">${boardIcon('utility_public')}<span>Public board</span></button><button type="button" data-contract-view="private">${boardIcon('utility_private')}<span>Private contracts</span><b data-nav-private>0</b></button><button type="button" data-contract-view="expeditions">${boardIcon('utility_party')}<span>Your expeditions</span><b data-nav-expeditions>0</b></button>`;nav.querySelectorAll('[data-contract-view]').forEach(button=>button.onclick=()=>{const view=button.dataset.contractView;$(`.tabs button[data-tab="${view==='expeditions'?'missions':view}"]`).click();if(view==='expeditions'){const block=$('#expedition-section');block.scrollIntoView({behavior:window.matchMedia('(prefers-reduced-motion: reduce)').matches?'instant':'smooth',block:'center'});block.querySelector('button')?.focus({preventScroll:true})}})}
    nav.querySelector('[data-nav-private]').textContent=privateCount;nav.querySelector('[data-nav-expeditions]').textContent=expeditions;
    nav.querySelectorAll('[data-contract-view]').forEach(button=>{const current=button.dataset.contractView===tab;button.classList.toggle('active',current);if(current)button.setAttribute('aria-current','page');else button.removeAttribute('aria-current')});
  });
}

function syncRegionalTheme(){
  const event=pool?.event||{id:'general'};
  const themeClass=event.id==='general'?null:`theme-${event.theme}`;
  for(const theme of ['goblin','undead','arcane','beast','starfall'])document.body.classList.toggle(`theme-${theme}`,`theme-${theme}`===themeClass);
}
function renderMissions(){
  if(!pool)return;$('#pool-countdown').textContent=countdown(pool.next_refresh);$('#mission-rank-label').textContent=`${pool.rank}-RANK`;$('#pool-player-count').textContent=`Pool scaled for ${pool.active_players??pool.registered_players} active player${(pool.active_players??pool.registered_players)===1?'':'s'}`;
  if(pool.budget)$('#pool-player-count').innerHTML+=` · ${pool.budget.phase==='free'?'Free-for-all':pool.budget.phase==='wave1'?'Wave 1':'Wave 2'} · ${pool.budget.remaining}/${pool.budget.limit} Contract Points${pool.budget.solo_bonus?' · +10 solo bonus':''}${pool.budget.next_phase_at?` · next phase <span data-phase-countdown data-countdown-end="${pool.budget.next_phase_at}">${countdown(pool.budget.next_phase_at)}</span>`:''}`;
  const eventBanner=$('#mission-event-banner'),event=pool.event||{id:'general'};
  syncRegionalTheme();
  eventBanner.className=`event-banner guild-board-event event-${event.theme||'general'}`;stableBoardHTML(eventBanner,eventHeader(event));syncContractNavigation();
  const debugBox=$('#debug-pool-controls');debugBox.classList.toggle('hidden',!debugEnabled());
  if(debugEnabled()&&!$('#debug-pool-event').options.length){$('#debug-pool-event').innerHTML=Object.entries(content.mission_events).map(([id,e])=>`<option value="${id}">${esc(e.name)}</option>`).join('');$('#debug-force-refresh').onclick=async()=>{const btn=$('#debug-force-refresh');btn.disabled=true;try{const d=await rawApi('/api/debug/missions/refresh',{method:'POST',body:JSON.stringify({event_id:$('#debug-pool-event').value})});toast(`Forced ${d.event.name}`);await refreshDynamic(true)}catch(err){toast(err.message)}finally{btn.disabled=false}};$('#debug-goblin-battle').onclick=()=>launchDebugBattle($('#debug-goblin-battle'),'/api/debug/battles/goblin-warcamp','Goblin Warcamp battle')}
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
  stableBoardHTML($('#board-filter-chips'),filterChips(missionFilters));
  $$('[data-clear-filter]').forEach(button=>button.onclick=()=>{const key=button.dataset.clearFilter;missionFilters[key]=key==='available'?false:'';$('#board-search').value=missionFilters.query;rankFilter.value=missionFilters.rank;formFilter.value=missionFilters.form;$('#board-available').checked=missionFilters.available;renderMissions()});
  stableBoardHTML($('#mission-grid'),ranks.map((rank,index)=>{
    const unlocked=index<=viewerIndex;
    if(missionFilters.rank&&missionFilters.rank!==rank)return '';
    const entries=pool.missions.filter(m=>m.rank===rank&&(m.locked||matchesMission(m,missionFilters))),available=entries.filter(m=>m.status==='available').length;
    if((missionFilters.query||missionFilters.form)&&(!unlocked||!entries.length))return '';
    const open=rankBoardOpen[rank]??unlocked;
    const stacks=[...entries.filter(m=>!m.locked).reduce((groups,m)=>{const key=m.template_id||m.id;if(!groups.has(key))groups.set(key,[]);groups.get(key).push(m);return groups},new Map()).values()];
    stacks.sort((a,b)=>missionFilters.sort==='name'?a[0].name.localeCompare(b[0].name):a[0].duration_seconds-b[0].duration_seconds||a[0].name.localeCompare(b[0].name));
    const cards=unlocked?stacks.map(stack=>{const openCopies=stack.filter(m=>m.status==='available'),m=openCopies[0]||stack[0];return missionCard(m,{count:openCopies.length,claimed:stack.length-openCopies.length})}).join(''):`<div class="locked-rank-copy"><div><b>${available} ${rank}-Rank mission${available===1?'':'s'} available</b><p>Upgrade Guild Hall visibility to reveal these contracts.</p></div><span class="locked-rank-symbol" aria-hidden="true">&#9671;</span></div>`;
    return `<details class="rank-board rank-${rank.toLowerCase()} ${unlocked?'':'rank-board-locked'}" data-rank-board="${rank}" ${open?'open':''}><summary>${rankSeal(rank)}<span class="guild-rank-title"><strong>${rank}-Rank contracts</strong><small>${({E:'First steps',D:'Local work',C:'Proven adventurers',B:'Dangerous expeditions',A:'Exceptional challenges',S:'Legendary opportunities'})[rank]}</small></span><span class="guild-rank-count">${available} available</span><i>${unlocked?'':'LOCKED'}</i></summary><div class="rank-mission-grid">${cards||'<p class="muted">No contracts of this rank appeared this refresh.</p>'}</div></details>`;
  }).join('')+(!matching.length?'<div class="board-empty"><b>No revealed contracts match.</b><span>Try another search or reset your filters. Locked boards reveal only their available counts.</span></div>':''));
  $$('[data-rank-board]').forEach(board=>board.ontoggle=()=>{if(board.isConnected)rankBoardOpen[board.dataset.rankBoard]=board.open});
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
    try{await rawApi('/api/debug/private-contracts/hedgerow-watch',{method:'POST',body:'{}'});toast('Defense contract added');await refreshDynamic(true)}
    catch(error){toast(error.message)}finally{debugButton.disabled=false}
  };
  if(!privateContracts.length){
    stableBoardHTML(grid,'<div class="private-empty"><div class="eyebrow">NO OPEN LEADS</div><h3>Your contacts have no private work waiting.</h3><p>Investigations, faction trust, rescued characters, and story consequences can place contracts here. They are visible only to you and expire if ignored.</p></div>');
    return;
  }
  stableBoardHTML(grid,privateContracts.map(m=>missionCard(m,{privateContract:true})).join(''));
  $$('[data-private-mission]').forEach(card=>card.onclick=()=>openMission(privateContracts.find(m=>m.id===card.dataset.privateMission)));
}
function renderActive(){
  const running=activeMissions.filter(m=>['claimed','battle','decision'].includes(m.status));const recent=activeMissions.filter(m=>m.status==='completed').slice(0,3);
  const debug=debugEnabled();
  syncContractNavigation();
  stableBoardHTML($('#active-missions'),(running.length||recent.length)?`<div class="active-title">Your missions${debug?' · DEBUG ENABLED':''}</div>${running.map(m=>m.status==='decision'?`<button class="active-card" data-resume-scene="${m.id}"><div class="active-main"><b>${esc(m.name)}</b><span>Decision waiting · Continue story</span></div></button>`:m.status==='battle'?`<button class="active-card battle-active" data-resume-battle="${m.id}"><div class="active-main"><b>${esc(m.name)}</b><span>Tactical battle in progress · Resume</span></div></button>`:`<div class="active-card mission-running"><div class="active-main"><b>${esc(m.name)}</b><span data-countdown-end="${m.completes_at}" data-countdown-suffix=" remaining">--:-- remaining</span></div>${debug?`<div class="debug-complete"><small>Debug resolution</small><button class="debug-resolve-natural" data-debug-resolve-now="${m.id}">Resolve Now · Real Roll</button><button data-debug="critical_failure" data-debug-mission="${m.id}">Critical Failure</button><button data-debug="failure" data-debug-mission="${m.id}">Failure</button><button data-debug="success" data-debug-mission="${m.id}">Success</button><button data-debug="critical_success" data-debug-mission="${m.id}" ${m.critical_success_available?'':'disabled'}>Critical Success</button></div>`:''}</div>`).join('')}${recent.map(m=>`<button class="active-card result-card" data-result="${m.id}"><b>${esc(m.name)}</b><span>${title(m.result?.outcome||'completed')}${m.result?.debug_forced?' · DEBUG':''}</span></button>`).join('')}`:'<div class="expeditions-empty"><b>Your next story starts here.</b><span>Accepted contracts and saved decisions will appear in Your Expeditions.</span></div>');
  $$('[data-resume-scene]').forEach(el=>el.onclick=()=>openDecision(el.dataset.resumeScene));
  $$('[data-resume-battle]').forEach(el=>el.onclick=()=>openBattle(el.dataset.resumeBattle));
  $$('[data-result]').forEach(el=>el.onclick=()=>showResult(activeMissions.find(m=>m.id===el.dataset.result)?.result));
  $$('[data-debug-mission]').forEach(btn=>btn.onclick=async e=>{e.stopPropagation();await debugCompleteMission(btn.dataset.debugMission,btn.dataset.debug)});
  $$('[data-debug-resolve-now]').forEach(btn=>btn.onclick=async e=>{e.stopPropagation();btn.disabled=true;try{const data=await rawApi(`/api/debug/missions/${btn.dataset.debugResolveNow}/resolve-now`,{method:'POST',body:'{}'});syncMissionMutation(data.mission);if(data.mission.status==='battle'){toast('The investigation turned into a fight');await openBattle(data.mission.id);await refreshDynamic(true);return}const local=activeMissions.find(m=>m.id===btn.dataset.debugResolveNow);if(local){local.status='completed';local.result=data.result}playOutcomeSound(data.result.outcome);toast(`Resolved: ${title(data.result.outcome)}`);showResult(data.result);await refreshDynamic(true)}catch(error){toast(error.message)}finally{btn.disabled=false}});
}

function currentMissionSelection(){return missionPlanner?.selection()||{party_ids:[],role_assignments:null,bodyguard_ids:[]}}

async function debugCompleteMission(missionId,outcome,selection={party_ids:[],role_assignments:null}){
  try{
    const data=await rawApi(`/api/debug/missions/${missionId}/complete`,{method:'POST',body:JSON.stringify({outcome,...selection})});
    syncMissionMutation(data.mission||{...(activeMissions.find(m=>m.id===missionId)||selectedMission),id:missionId,status:'completed',result:data.result})
    playOutcomeSound(data.result.outcome);toast(`DEBUG: ${title(data.result.outcome)}`);showResult(data.result);await refreshDynamic(true);
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
  if(m.status==='available'&&!m.private_source&&!m.chain){
    const pointCost=m.point_cost||content.economy?.point_cost?.[m.rank]||1;
    mountReservation($('#mission-detail'),m,{budget:pool.budget,cost:pointCost,api:rawApi,
      onRefresh:data=>{syncMissionMutation(data?.mission);return refreshDynamic(true)},onOpen:owned=>openMission(owned),
      onBrowse:()=>$('#mission-close').click()});
    return;
  }
  if(m.status!=='available'&&m.status!=='reserved'){$('#mission-detail').innerHTML=`<div class="eyebrow">${title(m.status)}</div><h2>${esc(m.name)}</h2><p>${m.claimed_by_name?`Claimed by ${esc(m.claimed_by_name)}.`:'No longer available.'}</p>`;return}
  missionPlanner=mountMissionPlanner($('#mission-detail'),m,state.characters,{
    esc,title,portrait:c=>portraitHTML(c,true),metrics:combatMetrics,rating:effectiveStat,
    statLabel:content.perk_tracks?.[m.stat]?.name||title(m.stat),debug:debugEnabled(),
    onChange:updateAnalysis,onClaimDebug:(outcome,selection)=>debugCompleteMission(m.id,outcome,selection)
  });
  if(m.status==='reserved'){$('#mission-detail').insertAdjacentHTML('beforeend','<button id="abandon-contract">Abandon unstarted contract</button>');$('#abandon-contract').onclick=async()=>{if(!confirm('Abandon this contract? Contract Points are not refunded.'))return;try{await rawApi(`/api/missions/${m.id}/abandon`,{method:'POST',body:'{}'});$('#mission-modal').classList.add('hidden');await refreshDynamic(true)}catch(error){toast(error.message)}}}
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
    const p=Object.fromEntries(Object.entries(analysis.probabilities).map(([key,value])=>[key,Number(Number(value).toFixed(2))])),roles=(analysis.roles||[]).map(r=>`<div class="role-result ${r.meets_recommendation?'met':'below'}"><b>${esc(r.label)} · ${r.metric==='constitution'?'CON':r.metric.toUpperCase()} ${r.score}</b><span>Recommended ${r.recommended}${r.metric==='dps'?` · ${String(r.dps_attribute||'str').toUpperCase()} · ${esc(r.weapon||'Unarmed')}`:''}</span></div>`).join('');
    $('#odds').innerHTML=selectedMission.has_decisions?`<div class="tactical-readiness"><b>Choose how this contract unfolds.</b><span>Each decision shows its check, risks and odds. Choices can change rewards, reveal a lead or start a fight.</span></div>${roles?`<div class="role-results">${roles}</div>`:''}${analysis.requirements.length?`<div class="req-checks">${analysis.requirements.map(r=>`<span class="${r.met?'met':'unmet'}">${r.met?'✓':'✕'} ${esc(r.label)}</span>`).join('')}</div>`:''}`:selectedMission.combat_encounter?`<div class="tactical-readiness"><b>Lineup ready for tactical deployment.</b><span>Mission rolls do not decide this outcome. Positioning, objectives, combat actions, and safe extraction determine the result.</span>${selectedMission.combat_critical_condition?`<small><b>Critical Success:</b> ${esc(selectedMission.combat_critical_condition)}</small>`:''}</div>${roles?`<div class="role-results">${roles}</div>`:''}${analysis.requirements.length?`<div class="req-checks">${analysis.requirements.map(r=>`<span class="${r.met?'met':'unmet'}">${r.met?'✓':'✕'} ${esc(r.label)}</span>`).join('')}</div>`:''}`:`<div class="odds-grid"><div class="bad"><b>${p.critical_failure}%</b><span>Critical Failure</span></div><div><b>${p.failure}%</b><span>Failure</span></div><div class="good"><b>${p.success}%</b><span>Success</span></div><div class="crit"><b>${p.critical_success}%</b><span>Critical Success</span></div></div>${roles?`<div class="role-results">${roles}</div>`:''}${analysis.requirements.length?`<div class="req-checks">${analysis.requirements.map(r=>`<span class="${r.met?'met':'unmet'}">${r.met?'✓':'✕'} ${esc(r.label)}</span>`).join('')}</div>`:''}${analysis.secret_event_possible?'<div class="secret-event-hint"><b>Something unusual resonates with this lineup.</b><br>This party has a chance to trigger a secret event.</div>':''}${analysis.critical_path_active?'<div class="critical-path">A special critical-success path is active for this team.</div>':!analysis.critical_success_available?'<div class="critical-locked">Critical Success is locked until this mission’s special criterion is met.</div>':''}`;
    const debugCrit=$('[data-debug-available="critical_success"]');if(debugCrit)debugCrit.disabled=!analysis.critical_success_available;
    btn.disabled=!analysis.claimable||missionClaimPending;btn.onclick=()=>claimMission(selection);
  }catch(e){if(requestId!==analysisSequence||selectedMission?.id!==missionId||!$('#odds'))return;$('#odds').textContent=e.message;btn.disabled=true}
}
async function claimMission(selection){if(missionClaimPending)return;missionClaimPending=true;const button=$('#claim-mission');if(button)button.disabled=true;try{const data=await rawApi(`/api/missions/${selectedMission.id}/claim`,{method:'POST',body:JSON.stringify(selection)});syncMissionMutation(data.mission);playSfx('ui_confirm',.25);toast(data.mission.status==='decision'?'Contract started · choose your approach':data.mission.status==='battle'?'Battle started':'Mission claimed');if(data.mission.status==='decision'){await openDecision(data.mission.id,data.mission,data.decision)}else if(data.mission.status==='battle'){await openBattle(data.mission.id)}else if(data.mission.status==='completed'&&data.mission.result){playOutcomeSound(data.mission.result.outcome);showResult(data.mission.result)}else{$('#mission-modal').classList.add('hidden')}await refreshDynamic(true)}catch(e){toast(e.message);await refreshDynamic(true)}finally{missionClaimPending=false;if($('.mission-planner'))await updateAnalysis()}}

async function openDecision(missionId,mission,initialDecision){
  missionPlanner=null;analysisSequence++;activeBattleView=null;activeDecisionMission=null;syncMusic();
  const data=initialDecision?{decision:initialDecision}:await rawApi(`/api/missions/${missionId}/decision`);
  const current=mission||activeMissions.find(m=>m.id===missionId)||selectedMission;
  activeDecisionMission=current;syncMusic();
  $('#mission-modal').classList.remove('hidden');
  const draw=scene=>{mountDecisionScene($('#mission-detail'),current,scene,{esc,title,onChoose:async payload=>{
    const response=await rawApi(`/api/missions/${missionId}/decision`,{method:'POST',body:JSON.stringify(payload)});
    syncMissionMutation(response.mission);
    playSfx('ui_confirm',.25);
    if(response.decision)draw(response.decision);
    else if(response.mission.status==='battle')await openBattle(missionId);
    else if(response.result){const local=activeMissions.find(m=>m.id===missionId);if(local){local.status='completed';local.result=response.result}playOutcomeSound(response.result.outcome);showResult(response.result)}
    await refreshDynamic(true);
  }});const card=$('#mission-modal .modal-card');card.scrollTop=0;$('#mission-detail').querySelector('[data-scene-choice]:not(:disabled)')?.focus({preventScroll:true})};
  draw(data.decision);
}

async function openBattle(missionId){
  try{activeBattleMissionId=missionId;activeBattleView=null;selectedCombatAction='move';selectedPreparation={mode:'defense',id:null};contextMenuOpen=false;tileActionMenu=null;retreatAllArmed=false;battleZoom=DEFAULT_BATTLE_ZOOM;battleFit=true;battlePan={left:0,top:0};const data=await rawApi(`/api/missions/${missionId}/battle`);$('#mission-modal').classList.remove('hidden');renderBattle(data.battle)}catch(e){toast(e.message)}
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
  const statuses=(unit.statuses||[]).map(status=>{const d=battle.status_definitions?.[status.id]||{name:title(status.id),icon:'•',description:'Status effect'},duration=status.turns??status.duration;return `<span class="status-icon" tabindex="0">${esc(d.icon)}<span class="status-tooltip"><b>${esc(d.name)}</b><small>${esc(d.description)}</small>${duration!=null?`<em>${duration} activation${duration===1?'':'s'} remaining</em>`:''}</span></span>`}).join('');
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
    if(previews.attack)actions.push({label:`${previews.attack.move_to?"Move & Attack":"Attack"} ${livingEnemy.name}`,detail:`${approachDescription(previews.attack)}${previews.attack.chance}% accuracy`,command:attackCommand('attack',livingEnemy.id,previews.attack),icon:'⚔'});
    if(previews.subdue)actions.push({label:`${previews.subdue.move_to?"Move & Subdue":"Subdue"} ${livingEnemy.name}`,detail:`${approachDescription(previews.subdue)}${previews.subdue.chance}% accuracy`,command:attackCommand('subdue',livingEnemy.id,previews.subdue),icon:'◇'});
    if(previews.skill&&current.special)actions.push({label:`${current.special.name}: ${livingEnemy.name}`,detail:`${approachDescription(previews.skill)}${previews.skill.chance}% accuracy`,command:attackCommand('skill',livingEnemy.id,previews.skill),icon:'✦'});
    if((b.throw_profile?.target_ids||[]).includes(livingEnemy.id))actions.push({label:`Throw ${b.throw_profile.payload_name}`,detail:`${b.throw_profile.damage} impact damage`,command:{action:'throw',target_id:livingEnemy.id},icon:'➶'});
  }
  const terrain=b.terrain?.find(t=>t.x===x&&t.y===y&&t.destructible&&!t.destroyed);
  if(terrain&&b.terrain_attack_previews?.[terrain.id]){
    const preview=b.terrain_attack_previews[terrain.id];
    actions.push({label:`${preview.move_to?'Move & Attack':'Attack'} ${terrain.name||title(terrain.kind)}`,detail:approachDescription(preview)||'Destroy this obstacle',command:attackCommand('attack',terrain.id,preview),icon:'?'});
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

function animateBattleMovement(previous,battle,durationFloor=260,movingPositions=new Map()){
  const animationEvents=[...(battle.animation_events||[])];
  battle.animation_events=[];
  if(!previous||previous.encounter_id!==battle.encounter_id)return;
  const field=$('.battlefield');if(!field)return;combatEffects.mount(field);
  const cellWidth=field.getBoundingClientRect().width/battle.width,cellHeight=field.getBoundingClientRect().height/battle.height;
  if(animationEvents.length){
    const actingId=previous.current_unit_id,actingToken=field.querySelector(`[data-battle-unit="${CSS.escape(actingId||'')}"]`);
    if(movingPositions.has(actingId)&&!animationEvents.some(event=>event.unit_id===actingId&&event.type==='movement')){
      const remaining=Math.max(0,...(actingToken?.getAnimations()||[]).map(a=>Number(a.effect.getTiming().duration)-Number(a.currentTime||0)));
      if(remaining>0)animationEvents.unshift({type:'sound',cues:[],duration:Math.min(remaining,350)});
    }
    const animatedUnits=new Set();
    playBattleSounds(battle,animationEvents);
    let delay=0;
    animationEvents.forEach(event=>{
      if(event.type==='death_burst'){
        combatEffects.emit(event,battle,delay+220);
        const before=previous.units?.[event.unit_id],finalToken=field.querySelector(`[data-battle-unit="${CSS.escape(event.unit_id)}"]`);
        if(before&&finalToken&&!window.matchMedia('(prefers-reduced-motion: reduce)').matches){
          const holder=document.createElement('div');holder.innerHTML=battleToken({...before,x:event.x,y:event.y,alive:true,conscious:true,condition:'active'},false,previous);
          const ghost=holder.firstElementChild;
          if(ghost){
            ghost.dataset.battleUnit=`death-ghost-${event.unit_id}`;ghost.style.pointerEvents='none';ghost.style.zIndex='23';field.append(ghost);finalToken.style.visibility='hidden';
            const dying=ghost.animate([{opacity:1,filter:'brightness(1)',offset:0},{opacity:1,filter:'brightness(1.8)',offset:.48},{opacity:.55,filter:'brightness(.7)',offset:.64},{opacity:0,filter:'brightness(.6)',offset:1}],{duration:460,delay,fill:'both'});
            const finish=()=>{ghost.remove();finalToken.style.visibility=''};dying.onfinish=finish;dying.oncancel=finish;
          }
        }
        return;
      }
      if(event.type==='magic_projectile'){combatEffects.emit(event,battle,delay);return}
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
        ],{duration:420,delay,easing:'cubic-bezier(.2,.8,.25,1)',fill:'forwards'});
        trackBattleAnimation(attackerToken,lunge,'is-attacking');
        if(event.hit){
          targetToken.classList.add('is-hit');
          const impactX=Math.sign(target.x-attacker.x)*cellWidth*.12,impactY=Math.sign(target.y-attacker.y)*cellHeight*.12;
          const impact=targetToken.animate([
            {transform:`translate(0,0) scale(${targetScale})`,filter:'brightness(1)',offset:0},
            {transform:`translate(${impactX}px,${impactY}px) scale(${targetScale*.94})`,filter:'brightness(1.8) saturate(.6)',offset:.28},
            {transform:`translate(${-impactX*.25}px,${-impactY*.25}px) scale(${targetScale})`,filter:'brightness(.8)',offset:.55},
            {transform:`translate(0,0) scale(${targetScale})`,filter:'brightness(1)',offset:1},
          ],{duration:300,delay:delay+185,easing:'ease-out',fill:'forwards'});
          trackBattleAnimation(targetToken,impact,'is-hit');
        }
        delay+=490;
        return;
      }
      const unit=battle.units?.[event.unit_id],points=event.points||[];
      const token=field.querySelector(`[data-battle-unit="${CSS.escape(event.unit_id)}"]`);
      if(!unit||!token||!points.length)return;
      const offset=animatedUnits.has(unit.id)?null:restartWalking(token,movingPositions.get(unit.id));
      animatedUnits.add(unit.id);
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
      if(offset)frames[0].transform=`translate(${offset.x}px,${offset.y}px) scale(${baseScale})`;
      token.classList.remove('extracted');
      token.classList.add('is-walking');
      const duration=Math.max(220,Math.min(850,Math.max(1,points.length-1)*155));
      const animation=token.animate(frames,{duration,delay,easing:'ease-in-out',fill:'both'});
      trackBattleAnimation(token,animation,'is-walking',()=>{if(event.extracted)token.classList.add('extracted')});
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
    if(unit.id===battle.current_unit_id&&battle.preview_movement_points?.length)points=battle.preview_movement_points;
    if(points.length<2||points.at(-1).x!==unit.x||points.at(-1).y!==unit.y)points.push({x:unit.x,y:unit.y});
    const offset=restartWalking(token,movingPositions.get(unit.id));
    const baseScale=unit.id===battle.current_unit_id?1.15:1;
    const frames=[];
    for(let index=0;index<points.length-1;index++){
      const from=points[index],to=points[index+1],start=index/(points.length-1),middle=(index+.5)/(points.length-1);
      frames.push({transform:`translate(${(from.x-unit.x)*cellWidth}px, ${(from.y-unit.y)*cellHeight}px) scale(${baseScale}) rotate(${index%2?-2:2}deg)`,offset:start});
      frames.push({transform:`translate(${((from.x+to.x)/2-unit.x)*cellWidth}px, ${((from.y+to.y)/2-unit.y)*cellHeight-5}px) scale(${baseScale*1.025}) rotate(${index%2?2:-2}deg)`,offset:middle});
    }
    frames.push({transform:`translate(0px, 0px) scale(${baseScale}) rotate(0deg)`,offset:1});
    token.classList.add('is-walking');
    if(offset)frames[0].transform=`translate(${offset.x}px,${offset.y}px) scale(${baseScale})`;
    const instantPreview=!!battle.preview_movement_points;
    const duration=instantPreview?Math.max(140,Math.min(800,(points.length-1)*140)):Math.max(durationFloor,Math.min(950,(points.length-1)*190));
    playWalkingSounds(battle,unit,points,duration);
    const animation=token.animate(frames,{duration,easing:instantPreview?'linear':'ease-in-out'});
    trackBattleAnimation(token,animation,'is-walking');
  });
}
function renderBattlePreparation(b){
  const previousBattle=activeBattleView;
  activeDecisionMission=null;activeBattleView=b;syncMusic();
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
  const movingPositions=captureMovingPositions($('.battlefield'));
  patchLiveHTML($('#mission-detail'),`<div class="battle-header preparation-header"><div><div class="eyebrow">DEFENSE PREPARATION</div><h2>${esc(b.name)}</h2><p>Choose a defense, then click a blue tile. Choose a character, then click a gold deployment tile. Placed defenses can be removed for a full refund until battle begins.</p></div><div class="prep-budget"><b>${prep.remaining}</b><span>of ${prep.budget} points left</span><small>${prep.base_budget} base${bonus.length?` · ${bonus.join(' · ')}`:''}</small></div></div><div class="battle-layout"><div class="battle-viewport" id="battle-viewport"><div class="battlefield preparing terrain-style-custom-painted theme-${b.theme||'wilds'}" style="--battle-w:${b.width};--battle-h:${b.height};--battle-scale-width:${battleZoom*100}%;--battle-scale-min:${Math.round(b.width*72*battleZoom)}px">${cells}${elevations}${decorations}${terrain}${units}</div></div><aside class="battle-sidebar prep-sidebar"><div class="battle-camera"><b>Map view</b><button data-battle-fit title="Fit the entire map without stretching">Fit map</button><button data-battle-zoom="out">−</button><button data-battle-zoom="reset">${battleFit?'50% view':Math.round(battleZoom*100)+'%'}</button><button data-battle-zoom="in">+</button></div><section><h3>Field defenses</h3><div class="prep-options">${options}</div></section><section><h3>Deploy party</h3><div class="prep-units">${deployButtons}</div></section><button id="start-defense" class="primary big">Start Defense</button><div class="prep-legend"><span><i class="prep-swatch"></i>Defense zone</span><span><i class="deploy-swatch"></i>Deployment zone</span></div><div class="battle-log">${(b.log||[]).slice().reverse().map(line=>`<p>${esc(line)}</p>`).join('')}</div></aside></div>`);
  $$('[data-prep-defense]').forEach(button=>button.onclick=()=>{selectedPreparation={mode:'defense',id:button.dataset.prepDefense};renderBattlePreparation(b)});
  $$('[data-prep-unit]').forEach(button=>button.onclick=()=>{selectedPreparation={mode:'deploy',id:button.dataset.prepUnit};renderBattlePreparation(b)});
  $$('[data-battle-unit]').forEach(token=>{const unit=b.units[token.dataset.battleUnit];if(unit?.team==='player'&&!unit.defense_objective)token.onclick=e=>{e.stopPropagation();selectedPreparation={mode:'deploy',id:unit.id};renderBattlePreparation(b)}});
  $$('[data-battle-cell]').forEach(cell=>cell.onclick=()=>{if(combatRequestPending)return;const [x,y]=cell.dataset.battleCell.split(',').map(Number),key=`${x},${y}`;if(selectedPreparation.mode==='defense'&&selectedPreparation.id&&prepZone.has(key))sendCombat({action:'place_defense',placement_id:selectedPreparation.id,x,y});else if(selectedPreparation.mode==='deploy'&&selectedPreparation.id&&deploymentZone.has(key)){const optimistic=structuredClone(b),unit=optimistic.units[selectedPreparation.id];if(unit){unit.x=x;unit.y=y;renderBattlePreparation(optimistic)}sendCombat({action:'deploy_unit',target_id:selectedPreparation.id,x,y})}});
  $$('[data-prep-remove]').forEach(button=>button.onclick=e=>{e.stopPropagation();sendCombat({action:'remove_defense',target_id:button.dataset.prepRemove})});
  $('#start-defense').onclick=()=>sendCombat({action:'start_battle'});
  combatEffects.mount($('.battlefield'));
  $$('[data-battle-zoom]').forEach(button=>button.onclick=()=>{changeBattleZoom(b,button.dataset.battleZoom);renderBattlePreparation(b)});
  const fitButton=$('[data-battle-fit]');if(fitButton)fitButton.onclick=()=>{battleFit=true;renderBattlePreparation(b)};updateBattleCamera(b);
  requestAnimationFrame(()=>animateBattleMovement(previousBattle,b,140,movingPositions));
}
function renderBattle(b){
  if(activeBattleView?.current_unit_id!==b.current_unit_id)selectedCombatAction='move';
  if(b.status==='preparing'){renderBattlePreparation(b);return}
  const previousBattle=activeBattleView;
  const previousViewport=$('#battle-viewport');
  if(previousViewport)battlePan={left:previousViewport.scrollLeft,top:previousViewport.scrollTop};
  b=selectBattleSkill(b,selectedGearSkills.get(`${b.seed}:${b.current_unit_id}`));
  activeDecisionMission=null;activeBattleView=b;syncMusic();
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
  const victoryPrompt=victoryMarkup(b,{expanded:expandedVictory.has(b.seed),escape:esc});
  const usedMaterials=[...new Set((b.ground_tiles||[]).map(tile=>tile.material))].map(material=>{const info=groundMaterials[material]||{name:title(material),description:''};return `<span title="${esc(info.description||'')}"><i class="ground-swatch ground-${material}"></i>${esc(info.name)}</span>`}).join('');
  const mapLegend=`<div class="battle-map-legend"><b>Terrain</b><div>${usedMaterials}<span title="Higher terrain affects movement and physical accuracy"><i class="legend-height">▲</i>Elevation</span><span title="Guild extraction region"><i class="legend-exit">↙</i>Exit</span></div></div>`;
  const actionHelp={move:`Choose any green tile. Path numbers show cumulative movement cost.${throwProfile?` Carrying ${throwProfile.payload_name} applies a ${current?.carried_payload_penalty||0}-point movement penalty from STR versus weight.`:''} Shallow water and rubble cost 2. Uphill movement costs 2 per level and a single step can climb at most 2 levels.`,attack:'Hover a target to preview your approach. Click a reachable target outside weapon range, then choose Move & Attack to commit. After attacking, controls return to Move. Walls and gates can also be attacked.',subdue:'Make a reduced-damage adjacent attack to knock the target unconscious. Hover to preview an approach; choose Move & Subdue to commit. Requires an unarmed or blunt-capable weapon. Returns to Move after use.',throw:throwProfile?`Throw ${throwProfile.payload_name} at an enemy. STR ${throwProfile.strength} against weight ${throwProfile.weight} gives range ${throwProfile.range} and ${throwProfile.damage} base impact before armor. The payload lands beside the target.`:'Pick up a portable object or carry an unconscious body before throwing.',skill:`${special?.description||'No combat skill is equipped.'} This commits movement and ends the activation.`,context:'Show actions available from the current tile, including objectives, portable objects, bodies, carried units, and extraction handoff.',carry:'Select an adjacent unconscious unit or corpse. The movement penalty is calculated from the carrier’s STR and the target’s weight.',drop:'Put the carried payload into the first safe adjacent tile.',extract_body:'After holding an EXIT for one activation, hand the carried body or prisoner over for free. The carrier may then leave or continue fighting.',interact:'Use an adjacent objective or pick up a portable battlefield object.',guard:'End this activation in a defensive stance. The next incoming hit deals half damage.',end_turn:'End this activation without attacking or gaining Guard.',leave:`Leave through ${b.extraction?.name||'the exit'}. End one activation on an EXIT tile first; Leave becomes available on that character’s next activation.`,retreat_all:'Order every guild fighter to path toward the nearest exit, hold there for one turn, and then leave automatically. Before securing the required objective this concedes the mission; afterward it preserves the victory.'};
  if(current?.gear_rules?.guard_heal)actionHelp.guard+=` Equipped gear also restores up to ${current.gear_rules.guard_heal} HP.`;
  if(current?.gear_rules?.subdue_gloves)actionHelp.subdue+=' Your Capture Gloves enable this with your equipped weapon.';
  if(current?.gear_rules?.water_walk||current?.gear_rules?.rubble_walk)actionHelp.move+=` Equipped gear lowers ${[current.gear_rules.water_walk?'shallow water':null,current.gear_rules.rubble_walk?'rubble':null].filter(Boolean).join(' and ')} terrain cost to 1. Climbing still costs extra.`;
  if(current?.skills?.length>1)actionHelp.skill+=' All equipped techniques share one use per battle.';
  const movingPositions=captureMovingPositions($('.battlefield'));
  patchLiveHTML($('#mission-detail'),`<div class="battle-header"><div><div class="eyebrow">TACTICAL BATTLE · ROUND ${b.round}</div><h2>${esc(b.name)}</h2>${currentActor}</div><div class="battle-objectives"><b>Objectives</b><ul>${objectives}</ul></div></div><div class="turn-order"><b>Turn order</b><div>${turnOrder}</div></div><div class="battle-layout"><div class="battle-map-stage"><div class="battle-viewport" id="battle-viewport"><div class="battlefield terrain-style-custom-painted theme-${b.theme||'wilds'} mode-${selectedCombatAction} ${contextMenuOpen?'context-open':''}" style="--battle-w:${b.width};--battle-h:${b.height};--battle-scale-width:${battleZoom*100}%;--battle-scale-min:${Math.round(b.width*72*battleZoom)}px">${cells}${elevations}${decorations}${terrain}${objects}${units}${bodyMarkers}${tileMenu}</div></div>${victoryPrompt}</div><aside class="battle-sidebar"><div class="battle-camera"><b>Map view</b><button data-battle-fit title="Fit the entire map without stretching">Fit map</button><button data-battle-zoom="out" title="Zoom out">−</button><button data-battle-zoom="reset" title="Switch to 50% zoom">${battleFit?'50% view':Math.round(battleZoom*100)+'%'}</button><button data-battle-zoom="in" title="Zoom in">+</button><small>Middle-click to auto-scroll · wheel to scroll</small></div>${mapLegend}${current&&!current.player_avatar?`<p class="loyalty-note" title="Checked once per activation. Personality decides behavior.">${current.loyalty??100} loyalty - ${100-(current.loyalty??100)}% independent-turn chance</p>`:''}<div class="combat-actions ${!current?'combat-locked':''}"><button data-combat-mode="move" data-description="${esc(actionHelp.move)}" title="${esc(actionHelp.move)}" class="${selectedCombatAction==='move'?'active':''}">${combatActionArt('move')}<span><kbd>M</kbd> Move</span></button><button data-combat-mode="attack" data-description="${esc(actionHelp.attack)}" title="${esc(actionHelp.attack)}" class="${selectedCombatAction==='attack'?'active':''}" ${current?.acted?'disabled':''}>${combatActionArt('attack')}<span><kbd>A</kbd> Attack</span></button><button data-combat-mode="subdue" data-description="${esc(actionHelp.subdue)}" title="${esc(actionHelp.subdue)}" class="${selectedCombatAction==='subdue'?'active':''}" ${b.can_subdue?'':'disabled'}>${combatActionArt('subdue')}<span><kbd>N</kbd> Subdue</span></button><button data-combat-mode="throw" data-description="${esc(actionHelp.throw)}" title="${esc(actionHelp.throw)}" class="${selectedCombatAction==='throw'?'active':''}" ${throwProfile&&!current?.acted?'':'disabled'}>${combatActionArt('throw')}<span><kbd>T</kbd> Throw</span></button>${skillButton}${skillPicker(current,esc)}<button data-combat-action="guard" data-description="${esc(actionHelp.guard)}" title="${esc(actionHelp.guard)}" ${current?.acted?'disabled':''}>${combatActionArt('guard')}<span><kbd>G</kbd> Guard</span></button><button data-context-toggle data-description="${esc(actionHelp.context)}" title="${esc(actionHelp.context)}" class="${contextMenuOpen?'active':''}" ${contextActions.length?'':'disabled'}>${combatActionArt('interact')}<span><kbd>I</kbd> Actions <span class="action-count">${contextActions.length}</span></span></button><button data-combat-action="end_turn" data-description="${esc(actionHelp.end_turn)}" title="${esc(actionHelp.end_turn)}"><span><kbd>Space</kbd> End Turn</span></button><button data-combat-action="leave" data-description="${esc(actionHelp.leave)}" title="${esc(actionHelp.leave)}" class="leave-map" ${b.can_extract?'':'disabled'}>${combatActionArt('exit')}<span>Leave Map</span></button><button data-combat-action="retreat_all" data-description="${esc(actionHelp.retreat_all)}" title="${esc(actionHelp.retreat_all)}" class="retreat-all ${retreatAllArmed?'armed':''}">${combatActionArt('exit')}<span><kbd>R</kbd> ${retreatAllArmed?'Confirm Retreat All':'Retreat All'}</span></button></div><small class="combat-hotkey-note">Keyboard: M Move · A Attack · N Subdue · T Throw · S Skill · I Actions · G Guard · Space End Turn</small>${contextPanel}<div id="combat-action-help" class="combat-action-help">${esc(actionHelp[selectedCombatAction]||actionHelp.move)}</div><div class="auto-controls"><select id="battle-tactic"><option value="balanced">Balanced</option><option value="objective">Seek Objectives</option><option value="defensive">Defensive</option></select><button id="auto-step">Auto One Turn</button><button id="auto-resolve">Auto Resolve Battle</button></div><div class="battle-log">${(b.log||[]).slice().reverse().map(line=>`<p>${esc(line)}</p>`).join('')}</div></aside></div>`);
  $$('[data-combat-mode]').forEach(btn=>btn.onclick=()=>{retreatAllArmed=false;contextMenuOpen=false;tileActionMenu=null;selectedCombatAction=btn.dataset.combatMode;renderBattle(b)});
  const technique=$('#battle-gear-skill');if(technique)technique.onchange=()=>{selectedGearSkills.set(`${b.seed}:${b.current_unit_id}`,technique.value);selectedCombatAction='skill';tileActionMenu=null;renderBattle(b)};
  combatEffects.mount($('.battlefield'));
  $$('[data-battle-zoom]').forEach(button=>button.onclick=()=>{changeBattleZoom(b,button.dataset.battleZoom);renderBattle(b)});
  const fitButton=$('[data-battle-fit]');if(fitButton)fitButton.onclick=()=>{battleFit=true;renderBattle(b)};updateBattleCamera(b);
  const viewport=$('#battle-viewport');
  if(viewport){viewport.scrollLeft=battlePan.left;viewport.scrollTop=battlePan.top;viewport.onscroll=()=>{battlePan={left:viewport.scrollLeft,top:viewport.scrollTop}}}
  const expandVictory=$('[data-victory-expand]');if(expandVictory)expandVictory.onclick=()=>{expandedVictory.add(b.seed);renderBattle(b)};
  const minimizeVictory=$('[data-victory-minimize]');if(minimizeVictory)minimizeVictory.onclick=()=>{expandedVictory.delete(b.seed);renderBattle(b)};
  const contextToggle=$('[data-context-toggle]');if(contextToggle)contextToggle.onclick=()=>{retreatAllArmed=false;contextMenuOpen=!contextMenuOpen;renderBattle(b)};
  $$('[data-context-action]').forEach(btn=>btn.onclick=()=>{const entry=contextActions[Number(btn.dataset.contextAction)];if(!entry)return;contextMenuOpen=false;retreatAllArmed=false;sendCombat(entry.command)});
  $$('[data-tile-action]').forEach(button=>button.onclick=e=>{e.stopPropagation();const entry=tileActions[Number(button.dataset.tileAction)];if(!entry)return;tileActionMenu=null;sendCombat(entry.command,entry.nextMode)});
  $$('.combat-actions button').forEach(btn=>{btn.onmouseenter=()=>{$('#combat-action-help').textContent=btn.dataset.description||''};btn.onmouseleave=()=>{$('#combat-action-help').textContent=retreatAllArmed?'Warning: Retreat All automatically withdraws the entire party and cannot be cancelled once confirmed.':actionHelp[selectedCombatAction]||actionHelp.move}});
  $$('[data-combat-action]').forEach(btn=>btn.onclick=()=>{const action=btn.dataset.combatAction;if(action==='continue_pursuit')expandedVictory.delete(b.seed);if(action==='retreat_all'){if(!retreatAllArmed){retreatAllArmed=true;contextMenuOpen=false;renderBattle(b);$('#combat-action-help').textContent='Warning: Retreat All automatically withdraws the entire party and cannot be cancelled once confirmed. Click again or press R again to confirm.';return}retreatAllArmed=false}else{retreatAllArmed=false;contextMenuOpen=false}sendCombat({action})});
  $$('[data-battle-cell]').forEach(cell=>cell.onclick=()=>{const [x,y]=cell.dataset.battleCell.split(',').map(Number),actions=tileActionsForBattle(b,x,y),ambiguous=actions.length>1||Object.values(b.units||{}).some(unit=>unit.x===x&&unit.y===y&&unit.conscious===false&&!unit.extracted&&!unit.carried_by);retreatAllArmed=false;contextMenuOpen=false;if(ambiguous){tileActionMenu={x,y};renderBattle(b);return}tileActionMenu=null;if(actions.length===1){sendCombat(actions[0].command,actions[0].nextMode);return}renderBattle(b)});
  $$('[data-battle-unit]').forEach(token=>token.onclick=e=>{e.stopPropagation();const target=b.units[token.dataset.battleUnit];if(target.team==='enemy'&&target.conscious!==false&&['attack','skill','subdue'].includes(selectedCombatAction)&&b.attack_previews?.[target.id]?.[selectedCombatAction]){tileActionMenu=null;retreatAllArmed=false;const preview=b.attack_previews[target.id][selectedCombatAction];if(preview.move_to){tileActionMenu={x:target.x,y:target.y};renderBattle(b);return}sendCombat(attackCommand(selectedCombatAction,target.id,preview));return}if(target.team==='enemy'&&target.conscious!==false&&selectedCombatAction==='throw'&&throwTargets.has(target.id)){tileActionMenu=null;retreatAllArmed=false;sendCombat({action:'throw',target_id:target.id});return}const actions=tileActionsForBattle(b,target.x,target.y);if(actions.length){contextMenuOpen=false;tileActionMenu={x:target.x,y:target.y};renderBattle(b);return}tileActionMenu=null;if(contextMenuOpen){const entry=contextActions.find(item=>item.command?.target_id===target.id);if(entry){contextMenuOpen=false;sendCombat(entry.command)}}});
  $$('[data-battle-object]').forEach(object=>object.onclick=e=>{e.stopPropagation();const target=b.objects?.[object.dataset.battleObject],tile=target?`${target.x},${target.y}`:'';if(selectedCombatAction==='move'&&target&&!target.blocking&&reachable.has(tile)){tileActionMenu=null;retreatAllArmed=false;sendCombat({action:'move',x:target.x,y:target.y});return}if(contextMenuOpen){const entry=contextActions.find(item=>item.command?.target_id===object.dataset.battleObject);if(entry){contextMenuOpen=false;tileActionMenu=null;retreatAllArmed=false;sendCombat(entry.command);return}}const actions=target?tileActionsForBattle(b,target.x,target.y):[];tileActionMenu=actions.length?{x:target.x,y:target.y}:null;renderBattle(b)});
  $$('[data-battle-terrain]').forEach(tile=>tile.onclick=e=>{e.stopPropagation();if(selectedCombatAction==='attack'&&terrainTargets.has(tile.dataset.battleTerrain)){contextMenuOpen=false;tileActionMenu=null;retreatAllArmed=false;const preview=b.terrain_attack_previews?.[tile.dataset.battleTerrain];if(preview?.move_to){const target=b.terrain.find(t=>t.id===tile.dataset.battleTerrain);tileActionMenu={x:target.x,y:target.y};renderBattle(b);return}sendCombat(attackCommand('attack',tile.dataset.battleTerrain,preview));return}const target=b.terrain?.find(entry=>entry.id===tile.dataset.battleTerrain),actions=target?tileActionsForBattle(b,target.x,target.y):[];tileActionMenu=actions.length?{x:target.x,y:target.y}:null;renderBattle(b)});
  $('#auto-step').onclick=()=>{retreatAllArmed=false;sendCombatAuto(false)};$('#auto-resolve').onclick=()=>{retreatAllArmed=false;sendCombatAuto(true)};
  const clearApproach=()=>{
    $$('.attack-approach-path,.attack-approach-stop').forEach(cell=>{cell.classList.remove('attack-approach-path','attack-approach-stop');cell.querySelector('.approach-step')?.remove()});
  };
  const showApproach=(targetId,mode=selectedCombatAction)=>{
    clearApproach();const preview=b.attack_previews?.[targetId]?.[mode]||(mode==='attack'?b.terrain_attack_previews?.[targetId]:null);
    if(!preview?.move_to)return;
    for(const point of preview.path||[]){
      const cell=$(`[data-battle-cell="${point.x},${point.y}"]`);if(!cell)continue;
      cell.classList.add('attack-approach-path');const step=document.createElement('span');step.className='approach-step';step.textContent=point.cost;cell.append(step);
    }
    $(`[data-battle-cell="${preview.move_to.x},${preview.move_to.y}"]`)?.classList.add('attack-approach-stop');
    const target=b.units?.[targetId]||b.terrain?.find(t=>t.id===targetId);
    $('#combat-action-help').textContent=`${approachDescription(preview)}${mode==='skill'?current?.special?.name:title(mode)} ${target?.name||'target'}. Click the target, then confirm the approach.`;
  };
  $$('[data-battle-unit],[data-battle-terrain]').forEach(token=>{
    token.onmouseenter=()=>showApproach(token.dataset.battleUnit||token.dataset.battleTerrain);
    token.onmouseleave=()=>{if(!tileActionMenu){clearApproach();$('#combat-action-help').textContent=actionHelp[selectedCombatAction]||actionHelp.move}};
  });
  $$('[data-tile-action]').forEach(button=>{
    const entry=tileActions[Number(button.dataset.tileAction)];
    button.onmouseenter=()=>showApproach(entry?.command?.target_id,entry?.command?.action);
    button.onfocus=button.onmouseenter;
  });
  if(tileActionMenu){const entry=tileActions.find(a=>a.command.action===selectedCombatAction);if(entry)showApproach(entry.command.target_id,entry.command.action)}
  if(b.preview_movement_points)animateBattleMovement(previousBattle,b,260,movingPositions);
  else requestAnimationFrame(()=>{if(activeBattleView===b)animateBattleMovement(previousBattle,b,260,movingPositions)});
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
  if(command.action==='skill'&&activeBattleView?.units?.[activeBattleView.current_unit_id]?.special)command={...command,skill_id:activeBattleView.units[activeBattleView.current_unit_id].special.id};
  const movementContext=`${activeBattleMissionId}:${activeBattleView?.current_unit_id}:${activeBattleView?.round}`;
  const requestMissionId=activeBattleMissionId;
  if(command.action==='move'&&(!combatRequestPending||inFlightCombatAction==='move')){
    const field=$('.battlefield'),token=field?.querySelector(`[data-battle-unit="${CSS.escape(activeBattleView?.current_unit_id||'')}"]`);
    const current=activeBattleView?.units?.[activeBattleView.current_unit_id];
    if(token&&field&&current&&(current.x!==command.x||current.y!==command.y)){
      const rect=field.getBoundingClientRect(),visual=token.getBoundingClientRect();
      const position={x:(visual.x+visual.width/2-rect.x)/(rect.width/activeBattleView.width)-.5,y:(visual.y+visual.height/2-rect.y)/(rect.height/activeBattleView.height)-.5};
      const preview=previewMovement(activeBattleView,{x:command.x,y:command.y},position);
      if(preview)renderBattle(preview);
    }
  }
  if(combatRequestPending){if(command.action==='move'&&inFlightCombatAction==='move')latestMovement.remember(command,movementContext);return}
  if(command.action!=='move')latestMovement.clear();
  combatRequestPending=true;inFlightCombatAction=command.action;
  try{
    const data=await rawApi(`/api/missions/${activeBattleMissionId}/battle/command`,{method:'POST',body:JSON.stringify(command)});
    if(activeBattleMissionId!==requestMissionId||!activeBattleView||$('#mission-modal').classList.contains('hidden'))return;
    // An older acknowledgement must not pull the displayed unit away from the
    // newest click while that destination is waiting to be sent.
    if(command.action==='move'&&latestMovement.peek(movementContext)&&data.battle?.current_unit_id===activeBattleView.current_unit_id&&data.battle?.round===activeBattleView.round)return;
    tileActionMenu=null;
    selectedCombatAction=nextCombatMode(command.action,nextMode,selectedCombatAction);
    if(data.result){syncMissionMutation({...activeMissions.find(m=>m.id===activeBattleMissionId),id:activeBattleMissionId,status:'completed',result:data.result});const soundDuration=playBattleSounds(data.battle);activeBattleView=null;retreatAllArmed=false;playOutcomeSound(data.result.outcome,soundDuration);showResult(data.result);await refreshDynamic(true);return}
    const optimisticDeployment=command.action==='deploy_unit'&&activeBattleView?.status==='preparing'&&activeBattleView.units?.[command.target_id]?.x===command.x&&activeBattleView.units?.[command.target_id]?.y===command.y;
    if(optimisticDeployment){
      activeBattleView=data.battle;
      const log=$('.battle-log');if(log)log.innerHTML=(data.battle.log||[]).slice().reverse().map(line=>`<p>${esc(line)}</p>`).join('');
      return;
    }
    renderBattle(data.battle);
  }catch(e){
    latestMovement.clear();
    toast(e.message);
    if(activeBattleMissionId===requestMissionId&&activeBattleView&&!$('#mission-modal').classList.contains('hidden'))try{const fresh=await rawApi(`/api/missions/${requestMissionId}/battle`);if(activeBattleMissionId===requestMissionId&&activeBattleView&&!$('#mission-modal').classList.contains('hidden'))renderBattle(fresh.battle)}catch{}
  }finally{
    combatRequestPending=false;inFlightCombatAction=null;
    const pending=latestMovement.take(`${activeBattleMissionId}:${activeBattleView?.current_unit_id}:${activeBattleView?.round}`);
    if(pending&&activeBattleView?.status==='active'&&!$('#mission-modal').classList.contains('hidden'))sendCombat(pending);
  }
}
async function sendCombatAuto(resolveAll){if(combatRequestPending)return;combatRequestPending=true;try{const tactic=$('#battle-tactic')?.value||'balanced',data=await rawApi(`/api/missions/${activeBattleMissionId}/battle/auto`,{method:'POST',body:JSON.stringify({tactic,resolve_all:resolveAll})});tileActionMenu=null;selectedCombatAction='move';if(data.result){syncMissionMutation({...activeMissions.find(m=>m.id===activeBattleMissionId),id:activeBattleMissionId,status:'completed',result:data.result});const soundDuration=resolveAll?0:playBattleSounds(data.battle);activeBattleView=null;retreatAllArmed=false;playOutcomeSound(data.result.outcome,soundDuration);showResult(data.result);await refreshDynamic(true)}else renderBattle(data.battle)}catch(e){toast(e.message)}finally{combatRequestPending=false}}
$('#mission-close').onclick=()=>{latestMovement.clear();retreatAllArmed=false;tileActionMenu=null;activeBattleView=null;activeDecisionMission=null;$('#mission-modal').classList.add('hidden');syncMusic();renderVisiblePanels()};
$('#sound-settings-open').onclick=()=>{closeAudioSettings?.();closeAudioSettings=mountAudioSettings($('#sound-settings-content'),audioMixer,name=>playSfx(name,name.startsWith('mission_')?.5:name.startsWith('ui_')?.16:.5));$('#sound-settings-modal').showModal()};
$('#sound-settings-close').onclick=()=>$('#sound-settings-modal').close();
$('#sound-settings-modal').addEventListener('close',()=>{closeAudioSettings?.();closeAudioSettings=null});
$('#sound-settings-modal').addEventListener('click',event=>{if(event.target===$('#sound-settings-modal')){const rect=event.target.getBoundingClientRect();if(event.clientX<rect.left||event.clientX>rect.right||event.clientY<rect.top||event.clientY>rect.bottom)event.target.close()}});
function closePortraitViewer(){$('#portrait-lightbox').classList.add('hidden');$('#portrait-lightbox-image').src=''}
document.addEventListener('click',event=>{const portrait=event.target.closest?.('[data-portrait-view]');if(!portrait)return;event.preventDefault();event.stopPropagation();$('#portrait-lightbox-image').src=portrait.dataset.portraitView;$('#portrait-lightbox-image').alt=portrait.dataset.portraitName;$('#portrait-lightbox-name').textContent=portrait.dataset.portraitName;$('#portrait-lightbox').classList.remove('hidden')},true);
$('#portrait-lightbox-close').onclick=closePortraitViewer;$('#portrait-lightbox').onclick=event=>{if(event.target===$('#portrait-lightbox'))closePortraitViewer()};document.addEventListener('keydown',event=>{if(event.key==='Escape')closePortraitViewer()});
function showResult(r){
  if(!r)return;
  missionPlanner=null;analysisSequence++;activeBattleView=null;activeDecisionMission=null;syncMusic();
  renderVisiblePanels();
  const rw=r.rewards||{},bits=[];
  if(rw.gold)bits.push(`+${rw.gold} Gold`);
  Object.entries(rw.materials||{}).forEach(([k,v])=>bits.push(`+${v} ${title(k)}`));
  (rw.items||[]).forEach(x=>{const item=content.items[x];bits.push(item?{icon:iconPath(x),text:`${item.name} · ${title(item.rarity||'common')}${item.granted_perks?.length?` · grants ${item.granted_perks.map(p=>content.standalone_perks?.[p]?.name||title(p)).join(', ')}`:''}`} :x)});
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
  $('#mission-detail').innerHTML=`<div class="eyebrow">MISSION AFTERMATH${r.debug_forced?' · DEBUG FORCED':''}</div><h2>${esc(r.mission)}</h2><div class="aftermath-heading"><span class="outcome ${r.outcome}">${title(r.outcome)}</span><small>The choices, consequences, and rewards of this expedition.</small></div><div class="aftermath-layout"><section class="aftermath-story"><div class="mission-story">${story.map(p=>`<p>${esc(p)}</p>`).join('')}</div>${r.special_events?.length?`<div class="special-event"><b>Special event</b><br>${r.special_events.map(esc).join('<br>')}</div>`:''}${r.board_followups?.length?`<div class="world-consequence"><b>New leads</b><br>${r.board_followups.map(x=>esc(x.name)).join('<br>')}</div>`:''}${r.chain_unlocked?.length?`<div class="chain-unlocked"><b>Follow-ups ready in Private Contracts</b><br>${r.chain_unlocked.map(x=>`<button class="private-followup-link" data-open-followup="${esc(x.mission_id)}">${esc(x.name)} → <small>${countdown(x.expires_at)} to claim</small></button>`).join('')}</div>`:''}</section><aside class="aftermath-rewards"><h3>Recovered & earned</h3><div class="reward-list">${bits.length?bits.map(x=>`<div>${typeof x==='object'?`<img class="aftermath-item-icon" src="${esc(x.icon)}" alt="">${esc(x.text)}`:esc(x)}</div>`).join(''):'<div>No rewards recovered.</div>'}</div></aside></div><details class="aftermath-details"><summary>Checks & expedition details</summary>${resolutionRoll}${sceneRolls}${roles?`<div class="role-aftermath">${roles}</div>`:''}${battleReport}</details>${rolls?`<details class="aftermath-details"><summary>Loot chances & rolls</summary><div class="loot-rolls">${rolls}</div></details>`:''}`;
  $('#mission-modal .modal-card').scrollTop=0;
  $$('[data-open-followup]').forEach(button=>button.onclick=async()=>{button.disabled=true;await refreshDynamic(true);const mission=privateContracts.find(m=>m.id===button.dataset.openFollowup);if(mission)openMission(mission);else{toast('This contract is already claimed or has expired');button.disabled=false}});
}

function placementType(){
  if(buildMode)return buildMode;
  if(moveModeBuildingId)return state.buildings.find(b=>b.id===moveModeBuildingId)?.type||null;
  return null;
}
function placementValid(type,x,y,ignoreId=null){
  const d=content.buildings[type];if(!d)return false;
  if(x<0||y<0||x+d.w>(state.base_size?.w||content.grid.w)||y+d.h>(state.base_size?.h||content.grid.h))return false;
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
  const placed=new Set(state.buildings.map(b=>b.type)),available=state.learned_blueprints.filter(id=>!placed.has(id)&&`${content.buildings[id]?.name} ${content.buildings[id]?.description}`.toLowerCase().includes(baseBlueprintQuery));
  if(!available.length){root.innerHTML=baseBlueprintQuery?'<p class="muted small">No matching blueprints.</p>':'<p class="muted small">All learned buildings are already placed.</p>';return}
  patchLiveHTML(root,available.map(id=>{const b=content.buildings[id],cost=Object.entries(b.cost||{}).map(([k,v])=>`${v} ${k}`).join(' · '),aff=Object.entries(b.cost||{}).every(([k,v])=>(state.resources[k]||0)>=v);return `<div class="blueprint"><strong>${esc(b.name)}</strong><small>${esc(b.description)}</small><span><b>${b.w} × ${b.h}</b> footprint · ${cost||'Free'}</span><button data-build="${id}" ${aff?'':'disabled'}>Place ${b.w}×${b.h}</button></div>`}).join(''));
  $$('[data-build]').forEach(b=>b.onclick=()=>{buildMode=b.dataset.build;moveModeBuildingId=null;const d=content.buildings[buildMode];$('#build-mode-label').textContent=`placing ${d.name} (${d.w}×${d.h})`;$('#cancel-build').classList.remove('hidden');renderBaseGrid()})
}
function renderSelectedBuilding(){
  const root=$('#selected-building');const b=state.buildings.find(x=>x.id===selectedBuildingId);
  if(!b){root.classList.add('hidden');root.innerHTML='';return}
  const d=content.buildings[b.type],ranks=content.mission_ranks||['E','D','C','B','A','S'],current=state.mission_rank||'E',next=ranks[ranks.indexOf(current)+1],upgrade=next&&content.guild_hall_upgrades?.[next],canUpgrade=upgrade&&Object.entries(upgrade).every(([k,v])=>(state.resources[k]||0)>=v),cost=upgrade?Object.entries(upgrade).map(([k,v])=>`${v} ${k}`).join(' · '):'';
  const tracks=Object.entries(content.perk_tracks||{}).filter(([,definition])=>definition.facility===b.type);
  const idle=state.characters.filter(c=>c.status==='idle');
  const supplies=Object.values(content.perk_training_items||{}).map(id=>`${content.items[id].name} ×${state.inventory.filter(item=>item.item_id===id).length}`).join(' · ');
  const training=tracks.length?`<div class="training-panel"><div class="eyebrow">PROFICIENCY TRAINING</div>${tracks.map(([track,definition])=>{const currentLevels=idle.map(c=>perkLevel(c,track)),allMaster=idle.length&&currentLevels.every(level=>level==='master');return `<div class="training-row"><b>${esc(definition.name)}</b><select data-trainee="${track}">${idle.map(c=>`<option value="${c.id}">${esc(c.name)} · ${title(perkLevel(c,track))}</option>`).join('')}</select><button data-train="${track}" ${!idle.length||allMaster?'disabled':''}>Train next tier</button></div>`}).join('')}<small>Relevant work builds proficiency. A local Basic instructor costs 8 gold; higher tiers need an idle teacher at that tier. Skilled uses a Training Manual, Expert a Specialist Tome, and Master a Mastery Codex.</small><small>${esc(supplies)}</small></div>`:'';
  const wardenId=(b.assigned||[])[0]||'',warden=state.characters.find(c=>c.id===wardenId);
  const wardenPanel=b.type==='prison_cell'?`<div class="warden-panel"><div class="eyebrow">WARDEN</div><b>${warden?esc(warden.name):'No warden assigned'}</b><small>Warden mechanics will be added later. This assignment reserves the facility worker slot.</small><select id="warden-select"><option value="">— No warden —</option>${idle.map(c=>`<option value="${c.id}" ${c.id===wardenId?'selected':''}>${esc(c.name)}</option>`).join('')}</select><button id="assign-warden">Save Warden</button></div>`:'';
  root.classList.remove('hidden');patchLiveHTML(root,`<div class="eyebrow">SELECTED BUILDING</div><strong>${esc(d.name)}</strong><small>${d.w} × ${d.h} footprint · position ${b.x+1},${b.y+1}</small>${b.type==='guild_hall'?`<div class="guild-rank"><span>Mission visibility</span><b>${current}-Rank</b>${next?`<small>Next: ${next}-Rank · ${cost}</small><button id="upgrade-guild-hall" ${canUpgrade?'':'disabled'}>Unlock ${next}-Rank Missions</button>`:'<small>Maximum rank reached</small>'}</div>`:''}${wardenPanel}${training}<button id="move-building">Move building</button>`);
  $('#move-building').onclick=()=>{moveModeBuildingId=b.id;buildMode=null;$('#build-mode-label').textContent=`moving ${d.name} (${d.w}×${d.h})`;$('#cancel-build').classList.remove('hidden');renderBaseGrid()};
  if($('#upgrade-guild-hall'))$('#upgrade-guild-hall').onclick=async()=>{try{const data=await rawApi('/api/guild-hall/upgrade',{method:'POST',body:'{}'});state=data.state;toast(`${data.rank}-Rank missions unlocked`);renderResources();renderBase();await refreshDynamic(true)}catch(e){toast(e.message)}};
  if($('#assign-warden'))$('#assign-warden').onclick=async()=>{const selected=$('#warden-select').value;try{if(wardenId&&wardenId!==selected){const removed=await rawApi('/api/assign',{method:'POST',body:JSON.stringify({character_id:wardenId,building_id:null})});state=removed.state}if(selected){const assigned=await rawApi('/api/assign',{method:'POST',body:JSON.stringify({character_id:selected,building_id:b.id})});state=assigned.state}toast(selected?'Warden assigned':'Warden removed');renderBase();renderRoster()}catch(e){toast(e.message)}};
  $$('[data-train]').forEach(button=>button.onclick=async()=>{const track=button.dataset.train,charId=$(`[data-trainee="${track}"]`).value;try{const data=await rawApi('/api/train-perk',{method:'POST',body:JSON.stringify({character_id:charId,track})});state=data.state;toast(`${title(data.training.level)} ${content.perk_tracks[track].name} trained`);renderBase();renderRoster();renderMissions()}catch(e){toast(e.message)}});
}
function renderBase(){if(!state||!content)return;const w=state.base_size?.w||12,h=state.base_size?.h||8;$('#base-size-label').textContent=`${w} \u00d7 ${h} SETTLEMENT`;patchLiveHTML($('#base-summary'),`<div><b>${state.buildings.length}</b><small>Facilities</small></div><div><b>${state.characters.filter(c=>c.status==='idle').length}</b><small>Available characters</small></div><div><b>${w} \u00d7 ${h}</b><small>Settlement size</small></div>`);$('#base-blueprint-search').oninput=event=>{baseBlueprintQuery=event.target.value.trim().toLowerCase();renderBlueprints()};renderCampEconomy($('#camp-economy'),{state,content,api:rawApi,onState:value=>{state=value;rosterNeedsRefresh=true;baseNeedsRefresh=true;renderResources();renderVisiblePanels()},notify:toast});renderBlueprints();renderSelectedBuilding();const idle=state.characters.filter(c=>!c.assignment&&c.status==='idle');patchLiveHTML($('#idle-zone'),idle.length?idle.map(c=>portraitHTML(c)).join(''):'<span class="muted small">No idle unassigned characters.</span>');renderBaseGrid();bindDrag()}
function renderBaseGrid(){
  const grid=$('#base-grid');if(!grid||!state)return;const placing=!!placementType();let html='';
  grid.style.gridTemplateColumns=`repeat(${state.base_size?.w||content.grid.w},58px)`;for(let y=0;y<(state.base_size?.h||content.grid.h);y++)for(let x=0;x<(state.base_size?.w||content.grid.w);x++)html+=`<div class="grid-cell ${placing?'build-target':''}" data-x="${x}" data-y="${y}" style="grid-column:${x+1};grid-row:${y+1}"></div>`;
  html+=state.buildings.map(b=>{const d=content.buildings[b.type],chars=(b.assigned||[]).map(id=>state.characters.find(c=>c.id===id)).filter(Boolean);return `<div class="building ${b.type} ${d.w*d.h<=2?'compact-building':''} ${b.id===selectedBuildingId?'selected':''}" data-building="${b.id}" title="${esc(d.name)} - ${esc(d.description)}" style="grid-column:${b.x+1}/span ${d.w};grid-row:${b.y+1}/span ${d.h}"><b>${esc(d.name)}</b><small>${d.w}×${d.h} · ${d.workers?`${chars.length}/${d.workers+(d.production?(b.level||1)-1:0)} assigned`:d.beds?`${d.beds} beds`:'Facility'}</small><div class="assigned">${chars.map(c=>portraitHTML(c,true)).join('')}</div></div>`}).join('');
  if(placing)html+='<div id="placement-ghost" class="placement-ghost hidden"></div>';patchLiveHTML(grid,html);
  $$('.grid-cell').forEach(cell=>{
    cell.onmouseenter=()=>{if(placementType())updatePlacementGhost(Number(cell.dataset.x),Number(cell.dataset.y))};
    cell.onclick=async()=>{const type=placementType();if(!type){selectedBuildingId=null;renderSelectedBuilding();renderBaseGrid();return}const x=Number(cell.dataset.x),y=Number(cell.dataset.y);if(!placementValid(type,x,y,moveModeBuildingId||null))return toast('That footprint does not fit there');try{let d;if(moveModeBuildingId)d=await rawApi('/api/move-building',{method:'POST',body:JSON.stringify({building_id:moveModeBuildingId,x,y})});else d=await rawApi('/api/build',{method:'POST',body:JSON.stringify({blueprint_id:buildMode,x,y})});state=d.state;selectedBuildingId=d.building?.id||selectedBuildingId;stopPlacement();renderBase();renderResources();if(d.building?.type==='guild_hall')await refreshDynamic(true)}catch(e){toast(e.message)}};
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
  patchLiveHTML($('#roster-page-controls'),`<span>${page.total} matching · page ${page.page+1}/${page.pages}</span><button data-roster-page="-1" ${page.page===0?'disabled':''} aria-label="Previous page">←</button><button data-roster-page="1" ${page.page+1===page.pages?'disabled':''} aria-label="Next page">→</button>`);
  $$('[data-roster-page]').forEach(el=>el.onclick=()=>{rosterFilters.page+=Number(el.dataset.rosterPage);$('#roster-list').scrollTop=0;renderRoster()});
  if(!$('#roster-collections'))$('.roster-layout').insertAdjacentHTML('afterend','<div id="roster-collections" class="roster-collections"></div>');
  patchLiveHTML($('#roster-collections'),prisonerCollection+celestialCollection+collection);
  patchLiveHTML($('#roster-list'),page.rows.map(c=>`<div class="roster-card ${c.id===selectedCharacterId?'active':''}" data-roster="${c.id}">${portraitHTML(c,true,true)}<div><b>${esc(c.name)}</b><small>${c.source_kind==='champion'?'CHAMPION · ':c.source_kind==='celestial'?'CELESTIAL · ':''}${esc(c.specialty)} · ${esc(characterStatus(c))}</small></div></div>`).join(''));
  if(!page.rows.length)patchLiveHTML($('#roster-list'),'<p class="muted">No characters match. Change the search or filters.</p>');
  $$('[data-roster-collection]').forEach(details=>details.ontoggle=()=>{rosterCollectionOpen[details.dataset.rosterCollection]=details.open});
  $$('[data-prisoner-action]').forEach(button=>button.onclick=async event=>{event.stopPropagation();const action=button.dataset.prisonerAction,id=button.dataset.prisonerId,prisoner=prisoners.find(p=>p.id===id);if(action==='sell'&&!confirm(`Sell ${prisoner?.name||'this prisoner'} for ${prisoner?.sale_value??8} gold?`))return;const swapId=action==='secure'?document.querySelector(`[data-prisoner-swap="${CSS.escape(id)}"]`)?.value||null:null;try{const data=await rawApi(`/api/prisoners/${encodeURIComponent(id)}/action`,{method:'POST',body:JSON.stringify({action,swap_prisoner_id:swapId})});state=data.state;toast(action==='sell'?`${data.result.name} sold for ${data.result.gold} gold`:action==='secure'?'Prisoner secured':'Prisoner moved to stockade');renderResources();renderRoster();renderBase()}catch(e){toast(e.message)}});
  $$('[data-roster]').forEach(el=>el.onclick=()=>{selectedCharacterId=el.dataset.roster;renderRoster()});
  const c=state.characters.find(x=>x.id===selectedCharacterId);if(!c)return;const metrics=combatMetrics(c);
  const appearance=appearanceDrafts[c.id]||c.appearance||{},raceFamilies=content.races?.[c.race]?.families||[];
  const appearanceOpen=appearanceEditorOpen[c.id]??Object.values(appearance).some(Boolean);
  const appearanceEditor=`<details class="appearance-editor" data-appearance-editor="${c.id}" ${appearanceOpen?'open':''}><summary><b>Appearance</b><span>${c.appearance_source==='portrait'?'Filled from portrait tags':c.appearance_source==='manual'?'Custom description':'Add visible details for story scenes'}</span></summary><div class="appearance-grid"><label>Hair color<input id="appearance-hair-color" value="${esc(appearance.hair_color||'')}" maxlength="48"></label><label>Hair length<input id="appearance-hair-length" value="${esc(appearance.hair_length||'')}" maxlength="48"></label><label>Eye color<input id="appearance-eye-color" value="${esc(appearance.eye_color||'')}" maxlength="48"></label><label>Skin / surface<input id="appearance-skin-tone" value="${esc(appearance.skin_tone||'')}" maxlength="64"></label><label>Build<input id="appearance-build" value="${esc(appearance.build||'')}" maxlength="64"></label><label class="wide">Distinctive features<textarea id="appearance-distinctive-features" maxlength="240">${esc(appearance.distinctive_features||'')}</textarea></label><label class="wide">Natural description used in event prose<textarea id="appearance-summary" maxlength="360" placeholder="A compact visual description; leave blank to assemble one from the fields above.">${esc(appearance.summary||'')}</textarea></label></div><div class="appearance-actions"><button id="save-character-appearance" class="primary">Save Appearance</button>${c.portrait_metadata_available?'<button id="fill-appearance-tags">Fill from portrait tags</button>':''}</div><small>Uploaded override portraits use the description you enter here. Tagged pool portraits can restore their saved fields.</small></details>`;
  const tiered=Object.entries(content.perk_tracks||{}).filter(([track])=>perkRank(c,track)>0).map(([track,d])=>`<div class="perk-card tier-${perkLevel(c,track)}" tabindex="0"><span>${esc(d.name)}</span><b>${title(perkLevel(c,track))}</b><small>+1 ${d.attribute_bonus.toUpperCase()} · rating ${effectiveStat(c,track)}</small><div class="perk-tooltip"><p>${esc(d.description||'A trained proficiency.')}</p><strong>Effect</strong><span>+1 ${d.attribute_bonus.toUpperCase()}. Work in this proficiency improves related gathering by ${15*perkRank(c,track)}% where applicable. Relevant work and expeditions build practice. ${title(perkLevel(c,track))} adds +${perkRank(c,track)} to ${esc(d.name)} mission capability before equipment.</span></div></div>`).join('');
  const standalone=equippedPerks(c).map(([p,item])=>{const racial=Object.entries(content.races||{}).find(([name])=>name.toLowerCase().replaceAll('-','_').replaceAll(' ','_')===p);const d= racial?{name:racial[0],description:racial[1].gameplay.summary,effect:raceEffects(racial[1].gameplay).join('. ')}:content.standalone_perks?.[p]||{name:title(p),description:'A unique characteristic, background, or mission-earned perk.',effect:'Can unlock matching mission conditions and special paths.'};return `<span class="perk-pill" tabindex="0">${esc(d.name)}${item?' ◇':''}<span class="perk-tooltip"><span class="tooltip-description">${esc(d.description)}</span><strong>Effect</strong><span>${esc(d.effect)}${item?` Granted by ${esc(item)} while equipped.`:''}</span></span></span>`}).join('');
  $('#character-detail').innerHTML=`<div class="char-head">${portraitHTML(c,false,true)}<div><div class="eyebrow">${title(c.source_kind||'character')}</div><h2>${esc(c.name)}</h2><div class="tags"><span>${esc(c.race)}</span>${raceFamilies.map(f=>`<span>${esc(f)}</span>`).join('')}${c.gender?`<span>${title(c.gender)}</span>`:''}<span>${esc(c.series)}</span></div></div></div><div class="portrait-editor upload-editor"><label><span>Upload override · stored at max 1200px with a separate 192px thumbnail</span><input id="character-portrait-upload" type="file" accept="image/png,image/jpeg,image/gif,image/webp"></label></div>${c.source_kind==='generic'?`<div class="portrait-pool-control"><span>Assigned pool: ${esc(c.portrait_pool||'none')} · portrait selection locked</span></div>`:''}${c.is_player?`<div class="portrait-editor"><label><span>Portrait URL</span><input id="player-portrait-url" value="${esc(c.portrait||'')}" placeholder="https://..."></label><button id="save-player-portrait">Save Portrait URL</button></div>`:''}${appearanceEditor}<h3>Proficiencies</h3><div class="perk-section">${tiered||'<p class="muted small">No trained proficiencies.</p>'}</div>${standalone?`<div class="standalone-perks"><small>Perks</small><div class="tags">${standalone}</div></div>`:''}<h3>Attributes</h3><div class="stat-grid attributes">${attributeNames.map(a=>`<div data-stat-help tabindex="0"><span>${a.toUpperCase()}</span><b>${effectiveAttribute(c,a)}</b><small>base ${c.attributes?.[a]??5}</small><span class="stat-tooltip"><strong>${a.toUpperCase()}</strong><p>${esc(attributeTotalHelp)}</p><p>${esc(attributeHelp[a])}</p></span></div>`).join('')}</div><div class="combat-ratings"><div data-stat-help tabindex="0"><span>CON</span><b>${metrics.constitution}</b><small>Effective VIT</small><span class="stat-tooltip"><strong>Constitution</strong><p>CON equals effective VIT, including gear and perk bonuses. Tank roles compare this number with their recommendation.</p></span></div><div data-stat-help tabindex="0"><span>DPS</span><span class="stat-tooltip"><strong>Mission damage rating</strong><p>Effective weapon scaling attribute + weapon power + half your Combat capability (rounded down). Uses STR for melee, DEX for ranged or INT for magic. This is a mission role rating, not damage per second or the combat damage formula.</p></span><b>${metrics.dps}</b><small>${metrics.dps_attribute.toUpperCase()} · ${esc(metrics.weapon)}</small></div></div><h3>Equipment</h3>`;
  $('[data-appearance-editor]')?.addEventListener('toggle',event=>{appearanceEditorOpen[event.currentTarget.dataset.appearanceEditor]=event.currentTarget.open});
  const detail=$('#character-detail'),nodes=[...detail.children],panels={};
  for(const tab of ['overview','equipment','appearance','conversation','record']){const panel=document.createElement('section');panel.dataset.rosterPanel=tab;panels[tab]=panel}
  let section='overview';
  for(const node of nodes.slice(1)){
    if(node.tagName==='H3'&&node.textContent.startsWith('Equipment'))section='equipment';
    const appearanceNode=node.matches('.portrait-editor,.portrait-pool-control,.appearance-editor');
    panels[appearanceNode?'appearance':section].append(node);
  }
  const tabs=document.createElement('div');tabs.className='roster-detail-tabs';tabs.innerHTML=['overview','equipment','appearance','conversation','record'].map(tab=>`<button data-roster-tab="${tab}" class="${tab===rosterDetailTab?'active':''}">${tab==='record'?'Service Record':title(tab)}</button>`).join('');detail.append(tabs,...Object.values(panels));
  const switchTab=tab=>{rosterDetailTab=tab;Object.entries(panels).forEach(([key,panel])=>panel.classList.toggle('hidden',key!==tab));tabs.querySelectorAll('button').forEach(button=>button.classList.toggle('active',button.dataset.rosterTab===tab))};
  mountEquipmentBrowser(panels.equipment,{state,content,character:c,preferenceKey:`fortcamp:hide-equipped:${identity.guild_id}:${identity.user_id}`,editable:equipmentEditable,onError:e=>toast(e.message),onEquip:async(slot,instance_id)=>{const data=await rawApi('/api/equip',{method:'POST',body:JSON.stringify({character_id:c.id,slot,instance_id})});state=data.state;renderRoster();renderMissions()}});
  mountServiceRecord(panels.record,c);
  mountRelationships(panels.conversation,{character:c,state,content,onError:e=>toast(e.message),onAction:async payload=>{const data=await rawApi(`/api/characters/${encodeURIComponent(c.id)}/conversation`,{method:'POST',body:JSON.stringify(payload)});state=data.state;return data}});
  tabs.querySelectorAll('button').forEach(button=>button.onclick=()=>switchTab(button.dataset.rosterTab));switchTab(rosterDetailTab);
  detail.querySelector('.char-head').insertAdjacentHTML('afterend',`<div class="roster-status-bar">${esc(characterStatus(c))} · ${esc(c.specialty||'No specialty')} ${c.is_player?'· Your character':''}</div>`);
  const racialProfile=content.races?.[c.race]?.gameplay;
  if(racialProfile)panels.overview.insertAdjacentHTML('afterbegin',`<div class="race-gameplay-card"><h3><img class="race-catalogue-icon" src="${esc(iconPath(c.race,'races'))}" alt="">${esc(c.race)} · Racial identity</h3><p>${esc(racialProfile.summary)}</p><div class="tags">${raceEffects(racialProfile).map(effect=>`<span>${esc(effect)}</span>`).join('')}</div><small>These are derived effects; base attributes do not include HP, movement or evasion modifiers.</small></div>`);
  const appearanceFields=['hair-color','hair-length','eye-color','skin-tone','build','distinctive-features','summary'];
  appearanceFields.forEach(field=>$('#appearance-'+field).oninput=()=>{appearanceDrafts[c.id]=Object.fromEntries(appearanceFields.map(key=>[key.replaceAll('-','_'),$('#appearance-'+key).value]))});
  $('#character-portrait-upload').onchange=async e=>{const file=e.target.files?.[0];if(!file)return;if(file.size>4*1024*1024){toast('Portrait must be 4 MB or smaller');return}const reader=new FileReader();reader.onload=async()=>{try{const data=await rawApi(`/api/characters/${encodeURIComponent(c.id)}/portrait-upload`,{method:'POST',body:JSON.stringify({data_url:reader.result})});state=data.state;toast('Portrait uploaded');renderRoster();renderBase()}catch(err){toast(err.message)}};reader.readAsDataURL(file)};
  $('#save-character-appearance').onclick=async()=>{const payload={hair_color:$('#appearance-hair-color').value,hair_length:$('#appearance-hair-length').value,eye_color:$('#appearance-eye-color').value,skin_tone:$('#appearance-skin-tone').value,build:$('#appearance-build').value,distinctive_features:$('#appearance-distinctive-features').value,summary:$('#appearance-summary').value};try{const d=await rawApi(`/api/characters/${encodeURIComponent(c.id)}/appearance`,{method:'POST',body:JSON.stringify(payload)});state=d.state;delete appearanceDrafts[c.id];toast('Appearance saved');renderRoster()}catch(e){toast(e.message)}};
  if($('#fill-appearance-tags'))$('#fill-appearance-tags').onclick=async()=>{try{const d=await rawApi(`/api/characters/${encodeURIComponent(c.id)}/appearance-from-portrait`,{method:'POST',body:'{}'});state=d.state;delete appearanceDrafts[c.id];toast('Appearance filled from portrait tags');renderRoster()}catch(e){toast(e.message)}};
  if(c.is_player&&$('#save-player-portrait'))$('#save-player-portrait').onclick=async()=>{try{const d=await rawApi('/api/player-character/portrait',{method:'POST',body:JSON.stringify({portrait:$('#player-portrait-url').value.trim()})});state=d.state;toast('Portrait updated');renderRoster();renderBase()}catch(e){toast(e.message)}};
}

const portraitInput=$('#cc-portrait');
if(portraitInput){
  const updateCreatorPortraitPreview=()=>{const box=$('#cc-portrait-preview'),url=portraitInput.value.trim();if(!box)return;box.innerHTML=url?`<img src="${esc(portraitSrc(url))}" onerror="this.outerHTML='<span>Image could not be loaded from that URL.</span>'">`:'<span>Portrait preview</span>'};
  portraitInput.addEventListener('input',updateCreatorPortraitPreview);updateCreatorPortraitPreview();
}

init();



new MutationObserver(()=>{if($('#mission-modal')?.classList.contains('hidden'))combatEffects.pause()}).observe($('#mission-modal'),{attributes:true,attributeFilter:['class']});

mountHoverHelp();
$('#mission-modal').addEventListener('click',event=>{if(event.target===$('#mission-modal'))$('#mission-close').click()});

import {test} from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {runInNewContext} from 'node:vm';
test('acceptance opens returned choices immediately without a second fetch or stale scroll',async()=>{
  const source=readFileSync(new URL('./main.js',import.meta.url),'utf8');
  const functions=source.slice(source.indexOf('async function claimMission('),source.indexOf('async function openBattle('));
  const scene={node_id:'case',revision:0},requests=[],calls=[];
  const card={scrollTop:900},modal={classList:{remove:name=>calls.push(`show:${name}`)}},detail={querySelector:()=>({focus:()=>calls.push('focus')})},button={disabled:false};
  await runInNewContext(functions+'\nclaimMission({party_ids:["player"]})',{
    missionClaimPending:false,missionPlanner:{},analysisSequence:0,activeBattleView:null,
    selectedMission:{id:'ledger'},activeMissions:[],
    $:selector=>({'#claim-mission':button,'#mission-modal':modal,'#mission-modal .modal-card':card,'#mission-detail':detail}[selector]),
    rawApi:async path=>{requests.push(path);return {mission:{id:'ledger',name:'Ledger',status:'decision'},decision:scene}},
    toast:()=>{},playSfx:()=>{},syncMusic:()=>{},esc:v=>v,title:v=>v,
    mountDecisionScene:(_,mission,value)=>{assert.equal(mission.id,'ledger');assert.equal(value,scene);calls.push('choices')},
    refreshDynamic:async()=>calls.push('refresh'),updateAnalysis:async()=>{},
  });
  assert.deepEqual(requests,['/api/missions/ledger/claim']);
  assert.ok(calls.indexOf('choices')<calls.indexOf('refresh'));assert.equal(card.scrollTop,0);
  assert.ok(calls.includes('show:hidden'));assert.ok(calls.includes('focus'));
});

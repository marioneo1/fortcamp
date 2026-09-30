import {test} from 'node:test';
import assert from 'node:assert/strict';
import {missionCard,eventHeader,filterChips,rankSeal,stableBoardHTML} from './mission-board-ui.js';
const mission={id:'one',rank:'D',name:'The Captive Cart',description:'Stop the wagon.',stat:'combat',difficulty:12,duration_seconds:600,party_size:2,mission_form:'rescue',resolution_mode:'combat',reward_preview:['Gold chance','Goblin gear','War Token','Recruit'],requirements:['Skilled combatant']};
test('cards separate possible rewards, requirements and explicit combat disclosure',()=>{
  const html=missionCard(mission,{count:3,claimed:1});
  assert.match(html,/Possible rewards/);assert.match(html,/Gold chance/);assert.match(html,/Required/);assert.match(html,/Inspect &amp;/);assert.match(html,/10 min/);assert.match(html,/3 available/);assert.match(html,/contract-mode.*Combat/);assert.match(html,/\+1 more/);
});
test('hidden combat and secret criteria are not disclosed, and locked cards reveal nothing',()=>{
  const html=missionCard({...mission,resolution_mode:'roll',encounter_plan:{secret:true},secret_team:'bring a vampire'});
  assert.doesNotMatch(html,/contract-mode|secret_team|bring a vampire/);
  assert.equal(missionCard({...mission,locked:true}), '');
});
test('card values are escaped and unsupported forms use an existing fallback',()=>{
  const html=missionCard({...mission,name:'<script>evil</script>',mission_form:'../../bad',reward_preview:['<img onerror="bad">']});
  assert.doesNotMatch(html,/<script>|<img onerror|form_\.\./);assert.match(html,/&lt;script&gt;/);assert.match(html,/form_operation/);
});
test('private deadlines use live countdown targets and rank letters are outside the art',()=>{
  const html=missionCard({...mission,expires_at:12345,private_source:'A saved courier'},{privateContract:true});assert.match(html,/data-private-mission/);assert.match(html,/data-countdown-end="12345"/);assert.match(html,/Only you/);assert.match(rankSeal('S'),/rank_s.png/);assert.match(rankSeal('S'),/<b>S<\/b>/);
});
test('event header and filter chips only expose escaped known information',()=>{
  assert.match(eventHeader(),/THE GUILD IS OPEN/);assert.match(eventHeader({id:'starfall_omen',name:'Starfall',splash:'<danger>'}),/event_starfall_omen/);assert.match(eventHeader({id:'starfall_omen',name:'Starfall',splash:'<danger>'}),/&lt;danger&gt;/);
  assert.match(filterChips({query:'<script>',rank:'C'}),/&lt;script&gt;/);assert.doesNotMatch(filterChips({query:'<script>'}),/<script>/);
});
test('unchanged polls do not rewrite cards or reset a manually collapsed rank',()=>{
  let writes=0;const root={ownerDocument:{activeElement:null},contains:()=>false,set innerHTML(value){writes++}};
  assert.equal(stableBoardHTML(root,'<details data-rank-board="E" open><p>One</p></details>'),true);
  assert.equal(stableBoardHTML(root,'<details data-rank-board="E" ><p>One</p></details>'),false);
  assert.equal(writes,1);assert.equal(stableBoardHTML(root,'<details data-rank-board="E" ><p>Two</p></details>'),true);assert.equal(writes,2);
});

import test from 'node:test';import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';import {runInNewContext} from 'node:vm';
test('phase countdown ticks each second and requests a refresh at the deadline, with a waiting label',()=>{
  const source=readFileSync(new URL('./main.js',import.meta.url),'utf8');
  const fn=source.slice(source.indexOf('function updateLiveCountdowns(){'),source.indexOf('function showGame(){'));
  let now=100,refreshes=0;const phase={dataset:{countdownEnd:'115'},textContent:''},poolClock={textContent:''};
  const context={Date:{now:()=>now*1000},fmtDuration:v=>String(v),countdown:ts=>String(Math.ceil(ts-now)),
    $$:selector=>selector==='[data-countdown-end]'?[phase]:[],$:selector=>selector==='.mission-planner'?null:selector==='[data-phase-countdown]'?phase:poolClock,
    pool:{next_refresh:200,budget:{next_phase_at:115}},activeMissions:[],lastDeadlineRefresh:0,refreshDynamic:()=>refreshes++};
  for(const t of [100,101,102,114]){now=t;runInNewContext(fn+'updateLiveCountdowns()',context);assert.equal(phase.textContent,String(115-t));}
  now=115;runInNewContext(fn+'updateLiveCountdowns()',context);assert.equal(phase.textContent,'Opening…');assert.equal(refreshes,1);
  now=200;runInNewContext(fn+'updateLiveCountdowns()',context);assert.equal(poolClock.textContent,'Refreshing…');
});

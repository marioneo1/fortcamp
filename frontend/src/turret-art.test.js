import test from 'node:test';
import assert from 'node:assert/strict';
import {existsSync} from 'node:fs';
import {isTurret,turretMarkup,turretBearing} from './turret-art.js';
test('Turret has anchored idle/fire/recoil art and destroyed replacement',()=>{const u={entity_kind:'scrap_turret',alive:true};assert.ok(isTurret(u));assert.ok(!isTurret({entity_kind:'companion'}));const html=turretMarkup(u);for(const name of ['idle','fire','recoil']){assert.ok(html.includes('turret_'+name+'.png'));assert.ok(existsSync(new URL('../public/assets/tactical-props-v1/turret_'+name+'.png',import.meta.url)))}const dead=turretMarkup({...u,alive:false});assert.ok(dead.includes('turret_destroyed.png'));assert.ok(!dead.includes('turret_idle.png'));assert.ok(existsSync(new URL('../public/assets/tactical-props-v1/turret_bolt.png',import.meta.url)))});
test('Turret north-facing art points toward target in each cardinal direction',()=>{const o={x:2,y:2};assert.equal(turretBearing(o,{x:2,y:1}),0);assert.equal(turretBearing(o,{x:3,y:2}),90);assert.equal(turretBearing(o,{x:2,y:3}),180);assert.equal(turretBearing(o,{x:1,y:2}),270)});

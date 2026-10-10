import test from 'node:test';
import assert from 'node:assert/strict';
import {existsSync} from 'node:fs';
import {mountMarkup,mountedAnimal,mountedCorpse,motionPartner,pairedMotionFrames,mountAngle,turnMount} from './mount-art.js';
import {skillIcon} from './ability-icons.js';
test('mounted boars use overhead poses, while free boars retain portrait tokens',()=>{
 assert.equal(mountedCorpse({boar_mount:true,alive:false}),false);
 assert.equal(mountedCorpse({boar_mount:true,alive:false,mounted_death:true}),true);
 assert.equal(mountedAnimal({boar_mount:true}),false);
 assert.equal(mountedAnimal({boar_mount:true,rider_id:'rider'}),true);
 for(const direction of ['n','ne','e','se','s','sw','w','nw']){
  const html=mountMarkup({alive:true,mount_facing:direction});
  assert.match(html,/idle_n\.png/);
  assert.match(html,new RegExp(`--mount-angle:${mountAngle(direction)}deg`));
  assert.doesNotMatch(html,/boar-stride/);
  for(const [,url] of html.matchAll(/src="([^"]+)"/g))assert.ok(existsSync(new URL('../public'+url.split('?')[0],import.meta.url)));
 }
 assert.match(mountMarkup({alive:false}),/dead\.png/);
 assert.doesNotMatch(mountMarkup({alive:false}),/boar-stride/);
 assert.match(skillIcon({mount_kind:'mount',self_only:false}),/mount_icon\.png/);
 assert.match(skillIcon({mount_kind:'mount',self_only:true}),/dismount_icon\.png/);
});
test('boar turns by the shortest angle without spinning across the north boundary',()=>{
 let value='0deg';
 const token={querySelector:()=>({style:{getPropertyValue:()=>value,setProperty:(_,v)=>{value=v}}})};
 turnMount(token,1,-1);assert.equal(value,'45deg');
 turnMount(token,1,0);assert.equal(value,'90deg');
 turnMount(token,0,1);assert.equal(value,'180deg');
 turnMount(token,0,0);assert.equal(value,'180deg');
});

test('mounted motion stays paired through knockback, attack and subsequent walking until the actual fall',()=>{
 const previous={units:{r:{animal_mount_id:'b'},b:{rider_id:'r'}}};
 const battle={units:{r:{},b:{}}};
 const timeline=[{start:500,event:{type:'mount_fall',unit_id:'r',mount_id:'b'}}];
 assert.equal(motionPartner('r',previous,battle,timeline,0),'b');
 assert.equal(motionPartner('b',previous,battle,timeline,450),'r');
 assert.equal(motionPartner('r',previous,battle,timeline,500),null);
 const frames=[{transform:'translate(-80px,0px) scale(1)',offset:0},{transform:'translate(0,0) scale(1)',offset:1}];
 const paired=pairedMotionFrames(frames,{x:4,y:2},{x:3,y:2},80,80);
 assert.equal(paired[0].transform,'translate(80px,0px) translate(-80px,0px) scale(1)');
 assert.equal(paired[1].offset,1);
});
test('boarding does not drag the stationary mount before contact',()=>{
 const previous={units:{r:{},b:{}}},battle={units:{r:{animal_mount_id:'b'},b:{rider_id:'r'}}};
 const timeline=[{start:0,duration:250,event:{type:'movement',unit_id:'r',mount_boarding:true}}];
 assert.equal(motionPartner('r',previous,battle,timeline,100),null);
 assert.equal(motionPartner('r',previous,battle,timeline,250),'b');
 assert.equal(motionPartner('b',previous,battle,timeline,250),'r');
});

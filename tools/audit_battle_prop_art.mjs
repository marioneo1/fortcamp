// Run after build_prop_coverage_preview.py; audit the same resolver used by the UI.
import {readFile,writeFile,access} from 'node:fs/promises';
import {paintedObjectSprite,paintedTerrainSprite,paintedDestroyedTerrainSprite} from '../frontend/src/map-object-art.js';
const battles=JSON.parse(await readFile('staging-terrain/overhead-props-v2/coverage-input.json','utf8'));
const registry=JSON.parse(await readFile('frontend/src/map-prop-art.json','utf8'));
const records=[],problems=[];
for(const [encounter,battle] of Object.entries(battles)){
  const entries=[...(battle.decorations||[]).map(item=>({item,type:'decoration',sprite:item.sprite})),
    ...(battle.terrain||[]).map(item=>({item,type:'terrain',sprite:paintedTerrainSprite(item)})),
    ...Object.values(battle.objects||{}).map(item=>({item,type:'object',sprite:paintedObjectSprite(item)})),
    ...(battle.terrain||[]).filter(item=>item.destructible||item.prepared_trap).map(item=>({item,type:'destroyed',sprite:paintedDestroyedTerrainSprite(item)}))];
  for(const {item,type,sprite} of entries){
    // Water is ground, with no separate object image by design.
    if(!sprite&&type==='terrain'&&item.kind==='shallow_water')continue;
    if(!sprite){problems.push({encounter,id:item.id,type,problem:'no sprite assignment'});continue}
    const [layer,name]=sprite.startsWith('structure:')?['structures',sprite.slice(10)]:sprite.startsWith('terrain:')?['mega-terrain-tiles',sprite.slice(8)]:['props',sprite];
    const file=registry[sprite]||`${layer}/${name}.png`;
    try{await access('frontend/public/assets/combat-terrain/'+file)}catch{problems.push({encounter,id:item.id,type,sprite,problem:'missing runtime file'})}
    records.push({encounter,id:item.id,type,sprite,file,overhead:Boolean(registry[sprite])});
  }
}
await writeFile('staging-terrain/overhead-props-v2/coverage-audit.json',JSON.stringify({encounters:Object.keys(battles).length,checks:records.length,problems,legacySprites:[...new Set(records.filter(r=>!r.overhead).map(r=>r.sprite))]},null,2)+'\n');
console.log(JSON.stringify({encounters:Object.keys(battles).length,checks:records.length,problems}));
if(problems.length)process.exitCode=1;

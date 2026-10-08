"""Concise combat copy; full authored mechanics remain in detailed_description."""
SUMMARIES={
 'engineer':{
  'sentry_turret':'Build a tough automatic turret over two working turns; you can maintain three.',
  'heavy_emplacement':'Build a long-range explosive ballista over three working turns; you can maintain one.',
 'dynamite':'Throw dynamite that explodes next turn, damaging and pushing nearby units with a chance to stun.',
  'rapid_assembly':'Make your next turret build this turn instant without ending your movement.',
  'man_the_guns':'Mount a nearby turret to aim stronger, longer-range shots yourself.',
  'overclock':'Fire your mounted turret twice per turn for two turns before it breaks.',
  'scuttle_protocol':'Detonate an owned turret, hurting everyone nearby and ejecting you if mounted.',
  'proximity_charge':'Plant a mine that stops and stuns any unit entering its nearby trigger area.',
 },
 'summoner':{
  'bound_companion':'Choose and place one autonomous Fire, Earth or Grass companion.',
  'wisp_swarm':'Place three fragile flying Wisps that move and attack on their own.',
  'transposition':'Swap yourself with a summon, or swap two summons, while keeping your main action.',
  'spirit_projection':'Strike an enemy once for each owned summon nearby.',
  'sacrifice':'Destroy summons in an area so each explodes, damaging and blinding nearby allies and enemies.',
  'overload':'Triple a summon’s attack and maximum health for three turns, then it dies.',
  'life_pact':'Spend a quarter of your maximum health to heal an injured summon by that amount.',
  'rapid_conjuration':'Summoning becomes a Quick Action so you can still use your main action afterward.',
  'orders':'Give one summon or your whole group an order that lasts until changed.',
 }
}

def summarize(skill):
 for job,rows in SUMMARIES.items():
  kind=skill.get(job+'_kind')
  if kind in rows:
   skill.setdefault('detailed_description',skill.get('description',''))
   skill['description']=rows[kind]
 return skill

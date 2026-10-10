import unittest, random
from copy import deepcopy
from unittest.mock import patch
from backend import combat, enemy_specialties as npc, job_loadouts as jobs, combat_conditions as conditions
from backend import combat_hazard_preview
from backend.game import new_game, _incapacitate_character, RECOVERY_SECONDS
from backend.prison_recruitment import initialize_prisoner
from backend.battle_lab import layout_presets


class SpecialtyTests(unittest.TestCase):
    def test_prison_layouts_reachable_and_consistent_hp_budgets(self):
        total=0
        for mission in ('prison_rival_e','prison_former_e','prison_proof_e'):
            budgets=[]
            for preset in layout_presets('contract:'+mission):
                b=combat.create_contract_battle(new_game({'name':'QA'}),['player'],preset['seed'],mission,True)
                enemies=combat._living(b,'enemy');budgets.append(sum(u['max_hp'] for u in enemies))
                self.assertEqual(len(enemies),2)
                self.assertEqual(len({(u['x'],u['y']) for u in b['units'].values()}),len(b['units']))
                probe=deepcopy(b);walker=probe['units']['player'];walker.update(move=1000,movement_origin=None)
                # Closed usable doors are intentional; verify access after opening them.
                for terrain in probe['terrain']:
                    if terrain.get('kind')=='gate':terrain.update(state='open',blocking=False)
                probe['units']={'player':walker}
                reachable,_=combat._movement_tree(probe,walker)
                for enemy in enemies:
                    self.assertIn((enemy['x'],enemy['y']),reachable)
                    self.assertFalse(enemy['boss']);self.assertGreaterEqual(enemy['max_hp'],24)
                total+=1
            self.assertLessEqual(max(budgets)/min(budgets),1.15)
        self.assertEqual(total,12)

    def arena(self):
        b=combat.create_contract_battle(new_game({'name':'QA','starting_role':'fighter'}),['player'],'layout-1','roadside_toll',True)
        b.update(width=16,height=16,terrain=[],decorations=[],objects={},zones=[],elevation=[],ground_tiles=[],animation_events=[])
        a=b['units']['player'];t=combat._living(b,'enemy')[0]
        b['units']={a['id']:a,t['id']:t}
        for u,x in ((a,5),(t,6)):
            u.update(x=x,y=5,hp=200,max_hp=200,armor=0,attack=10,statuses=[],guarding=False,passives=[],reactions=[],
                     skills=[],ability_state={},ability_activation=1,acted=False,move=4,zone_location=[x,5],boss=False)
        return b,a,t

    def use(self,b,a,t,kind):
        skill=deepcopy(jobs.SKILLS['npc:bandit:'+kind]);a['skills']=[skill]
        with patch.object(combat,'_attack_hits',return_value=(True,{'chance':100,'damage_bonus':0},1)):
            return combat._resolve_ability(b,a,t,skill)

    def test_captured_specialists_learn_starters_without_equipping_them(self):
        for job in jobs.JOBS:
            p={'id':'c','name':'QA','race':'Human','recruitable_snapshot':{
                'job_id':job,'learned_skills':['npc:bandit:road_bola'],
                'equipped_skills':['npc:bandit:road_bola'],'job_practice':0}}
            initialize_prisoner(p,now=0);c=p['recruitment']['candidate']
            self.assertTrue(set(jobs.JOBS[job]['starter_skills'])<=set(c['learned_skills']))
            self.assertEqual(c['equipped_skills'],['npc:bandit:road_bola'])
            before=deepcopy(c);initialize_prisoner(p,now=1);self.assertEqual(c,before)

    def test_recovery_uses_rank_not_building_or_roster_size(self):
        for rank,seconds in RECOVERY_SECONDS.items():
            for building in (None,'tent','infirmary'):
                s=new_game({'name':'QA'});s['buildings']=[] if building is None else [{'type':building,'assigned':[]}]
                r=_incapacitate_character(s,s['characters'],random.Random(1),1000,rank)
                self.assertEqual(r['recovers_at'],1000+seconds)
                self.assertEqual(s['characters'][0]['hp'],1)

    def test_shakedown_and_parting_cut_damage_and_blocked_retreat(self):
        b,a,t=self.arena();self.use(b,a,t,'shakedown');self.assertEqual(t['hp'],180)
        self.assertEqual(a['ability_state']['npc:bandit:shakedown']['ready_at'],3)
        b,a,t=self.arena();self.use(b,a,t,'parting_cut');self.assertEqual((a['x'],a['y']),(4,5))
        self.assertEqual(t['hp'],188)
        attack=next(e for e in b['animation_events'] if e.get('type')=='melee_attack')
        retreat=next(e for e in b['animation_events'] if e.get('skid_back') and e.get('type')=='movement')
        self.assertEqual(attack['parting_retreat'],{'x':4,'y':5})
        self.assertEqual(retreat['attack_packet'],attack['attack_packet'])
        self.assertEqual(retreat['points'],[{'x':5,'y':5},{'x':4,'y':5}])
        b,a,t=self.arena();b['terrain']=[{'id':'rock','x':4,'y':5,'blocking':True}]
        self.use(b,a,t,'parting_cut');self.assertEqual(a['x'],5);self.assertEqual(t['hp'],188)
        self.assertFalse(any(e.get('parting_retreat') for e in b['animation_events']))

    def test_ankle_bite_checks_another_ally_not_the_attacker(self):
        b,a,t=self.arena();self.use(b,a,t,'ankle_bite')
        self.assertEqual(t['hp'],190);self.assertEqual(next(s for s in t['statuses'] if s['id']=='hobbled')['stacks'],1)
        b,a,t=self.arena();ally=deepcopy(a);ally.update(id='ally',x=6,y=6);b['units']['ally']=ally
        self.use(b,a,t,'ankle_bite');self.assertEqual(t['hp'],183)
        self.assertEqual(next(s for s in t['statuses'] if s['id']=='hobbled')['stacks'],2)

    def test_goliath_sword_bonus_excludes_axes_and_dot(self):
        b,a,t=self.arena();npc.landed(b,a,t,jobs.SKILLS['npc:bandit:goliath_shot'],1)
        self.assertTrue(conditions.has(t,'sword_exposed'))
        a['weapon_type']='sword';self.assertEqual(combat._damage_before_barrier(b,a,t),12)
        a['weapon_type']='axe';self.assertEqual(combat._damage_before_barrier(b,a,t),10)
        a.update(weapon_type='sword',status_tick=True);self.assertEqual(combat._damage_before_barrier(b,a,t),10)

    def test_tag_team_crossing_and_user_only_bonus(self):
        b,a,t=self.arena();ally=deepcopy(a);ally.update(id='ally',x=8);b['units']['ally']=ally
        self.use(b,a,ally,'tag_team')
        self.assertEqual((a['x'],ally['x']),(8,5));self.assertTrue(conditions.has(t,'stun'))
        self.assertTrue(conditions.has(a,'tag_team_power'));self.assertFalse(conditions.has(ally,'tag_team_power'))

    def test_heel_cut_matches_route_warning_and_backtracking_is_free(self):
        b,a,t=self.arena();self.use(b,a,t,'heel_cut');before=deepcopy(t)
        path=[{'x':7,'y':5},{'x':8,'y':5}]
        warning=combat_hazard_preview.forecast(b,t,path,combat._combat_active,combat._damage_before_barrier,combat._living)
        self.assertEqual(t,before)
        hp=t['hp']
        for p in path:t.update(p);combat._apply_tile_entry(b,t)
        self.assertEqual(hp-t['hp'],warning['damage']);self.assertEqual(warning['effects']['bleed']['stacks'],2)
        paid=t['hp'];t.update(x=7);combat._apply_tile_entry(b,t);t.update(x=8);combat._apply_tile_entry(b,t)
        self.assertEqual(t['hp'],paid)

    def test_tripline_snaps_once_for_whole_strip_and_allies_are_safe(self):
        b,a,t=self.arena();skill=deepcopy(jobs.SKILLS['npc:bandit:tripline']);a['skills']=[skill]
        combat.rogue.utility_command(b,a,skill,{'x':7,'y':5,'rotation':1})
        self.assertTrue(a['acted']);self.assertEqual(len(b['zones'][0]['cells']),3)
        a.update(x=7,y=4);combat._apply_tile_entry(b,a);self.assertEqual(len(b['zones']),1)
        t.update(x=7,y=5);combat._apply_tile_entry(b,t);self.assertEqual(b['zones'],[])
        count=next(s for s in t['statuses'] if s['id']=='hobbled')['stacks']
        t.update(y=6);combat._apply_tile_entry(b,t)
        self.assertEqual(next(s for s in t['statuses'] if s['id']=='hobbled')['stacks'],count)

    def test_cornered_fury_sweeps_cardinal_enemies_once_without_hitting_allies(self):
        b,a,t=self.arena();other=deepcopy(t);other.update(id='other',x=5,y=6);b['units']['other']=other
        a.update(hp=80,passives=[jobs.SKILLS['npc:bandit:cornered_fury']])
        with patch.object(combat,'_attack_hits',return_value=(True,{'chance':100,'damage_bonus':0},1)):
            combat._perform_attack(b,a,t,'melee')
        self.assertEqual((t['hp'],other['hp']),(190,190))
        a['hp']=100
        with patch.object(combat,'_attack_hits',return_value=(True,{'chance':100,'damage_bonus':0},1)):
            combat._perform_attack(b,a,t,'melee')
        self.assertEqual((t['hp'],other['hp']),(180,190))

    def test_all_prisoner_story_layouts_preserve_recruitable_roles(self):
        for mid in ('prison_rival_e','prison_former_e','prison_proof_e'):
            for preset in layout_presets('contract:'+mid):
                b=combat.create_contract_battle(new_game({'name':'QA'}),['player'],preset['seed'],mid,True)
                es=combat._living(b,'enemy');self.assertEqual(len(es),2)
                self.assertTrue(all(not u['boss'] and u['max_hp']>=24 for u in es))
                for u in es:
                    p={'id':u['id'],'name':u['name'],'race':u['race'],'recruitable_snapshot':u['recruitable_snapshot']}
                    initialize_prisoner(p,now=0);c=p['recruitment']['candidate']
                    self.assertEqual(c['origin_mission_id'],mid)
                    self.assertTrue(set(jobs.JOBS[c['job_id']]['starter_skills'])<=set(c['learned_skills']))

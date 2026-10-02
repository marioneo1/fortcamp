import unittest
from copy import deepcopy
from unittest.mock import patch
from backend.relationships import ensure_character, independent_chance, independence_check, conversation, record_mission, record_mission_start, record_battle
from backend.game import new_game, normalize_state
from backend.combat import create_goblin_warcamp_battle, apply_player_command, battle_view, _deal_damage

class RelationshipTests(unittest.TestCase):
    def state(self):
        state=new_game({'name':'Leader'})
        c=deepcopy(state['characters'][0]);c.update(id='companion',is_player=False,name='Mog',status='idle')
        c.pop('loyalty',None);c.pop('personality_id',None);c.pop('relationship',None)
        state['characters'].append(c)
        return normalize_state(state),c

    def test_persistent_identity_tastes_and_player_immunity(self):
        state,c=self.state();before=deepcopy(c)
        normalize_state(state)
        self.assertEqual(c['personality_id'],before['personality_id'])
        self.assertEqual(c['relationship'],before['relationship'])
        favorite=c['relationship']['favorite_meal'];c['race']='Goblin';c['personality_id']='berserker'
        ensure_character(c);self.assertEqual(favorite,c['relationship']['favorite_meal'])
        state['characters'][0]['loyalty']=0;normalize_state(state)
        self.assertEqual(state['characters'][0]['loyalty'],100)
        self.assertEqual(independent_chance({'player_avatar':True,'loyalty':0}),0)
        for loyalty in (0,20,80,99,100):
            self.assertEqual(independent_chance({'loyalty':loyalty}),100-loyalty)

    def test_once_per_activation_and_exact_loyalty_boundary(self):
        b={'seed':'test','round':1,'turn_index':0};u={'id':'ally','loyalty':80}
        with patch('backend.relationships.random.Random') as rng:
            rng.return_value.randint.return_value=20
            self.assertTrue(independence_check(b,u))
            self.assertFalse(independence_check(b,u))
            b['round']=2;rng.return_value.randint.return_value=21
            self.assertFalse(independence_check(b,u))
            b['round']=3;u['acted']=True
            self.assertFalse(independence_check(b,u))
            self.assertEqual(rng.return_value.randint.call_count,2)

    def test_coward_ignores_move_and_uses_exit_path(self):
        state,c=self.state();c.update(loyalty=100)
        b=create_goblin_warcamp_battle(state,['companion'],'coward-test')
        u=b['units']['companion'];u.update(loyalty=0,personality_id='coward',x=0,y=6)
        b['turn_order']=['companion']+[uid for uid in b['turn_order'] if uid!='companion'];b['turn_index']=0
        apply_player_command(b,{'action':'move','x':1,'y':6})
        self.assertGreaterEqual(u.get('independent_actions',0),1)
        self.assertNotEqual((u['x'],u['y']),(1,6))
        self.assertTrue(any('acts independently' in line for line in b['log']))

    def test_talk_discovers_food_without_loyalty_farming_and_gifts_consume(self):
        state,c=self.state();favorite=c['relationship']['favorite_meal'];initial=c['loyalty']
        for _ in range(10):conversation(state,c['id'],topic='food')
        self.assertEqual(c['loyalty'],initial)
        self.assertIn(favorite,c['relationship']['discovered_tastes'])
        state['meals']={favorite:2}
        reply=conversation(state,c['id'],'gift_meal',meal=favorite,now=100)
        self.assertEqual(reply['loyalty_gain'],4);self.assertEqual(state['meals'][favorite],1)
        with self.assertRaisesRegex(ValueError,'six hours'):conversation(state,c['id'],'gift_meal',meal=favorite,now=101)
        self.assertEqual(state['meals'][favorite],1)
        c['loyalty']=99;conversation(state,c['id'],'gift_meal',meal=favorite,now=21700)
        self.assertEqual(c['loyalty'],100)

    def test_accepted_mission_count_is_not_repeated_and_memories_are_owned(self):
        state,c=self.state();mission={'name':'Wolves at the Fence'}
        record_mission_start(state,[c['id']]);record_mission(state,mission,[c['id']],'success',started=True)
        self.assertEqual(c['service_record']['missions_taken'],1)
        self.assertEqual(c['service_record']['missions_completed'],1)
        self.assertEqual(state['characters'][0]['recent_memories'],[])
        self.assertIn('Wolves at the Fence',conversation(state,c['id'])['text'])
        for _ in range(12):record_mission(state,mission,[c['id']],'failure')
        self.assertEqual(len(c['recent_memories']),8)

    def test_actual_damage_not_overkill_and_lethal_only_blood(self):
        state,c=self.state();b=create_goblin_warcamp_battle(state,['player'],'record-test')
        source=b['units']['player'];target=b['units']['gob_guard'];source['attack']=100;target['hp']=3;target['guarding']=False
        _deal_damage(b,source,target)
        self.assertGreaterEqual(source['combat_record']['combat_turns'],1)
        turns=source['combat_record']['combat_turns']
        battle_view(b);battle_view(b)
        self.assertEqual(source['combat_record']['combat_turns'],turns)
        self.assertEqual(source['combat_record']['total_damage'],3)
        self.assertEqual(source['combat_record']['kills'],1)
        self.assertEqual(sum(e['type']=='death_burst' for e in b['animation_events']),1)
        record_mission(state,{'name':'Test fight'},['player'],'success');record_battle(state,b)
        self.assertEqual(state['characters'][0]['service_record']['kills'],1)
        self.assertEqual(state['characters'][0]['recent_memories'][-1]['combat']['kills'],1)
        b=create_goblin_warcamp_battle(state,['player'],'subdue-record');source=b['units']['player'];target=b['units']['gob_guard'];source['attack']=100;target['hp']=3
        _deal_damage(b,source,target,intent='nonlethal')
        self.assertEqual(source['combat_record']['subdues'],1)
        self.assertFalse(any(e['type']=='death_burst' for e in b['animation_events']))

    def test_champion_profile_can_override_voice_and_ai_without_changing_tastes(self):
        from backend.relationships import personality_profile
        state,c=self.state();favorite=c['relationship']['favorite_meal']
        c['personality_override']={'name':'Authored hero','voice':'I protect this village.','behavior':'guardian'}
        self.assertEqual(personality_profile(c)[2],'guardian')
        self.assertEqual(conversation(state,c['id'],topic='outlook')['text'],'I protect this village.')
        self.assertEqual(c['relationship']['favorite_meal'],favorite)

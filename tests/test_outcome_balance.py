import unittest
from backend.outcome_balance import CRITICAL_CAPS, critical_chance, classify_roll, outcome_probabilities
from backend.mission_decisions import classify
from backend.game import analyze_mission, new_game, resolve_mission
from backend.content import MISSION_TEMPLATES

class OutcomeBalanceTests(unittest.TestCase):
    def test_rank_caps_and_progression(self):
        for rank, cap in CRITICAL_CAPS.items():
            odds=[critical_chance(rank, margin) for margin in range(100)]
            self.assertEqual(odds, sorted(odds))
            self.assertEqual(odds[-1], cap)
            self.assertLess(odds[0], cap)
            strong=outcome_probabilities(100, 10, rank)
            self.assertAlmostEqual(strong['critical_success'], cap * .95)
            self.assertGreater(strong['success'], strong['critical_success'])
            self.assertAlmostEqual(sum(strong.values()), 100)
        self.assertEqual([CRITICAL_CAPS[r] for r in 'EDCBAS'], sorted(CRITICAL_CAPS.values(),reverse=True))

    def test_no_automatic_critical_on_natural_twenty_or_massive_stats(self):
        self.assertEqual(classify_roll(20,120,10,critical_roll=100),'success')
        self.assertEqual(classify(20,120,10,critical_roll=100),'success')
        self.assertEqual(classify_roll(20,120,10,available=False,critical_roll=1),'success')
        self.assertEqual(classify_roll(20,20,24,critical_roll=1),'failure')
        self.assertEqual(classify_roll(1,101,10,critical_roll=1),'critical_failure')

    def test_odds_match_exhaustive_live_classifier(self):
        for rank in CRITICAL_CAPS:
            for bonus in (0,4,12,24,100):
                for available in (False,True):
                    counts=dict.fromkeys(('critical_failure','failure','success','critical_success'),0)
                    for die in range(1,21):
                        for crit in range(1,101):
                            counts[classify_roll(die,die+bonus,14,rank,available,crit)]+=1
                    expected={k:round(v/20,2) for k,v in counts.items()}
                    self.assertEqual(expected,outcome_probabilities(bonus,14,rank,available))

    def test_actual_mission_resolution_matches_preview_and_seed(self):
        state=new_game({'name':'Veteran','attributes':{'dex':10,'luk':10},'perks':{'scavenging':'master'}})
        mission=MISSION_TEMPLATES['fallen_orchard']
        analysis=analyze_mission(state,mission,['player'])
        self.assertLessEqual(analysis['probabilities']['critical_success'],CRITICAL_CAPS[mission['rank']])
        import random
        from copy import deepcopy
        for seed in map(str,range(200)):
            rng=random.Random(seed);die=rng.randint(1,20);crit=rng.randint(1,100)
            bonus=sum(analysis[k] for k in ('lead_stat','support_bonus','criteria_bonus'))
            expected=classify_roll(die,die+bonus,mission['difficulty'],mission['rank'],analysis['critical_success_available'],crit)
            result=resolve_mission(deepcopy(state),mission,['player'],analysis,seed)
            self.assertEqual(result['outcome'],expected)

    def test_scene_length_does_not_inflate_final_critical_chance(self):
        from backend.outcome_balance import scene_critical_chance
        check={'outcome':'success','die':15,'total':25,'difficulty':14}
        self.assertEqual(scene_critical_chance([check],'D',True),scene_critical_chance([check]*10,'D',True))
        self.assertEqual(scene_critical_chance([check],'D',False),0)
        self.assertEqual(scene_critical_chance([check,{'outcome':'failure'}],'D',True),0)
        self.assertEqual(scene_critical_chance([{'outcome':'success','die':None}],'D',True),0)

import unittest
from backend.outcome_balance import CRITICAL_SOFT_CAPS, CRITICAL_STAT_LIMITS, SOFT_CAP_MARGINS, critical_chance, classify_roll, outcome_probabilities
from backend.mission_decisions import classify
from backend.game import analyze_mission, new_game, resolve_mission
from backend.content import MISSION_TEMPLATES

class OutcomeBalanceTests(unittest.TestCase):
    def test_soft_caps_are_crossable_with_diminishing_returns(self):
        for rank, soft in CRITICAL_SOFT_CAPS.items():
            knee=SOFT_CAP_MARGINS[rank]
            self.assertEqual(critical_chance(rank,knee),soft)
            odds=[critical_chance(rank,margin) for margin in range(3000)]
            self.assertEqual(odds,sorted(odds))
            if rank!='S': self.assertGreater(critical_chance(rank,knee+100),soft)
            self.assertLessEqual(odds[-1],CRITICAL_STAT_LIMITS[rank])
            if rank in 'EDC':
                self.assertLess(critical_chance(rank,knee+20)-soft,critical_chance(rank,knee+10)-soft+critical_chance(rank,knee+10)-soft)
        self.assertGreater(critical_chance('E',50),critical_chance('D',50))
        self.assertGreater(critical_chance('D',50),critical_chance('C',50))

    def test_stat_only_limits_and_low_rank_certainty(self):
        for bonus in (0,24,100,300,2000,1000000):
            self.assertLess(outcome_probabilities(bonus,14,'B')['critical_success'],50)
            self.assertLess(outcome_probabilities(bonus,14,'A')['critical_success'],10)
            self.assertLessEqual(outcome_probabilities(bonus,14,'S')['critical_success'],5)
        for rank, margin in [('E',140),('D',228),('C',1460)]:
            self.assertEqual(critical_chance(rank,margin),100)
            self.assertLess(critical_chance(rank,margin-1),100)
            odds=outcome_probabilities(14+margin-1,14,rank)
            self.assertEqual(odds['critical_success'],100)
            self.assertEqual(odds['critical_failure'],0)
            self.assertEqual(classify_roll(1,14+margin,14,rank,True,100),'critical_success')
            self.assertEqual(classify_roll(1,14+margin,14,rank,False,1),'critical_failure')
        self.assertLess(critical_chance('C',1000),100)

    def test_no_automatic_critical_on_natural_twenty_or_massive_stats(self):
        self.assertEqual(classify_roll(20,120,10,critical_roll=100),'success')
        self.assertEqual(classify(20,120,10,critical_roll=100),'success')
        self.assertEqual(classify_roll(20,120,10,available=False,critical_roll=1),'success')
        self.assertEqual(classify_roll(20,20,24,critical_roll=1),'failure')
        self.assertEqual(classify_roll(1,31,10,critical_roll=1),'critical_failure')

    def test_odds_match_exhaustive_live_classifier(self):
        for rank in CRITICAL_SOFT_CAPS:
            for available in (False,True):
                counts=dict.fromkeys(('critical_failure','failure','success','critical_success'),0)
                for die in range(1,21):
                    for face in range(1,10001):
                        counts[classify_roll(die,die+30,14,rank,available,face/100)]+=1
                expected={k:round(v/2000,4) for k,v in counts.items()}
                self.assertEqual(expected,outcome_probabilities(30,14,rank,available))
                self.assertAlmostEqual(sum(expected.values()),100)

    def test_actual_mission_resolution_matches_preview_and_seed(self):
        state=new_game({'name':'Veteran','attributes':{'dex':10,'luk':10},'perks':{'scavenging':'master'}})
        mission=MISSION_TEMPLATES['fallen_orchard']
        analysis=analyze_mission(state,mission,['player'])
        self.assertLessEqual(analysis['probabilities']['critical_success'],CRITICAL_STAT_LIMITS[mission['rank']])
        import random
        from copy import deepcopy
        for seed in map(str,range(200)):
            rng=random.Random(seed);die=rng.randint(1,20);crit=rng.randint(1,10000)/100
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

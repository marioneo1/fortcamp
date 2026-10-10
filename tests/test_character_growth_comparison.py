"""Checks for the offline proposal's rank and allocation accounting."""
import unittest

from tools.compare_character_growth import ATTRS, allocate, allocation_cost, project, samples


class GrowthComparisonTests(unittest.TestCase):
    def test_rank_applies_once_and_projection_does_not_mutate_body(self):
        body = dict.fromkeys(ATTRS, 6)
        result = project(body, 'S', weapon_power=3, training=1)
        self.assertEqual(body, dict.fromkeys(ATTRS, 6))
        self.assertEqual(result['hp'], 84)
        self.assertEqual(result['attack'], 16)
        self.assertEqual(result['armor'], 5)

    def test_creation_cost_and_threshold_refunds(self):
        for value in range(1, 11):
            body = dict.fromkeys(ATTRS, value)
            self.assertEqual(allocation_cost(body), allocation_cost(body, True))
        body = dict.fromkeys(ATTRS, 4)
        for old, new, price in ((9, 10, 1), (10, 11, 2), (15, 16, 3)):
            body['str'] = old
            before = allocation_cost(body, True)
            body['str'] = new
            self.assertEqual(allocation_cost(body, True) - before, price)

    def test_higher_budget_keeps_existing_allocation_and_stays_within_budget(self):
        weights = dict(zip(ATTRS, (2, 1, 1, 5, 1, 1)))
        for graduated in (False, True):
            previous = dict.fromkeys(ATTRS, 4)
            for budget in range(36, 67):
                body = allocate(budget, weights, graduated)
                self.assertLessEqual(allocation_cost(body, graduated), budget)
                self.assertTrue(all(body[k] >= previous[k] for k in ATTRS))
                previous = body

    def test_live_d_samples_use_unranked_snapshot_baseline(self):
        rows = list(samples())
        self.assertTrue(any(rank == 'D' for _, _, _, rank in rows))
        for _, unit, body, rank in rows:
            if rank == 'D':
                effective = project(body, rank)['attributes']
                self.assertEqual(body, unit['recruitable_snapshot']['attributes'])
                self.assertEqual(unit['recruitable_snapshot']['adventurer_rank'],'D')
                self.assertLess(sum(body.values()), sum(effective.values()))


if __name__ == '__main__':
    unittest.main()

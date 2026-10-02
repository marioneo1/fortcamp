import unittest
from copy import deepcopy
from types import SimpleNamespace
from unittest.mock import patch

from backend.content import ITEMS, MISSION_TEMPLATES
from backend.economy import purchase, trade_view
from backend.game import new_game, normalize_state
from backend.inventory import sale_price
from backend.mercenaries import market, prepare, quote
from backend.starter_equipment import STARTING_ROLES


class VendorHiringPacingTests(unittest.TestCase):
    def state(self):
        state=normalize_state(new_game({'starting_role':'fighter'}))
        state['resources']['gold']=1000
        return state

    def test_every_starter_kit_is_always_available_and_cannot_make_resale_profit(self):
        state=self.state()
        for now in [1000,172800,999999]:
            offers={o['item']:o for o in trade_view(state,'player',now)['camp_items']}
            for iid in {i for role in STARTING_ROLES.values() for i in role['kit']}|{'worn_jacket','work_boots'}:
                self.assertIn(iid,offers)
                self.assertGreater(offers[iid]['price'],sale_price(iid))
                self.assertEqual(ITEMS[iid]['rarity'],'common')

    def test_repeat_purchases_are_distinct_and_do_not_change_equipment(self):
        state=self.state();equipment=deepcopy(state['characters'][0]['equipment'])
        for _ in range(2):purchase(state,'player','camp:frayed_capture_net',1000)
        copies=[i for i in state['inventory'] if i['item_id']=='frayed_capture_net']
        self.assertEqual(len(copies),2)
        self.assertEqual(len({i['instance_id'] for i in copies}),2)
        self.assertEqual(state['resources']['gold'],988)
        self.assertEqual(state['characters'][0]['equipment'],equipment)
        state['resources']['gold']=0;before=deepcopy(state)
        with self.assertRaises(ValueError):purchase(state,'player','camp:cracked_wand',1000)
        self.assertEqual(state['inventory'],before['inventory'])

    def test_same_contact_costs_more_on_harder_contract_and_trust_still_discounts(self):
        state=self.state();market(state,'player');contact=state['mercenaries'][0]
        fees=[quote(contact,rank)['fee'] for rank in 'EDCBAS']
        self.assertEqual(fees,[10,15,22,32,45,65])
        contact['relationship']=40
        self.assertEqual(quote(contact,'S')['fee'],52)
        self.assertEqual(quote({**contact,'rank':'S','relationship':0},'S')['fee'],845)
        with self.assertRaises(ValueError):quote(contact,'unknown')

    def test_market_quote_does_not_reroll_contact_identity_or_trust(self):
        state=self.state();first=market(state,'player','E');snap=deepcopy(state['mercenaries'])
        second=market(state,'player','A')
        self.assertEqual(state['mercenaries'],snap)
        self.assertEqual([o['id'] for o in first],[o['id'] for o in second])
        self.assertGreater(second[0]['fee'],first[0]['fee'])

    def test_acceptance_uses_server_template_rank_and_does_not_double_charge(self):
        state=self.state();state['_mercenary_owner']='owner';market(state,'player');mid=state['mercenaries'][0]['id']
        mission=SimpleNamespace(id='hiring',claimed_by_user_id='owner',template_id='price-test',analysis={})
        with patch.dict(MISSION_TEMPLATES,{'price-test':{'rank':'B'}}):
            prepare(state,mission,[mid],['player',mid],spend=True)
            self.assertEqual(state['resources']['gold'],968)
            with self.assertRaises(ValueError):prepare(state,mission,[mid],['player',mid],spend=True)
            self.assertEqual(state['resources']['gold'],968)


if __name__=='__main__':unittest.main()

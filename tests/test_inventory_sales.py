import unittest
from copy import deepcopy
from backend.game import new_game, public_content
from backend.inventory import sell_items, sale_price
from backend.economy import FACTIONS

class InventorySalesTests(unittest.TestCase):
    def state(self):
        state=new_game({'name':'Seller'})
        state['inventory'] += [{'instance_id':'manual-a','item_id':'training_manual'}, {'instance_id':'manual-b','item_id':'training_manual'}]
        return state

    def test_sale_removes_selected_copies_and_credits_exact_price(self):
        state=self.state();gold=state['resources']['gold']
        result=sell_items(state,['manual-a'])
        self.assertEqual(result,{'quantity':1,'gold':3})
        self.assertEqual(state['resources']['gold'],gold+3)
        self.assertIn('manual-b',[i['instance_id'] for i in state['inventory']])
        snapshot=deepcopy(state)
        with self.assertRaises(ValueError):sell_items(state,['manual-a'])
        self.assertEqual(state,snapshot)

    def test_equipped_copy_rejects_entire_batch_without_partial_sale(self):
        state=self.state();item=state['inventory'][0]
        state['characters'][0]['equipment']['weapon']=item['instance_id']
        snapshot=deepcopy(state)
        with self.assertRaises(ValueError):sell_items(state,['manual-a',item['instance_id']])
        self.assertEqual(state,snapshot)

    def test_duplicate_missing_and_unknown_instances_cannot_credit_gold(self):
        for ids in [['manual-a','manual-a'],['manual-a','missing'],[]]:
            state=self.state();snapshot=deepcopy(state)
            with self.assertRaises(ValueError):sell_items(state,ids)
            self.assertEqual(state,snapshot)

    def test_published_quotes_match_sales_and_no_faction_resale_profit(self):
        prices=public_content()['sale_prices']
        self.assertEqual(prices['training_manual'],sale_price('training_manual'))
        for faction in FACTIONS.values():
            for index,item in enumerate(faction['goods']):
                self.assertLess(prices[item],(12,30,65,120)[index])

class InventorySaleEndpointTests(unittest.IsolatedAsyncioTestCase):
    async def test_concurrent_repeat_sale_is_credited_only_once(self):
        import asyncio
        from types import SimpleNamespace
        from unittest.mock import patch
        from sqlalchemy.ext.asyncio import create_async_engine,async_sessionmaker
        from sqlalchemy import select
        from fastapi import HTTPException
        from backend.db import Base
        from backend.models import PlayerState
        from backend.main import sell_inventory,SellItemsRequest
        engine=create_async_engine('sqlite+aiosqlite:///:memory:')
        try:
            async with engine.begin() as conn:await conn.run_sync(Base.metadata.create_all)
            factory=async_sessionmaker(engine,expire_on_commit=False)
            state=new_game({'name':'Seller'})
            state['inventory'].append({'instance_id':'endpoint-manual','item_id':'training_manual'})
            gold=state['resources']['gold']
            async with factory() as session:
                session.add(PlayerState(guild_id='sales-fixture',user_id='owner',display_name='Seller',state=state,updated_at=1));await session.commit()
            identity=SimpleNamespace(guild_id='sales-fixture',user_id='owner')
            with patch('backend.main.SessionLocal',factory):
                results=await asyncio.gather(*[sell_inventory(SellItemsRequest(instance_ids=['endpoint-manual']),identity) for _ in range(2)],return_exceptions=True)
            self.assertEqual(sum(isinstance(r,dict) for r in results),1)
            error=next(r for r in results if isinstance(r,HTTPException));self.assertEqual(error.status_code,400)
            async with factory() as session:
                row=(await session.execute(select(PlayerState))).scalar_one()
                self.assertEqual(row.state['resources']['gold'],gold+3)
                self.assertNotIn('endpoint-manual',[i['instance_id'] for i in row.state['inventory']])
        finally:await engine.dispose()

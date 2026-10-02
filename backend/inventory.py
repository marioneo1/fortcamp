"""Sell explicitly selected, unequipped inventory instances for gold."""
SALE_VALUES={'common':3,'uncommon':7,'rare':18,'epic':40,'legendary':90,'mythic':180,'event':8,'story':12}

def sale_price(item_id,items=None):
    from .content import ITEMS
    from .economy import FACTIONS
    item=(ITEMS if items is None else items).get(item_id)
    if not item:return 0
    value=SALE_VALUES.get(item.get('rarity','common'),3)
    # Faction stores sell some rare equipment cheaply. Resale must never turn
    # repeat purchases into a gold-printing loop.
    for faction in FACTIONS.values():
        if item_id in faction['goods']:
            value=min(value,(12,30,65,120)[faction['goods'].index(item_id)]//3)
    return value

def sell_items(state,instance_ids):
    from .content import ITEMS
    if not instance_ids or len(set(instance_ids))!=len(instance_ids):
        raise ValueError('Select each item once')
    inventory={i['instance_id']:i for i in state.get('inventory',[])}
    equipped={iid for c in state.get('characters',[]) for iid in c.get('equipment',{}).values() if iid}
    selected=[]
    for iid in instance_ids:
        if iid not in inventory:raise ValueError('An item is no longer in inventory. Refresh and try again.')
        if iid in equipped:raise ValueError('Unequip items before selling them')
        item=inventory[iid]
        if item.get('mercenary_gear'):raise ValueError('Mercenary gear cannot be sold')
        if item['item_id'] not in ITEMS:raise ValueError('This item cannot be sold')
        selected.append(item)
    gold=sum(sale_price(i['item_id']) for i in selected)
    ids=set(instance_ids)
    state['inventory']=[i for i in state['inventory'] if i['instance_id'] not in ids]
    state['resources']['gold']=state['resources'].get('gold',0)+gold
    return {'quantity':len(selected),'gold':gold}

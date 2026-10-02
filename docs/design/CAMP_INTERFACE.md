# Camp and roster workspaces

## October 2 usability refinement

Base / Prisoners now uses a compact list and detail workspace rather than a long set of expanded cards. Conversation uses a portrait sidebar and topic/transcript layout, retaining session state during refreshes. Starter equipment is accessible near the top of Trade in an always-available drawer. Responsive browser checks cover conversation, prisoners and trade at 1440, 800 and 430 pixels. These changes are dev only; production is not deployed by this pass.

Implemented October 1, 2026 in alpha/dev. Production trial.2 remains pinned to its prepared source and is not updated by this pass.

## Navigation

Base contains five direct sections:

- Settlement: map beside a Facilities / Build sidebar. Choose placed facilities from the list or map; manage training, mission-rank upgrades, wardens and staffing in its inspector. Workers can still be dragged, or assigned/removed using controls. Construction remains separate from blueprint research; placed building types are removed from available plans.
- Supplies: personal work focus, production facility upgrades and a Trade entry point. Affordability is displayed before submitting an upgrade.
- Development: expansion, free-for-all allowance, and blueprint research cards. Costs highlight resource shortages. Allowance upgrades require a Guild Hall.
- Kitchen: meal recipient, study proficiency and recipe cards, or an explanation when no Kitchen is placed. Existing cooking rules remain authoritative.
- Prisoners: capacity, secure/stockade filters, name/race search, recruitment conversations and custody actions. Manage prison facilities opens the selected Prison Cell inspector in Settlement (or Build when none exists).

Roster contains Characters, Inventory and Collections. Its Prisoners shortcut opens Base / Prisoners. Prisoners and Champion/Celestial collections no longer appear below the character screen. Base sections, sidebar view, roster view, searches and prisoner conversation/profile tabs remain selected through rerenders within the session. Top-level tab changes return to the top of the page. Narrow layouts stack the map and sidebar; scrolling large maps stays inside their panel.

## Inventory and selling

Character Equipment shows only items in wearable slots. Inventory shows all items, grouped by item ID, with category/rarity/search and 24 item types per page. Training Manuals and materials such as Consecrated Grave Ash have no equipment action. Gear effects remain visible.

Inventory lets players choose a quantity and sell unequipped copies. A shared in-game confirmation shows the exact quantity and total gold before submission. Equipped copies are excluded in the UI and rejected by the server. Sales identify exact instance IDs; invalid, missing, duplicate or equipped selections reject the entire operation. A replay cannot credit the same item twice. Equip and sale requests share a per-player lock, and prices are computed by the server rather than accepted from clients.

Initial resale gold per rarity: common 3, uncommon 7, rare 18, epic 40, legendary 90, mythic 180, event 8, story 12. Items stocked by faction stores have resale capped at one third of their lowest faction purchase price. This is a starting economy pass, not a final item-value system; there is no buyback or batch sale across different item types yet. No new generic use-item actions are claimed for materials.

## Verification

Browser fixtures exercise section/sidebar persistence, narrow-screen overflow, facility selection, roster-to-prison access, prisoner filtering, inventory separation, sale cancellation/confirmation and recruitment. Backend tests cover atomic sales, equipped-copy protection, replay rejection, concurrent duplicate sale requests and price publication. The fixtures do not change live saves or contact Discord.

Validation completed: 240 backend tests and 96 frontend tests passed; production frontend build and real frontend browser fixture passed. Collections and Inventory render when selected rather than rebuilding their hidden contents on every character update. Production trial.2 source remains unchanged.

> Historical snapshot. Use the root README and feature backlog for current behavior.

# Fortcamp Alpha 0.3.1 — Base Placement, Mission Aftermath + Contextual Recruits

Alpha 0.3.1 keeps the **server-wide competitive mission board** and adds the first polish pass around base management and mission resolution: visible building footprints, movable buildings, outcome sounds, mission aftermath stories, and context-sensitive procedural recruits.

Current development tracking: [Feature backlog](../../FEATURE_BACKLOG.md), [gameplay vision](../../GAMEPLAY_VISION.md), [implementation log](MISSION_REFINEMENT_PHASE.md), [music guide](../audio/MUSIC_GENERATION_GUIDE.md), [Mureka prompts](../audio/MUREKA_MUSIC_PROMPTS.md), and [Windows tool inventory](../../WINDOWS_TOOLS.md). The local Git repository tracks code and documentation; generated assets and player databases still require separate backups. No remote is configured.


## 0.3 additions

- Construction cards now show exact `width × height` footprints.
- Placement and moving show a live green/red ghost at the building's **true grid size**.
- Click any placed building to select it, then use **Move** to relocate it without paying its construction cost again. Assigned workers remain attached while the structure moves.
- Mission completion now plays a distinct synthesized cue for Critical Failure, Failure, Success, and Critical Success while the Activity is open. No external audio files are required.
- When a mission changes from `claimed` to `completed` while you are watching, the Activity opens its aftermath automatically.
- Mission results now include mission-specific, non-NSFW narrative aftermath before the roll and reward summary.
- Procedural recruits now support mission-specific generation profiles (race, archetype, traits and name pools).
- Added **Goblin Warcamp** as the first explicit contextual-recruit example: a critical recruit is usually a Goblin from the camp, but can instead be a captive survivor.
- Added **The Captive Cart** as the first retrieval and live-capture battle: rescue Courier Lysa, optionally bring Cartmaster Vrak back alive, and recover the stolen dispatch satchel. Its result report and rewards distinguish rescued, captured, and recovered objectives.
- Tactical encounters now use reusable map blueprints and a modular environment renderer. Grass, dirt, mud, timber, stone and water have distinct tiles and movement rules, while automatic material edges, elevation, animated props and an in-battle legend keep larger rectangular maps readable.
- Existing recruit-bearing missions now use contextual profiles such as raider defectors, clinic survivors, industrial workers and wilds explorers.
- Characters use STR, DEX, AGI, VIT, INT and LUK alongside perks. Weapon scaling uses STR for melee, DEX for ranged and INT for magic.
- Numeric character skills have been replaced by tiered proficiency perks and standalone perks. Trainable proficiencies use Basic, Skilled, Expert and Master tiers; perks such as Goblin Hunter, Fire Magic and Moon Sense stand alone without tiers.
- Missions can define named party roles. Goblin Warcamp now requires a Tank and DPS assignment and shows recommended CON/DPS before claiming.
- The board now uses E, D, C, B, A and S mission ranks. New settlements start with E visibility; building the Guild Hall unlocks D, followed by paid C/B/A/S visibility upgrades.
- The mission pool scales from a generous first-player rank floor and adds more opportunities for every additional registered Fortcamp player.
- Added 16 missions across the rank ladder, bringing the current mission-template total to 25.
- Any owned character portrait can now be replaced with an uploaded PNG, JPEG, GIF or WebP file up to 4 MB.

## 0.2.1 Activity + bot sync fix

Discord automatically creates a global **Launch / Entry Point** command when Activities are enabled. Fortcamp no longer calls a bulk global application-command sync, because doing so can cause Discord error `50240` by attempting to remove that Entry Point. Fortcamp slash commands are now synced per guild after the bot connects. Leave `DISCORD_TEST_GUILD_ID` blank to sync `/fortcamp_setup` and `/fortcamp_pool` to every server where the bot is installed.

The Vite dev server also now allows `*.trycloudflare.com` hosts by default for local Activity testing, and background bot-login failures are printed in the backend console.

## Implemented

- Discord Activity authentication using the official Embedded App SDK.
- Server membership verified by the Python backend before a game session is issued.
- Saves are keyed to **Discord guild + Discord user**.
- Player-created first character with race, series/origin, traits, stats and full equipment.
- All recruits use the same full equipment model.
- Equipment can add stats **and** satisfy mission conditions (weapon type, item tags, etc.).
- Shared mission pool generated every 30 minutes.
- Atomic mission claiming so one mission cannot be won by two players.
- Mission party-size and eligibility requirements.
- Exact Critical Failure / Failure / Success / Critical Success percentages before claiming.
- Variable mission durations, including 1m, 5m, 30m, multi-hour and 24h definitions.
- Deployed characters are unavailable and their gear is locked until they return.
- Offline/background mission resolution while the Python process is running.
- Materials, gear, building blueprints, generic recruits and named **Champions** as rewards.
- `Saber` is isolated in the authored Champion data table as a placeholder/test named NPC; Champions can later be removed or swapped without changing engine code.
- Physical base grid, blueprints, buildings, assignments, inventory and equipment.
- Optional Discord bot announcements with `/fortcamp_setup` and `/fortcamp_pool`.
- SQLite by default for zero-friction local alpha testing; PostgreSQL is already supported through the same SQLAlchemy models.

## Architecture

```text
Discord server
   ├─ Activity (Vite + Embedded App SDK)  ← actual game screen
   └─ Bot                                  ← pool/result announcements
                 ↓
        FastAPI game server
        mission scheduler / dice engine
                 ↓
      SQLAlchemy persistence
       SQLite now / Postgres later
```

The Activity never gets to declare its own Discord identity. In Discord it completes Discord OAuth, and the backend independently checks the user and confirms membership in the guild before issuing a 12-hour signed game session.

The signed game session is cached for its 12-hour lifetime, so closing and reopening the Activity does not repeat Discord authorization. Activity login requests only `identify` and `guilds`; `applications.commands` belongs to the separate app installation flow and must not be requested on every launch.

## 1. Local setup on Windows

Install:

- Python 3.11+
- Node.js 20+
- `cloudflared` for Discord Activity testing
- Docker Desktop only if you want local PostgreSQL immediately

Then extract this folder and run:

```text
setup_windows.bat
```

That creates the Python virtual environment and installs both Python and frontend packages.

For browser-only testing, the defaults in `.env.example` are enough. Run:

```text
run_dev_windows.bat
```

Then open:

```text
http://127.0.0.1:5173
```

Keep the `run_dev_windows.bat` control window open. Press any key in that window to stop the backend, frontend, and Fortcamp tunnel together. You can also double-click `stop_dev_windows.bat` at any time to close all three Fortcamp process windows.

You can simulate a second player/server in browser mode with:

```text
http://127.0.0.1:5173/?guild_id=test-server&user_id=player-two&name=Player%20Two
```

## 2. Discord Developer Portal setup

Create a Discord application and configure it as an Activity.

In `.env`, fill:

```env
DISCORD_CLIENT_ID=YOUR_APPLICATION_ID
DISCORD_CLIENT_SECRET=YOUR_OAUTH_CLIENT_SECRET
DISCORD_BOT_TOKEN=YOUR_BOT_TOKEN
DISCORD_TEST_GUILD_ID=YOUR_TEST_SERVER_ID
APP_SESSION_SECRET=PUT_A_LONG_RANDOM_SECRET_HERE
BOT_ENABLED=true
```

For actual tunneled Discord testing, change:

```env
DEV_BYPASS_AUTH=false
```

**Do not expose a tunneled build with `DEV_BYPASS_AUTH=true`.** The bypass exists only to make local browser iteration easy.

In the Discord Developer Portal:

1. Enable **Activities**.
2. Configure Guild Install for the app/bot.
3. Add the placeholder OAuth redirect URI Discord documents for Activity auth (`https://127.0.0.1`).
4. Install the app/bot into your test guild.
5. Give the bot permission to View Channel, Send Messages and Embed Links in the channel where you want pool announcements.

Discord automatically creates the default Activity **Launch** entry point when Activities are enabled.

### Important unverified-Activity testing limit

As of this alpha's build date, Discord says unverified Activities are limited to **servers with fewer than 25 members** and are visible only to developers and invited App Testers. If your friend's normal server has 25+ members, make a small temporary dev server for Activity testing.

For friends who are only testing, add them under **App Testers** in the Developer Portal rather than giving them developer-team access. Testers must accept the invitation and enable Application Test Mode using your Application ID.

## 3. Start the Activity locally and expose it to Discord

Run:

```text
run_dev_windows.bat
```

Then in another terminal:

```text
cloudflared tunnel --url http://127.0.0.1:5173
```

Cloudflare prints a temporary hostname similar to:

```text
https://funny-example-name.trycloudflare.com
```

In Discord Developer Portal → Activities → URL Mappings, set:

```text
Prefix: /
Target: funny-example-name.trycloudflare.com
```

Do not include `https://` in the Target field.

### What the temporary-domain warning means

A quick tunnel hostname is **borrowed**, not yours. When `cloudflared` stops, you do not permanently control that hostname. Discord warns that a hostname you do not own could later be claimed/reused by someone else. If your Activity URL Mapping still points at that old hostname, your Discord Activity could then load whatever that other person serves there.

So when you finish a tunnel session, either:

- clear/reset the `/` URL Mapping, or
- replace it with the new tunnel hostname next time you test.

Nothing is being installed on your router, and you do **not** port-forward anything. The tunnel makes only the local web service you point it at reachable through its temporary HTTPS address.

### Keep one Cloudflare hostname

The `cloudflared tunnel --url ...` command creates a Quick Tunnel, so its `trycloudflare.com` hostname necessarily changes whenever that process is recreated. To keep Discord's URL Mapping unchanged, create a named tunnel in the Cloudflare dashboard and attach a hostname from a domain managed by your Cloudflare account. Cloudflare provides a tunnel token after creation.

Add the token and configured hostname to the local `.env` file:

```env
FORTCAMP_TUNNEL_TOKEN=YOUR_CLOUDFLARE_TUNNEL_TOKEN
FORTCAMP_PUBLIC_HOST=fortcamp.your-domain.example
```

Then use `start_tunnel_windows.bat`. It detects the token and starts the persistent tunnel; when no token or named tunnel is configured, it deliberately falls back to a temporary Quick Tunnel. Set Discord Developer Portal → Activities → URL Mappings only once to the value of `FORTCAMP_PUBLIC_HOST` without `https://`.

For a locally managed Cloudflare tunnel, set `FORTCAMP_TUNNEL_NAME` instead of a token. A stable Cloudflare hostname requires a Cloudflare account and a domain on that account; anonymous `trycloudflare.com` tunnels cannot reserve a hostname.

### Easier local option: Tailscale Funnel

Tailscale Funnel provides a stable public HTTPS hostname under your tailnet's `*.ts.net` domain without requiring a separate domain. Install and sign into Tailscale, then run this once:

```text
setup_tailscale_funnel_windows.bat
```

The script runs `tailscale funnel --bg 5173` and prints the stable public URL. Put that hostname into Discord Developer Portal → Activities → URL Mappings as the `/` target, without `https://`. Fortcamp's Vite server already accepts `*.ts.net`, so `FORTCAMP_PUBLIC_HOST` is unnecessary for this option.

Background Funnel configuration persists after the terminal closes and resumes after a reboot or Tailscale restart. Normal Fortcamp launches still use `run_dev_windows.bat`; no extra tunnel window is needed. To deliberately remove all Funnel configuration later, run `tailscale funnel reset`.

## 4. Configure announcements

Once the bot is online in the test guild, run this in the channel you want to use:

```text
/fortcamp_setup
```

The bot stores that channel ID and posts new mission-pool summaries there. `/fortcamp_pool` shows a quick summary on demand.

## 5. SQLite vs PostgreSQL

The default is:

```env
DATABASE_URL=sqlite+aiosqlite:///./data/fortcamp.db
```

This is appropriate for a **single local Python process** and a small alpha group. The claim operation is conditional/atomic, and the alpha also serializes same-player claim attempts in-process.

If you want PostgreSQL locally now:

```text
docker compose up -d postgres
```

and change `.env` to:

```env
DATABASE_URL=postgresql+asyncpg://fortcamp:fortcamp@127.0.0.1:5432/fortcamp
```

The game code does not change. When moving to Railway/Neon later, replace only `DATABASE_URL`. Alpha data migration between SQLite and Postgres is not automated yet; for an alpha, you can start the production database fresh, or we can add an export/import command before you care about preserving test saves.

## 6. Mission timing while testing

`.env.example` uses:

```env
MISSION_TIME_SCALE=0.05
```

That turns a one-minute mission into roughly three seconds so you can test results quickly. Set it to:

```env
MISSION_TIME_SCALE=1.0
```

for real durations.

The **pool itself always refreshes every 30 minutes** in this alpha. `MISSION_POOL_SIZE` controls the first player's E-Rank baseline (12 by default). Each registered player adds exactly seven D-Rank contracts. The first player also guarantees floors of four C, two B and one A contract, with additional 60% C, 35% B and 12% A rolls as the pool scales. S-Rank remains exceptional at three 1% attempts per player, with a hard ceiling of three S contracts per player in a refresh.

Most refreshes use Open Contracts. Regional events are selected by one shared guild roll: The Green Warhost (15%), The Ashen Procession (8%), Arcane Convergence (4.5%), The Great Beast Tide (1.9%), or Starfall Omen (0.6%). Event boards draw about 65% of compatible slots from more than 50 event-exclusive contracts. The whole Activity changes palette and adds event-specific ambient effects while Discord displays the event banner. Duplicate mission instances stack into one board card while remaining independently claimable.

## Mission ranks and Guild Hall progression

New settlements can inspect and claim E-Rank missions. The Guild Hall blueprint is known from the beginning and costs 45 wood, 18 scrap and 8 cloth to construct. Building it unlocks D-Rank mission visibility.

Select the built Guild Hall on the Base screen to purchase the remaining visibility upgrades in order: C, B, A, then S. Locked ranks appear only as a mission count; their names, requirements and rewards stay hidden. The server also rejects direct analysis or claim requests for ranks the player has not unlocked.

Public bot announcements show E-Rank mission details and counts for locked higher ranks. `/fortcamp_pool` is ephemeral and personalized to the requesting Discord user's current Guild Hall rank.

The Activity separates E through S into collapsible rank boards. Unlocked boards open by default; locked boards start collapsed and reveal only their available count.

Missions with authored special Critical Success criteria cannot critically succeed until the selected party satisfies at least one of those criteria. Their natural 20 and high-total results remain ordinary successes until the path is active. General missions without special criteria use the normal stat-and-die critical calculation.

## Security notes for local Discord testing

- Never commit or share `.env`.
- Never share the bot token or client secret.
- Keep FastAPI bound to `127.0.0.1` locally.
- Do not port-forward your router.
- Use `DEV_BYPASS_AUTH=false` when exposing the Activity through a tunnel.
- All game mutations are authoritative on the backend; the Activity cannot award itself gear, characters or mission results.
- The backend verifies Discord guild membership before issuing a game session.

## Current intentional omissions

- Multiple teams queuing into one mission/world event (future system).
- PvP/team battles.
- Automated enemy raids/base defense.
- Character-pack/mod uploader.
- WebSocket live claim updates; Alpha 0.2 polls every 5 seconds, which is enough to test the game loop.
- Production migrations/backup tooling.



## Debug mission completion (0.3.1)

Add this to `.env` while testing:

```env
GAME_DEBUG_MODE=true
```

Restart `run_dev_windows.bat`. In Discord, the debug completion buttons are visible only to users Discord reports as the server owner, Administrator, or Manage Server. Local browser dev-bypass sessions also receive debug access.

Each available mission and active mission gets four buttons: Critical Failure, Failure, Success, and Critical Success. On an available mission, these buttons bypass party size and eligibility requirements and immediately claim and resolve the mission for the admin. Selecting idle party members is optional; selected characters still contribute to story and special-event conditions. Active-mission buttons immediately resolve the already deployed party. Both paths apply the matching reward/failure logic, play the matching result sound, open the aftermath, and mark the result `DEBUG FORCED`.

The Mission Board also gains a **Force New Mission Pool** debug panel. Choose Open Contracts or any regional event and force an immediate reroll. The forced pool remains active until another debug reroll or the normal 30-minute refresh boundary.

## Perks and training

Combatant, Scavenger, Constructor, Medic, Survivalist, Arcanist and Alchemist are trainable proficiency perks. Basic training requires the matching facility. Skilled consumes a common Training Manual, Expert consumes a rare Specialist Tome, and Master consumes a mythic Mastery Codex. Each trained proficiency supplies a small fixed attribute bonus and contributes to mission capability checks together with attributes and equipment.

Training Ground handles combat, scavenging and survival; Workshop handles construction; Infirmary handles medicine; Arcane Sanctum handles magic; and Alchemy Lab handles alchemy. Mission rewards provide the advanced training items and can also grant proficiency tiers directly.

Standalone perks have no tier ladder. They come from character identity, missions, event paths and transformations. The Great Beast Tide now includes a rare Blood-Moon Den contract whose hard special path can transform its lead character into a Werewolf.

Hover or keyboard-focus any perk in the roster to see its description and exact mechanical effect. This includes proficiency rating and attribute bonuses as well as standalone effects such as Lycanthrope setting the character's race to Werewolf.

## Generic portrait pools

Generic recruits select an image from a matching portrait pool when they are created. Human and goblin pools are divided by gender and role, including separate special goblin pools for bosses and elite recruits. Werewolves use a single general pool per gender. The Goblin Chieftain's Critical Success reward can recruit a boss-profile goblin from the special sets.

Each pool stores a 768×768 full portrait and a matching 192×192 roster thumbnail. A generic recruit's pool portrait is selected once, stored with that character, and never rerolled on startup or reload. Click a portrait in the roster or character header to open the larger fixed-size viewer. Manual uploads can still override the locked pool selection; the backend downsizes them to a maximum of 1200×1200 and generates a separate 192×192 thumbnail instead of retaining a 4K source.

See `PORTRAIT_GENERATION_GUIDE.md` for the complete 18-set checklist, reusable GPT batch prompt and the command that splits a 5×4 contact sheet into twenty optimized portrait pairs.

## Mission rewards, gold, and recovery

Successful missions keep their authored material, blueprint, recruit, and special-path rewards, then make rank-scaled bonus loot rolls: one at E/D, two at C/B, three at A, and four at S. Higher ranks have better item odds, and Critical Success improves those odds while adding the mission's critical reward. Failed item rolls pay a small gold fallback only when the contract has a real patron.

Gold comes only from commissioned work, bounties, rescues, and settlement-defense contracts. Salvage expeditions and ruin delves pay in recovered goods instead. Failure awards no materials or items and at most a token expense payment on a paid contract. Critical Failure awards nothing, reduces party morale, and incapacitates one deployed character. Recovery takes 30 minutes in an Infirmary, two hours in a Tent, or four hours without either facility.

Regional events always award a themed keepsake on success and add exclusive equipment and standalone perks to their loot tables. The Green Warhost has goblin war relics, the Ashen Procession has grave relics, Arcane Convergence has unstable magical tools, the Great Beast Tide has monster equipment, and Starfall Omen has Starfall Shards plus rare star-metal, voidglass, and celestial gear.

The equipment catalog now contains 50 equippable items across common, uncommon, rare, epic and mythic tiers. Higher-tier gear has a clear numerical advantage and can grant active standalone perks while equipped. Those perks participate in mission conditions and event-affinity bonuses; the roster marks equipment-granted perks with a diamond and shows the exact item source.

Regional events also have exclusive recruit populations. Green Warhost encounters include Kobolds, Hobgoblins, Orcs and Bugbears; the Ashen Procession includes Undead, Vampires, Banshees and Revenants; Arcane Convergence includes Gnomes, High Elves, Homunculi, Dreamkin and Manaforged; the Great Beast Tide draws from concrete beast races such as Catfolk, Fauns, Foxkin, Lizardfolk, Harpies, Centaurs, Minotaurs and Dragonkin; and Starfall Omen includes Aliens, Astral Elves, Voidsent, Automatons and Aasimar. Beastkin remains a rules category for those related races, while every character displays their actual race. Recruit chances rise with mission rank and gain a large Critical Success bonus.

Ordinary higher-rank missions also have a smaller chance to encounter recruitable Dwarves, Wood Elves, Half-Orcs, Halflings and Tieflings. Every new race has a racial standalone perk and small attribute adjustments rather than being a cosmetic label alone.

## Champion collection

The Champion catalog includes 220 additional characters from anime, manga and manhwa, weighted heavily toward women while retaining a smaller group of iconic male leads. The 120-character expansion deliberately fills the lower grades with cult favorites, supporting cast and deep cuts; Hana Inuzuka is one example of an E-Rank character. Collection rank now represents audience recognition and discovery rarity rather than combat power: S is reserved for broadly iconic favorites, A for major well-known characters, B for established fandom favorites, C for recognizable supporting characters, D for minor recurring characters, and E for side characters best known to committed fans. Every Champion still has role-specific attributes, proficiency perks, race, and a signature perk. Existing authored Champions remain available, bringing the complete collection counter to 224.

Procedural recruitment supports 41 races plus the secret Werewolf transformation. Ordinary missions use location-specific frontier, deepwood, mountain, water, or ruin populations, while each regional event has its own weighted population and rank gates. Hidden recruitment events keep their composition requirements server-side and reveal only a generic possibility indicator for a qualifying lineup. See [RACES.md](../reference/RACES.md) for the non-secret discovery ledger.

Celestials are a separate eight-character limited collection drawn from Greek, Roman, Egyptian, and Norse pantheons. Each named god can join a player only once and is never placed in the ordinary Champion or procedural recruit pool. Four Celestials currently have three-chapter private mission chains. A hidden team composition can reveal the first chapter; each successful chapter creates the next only for that player, leaves it claimable for 24 hours, and raises the reward tier. Mission results use authored variant passages plus party, role, advantage, and recovered-reward details to produce longer aftermath reports.

The wider mission catalog is tied together by five recurring world threads: Roads of the Broken Crown, The Unpaid Ashen Oath, The Broken Meridian, The Titan Roads, and The Starless Gate. Lareth's collapse, the Black Banner, the Ashen Procession, the Meridian Collegium, displaced titans, Starfall arrivals, and the Voidsent now point back into the same regional history. Mission cards identify their thread and explain its place in the setting.

Some successful missions roll a world consequence. When triggered, the result names an otherwise unavailable contract that will be added to the guild's next generated mission board. Eleven consequence-only missions form five short public arcs, including the Black Banner's tithe network, the Procession's empty hearse, the surviving Meridian Engine, the redirected titan migration, and a Voidsent door between dead stars. Critical Success adds 20 percentage points to the trigger chance. Consequences are stored against the completed mission and consumed once, so they survive a delayed board refresh without repeating forever.

Each consequence arc now has guaranteed story keepsakes, exclusive perks, a named legendary finale relic, and a permanent completion flag that future mission conditions can recognize. The Starless Gate finale can additionally recruit a Voidsent exile on Critical Success. See [COMBAT_DESIGN.md](../design/COMBAT_DESIGN.md) for the tactical architecture, portrait-token presentation, shared manual/auto-battle rules, horizontal build philosophy, and expansion plan.

Goblin Warcamp now has the first playable tactical encounter. Claiming it creates a persistent 8×8 battle using roster portrait thumbnails as tokens. Players can move, use their weapon attack or weapon-family special, guard, free captives, disable the alarm, retreat, step through an auto-battle one activation at a time, or resolve it instantly with Balanced, Seek Objectives, or Defensive tactics. Palisades block movement and ranged line of sight; leaving the alarm active calls reinforcements. Completing both optional objectives before defeating Rattle-Crown earns Critical Success. The completed fight returns to the normal reward, injury, story, secret-event, and consequence systems.

C-rank and higher missions make a separate visible Champion encounter roll. The base chance is 0.5% at C, 1% at B, 2.5% at A and 6% at S. Critical Success raises those chances to 1.5%, 3%, 6.5% and 14%. A mission can only select Champions whose collection rank is unlocked by that mission rank, and an already-owned Champion is permanently removed from future random encounter pools. The Roster includes a collapsible collection catalog showing owned and missing Champions.

Before release, set:

```env
GAME_DEBUG_MODE=false
```

With debug mode off, the UI controls disappear and the debug endpoint returns 404.

## Portrait image URLs

The custom player portrait can be any direct `http://` or `https://` image URL. Paste it during character creation, or change it later from the Roster tab using the player's Portrait URL field. The browser loads the image directly and falls back to initials if it fails.

Google `encrypted-tbn*.gstatic.com` thumbnail links are loaded through Fortcamp's restricted same-origin image bridge because they can fail inside an Activity frame. Other image hosts continue to load directly.

The Roster screen also accepts direct portrait uploads for the player character, recruits and Champions. Uploaded PNG, JPEG, GIF and WebP files are limited to 4 MB and stored locally under `data/portraits/`, which is excluded from source control. Production hosting should move these assets to persistent object storage before relying on ephemeral deployment disks.

Direct hotlinks are convenient for alpha testing but are not ideal permanent storage: the remote host can delete/change the file, block hotlinking, or change its URL. For a public release, use stable image hosting you control or import/copy approved pack assets into controlled storage.

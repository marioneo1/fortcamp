"""Persistent character identity, bounded memories and first-pass relationships."""
import hashlib
import random
import time

PERSONALITIES = {
    "berserker": ("Berserker", "Rushes enemies without waiting for the plan.", "aggressive", "I would rather settle it face to face."),
    "survivor": ("Self-preserver", "Seeks cover and may withdraw when badly hurt.", "survival", "A plan should leave us a way home."),
    "coward": ("Timid", "Likely to withdraw when acting independently.", "coward", "I would rather have a safe way out."),
    "guardian": ("Protector", "Stays near a vulnerable ally and guards.", "guardian", "We need to look after each other."),
    "dutiful": ("Duty-bound", "Keeps pursuing the objective by their own judgment.", "objective", "Finishing the job matters."),
    "duelist": ("Proud duelist", "Seeks the strongest enemy instead of the safest target.", "duelist", "I want an opponent who can challenge me."),
    "opportunist": ("Opportunist", "Targets weakened enemies.", "aggressive", "An opening is an opening. I will take it."),
    "strategist": ("Strategist", "Prefers a protected position and guards.", "survival", "Good positioning can spare us a bad fight."),
    "reckless": ("Daredevil", "Charges despite danger.", "aggressive", "We will learn more by trying."),
    "merciful": ("Merciful", "Attempts safe nonlethal takedowns when possible.", "merciful", "Not every fight needs another grave."),
    "curious": ("Curious explorer", "Pursues nearby objectives rather than the ordered target.", "objective", "There is always something worth checking."),
    "steadfast": ("Steadfast companion", "Guards beside the player when acting independently.", "guardian", "You can count on me to stay close."),
}
CHAMPION_PERSONALITIES = {"goblin_slayer":"dutiful", "satoru_gojo":"duelist", "levi_ackerman":"dutiful", "himmel":"guardian", "sung_jinwoo":"strategist"}
RECORD_DEFAULTS = {"missions_taken":0,"missions_completed":0,"missions_failed":0,"kills":0,"subdues":0,"times_defeated":0,"total_damage":0,"combat_turns":0,"highest_turn_damage":0}
MEAL_NAMES = {"trail_meal":"Trail Meal", "study_meal":"Study Meal", "rest_meal":"Rest Meal"}


def ensure_character(character):
    avatar=character.get("is_player") or character.get("id")=="player"
    digest=hashlib.sha256(str(character.get("id",character.get("name",""))).encode()).digest()
    if character.get("personality_id") not in PERSONALITIES:
        character["personality_id"]=CHAMPION_PERSONALITIES.get(character.get("source_id"),list(PERSONALITIES)[digest[0]%len(PERSONALITIES)])
    character["loyalty"]=100 if avatar else max(0,min(100,int(character.get("loyalty",80))))
    record=character.setdefault("service_record",{})
    for key,value in RECORD_DEFAULTS.items():record.setdefault(key,value)
    character.setdefault("recent_memories",[])
    relation=character.setdefault("relationship",{})
    # Stable per-character tastes, independent of race and personality.
    meals=list(MEAL_NAMES)
    relation.setdefault("favorite_meal",meals[digest[1]%len(meals)])
    relation.setdefault("disliked_meal",meals[(digest[1]+1)%len(meals)])
    relation.setdefault("discovered_tastes",[])
    relation.setdefault("gift_ready_at",0)
    return character


def personality_profile(character):
    base=PERSONALITIES.get(character.get("personality_id"),PERSONALITIES["survivor"])
    override=character.get("personality_override",{})
    behavior=override.get("behavior",base[2])
    if behavior not in {"aggressive","survival","coward","guardian","objective","duelist","merciful"}:behavior=base[2]
    return (str(override.get("name",base[0]))[:80],str(override.get("description",base[1]))[:240],behavior,str(override.get("voice",base[3]))[:480])


def independent_chance(unit):
    return 0 if unit.get("player_avatar") else 100-max(0,min(100,int(unit.get("loyalty",100))))


def independence_check(battle,unit):
    stamp=[battle.get("round",1),battle.get("turn_index",0)]
    if unit.get("loyalty_activation")==stamp:return False
    unit["loyalty_activation"]=stamp
    if unit.get("acted"):return False  # Do not grant a second action when resuming an older save.
    chance=independent_chance(unit)
    roll=random.Random(f"{battle.get('seed')}:loyalty:{unit['id']}:{stamp[0]}:{stamp[1]}").randint(1,100)
    return chance>0 and roll<=chance


def record_mission_start(state,party_ids):
    for char in state.get("characters",[]):
        if char["id"] in party_ids:
            ensure_character(char)
            char["service_record"]["missions_taken"]+=1


def record_mission(state,mission,party_ids,outcome,started=False):
    for char in state.get("characters",[]):
        if char["id"] not in party_ids:continue
        ensure_character(char);record=char["service_record"]
        if not started:record["missions_taken"]+=1
        record["missions_completed" if outcome in {"success","critical_success"} else "missions_failed"]+=1
        if not (char.get("is_player") or char["id"]=="player"):
            gain=2 if outcome=="critical_success" else 1 if outcome=="success" else 0
            char["loyalty"]=min(100,char["loyalty"]+gain)
        char["recent_memories"].append({"mission":mission["name"],"outcome":outcome,"at":int(time.time())})
        char["recent_memories"]=char["recent_memories"][-8:]


def record_battle(state,battle):
    for char in state.get("characters",[]):
        unit=battle.get("units",{}).get(char["id"])
        if not unit:continue
        ensure_character(char);record=char["service_record"];facts=unit.get("combat_record",{})
        for key in ("kills","subdues","times_defeated","total_damage","combat_turns"):
            record[key]+=int(facts.get(key,0))
        record["highest_turn_damage"]=max(record["highest_turn_damage"],int(facts.get("highest_turn_damage",0)))
        if char["recent_memories"]:char["recent_memories"][-1]["combat"]={k:int(facts.get(k,0)) for k in ("kills","subdues","total_damage")}


def conversation(state,char_id,action="talk",topic="recent",meal=None,now=None):
    char=next((c for c in state.get("characters",[]) if c["id"]==char_id),None)
    if not char:raise ValueError("Character not found")
    ensure_character(char)
    if char.get("is_player") or char_id=="player":raise ValueError("Choose a companion to talk to")
    if char.get("status") not in {"idle","incapacitated"}:raise ValueError("This character is away on an assignment")
    relation=char["relationship"];voice=personality_profile(char)[3];now=int(time.time()) if now is None else now
    if action=="gift_meal":
        if meal not in MEAL_NAMES:raise ValueError("Choose a prepared meal")
        if now<relation["gift_ready_at"]:raise ValueError("Give them time before offering another gift (six hours between gifts)")
        if state.get("meals",{}).get(meal,0)<1:raise ValueError("Prepare this meal in the Kitchen first")
        state["meals"][meal]-=1
        favorite=meal==relation["favorite_meal"];disliked=meal==relation["disliked_meal"]
        gain=4 if favorite else 0 if disliked else 1
        char["loyalty"]=min(100,char["loyalty"]+gain)
        relation["gift_ready_at"]=now+21600
        if meal not in relation["discovered_tastes"]:relation["discovered_tastes"].append(meal)
        line="This is my favorite. Thank you for remembering." if favorite else "Thank you, but this is not really to my taste." if disliked else "Thank you. I appreciate the meal."
        return {"speaker":char["name"],"text":line,"loyalty_gain":gain,"loyalty":char["loyalty"]}
    if action!="talk":raise ValueError("Unknown relationship action")
    if topic=="food":
        favorite=relation["favorite_meal"]
        if favorite not in relation["discovered_tastes"]:relation["discovered_tastes"].append(favorite)
        text=f"If you are asking what I enjoy, {MEAL_NAMES[favorite]} is my favorite."
    elif topic=="recent":
        memories=char["recent_memories"]
        if not memories:text="We have not been on an expedition together yet. I would like a chance to prove myself."
        else:
            m=memories[-1];won=m["outcome"] in {"success","critical_success"}
            text=f"About {m['mission']}: "+("we finished what we came to do." if won else "we did not finish the job. I want us to think about our next attempt.")
            facts=m.get("combat",{})
            if facts.get("subdues"):text+=(" I knocked one of them unconscious." if facts['subdues']==1 else f" I knocked {facts['subdues']} of them unconscious.")
            if facts.get("kills"):text+=(" I killed one of them." if facts['kills']==1 else f" I killed {facts['kills']} of them.")
            text+=" "+voice
    elif topic=="trust":
        loyalty=char['loyalty']
        text="I trust you. I will follow your lead." if loyalty==100 else "I trust you most of the time, but I still make some decisions myself." if loyalty>=75 else "I am not ready to put every decision in your hands." if loyalty>=40 else "I do not trust your plans yet."
        if loyalty<100:text+=" "+voice
    elif topic=="outlook":text=voice
    else:raise ValueError("Unknown conversation topic")
    return {"speaker":char["name"],"text":text,"loyalty":char["loyalty"]}

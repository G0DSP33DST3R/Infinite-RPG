import json
import os
import random
import shutil
import sys
import time
from datetime import datetime

SAVE_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "infinite_factions_rpg.json")


class Colors:
    HEADER = "\033[95m"
    BLUE = "\033[94m"
    GREEN = "\033[92m"
    WARNING = "\033[93m"
    FAIL = "\033[91m"
    ENDC = "\033[0m"
    BOLD = "\033[1m"
    CYAN = "\033[96m"


SPELL_BOOK = {
    "Spark Arc": {"mp_cost": 15, "power": 35, "desc": "A crackling burst of arcane lightning from a brass coil."},
    "Steam Burst": {"mp_cost": 10, "power": 22, "desc": "A compressed burst of scalding vapor that jams enemy machinery."},
    "Null Rift": {"mp_cost": 20, "power": 25, "desc": "A destabilized ether pulse that siphons life from the target."},
    "Brass Barrage": {"mp_cost": 18, "power": 42, "desc": "A volley of copper-shot bolts launched from a mechanical wand."},
    "Cinder Pulse": {"mp_cost": 12, "power": 28, "desc": "A short-lived flame pulse that ignites soot and metal alike."},
    "Geargrind Hex": {"mp_cost": 14, "power": 31, "desc": "A cursed ratchet spell that locks enemy joints and slows their steps."},
    "Iron Ember": {"mp_cost": 16, "power": 36, "desc": "A hot iron flare that scorches armor and weakens resinous defenses."},
    "Copper Cyclone": {"mp_cost": 22, "power": 48, "desc": "A spinning vortex of copper dust and trapped wind that slices across the field."},
    "Clockwork Bloom": {"mp_cost": 17, "power": 39, "desc": "A mechanical flower that erupts in toxic petals of clockwork pollen."},
    "Soot Sigil": {"mp_cost": 11, "power": 24, "desc": "A soot-stamped rune that flashes with weak but persistent arcane heat."},
    "Molten Lattice": {"mp_cost": 28, "power": 58, "desc": "A lattice of glowing metal bars that traps enemies in blistering heat."},
    "Ether Siphon": {"mp_cost": 26, "power": 52, "desc": "A siphon of raw ether that drains vigor and returns it as force."},
    "Vapor Lash": {"mp_cost": 13, "power": 29, "desc": "A whip of condensed steam that lashes out with scalding precision."},
    "Pressure Dome": {"mp_cost": 24, "power": 45, "desc": "A reinforced dome of compressed air that shoves back nearby foes."},
    "Brass Tempest": {"mp_cost": 30, "power": 63, "desc": "A storm of spinning brass shards and static lightning unleashed in a fan."},
    "Rift Engine": {"mp_cost": 35, "power": 74, "desc": "A destabilized engine core tears open a small fracture in reality."},
    "Lantern of Ash": {"mp_cost": 19, "power": 41, "desc": "A dark lantern blaze that smothers the target in powdered cinders."},
    "Tidal Cog": {"mp_cost": 21, "power": 44, "desc": "A spinning flood of bronze gears and riverwater that crashes down in waves."},
    "Gravity Plunger": {"mp_cost": 27, "power": 57, "desc": "Crushes the air around a target with a mechanical compression of force."},
    "Bluefire Fuse": {"mp_cost": 29, "power": 61, "desc": "An electric blue ignition spell that detonates with a hiss of ionized steam."},
    "Railmaker's Wrath": {"mp_cost": 32, "power": 69, "desc": "A railgun-like ether blast that tears through armor and barricades."},
    "Gilded Dread": {"mp_cost": 23, "power": 49, "desc": "Golden sigils shimmer around the caster as fear and metal both turn against the foe."},
    "Bone Valve": {"mp_cost": 15, "power": 33, "desc": "A ritual valve that vents blood and steam into a punishing burst of force."},
    "Magnet Maw": {"mp_cost": 18, "power": 38, "desc": "A field of magnetic teeth that snatches steel from the air and tears at shields."},
    "Phantom Pistons": {"mp_cost": 34, "power": 72, "desc": "Ghostly pistons hammer the opponent from all sides with spectral force."},
    "Skyforge Volley": {"mp_cost": 38, "power": 81, "desc": "A rain of celestial steel and lightning hurled from a suspended forge in the clouds."},
    "Aetheric Resonator": {"mp_cost": 40, "power": 90, "desc": "A massive resonant machine that shatters the enemy's defenses with pure harmonic force."},
}

SPELL_TIERS = ("", "Refined", "Potent", "Advanced", "Grand", "Supreme", "Aetheric")
SPELL_MASTERY_LEVELS = ((0, "Learned"), (3, "Honed"), (8, "Practiced"), (15, "Mastered"))


SPELL_TIER_UNLOCKS = (3, 2, 2, 2, 2, 2, None)
ORDERED_SPELLS = sorted(SPELL_BOOK, key=lambda name: SPELL_BOOK[name]["power"])

SPELLS_BY_TIER = {}
cursor = 0
for tier, unlock_count in enumerate(SPELL_TIER_UNLOCKS, 1):
    if unlock_count is None:
        SPELLS_BY_TIER[tier] = ORDERED_SPELLS[cursor:]
    else:
        SPELLS_BY_TIER[tier] = ORDERED_SPELLS[cursor:cursor + unlock_count]
        cursor += unlock_count


def spell_tier(spell):
    if isinstance(spell, str):
        spell_name = spell
    else:
        for name, spell_data in SPELL_BOOK.items():
            if spell_data is spell:
                spell_name = name
                break
        else:
            return len(SPELL_TIERS)

    for tier, names in SPELLS_BY_TIER.items():
        if spell_name in names:
            return tier
    return len(SPELL_TIERS)


def spell_mastery(uses):
    level = "Learned"
    for required_uses, name in SPELL_MASTERY_LEVELS:
        if uses >= required_uses:
            level = name
    return level

BASE_ENEMIES = [
    {"name": "Clockwork Rat", "hp": 25, "atk": 5, "def": 1, "exp": 15, "gold": 5},
    {"name": "Scrap Goblin", "hp": 45, "atk": 9, "def": 3, "exp": 30, "gold": 15},
    {"name": "Steam Wolf", "hp": 55, "atk": 12, "def": 2, "exp": 40, "gold": 18},
    {"name": "Ironclad Raider", "hp": 85, "atk": 16, "def": 6, "exp": 70, "gold": 35},
    {"name": "Copper Golem", "hp": 120, "atk": 18, "def": 10, "exp": 100, "gold": 50},
    {"name": "Dire Boar", "hp": 60, "atk": 15, "def": 5, "exp": 45, "gold": 20},
    {"name": "Mire Crocodile", "hp": 78, "atk": 14, "def": 8, "exp": 58, "gold": 26},
    {"name": "Ashen Bandit", "hp": 70, "atk": 17, "def": 4, "exp": 52, "gold": 22},
    {"name": "Thornback Stag", "hp": 68, "atk": 13, "def": 7, "exp": 48, "gold": 21},
    {"name": "Ember Wisp", "hp": 52, "atk": 20, "def": 2, "exp": 44, "gold": 19},
    {"name": "Ironback Tortoise", "hp": 110, "atk": 12, "def": 12, "exp": 80, "gold": 40},
    {"name": "Sandfang Scorpion", "hp": 92, "atk": 19, "def": 8, "exp": 74, "gold": 32},
    {"name": "Frost Skulk", "hp": 66, "atk": 16, "def": 6, "exp": 55, "gold": 25},
    {"name": "Bone Reaver", "hp": 95, "atk": 18, "def": 9, "exp": 76, "gold": 33},
    {"name": "Lantern Ghoul", "hp": 74, "atk": 17, "def": 5, "exp": 60, "gold": 28},
    {"name": "Tidebreaker", "hp": 115, "atk": 21, "def": 11, "exp": 95, "gold": 48},
    {"name": "Rustfang", "hp": 88, "atk": 20, "def": 7, "exp": 68, "gold": 30},
    {"name": "Sable Panther", "hp": 82, "atk": 21, "def": 6, "exp": 64, "gold": 29},
    {"name": "Bramble Ogre", "hp": 132, "atk": 24, "def": 10, "exp": 110, "gold": 58},
    {"name": "Skyfin Harrier", "hp": 96, "atk": 23, "def": 5, "exp": 78, "gold": 36},
    {"name": "Blackwater Pirate", "hp": 102, "atk": 22, "def": 9, "exp": 86, "gold": 42},
    {"name": "Magma Imp", "hp": 64, "atk": 25, "def": 4, "exp": 54, "gold": 24},
    {"name": "Grave Warden", "hp": 130, "atk": 19, "def": 15, "exp": 108, "gold": 54},
    {"name": "Twilight Basilisk", "hp": 140, "atk": 28, "def": 12, "exp": 120, "gold": 64},
    {"name": "Cinder Drake", "hp": 150, "atk": 30, "def": 14, "exp": 132, "gold": 70},
    {"name": "Aegis Knight", "hp": 160, "atk": 27, "def": 18, "exp": 140, "gold": 75},
    {"name": "Nightshade Assassin", "hp": 90, "atk": 31, "def": 4, "exp": 79, "gold": 38},
    {"name": "Void Moth", "hp": 58, "atk": 18, "def": 3, "exp": 50, "gold": 20},
    {"name": "Stone Colossus", "hp": 172, "atk": 24, "def": 20, "exp": 150, "gold": 80},
    {"name": "Wolf of the Fallen", "hp": 108, "atk": 26, "def": 7, "exp": 90, "gold": 46},
    {"name": "Webweaver Spider", "hp": 75, "atk": 18, "def": 6, "exp": 62, "gold": 27},
    {"name": "Mossback Giant", "hp": 180, "atk": 26, "def": 16, "exp": 160, "gold": 85},
    {"name": "Ironclad Monk", "hp": 120, "atk": 21, "def": 13, "exp": 100, "gold": 52},
    {"name": "Wraithbound Archer", "hp": 98, "atk": 28, "def": 5, "exp": 82, "gold": 41},
    {"name": "Starforged Seraph", "hp": 220, "atk": 35, "def": 18, "exp": 200, "gold": 110},
]

RARITY_BONUSES = {
    "Worn": 0,
    "Untouched": 3,
    "Polished": 7,
    "Shining": 14,
    "Honed": 25,
    "Masterwork": 40,
    "Perfected": 60,
    "Fabled": 85,
    "Legendary": 120,
    "Mythic": 170,
    "Celestial": 250,
    "Ethereal": 400,
    "Divine": 600,
    "Chaotic": 900,
    "Eternal": 1300,
    "Voidforged": 2000,
    "Aetherial": 3000,
}

FACTIONS = (
    "Iron Vanguard",
    "Copper Concord",
    "Steamborne Assembly",
    "Clockwork Syndicate",
    "Ashen Reavers",
    "Velvet Mechanists",
    "Brass Republic",
    "The Gilded Dominion",
    "Morrow Rail League",
    "Sunforge Compact",
    "Blackwater Cartel",
    "Cinder Hegemony",
    "Turbine Choir",
    "Rivet Dominion",
    "Glasswrought Union",
    "Mastodon League",
    "Piston Covenant",
    "Aetherworks Guild",
    "Crimson Foundry",
    "Driftwood Freeholders",
    "Skyhook Brotherhood",
    "Sootfire Cabal",
    "Obsidian Relay",
    "Diesel Covenant",
    "Copperwold Marches",
    "Mire Engineers",
    "Brimstone Exchange",
    "Cloudline Imperium",
    "Tallow Arcocracy",
)

ARCHETYPE_STATS = {
    "Artificer": (90, 20, 18, 10),
    "Engineer": (80, 90, 10, 6),
    "Clockwork Paladin": (100, 35, 21, 7),
    "Artificial Construct": (135, 0, 16, 18),
    "Aether Manifestation": (70, 135, 26, 4),
    "Clockwork Construct": (115, 0, 14, 20),
    "Clockwork Artificer": (75, 115, 12, 24),
    "Aether Engineer": (105, 75, 25, 9),
    "Aether Artificer": (85, 105, 20, 12),
    "Clockwork Engineer": (95, 85, 22, 11),
}
ARCHETYPES = {str(index): name for index, name in enumerate(ARCHETYPE_STATS, 1)}
CLASS_UNLOCK_COST = 1_000_000_000
MULTICLASS_COST = 400_000
GARAGE_COSTS = {1: 19_000, 2: 250_000, 3: 560_000}


def clear_screen():
    if sys.stdout.isatty():
        os.system("cls" if os.name == "nt" else "clear")


def draw_header(title):
    print(f"{Colors.BLUE}╔══{'═' * len(title)}══╗{Colors.ENDC}")
    print(f"{Colors.BLUE}║  {Colors.BOLD}{Colors.HEADER}{title}{Colors.ENDC}{Colors.BLUE}  ║{Colors.ENDC}")
    print(f"{Colors.BLUE}╚══{'═' * len(title)}══╝{Colors.ENDC}")


class Item:
    def __init__(self, name, item_type, rarity, stat_bonus):
        self.name = name
        self.type = item_type
        self.rarity = rarity
        self.stat_bonus = stat_bonus

    def to_dict(self):
        return {
            "name": self.name,
            "type": self.type,
            "rarity": self.rarity,
            "stat_bonus": self.stat_bonus,
        }

    @classmethod
    def from_dict(cls, data):
        return cls(data["name"], data["type"], data["rarity"], int(data["stat_bonus"]))


class ProceduralWorld:
    BIOMES = (
        "Copper Marshes",
        "Ironstep Peaks",
        "Ashen Rail Plains",
        "Broken Foundries",
        "Fogglass Wilds",
        "Cinderfen Bog",
        "Brasswood Forest",
        "Sootfall Basin",
        "Rustwind Dunes",
        "Coalheart Highlands",
        "Smogveil Mire",
        "Blackiron Ridge",
        "Embercoil Badlands",
        "Steamshroud Valley",
        "Rivetroot Thicket",
        "Geargrave Flats",
        "Furnacecrest Mountains",
        "Oilspill Delta",
        "Charcoal Barrens",
        "Gasketwood Grove",
        "Boilerstone Canyon",
        "Smokestack Moor",
        "Tarnished Tundra",
        "Rivetstorm Coast",
        "Coking Pits",
        "Ashen Orchard",
        "Wreckage Steppe",
        "Thunderhead Moor",
        "Slagglass Desert",
        "Ironbark Jungle",
        "Redline Ravines",
        "Chimneyrock Plateau",
        "Brimstone Marsh",
        "Dynamo Downs",
        "Pistonwood Forest",
        "Blacksmoke Prairie",
        "Copperhead Ravines",
        "Carbonfall Gorge",
        "Locomotive Graveyard",
        "Steamvent Cliffs",
        "Bracken Boilerlands",
        "Rustwater Fen",
        "Sootmire Lowlands",
        "Gearwheel Mesa",
        "Boilerplate Barrens",
        "Sablecoal Mountains",
        "Flintlock Foothills",
        "Cinderrail Corridor",
        "Ashen Foundrylands",
        "Gaslight Gardens",
        "Ironroot Swamp",
        "Oilglass Flats",
        "Spindlewood Vale",
        "Rivetbank Marsh",
        "Furnacefield Steppe",
        "Smogbellows Basin",
        "Crankshaft Canyon",
        "Brassneedle Forest",
        "Dreadnought Coast",
        "Tarblack Moor",
        "Emberglass Reach",
        "Smokewater Delta",
        "Coalvein Hills",
        "Scrapyard Expanse",
        "Kettleback Mountains",
        "Blackpowder Barrens",
        "Steamhammer Highlands",
        "Railspike Prairie",
        "Rusted Crown Plateau",
        "Gloomcoil Thicket",
        "Sootstone Gorge",
        "Cinderwake Isles",
        "Ironclad Peninsula",
        "Pumiceworks Wastes",
        "Hushsmoke Hollow",
        "Brassfen Wetlands",
        "Ashrail Uplands",
        "Rivetfall Escarpment",
        "Fumarole Fields",
        "Oilbone Badlands",
        "Sootbloom Heath",
        "Carbide Caverns",
        "Steamcrack Ravines",
        "Charforge Basin",
        "Wreckers' Shoals",
        "Coppercoil Jungle",
        "Smokestack Highlands",
        "Rustmoss Woods",
        "Coalglass Shore",
        "Boilerpool Marshes",
        "Grayflame Steppe",
        "Ironmist Vale",
        "Slagheap Downs",
        "Emberline Ridge",
        "Cokingstone Wastes",
        "Gearmist Forest",
        "Furnacewind Flats",
        "Tarveil Marsh",
        "Ashen Propeller Coast",
        "Blackrail Barrens",
        "Bronzeblight Prairie",
        "Steamcrown Peaks",
        "Rivetstone Badlands",
        "Sootspire Plateau",
        "Lastlight Foundry",
    )
    TOWN_NAMES = (
        "Coppergate",
        "Ironmere",
        "Steamwake",
        "Brasswatch",
        "Clocktower",
        "Cinderkeep",
        "Gilded Hollow",
        "Rivetford",
        "Ashenhall",
        "Mireforge",
        "Kilnstead",
        "Coghaven",
        "Lanternford",
        "Furnacegate",
        "Stonegear",
        "Emberwick",
        "Steelhaven",
        "Blackspire",
        "Valveford",
        "Soothold",
        "Granitewake",
        "Rookengine",
        "Copper Quay",
        "Warden's Gate",
        "Sunforge",
        "Mothwell",
        "Helmshade",
        "Crankmere",
        "Ashcroft",
        "Briarworks",
        "Pistonfield",
        "Guildkeep",
        "Tallow Keep",
        "Brassmere",
        "Ironrune",
        "Steamwell",
        "Glasswheel",
        "Crownforge",
        "Rivetshade",
        "Barrowsteam",
        "Latticeford",
        "Gleamkeep",
        "Dawnforge",
        "Nettlewatch",
        "Sablemill",
    )
    VILLAGE_NAMES = (
        "Cinderwick",
        "Nettlefield",
        "Gilded Hollow",
        "Riverton",
        "Mothspur",
        "Copperhollow",
        "Ashenford",
        "Rookmill",
        "Gallowglass",
        "Stonewick",
        "Crankmere",
        "Bellwether",
        "Hearthweir",
        "Rivetnook",
        "Dawnbarrow",
        "Coalfen",
        "Threadwick",
        "Tallowgate",
        "Steamwell",
        "Gleamcliff",
        "Mireforge",
        "Lanternford",
        "Moorhollow",
        "Sooten",
        "Ironmere",
        "Cinderhollow",
        "Brassgate",
        "Turbineford",
        "Gallowmere",
        "Nettlewick",
        "Ashfall",
        "Miller's Rest",
        "Coppermead",
        "Rookford",
        "Gearhollow",
        "Tinspire",
        "Clockwell",
        "Fallowgate",
        "Mossed Run",
        "Tinmere",
        "Pistonfield",
        "Foundry Hollow",
        "Mothwell",
        "Wren's Rest",
        "Bellforge",
    )

    @staticmethod
    def get_sector(x, y):
        rng = random.Random((x * 73856093) ^ (y * 19349663))
        roll = rng.random()
        if roll < 0.0001:
            sector_type = "Capital"
            name = rng.choice(ProceduralWorld.TOWN_NAMES)
            faction = FACTIONS[0]
        elif roll < 0.0015:
            sector_type = "Town"
            name = rng.choice(ProceduralWorld.TOWN_NAMES)
            faction = FACTIONS[0]
        elif roll < 0.035:
            sector_type = "Village"
            name = rng.choice(ProceduralWorld.VILLAGE_NAMES)
            faction = FACTIONS[1]
        else:
            sector_type = "Wilderness"
            name = rng.choice(ProceduralWorld.BIOMES)
            faction = FACTIONS[2]

        quest = None
        if sector_type != "Wilderness":
            quest_target = rng.choice(("the old road", "nearby ruins", "the forest edge", "the river pass"))
            quest = {
                "title": f"Clear the dangers near {quest_target}",
                "gold": rng.randint(45, 85),
                "exp": rng.randint(50, 90),
                "rep_gain": 25,
                "faction": faction,
            }

        return {
            "name": name,
            "type": sector_type,
            "faction": faction,
            "x": x,
            "y": y,
            "quest": quest,
            "mechanic": sector_type == "Capital" and rng.random() < 0.05,
        }

    @staticmethod
    def quest_key(x, y):
        return f"{x},{y}"


class Player:
    def __init__(self, name, archetype):
        self.name = name
        self.cls = archetype
        self.gold = 100
        self.x = 0
        self.y = 0
        starting_weapon = {
            "Artificer": Item("Cannonblade", "Weapon", "Common", 0),
            "Engineer": Item("Rivet Knife", "Weapon", "Common", 0),
            "Clockwork Paladin": Item("Rivet Sword", "Weapon", "Common", 0),
            "Artificial Construct": Item("Hinged Pike", "Weapon", "Common", 0),
            "Aether Manifestation": Item("Copper Pike", "Weapon", "Common", 0),
            "Clockwork Construct": Item("Harpoon", "Weapon", "Common", 0),
            "Clockwork Artificer": Item("CannonPike", "Weapon", "Common", 0),
            "Aether Engineer": Item("Brass Knuckles", "Weapon", "Common", 0),
            "Aether Artificer": Item("Brass Claw", "Weapon", "Common", 0),
            "Clockwork Engineer": Item("Bronze Knuckles", "Weapon", "Common", 0),
        }
        starting_armor = {
            "Artificer": Item("Leather", "Armor", "Common", 0),
            "Engineer": Item("Studded Leather", "Armor", "Common", 0),
            "Clockwork Paladin": Item("Clockwork Mail", "Armor", "Common", 0),
            "Artificial Construct": Item("Riveted Mail", "Armor", "Common", 0),
            "Aether Manifestation": Item("Riveted PlateMail", "Armor", "Common", 0),
            "Clockwork Construct": Item("Riveted Hinge Metal", "Armor", "Common", 0),
            "Clockwork Artificer": Item("Studded Hinge Metal", "Armor", "Common", 0),
            "Aether Engineer": Item("Leather", "Armor", "Common", 0),
            "Aether Artificer": Item("Studded Leather", "Armor", "Common", 0),
            "Clockwork Engineer": Item("Clockwork Mail", "Armor", "Common", 0),
        }
        self.max_hp, self.max_mp, self.attack, self.defense = ARCHETYPE_STATS[archetype]
        self.chassis = [{
            "name": archetype,
            "stats": list(ARCHETYPE_STATS[archetype]),
            "dead": False,
            "level": 1,
            "exp": 0,
            "exp_needed": 100,
        }]
        self.active_chassis = archetype
        self.current_hp = self.max_hp
        self.current_mp = self.max_mp
        self.inventory = ["Health Potion", "Mana Potion"]
        selection_seed = sum(ord(char) for char in f"{name}{archetype}")
        weapons = list(starting_weapon.values())
        armor = list(starting_armor.values())
        self.equipped_weapon = weapons[selection_seed % len(weapons)]
        self.equipped_armor = armor[(selection_seed + 1) % len(armor)]
        self.chassis[0]["inventory"] = list(self.inventory)
        self.chassis[0]["equipped_weapon"] = self.equipped_weapon.to_dict()
        self.chassis[0]["equipped_armor"] = self.equipped_armor.to_dict()
        self.garage_owned = False
        self.garage_size = 0
        self.garage_x = None
        self.garage_y = None
        self.factions = {FACTIONS[0]: 0, FACTIONS[1]: 0, FACTIONS[2]: -10}
        self.completed_quests = []
        self.spell_uses = {name: 0 for name in SPELL_BOOK}
        self.secondary_classes = []
        self.total_kills = 0
        self.lifetime_gold = 0
        self.long_rests = 0
        self.best_item = self.equipped_weapon.to_dict()
        self.device_time = time.time()
        self.market_stocks = {}

    def to_dict(self):
        self._store_active_loadout()
        return {
            "name": self.name,
            "cls": self.cls,
            "chassis": self.chassis,
            "active_chassis": self.active_chassis,
            "gold": self.gold,
            "x": self.x,
            "y": self.y,
            "max_hp": self.max_hp,
            "max_mp": self.max_mp,
            "attack": self.attack,
            "defense": self.defense,
            "current_hp": self.current_hp,
            "current_mp": self.current_mp,
            "inventory": self.inventory,
            "equipped_weapon": self.equipped_weapon.to_dict(),
            "equipped_armor": self.equipped_armor.to_dict(),
            "factions": self.factions,
            "completed_quests": self.completed_quests,
            "spell_uses": self.spell_uses,
            "secondary_classes": self.secondary_classes,
            "total_kills": self.total_kills,
            "lifetime_gold": self.lifetime_gold,
            "long_rests": self.long_rests,
            "best_item": self.best_item,
            "device_time": self.device_time,
            "market_stocks": self.market_stocks,
            "garage_owned": self.garage_owned,
            "garage_size": self.garage_size,
            "garage_x": self.garage_x,
            "garage_y": self.garage_y,
        }

    @classmethod
    def from_dict(cls, data):
        chassis_data = data.get("chassis", [])
        active_name = data.get("active_chassis", data["cls"])
        start_name = active_name if active_name in ARCHETYPE_STATS else next(iter(ARCHETYPE_STATS))
        player = cls(data["name"], start_name)
        legacy_level = max(1, int(data.get("level", 1)))
        legacy_exp = max(0, int(data.get("exp", 0)))
        legacy_exp_needed = max(1, int(data.get("exp_needed", 100)))
        for key in (
            "gold", "x", "y", "max_hp", "max_mp",
            "attack", "defense", "current_hp", "current_mp",
        ):
            setattr(player, key, int(data[key]))
        player.inventory = list(data["inventory"])
        player.equipped_weapon = Item.from_dict(data["equipped_weapon"])
        player.equipped_armor = Item.from_dict(data["equipped_armor"])
        player.factions = {faction: int(data["factions"].get(faction, 0)) for faction in FACTIONS}
        player.completed_quests = list(data.get("completed_quests", []))
        player.spell_uses = {
            name: max(0, int(data.get("spell_uses", {}).get(name, 0)))
            for name in SPELL_BOOK
        }
        player.secondary_classes = list(data.get("secondary_classes", []))
        player.total_kills = max(0, int(data.get("total_kills", 0)))
        player.lifetime_gold = max(0, int(data.get("lifetime_gold", 0)))
        player.long_rests = max(0, int(data.get("long_rests", 0)))
        player.best_item = data.get("best_item", player.equipped_weapon.to_dict())
        player.device_time = float(data.get("device_time", time.time()))
        player.market_stocks = data.get("market_stocks", {})
        player.garage_size = max(0, min(3, int(data.get("garage_size", 1 if data.get("garage_owned", False) else 0))))
        player.garage_owned = player.garage_size > 0
        player.garage_x = data.get("garage_x")
        player.garage_y = data.get("garage_y")
        if chassis_data:
            player.chassis = [
                {"name": entry["name"], "stats": [int(value) for value in entry["stats"]],
                 "dead": bool(entry.get("dead", False)),
                 "level": max(1, int(entry.get("level", legacy_level if entry["name"] == active_name else 1))),
                 "exp": max(0, int(entry.get("exp", legacy_exp if entry["name"] == active_name else 0))),
                 "exp_needed": max(1, int(entry.get("exp_needed", legacy_exp_needed if entry["name"] == active_name else 100))),
                 "carried": bool(entry.get("carried", False)),
                 "inventory": list(entry.get("inventory", data["inventory"] if entry["name"] == active_name else [])),
                 "equipped_weapon": entry.get("equipped_weapon", data["equipped_weapon"] if entry["name"] == active_name else player.equipped_weapon.to_dict()),
                 "equipped_armor": entry.get("equipped_armor", data["equipped_armor"] if entry["name"] == active_name else player.equipped_armor.to_dict())}
                for entry in chassis_data
            ]
        player.active_chassis = active_name
        player._load_active_loadout()
        return player

    def _store_active_loadout(self):
        chassis = next((entry for entry in self.chassis if entry["name"] == self.active_chassis), None)
        if chassis:
            chassis["inventory"] = list(self.inventory)
            chassis["equipped_weapon"] = self.equipped_weapon.to_dict()
            chassis["equipped_armor"] = self.equipped_armor.to_dict()

    def _load_active_loadout(self):
        chassis = self._active_chassis()
        self.inventory = list(chassis.get("inventory", self.inventory))
        self.equipped_weapon = Item.from_dict(chassis.get("equipped_weapon", self.equipped_weapon.to_dict()))
        self.equipped_armor = Item.from_dict(chassis.get("equipped_armor", self.equipped_armor.to_dict()))

    @property
    def carrying_chassis(self):
        return any(chassis["name"] != self.active_chassis for chassis in self.chassis)

    def _active_chassis(self):
        return next(chassis for chassis in self.chassis if chassis["name"] == self.active_chassis)

    @property
    def level(self):
        return self._active_chassis()["level"]

    @property
    def exp(self):
        return self._active_chassis()["exp"]

    @property
    def exp_needed(self):
        return self._active_chassis()["exp_needed"]

    def activate_chassis(self, chassis):
        self._store_active_loadout()
        current = self._active_chassis()
        if current is not chassis and self.garage_size > 0:
            current["carried"] = False
        chassis["carried"] = False
        self.active_chassis = chassis["name"]
        self.cls = chassis["name"]
        self._load_active_loadout()
        level_bonus = chassis["level"] - 1
        self.max_hp = chassis["stats"][0] + 15 * level_bonus
        self.max_mp = chassis["stats"][1] + 8 * level_bonus
        self.attack = chassis["stats"][2] + 3 * level_bonus
        self.defense = chassis["stats"][3] + 2 * level_bonus
        self.current_hp = self.max_hp
        self.current_mp = self.max_mp

    def fuse_chassis(self, first, second):
        if first is second or first not in self.chassis or second not in self.chassis:
            raise ValueError("Choose two different chassis you own.")
        if first["level"] != second["level"]:
            raise ValueError("Chassis must be the same level to fuse.")
        if first["level"] <= 50:
            raise ValueError("Chassis must be above level 50 to fuse.")
        fused_size = self.chassis_archetype_count(first) + self.chassis_archetype_count(second)
        if fused_size > self.garage_size:
            raise ValueError(f"This fusion requires a size {fused_size} garage.")
        self._store_active_loadout()
        fused = {
            "name": f"{first['name']} / {second['name']}",
            "stats": [a + b for a, b in zip(first["stats"], second["stats"])],
            "dead": False,
            "level": first["level"],
            "exp": min(first["exp"], second["exp"]),
            "exp_needed": first["exp_needed"],
            "inventory": list(first.get("inventory", [])) + list(second.get("inventory", [])),
            "equipped_weapon": max(
                (first.get("equipped_weapon", self.equipped_weapon.to_dict()), second.get("equipped_weapon", self.equipped_weapon.to_dict())),
                key=lambda item: int(item.get("stat_bonus", 0)),
            ),
            "equipped_armor": max(
                (first.get("equipped_armor", self.equipped_armor.to_dict()), second.get("equipped_armor", self.equipped_armor.to_dict())),
                key=lambda item: int(item.get("stat_bonus", 0)),
            ),
        }
        self.chassis.remove(first)
        self.chassis.remove(second)
        self.chassis.append(fused)
        if first["name"] == self.active_chassis or second["name"] == self.active_chassis:
            self.activate_chassis(fused)
        return fused

    @staticmethod
    def chassis_archetype_count(chassis):
        return len(chassis["name"].split(" / "))

    def get_total_atk(self):
        return self.attack + self.equipped_weapon.stat_bonus

    def get_total_def(self):
        return self.defense + self.equipped_armor.stat_bonus

    def record_item(self, item):
        if item.stat_bonus > int(self.best_item.get("stat_bonus", -1)):
            self.best_item = item.to_dict()

    def begin_new_life(self):
        x, y = self.x, self.y
        fresh_player = Player(self.name, self.cls)
        self.__dict__.update(fresh_player.__dict__)
        self.x, self.y = x, y

    def multiclass(self, archetype):
        hp, mp, attack, defense = ARCHETYPE_STATS[archetype]
        self.max_hp += hp
        self.max_mp += mp
        self.current_hp += hp
        self.current_mp += mp
        self.attack += attack
        self.defense += defense
        self.secondary_classes.append(archetype)
        self.cls += f" / {archetype}"

    def reputation(self, faction):
        value = self.factions.get(faction, 0)
        if value >= 100:
            status = "Family"
        elif value >= 80:
            status = "Honored"
        elif value >= 60:
            status = "Respected"
        elif value >= 40:
            status = "Heard"
        elif value >= 20:
            status = "Known"
        elif value <= -50:
            status = "Hostile"
        else:
            status = "Neutral"
        return f"{status} ({value})"

    def gain_experience(self, amount):
        chassis = self._active_chassis()
        chassis["exp"] += amount
        while chassis["exp"] >= chassis["exp_needed"]:
            chassis["exp"] -= chassis["exp_needed"]
            chassis["level"] += 1
            chassis["exp_needed"] = int(chassis["exp_needed"] * 1.5)
            self.activate_chassis(chassis)
            print(f"{Colors.HEADER}Level up! You reached level {self.level}.{Colors.ENDC}")


def save_game(player):
    filename = "".join(char if char.isalnum() or char in " _-" else "_" for char in player.name).strip(" ._")
    filename = (filename or "Player")[:30]
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), f"{filename}.json")
    with open(path, "w", encoding="utf-8") as save_file:
        json.dump({"version": 1, "player": player.to_dict()}, save_file, indent=2)
    # Remove the old single-save file once its player has been saved by name.
    if os.path.exists(SAVE_FILE):
        try:
            with open(SAVE_FILE, "r", encoding="utf-8") as legacy_file:
                legacy_data = json.load(legacy_file)
            if legacy_data.get("player", {}).get("name", "").casefold() == player.name.casefold():
                os.remove(SAVE_FILE)
        except (OSError, ValueError, AttributeError):
            pass
    print(f"{Colors.GREEN}Game saved to {path}.{Colors.ENDC}")


def load_game(path=None):
    path = path or SAVE_FILE
    if not os.path.exists(path):
        return None
    with open(path, "r", encoding="utf-8") as save_file:
        data = json.load(save_file)
    if data.get("version") != 1 or not isinstance(data.get("player"), dict):
        raise ValueError(f"Save file has an unsupported format: {path}")
    return Player.from_dict(data["player"])


def list_saved_games():
    directory = os.path.dirname(os.path.abspath(__file__))
    saves_by_name = {}
    for filename in os.listdir(directory):
        path = os.path.join(directory, filename)
        if not filename.lower().endswith(".json") or not os.path.isfile(path):
            continue
        try:
            with open(path, "r", encoding="utf-8") as save_file:
                data = json.load(save_file)
            player_data = data.get("player", {})
            if data.get("version") != 1 or not isinstance(player_data, dict) or not player_data.get("name"):
                continue
            name = player_data["name"]
            key = name.casefold()
            # Prefer a name-based save over the legacy single-save file.
            if key not in saves_by_name or path != SAVE_FILE:
                saves_by_name[key] = (name, path)
        except (OSError, ValueError, AttributeError):
            continue
    return sorted(saves_by_name.values(), key=lambda save: save[0].casefold())


def make_enemy(player, sector):
    rng = random
    base = rng.choice(BASE_ENEMIES)
    level_scale = 1 + (player.level - 1) * 0.12
    prefix, hp_mod, atk_mod, def_mod, reward_mod = "Normal", 1.0, 1.0, 1.0, 1.0
    if sector["type"] == "Wilderness":
        prefix, hp_mod, atk_mod, def_mod, reward_mod = rng.choice((
            ("Normal", 1.0, 1.0, 1.0, 1.0),
            ("Stalking", 1.2, 1.3, 0.8, 1.3),
            ("Ravaging", 1.4, 0.9, 1.2, 1.3),
            ("Hunting", 0.9, 1.3, 1.0, 1.2),
            ("Fuming", 1.3, 1.1, 1.4, 1.2),
            ("Whirling", 1.1, 1.4, 0.9, 1.4),
            ("Crushing", 1.25, 1.2, 1.0, 1.5),
            ("Howling", 1.5, 1.1, 0.7, 1.45),
            ("Rending", 1.0, 1.5, 0.85, 1.6),
            ("Smoldering", 1.35, 1.05, 1.25, 1.3),
            ("Churning", 1.45, 0.95, 1.35, 1.2),
            ("Shattering", 1.6, 1.25, 0.9, 1.7),
            ("Drifting", 1.5, 1.0, 1.4, 1.4),
            ("Thundering", 1.8, 1.2, 1.1, 1.8),
        ))
    elif sector["type"] == "Town":
        prefix, hp_mod, atk_mod, def_mod, reward_mod = rng.choice((
            ("Normal", 1.0, 1.0, 1.0, 1.0),
            ("Patrolling", 1.35, 1.1, 1.2, 1.3),
            ("Defending", 1.5, 1.25, 1.3, 1.7),
            ("Warding", 1.7, 1.15, 1.45, 1.9),
            ("Overwatching", 1.8, 1.4, 1.5, 2.1),
        ))

    aetherial = random.random() < 0.01
    if aetherial:
        prefix = "Aetherial"
        hp_mod *= 2
        atk_mod *= 1.5
        reward_mod *= 2

    hp = max(1, int(base["hp"] * hp_mod * level_scale))
    return {
        "name": base["name"] if prefix == "Normal" else f"{prefix} {base['name']}",
        "aetherial": aetherial,
        "hp": hp,
        "max_hp": hp,
        "atk": max(1, int(base["atk"] * atk_mod * level_scale)),
        "def": int(base["def"] * def_mod),
        "exp": max(1, int(base["exp"] * reward_mod * level_scale)),
        "gold": max(1, int(base["gold"] * reward_mod)),
    }


def compare_and_equip_item(player, item):
    player.record_item(item)
    slot = "equipped_weapon" if item.type == "Weapon" else "equipped_armor"
    current = getattr(player, slot)
    stat_name = "ATK" if item.type == "Weapon" else "DEF"
    print(f"\n{item.type} comparison ({stat_name}):")
    print(f"Currently equipped: {current.name} | +{current.stat_bonus} {stat_name}")
    print(f"New item:          {item.name} | +{item.stat_bonus} {stat_name}")
    print(f"Change: {item.stat_bonus - current.stat_bonus:+} {stat_name}")
    if input("Equip the new item and leave the old item behind? (y/n) ").strip().lower() == "y":
        setattr(player, slot, item)
        print(f"{item.name} equipped. {current.name} left behind.")
    else:
        print(f"You keep {current.name} equipped and leave {item.name} behind.")


def create_equipment(item_type):
    rarity = random.choices(
        list(RARITY_BONUSES),
        weights=(100, 70, 45, 28, 17, 10, 6, 4, 3, 2, 1, 1, 1, 1, 1, 1, 1),
        k=1,
    )[0]
    weapon_names = ("Cannonblade", "Rivet Knife", "Rivet Sword", "Hinged Pike", "Copper Pike", "Harpoon", "CannonPike", "Brass Knuckles", "Brass Claw", "Bronze Knuckles", "Bronze Claw", "Brass CannonPike", "Brass Harpoon", "Brass Hinged Pike", "Bronze CannonPike", "Bronze Harpoon", "Bronze Hinged Pike")
    armor_names = ("Leather", "Studded Leather", "Clockwork Mail", "Riveted Mail", "Riveted PlateMail", "Riveted Hinge Metal", "Studded Hinge Metal")
    item_name = random.choice(weapon_names if item_type == "Weapon" else armor_names)
    bonus = RARITY_BONUSES[rarity] + random.randint(1, 3)
    return Item(f"{rarity} {item_name}", item_type, rarity, bonus)


class CombatEngine:
    @staticmethod
    def highest_unlocked_spell_tier(player):
        tier = 1
        for current_tier in range(1, len(SPELL_TIERS)):
            if all(
                spell_mastery(player.spell_uses.get(name, 0)) == "Mastered"
                for name in SPELLS_BY_TIER[current_tier]
            ):
                tier = current_tier + 1
            else:
                break
        return tier

    @staticmethod
    def cast_spell(player, enemy):
        unlocked_tier = CombatEngine.highest_unlocked_spell_tier(player)
        spells = [
            (name, spell) for name, spell in SPELL_BOOK.items()
            if spell_tier(spell) <= unlocked_tier
        ]
        print("\nArcana Engine:")
        for index, (name, spell) in enumerate(spells, 1):
            tier = spell_tier(spell)
            prefix = SPELL_TIERS[tier - 1]
            display_name = f"{prefix} {name}" if prefix else name
            mastery = spell_mastery(player.spell_uses.get(name, 0))
            print(f"{index}. [Tier {tier} | {mastery}] {display_name} ({spell['mp_cost']} MP) - {spell['desc']}")
        print("0. Back")
        choice = input("Choose a spell: ").strip()
        if choice == "0":
            return False
        if not choice.isdigit() or not 1 <= int(choice) <= len(spells):
            print("Choose a listed spell.")
            return False

        name, spell = spells[int(choice) - 1]
        if player.current_mp < spell["mp_cost"]:
            print("Not enough MP.")
            return False
        player.current_mp -= spell["mp_cost"]
        previous_mastery = spell_mastery(player.spell_uses.get(name, 0))
        player.spell_uses[name] = player.spell_uses.get(name, 0) + 1
        new_mastery = spell_mastery(player.spell_uses[name])
        damage = max(1, spell["power"] + random.randint(-3, 3) - enemy["def"] // 2)
        enemy["hp"] -= damage
        print(f"You cast {name} and deal {damage} damage.")
        if new_mastery != previous_mastery:
            print(f"{name} mastery increased: {new_mastery}!")
            if new_mastery == "Mastered":
                tier = spell_tier(spell)
                if all(
                    spell_mastery(player.spell_uses.get(tier_name, 0)) == "Mastered"
                    for tier_name in SPELLS_BY_TIER[tier]
                ) and tier < len(SPELL_TIERS):
                    print(f"Tier {tier + 1} spells are now unlocked!")
        return True

    @staticmethod
    def battle(player, sector):
        enemy = make_enemy(player, sector)
        print(f"\nA {enemy['name']} appears in {sector['name']}!")
        while enemy["hp"] > 0 and player.current_hp > 0:
            print(f"\n{player.name}: {player.current_hp}/{player.max_hp} HP, {player.current_mp}/{player.max_mp} MP")
            print(f"{enemy['name']}: {enemy['hp']}/{enemy['max_hp']} HP")
            print("[1] Attack  [2] Cast spell  [3] Use potion  [4] Flee")
            choice = input("> ").strip()
            acted = False

            if choice == "1":
                if player.carrying_chassis:
                    print("While carrying another chassis, you can only attack with spells.")
                    continue
                damage = max(1, player.get_total_atk() - enemy["def"] + random.randint(-2, 3))
                enemy["hp"] -= damage
                print(f"You hit for {damage} damage.")
                acted = True
            elif choice == "2":
                acted = CombatEngine.cast_spell(player, enemy)
            elif choice == "3":
                potions = [item for item in player.inventory if item in ("Health Potion", "Mana Potion")]
                if not potions:
                    print("You have no potions.")
                    continue
                for index, potion in enumerate(potions, 1):
                    print(f"{index}. {potion}")
                potion_choice = input("Use which potion (0 to cancel)? ").strip()
                if potion_choice == "0":
                    continue
                if not potion_choice.isdigit() or not 1 <= int(potion_choice) <= len(potions):
                    print("Choose a listed potion.")
                    continue
                potion = potions[int(potion_choice) - 1]
                player.inventory.remove(potion)
                if potion == "Health Potion":
                    restored = min(50, player.max_hp - player.current_hp)
                    player.current_hp += restored
                    print(f"You restore {restored} HP.")
                else:
                    restored = min(40, player.max_mp - player.current_mp)
                    player.current_mp += restored
                    print(f"You restore {restored} MP.")
                acted = True
            elif choice == "4":
                if random.random() < 0.6:
                    print("You escaped safely.")
                    return "fled"
                print("You failed to escape!")
                acted = True
            else:
                print("Choose 1, 2, 3, or 4.")
                continue

            if enemy["hp"] <= 0:
                break
            if acted:
                damage = max(1, enemy["atk"] - player.get_total_def() + random.randint(-2, 2))
                player.current_hp = max(0, player.current_hp - damage)
                print(f"The {enemy['name']} hits you for {damage} damage.")

        if player.current_hp <= 0:
            print("You were defeated. Your character's life has ended.")
            return "lost"

        player.gold += enemy["gold"]
        player.lifetime_gold += enemy["gold"]
        player.total_kills += 1
        player.gain_experience(enemy["exp"])
        print(f"Victory! You earn {enemy['gold']} gold and {enemy['exp']} experience.")
        if enemy.get("aetherial"):
            player.inventory.append("Aetherial Enemy Corpse")
            print("You recover the Aetherial Enemy's corpse.")
        CombatEngine.try_loot(player)
        return "won"

    @staticmethod
    def try_loot(player):
        loot_roll = random.randint(3, 1300)
        if loot_roll > 457:
            return
        loot_type = random.choice(("gold", "experience", "item"))
        if loot_type == "gold":
            amount = random.randint(3, 1300)
            player.gold += amount
            player.lifetime_gold += amount
            print(f"Loot found: {amount} extra gold!")
            return
        if loot_type == "experience":
            amount = random.randint(3, 1300)
            player.gain_experience(amount)
            print(f"Loot found: {amount} extra experience!")
            return

        item_type = random.choice(("Weapon", "Armor"))
        item = create_equipment(item_type)
        print(f"Loot found: {item.name} (+{item.stat_bonus} {'ATK' if item_type == 'Weapon' else 'DEF'}).")
        compare_and_equip_item(player, item)


class TownShop:
    @staticmethod
    def item_price(item):
        # Keep basic gear cheap while scaling exceptional gear up to the cap.
        return min(250_000, int(20 + max(0, item.stat_bonus - 3) ** 2 * 0.0278))

    @staticmethod
    def enter(player, faction, x, y, mechanic=False):
        player.device_time = time.time()
        market_key = f"{x},{y}"
        market = player.market_stocks.get(market_key)
        if market is None:
            market = {
                "Weapon": [item.to_dict() for item in (create_equipment("Weapon") for _ in range(5))],
                "Armor": [item.to_dict() for item in (create_equipment("Armor") for _ in range(3))],
                "restock_at": None,
            }
            player.market_stocks[market_key] = market
        while True:
            now = time.time()
            if market["restock_at"] is not None and now >= market["restock_at"]:
                market["Weapon"] = [item.to_dict() for item in (create_equipment("Weapon") for _ in range(5))]
                market["Armor"] = [item.to_dict() for item in (create_equipment("Armor") for _ in range(3))]
                market["restock_at"] = None
                print("This market has been restocked.")
            if not market["Weapon"] and not market["Armor"] and market["restock_at"] is None:
                market["restock_at"] = now + 3 * 24 * 60 * 60
            player.device_time = now
            stock = {
                "Weapon": [Item.from_dict(item) for item in market["Weapon"]],
                "Armor": [Item.from_dict(item) for item in market["Armor"]],
            }
            print(f"\nMerchant of the {faction} | Gold: {player.gold}")
            print("[1] Health Potion (25g)  [2] Mana Potion (25g)")
            print(f"[3] Weapons ({len(stock['Weapon'])} in stock)  [4] Armor ({len(stock['Armor'])} in stock)  [5] Leave")
            if mechanic:
                print("[6] Mechanic: revive a dead chassis (400000g)")
                print("[7] Mechanic: acquire a chassis (250000g or Aetherial Enemy corpse)")
            next_garage_size = player.garage_size + 1
            if next_garage_size <= 3:
                garage_label = "Purchase" if player.garage_size == 0 else "Upgrade"
                garage_name = {1: "1 chassis", 2: "2 chassis", 3: '3 chassis "Plus Sized"'}[next_garage_size]
                print(f"[8] {garage_label} garage to {garage_name} ({GARAGE_COSTS[next_garage_size]:,}g)")
            choice = input("> ").strip()
            if choice == "5":
                return
            if choice not in ("1", "2", "3", "4"):
                if choice == "6" and mechanic:
                    dead = [chassis for chassis in player.chassis if chassis["dead"]]
                    if not dead:
                        print("The mechanic finds no dead chassis to repair.")
                    elif player.gold < 400_000:
                        print("You need 400000 gold for the repair.")
                    else:
                        for index, chassis in enumerate(dead, 1):
                            print(f"{index}. {chassis['name']}")
                        repair_choice = input("Repair which chassis (0 to cancel)? ").strip()
                        if repair_choice.isdigit() and 1 <= int(repair_choice) <= len(dead):
                            chassis = dead[int(repair_choice) - 1]
                            player.gold -= 400_000
                            chassis["dead"] = False
                            print(f"{chassis['name']} has been revived.")
                    continue
                if choice == "7" and mechanic:
                    if player.garage_size == 0:
                        print("You need a town garage before owning another chassis.")
                        continue
                    if len(player.chassis) >= player.garage_size + 1:
                        print("Your garage has no room for another chassis. Upgrade it first.")
                        continue
                    owned_names = {chassis["name"] for chassis in player.chassis}
                    available = [name for name in ARCHETYPE_STATS if name not in owned_names]
                    if not available:
                        print("You already own every available chassis.")
                        continue
                    for index, name in enumerate(available, 1):
                        print(f"[{index}] {name}")
                    selection = input("Choose a chassis (0 to cancel): ").strip()
                    if not selection.isdigit() or not 1 <= int(selection) <= len(available):
                        continue
                    name = available[int(selection) - 1]
                    print("[1] Pay 250000 gold  [2] Trade an Aetherial Enemy corpse  [0] Cancel")
                    payment = input("Choose payment: ").strip()
                    if payment == "1":
                        if player.gold < 250_000:
                            print("You need 250000 gold to purchase a chassis.")
                            continue
                        player.gold -= 250_000
                    elif payment == "2":
                        if "Aetherial Enemy Corpse" not in player.inventory:
                            print("You need an Aetherial Enemy corpse for the trade.")
                            continue
                        player.inventory.remove("Aetherial Enemy Corpse")
                    else:
                        continue
                    player.chassis.append({
                        "name": name,
                        "stats": list(ARCHETYPE_STATS[name]),
                        "dead": False,
                        "carried": True,
                        "level": 1,
                        "exp": 0,
                        "exp_needed": 100,
                        "inventory": [],
                        "equipped_weapon": Item(name, "Weapon", "Common", 0).to_dict(),
                        "equipped_armor": Item(name, "Armor", "Common", 0).to_dict(),
                    })
                    print(f"You acquired the {name} chassis.")
                    continue
                if choice == "8" and player.garage_size < 3:
                    size = player.garage_size + 1
                    price = GARAGE_COSTS[size]
                    if player.gold < price:
                        print(f"You need {price:,} gold for this garage upgrade.")
                    elif input(f"Purchase the size {size} garage for {price:,} gold? (y/n) ").strip().lower() == "y":
                        player.gold -= price
                        player.garage_size = size
                        player.garage_owned = True
                        if player.garage_x is None or player.garage_y is None:
                            player.garage_x, player.garage_y = x, y
                        print(f"Your garage is now size {size}; it can store {size} additional chassis.")
                    continue
                print("Choose 1, 2, 3, 4, or 5.")
                continue
            if choice in ("3", "4"):
                item_type = "Weapon" if choice == "3" else "Armor"
                available = stock[item_type]
                if not available:
                    print(f"The shop is out of {item_type.lower()}s.")
                    continue
                print(f"\n{item_type} stock:")
                for index, item in enumerate(available, 1):
                    stat = "ATK" if item_type == "Weapon" else "DEF"
                    print(f"[{index}] {item.name} (+{item.stat_bonus} {stat}) | {TownShop.item_price(item):,}g")
                print("[0] Back")
                selection = input("Choose an item: ").strip()
                if selection == "0":
                    continue
                if not selection.isdigit() or not 1 <= int(selection) <= len(available):
                    print("Choose an item currently in stock.")
                    continue
                item = available[int(selection) - 1]
                price = TownShop.item_price(item)
                if player.gold < price:
                    print("You do not have enough gold.")
                    continue
                if input("Buy this item? (y/n) ").strip().lower() != "y":
                    continue
                player.gold -= price
                available.remove(item)
                market[item_type] = [entry for entry in market[item_type] if entry["name"] != item.name]
                if not market["Weapon"] and not market["Armor"] and market["restock_at"] is None:
                    market["restock_at"] = time.time() + 3 * 24 * 60 * 60
                compare_and_equip_item(player, item)
                continue
            if player.gold < 25:
                print("You do not have enough gold.")
                continue
            player.gold -= 25
            potion = "Health Potion" if choice == "1" else "Mana Potion"
            player.inventory.append(potion)
            print(f"Bought a {potion}.")


def rest(player, sector):
    print("\nRest:")
    print("[1] Short rest  [2] Long rest  [0] Cancel")
    choice = input("> ").strip()
    if choice == "0":
        return
    if choice == "1":
        hp_restored = min(max(1, player.max_hp // 4), player.max_hp - player.current_hp)
        mp_restored = min(max(1, player.max_mp // 4), player.max_mp - player.current_mp)
        player.current_hp += hp_restored
        player.current_mp += mp_restored
        print(f"You take a short rest and recover {hp_restored} HP and {mp_restored} MP.")
        if sector["type"] not in ("Town", "Village") and random.random() < 0.3:
            print("Your rest is interrupted by an enemy!")
            CombatEngine.battle(player, sector)
    elif choice == "2":
        if sector["type"] != "Village":
            print("You can only take a long rest in a village.")
            return
        player.current_hp = player.max_hp
        player.current_mp = player.max_mp
        print("You take a long rest in the village and fully recover your HP and MP.")
        player.long_rests += 1
        print("\nLife statistics:")
        print(f"Enemies defeated: {player.total_kills}")
        print(f"Gold earned this life: {player.lifetime_gold} | Current gold: {player.gold}")
        print(f"Best item found: {player.best_item['name']} ({player.best_item['rarity']}, +{player.best_item['stat_bonus']} {player.best_item['type']})")
        print(f"Level: {player.level} | Quests completed: {len(player.completed_quests)} | Long rests: {player.long_rests}")
    else:
        print("Choose 1, 2, or 0.")


def render_dashboard(player, sector):
    player.device_time = time.time()
    clear_screen()
    draw_header("STEAMFORGED CHRONICLES")
    print(f"{sector['name']} ({sector['type']}) | Coordinates: {player.x}, {player.y}")
    print("\nNearby map:")
    for y in range(player.y + 2, player.y - 3, -1):
        row = []
        for x in range(player.x - 2, player.x + 3):
            if (x, y) == (player.x, player.y):
                marker = "@"
            else:
                kind = ProceduralWorld.get_sector(x, y)["type"]
                marker = {"Town": "T", "Village": "V", "Wilderness": ".", "Capital": "C"}.get(kind, ".")
            row.append(marker)
        print(" ".join(row))
    print("@ You | T Town | V Village | C Capital | . Wilds | Capital settlements may have a mechanic")

    print("\nMove: [W] north [S] south [A] west [D] east")
    print("[Travel] Travel in a straight line")
    print("[1] Hunt  [2] Market (settlements)  [3] Contract (settlements)  [4] Rest")
    print("[Inv/Char] View character sheet  [Q] Save and quit")


def show_character_sheet(player, mechanic=False):
    while True:
        print(f"\n{player.name} the {player.cls} | Character Sheet / Inventory")
        active = player._active_chassis()
        print(f"Active chassis: {active['name']} | Level {active['level']}")
        carried = [chassis for chassis in player.chassis if chassis["name"] != player.active_chassis and chassis.get("carried", False)]
        if carried:
            print("Carried chassis: " + ", ".join(chassis["name"] for chassis in carried))
        stored = [chassis for chassis in player.chassis if chassis["name"] != player.active_chassis and chassis not in carried]
        if stored:
            garage_location = (
                f"({player.garage_x}, {player.garage_y})"
                if player.garage_x is not None and player.garage_y is not None
                else "location unknown"
            )
            print(f"Garage at {garage_location}: " + ", ".join(chassis["name"] for chassis in stored))
        print("[1] View Faction Standings")
        print("[2] View Total Player Stats")
        print("[3] View Player Stats")
        print("[4] View Player Items Stats")
        print("[5] Fuse two usable chassis" + (" (mechanic)" if mechanic else " (mechanic required)"))
        print("[6] Activate another chassis" + (" (mechanic)" if mechanic else " (mechanic required)"))
        if carried:
            print("[7] Abandon carried chassis")
        print("[0] Return")
        choice = input("> ").strip()

        if choice == "0":
            return
        if choice == "1":
            print("\nFaction standings:")
            for faction in FACTIONS:
                print(f"- {faction}: {player.reputation(faction)}")
        elif choice == "2":
            print("\nTotal player stats (including equipped items):")
            print(f"Level {player.level} | XP {player.exp}/{player.exp_needed} | Gold {player.gold}")
            print(f"HP {player.current_hp}/{player.max_hp} | MP {player.current_mp}/{player.max_mp}")
            print(f"Total ATK: {player.get_total_atk()} | Total DEF: {player.get_total_def()}")
        elif choice == "3":
            print("\nPlayer stats (without equipment bonuses):")
            print(f"Class: {player.cls} | Level: {player.level}")
            print(f"HP: {player.current_hp}/{player.max_hp} | MP: {player.current_mp}/{player.max_mp}")
            print(f"Base ATK: {player.attack} | Base DEF: {player.defense}")
        elif choice == "4":
            weapon = player.equipped_weapon
            armor = player.equipped_armor
            print("\nPlayer item stats:")
            print(f"Weapon: {weapon.name} ({weapon.rarity}) | +{weapon.stat_bonus} ATK")
            print(f"Armor: {armor.name} ({armor.rarity}) | +{armor.stat_bonus} DEF")
            print(f"Inventory: {', '.join(player.inventory) if player.inventory else 'Empty'}")
        elif choice == "5":
            if not mechanic:
                print("You must be at a mechanic to fuse chassis.")
                continue
            usable = [chassis for chassis in player.chassis if not chassis["dead"]]
            if len(usable) < 2:
                print("You need two usable chassis to fuse.")
                continue
            for index, chassis in enumerate(usable, 1):
                print(f"{index}. {chassis['name']} | Level {chassis['level']} | Stats: {tuple(chassis['stats'])}")
            first_choice = input("First chassis (0 to cancel)? ").strip()
            if first_choice == "0":
                continue
            second_choice = input("Second chassis? ").strip()
            if (not first_choice.isdigit() or not second_choice.isdigit()
                    or not 1 <= int(first_choice) <= len(usable)
                    or not 1 <= int(second_choice) <= len(usable)
                    or first_choice == second_choice):
                print("Choose two different listed chassis.")
                continue
            first = usable[int(first_choice) - 1]
            second = usable[int(second_choice) - 1]
            if first["level"] != second["level"]:
                print("Chassis must be the same level to fuse.")
                continue
            if first["level"] <= 50:
                print("Chassis must be above level 50 to fuse.")
                continue
            fused = player.fuse_chassis(first, second)
            print(f"Fused into {fused['name']} with stats {tuple(fused['stats'])}.")
        elif choice == "6":
            if not mechanic:
                print("You must be at a mechanic to activate another chassis.")
                continue
            usable = [chassis for chassis in player.chassis if not chassis["dead"] and chassis["name"] != player.active_chassis]
            if not usable:
                print("You have no other usable chassis to activate.")
                continue
            for index, chassis in enumerate(usable, 1):
                print(f"{index}. {chassis['name']} | Level {chassis['level']}")
            selection = input("Activate which chassis (0 to cancel)? ").strip()
            if selection.isdigit() and 1 <= int(selection) <= len(usable):
                player.activate_chassis(usable[int(selection) - 1])
                print(f"You now pilot {player.cls}.")
        elif choice == "7" and carried:
            for index, chassis in enumerate(carried, 1):
                print(f"{index}. {chassis['name']} | Level {chassis['level']}")
            selection = input("Abandon which chassis (0 to cancel)? ").strip()
            if selection.isdigit() and 1 <= int(selection) <= len(carried):
                abandoned = carried[int(selection) - 1]
                if input(f"Abandon the {abandoned['name']} chassis permanently? (y/n) ").strip().lower() == "y":
                    player.chassis.remove(abandoned)
                    print(f"You abandon the {abandoned['name']} chassis.")
        else:
            print("Choose 1, 2, 3, 4, 5, 6, 7, or 0.")


def resolve_chassis_death(player):
    active = next((chassis for chassis in player.chassis if chassis["name"] == player.active_chassis), None)
    if active:
        active["dead"] = True
    alternatives = [chassis for chassis in player.chassis if not chassis["dead"]]
    if not alternatives:
        print("No usable chassis remain. The adventure ends.")
        return False
    print("Your chassis is destroyed. Choose another usable chassis:")
    for index, chassis in enumerate(alternatives, 1):
        print(f"[{index}] {chassis['name']} | Stats: {tuple(chassis['stats'])}")
    while True:
        choice = input("> ").strip()
        if choice.isdigit() and 1 <= int(choice) <= len(alternatives):
            player.activate_chassis(alternatives[int(choice) - 1])
            print(f"You now pilot {player.cls}.")
            return True
        print("Choose a listed chassis number.")


def main():
    clear_screen()
    draw_header("CHOOSE A PLAYER SAVE FILE")
    saved_games = list_saved_games()
    for index, (name, path) in enumerate(saved_games, 1):
        print(f"[{index}] {name} ({os.path.basename(path)})")
    new_game_option = len(saved_games) + 1
    print(f"[{new_game_option}] Start a new adventure")

    while True:
        choice = input("Select a save file or start a new adventure: ").strip()
        if choice.isdigit() and 1 <= int(choice) <= len(saved_games):
            player = load_game(saved_games[int(choice) - 1][1])
            break
        if choice == str(new_game_option):
            player = None
            break
        print("Choose one of the listed options.")

    if player is None:
        clear_screen()
        draw_header("BEGIN YOUR ADVENTURE")
        name = input("Hero name: ").strip() or "ChosenOne"
        name = name[:30]
        print("\nChoose a chassis:")
        archetypes = {
            "1": "Artificer",
            "2": "Engineer",
            "3": "Clockwork Paladin",
            "4": "Artificial Construct",
            "5": "Aether Manifestation",
            "6": "Clockwork Construct",
            "7": "Clockwork Artificer",
            "8": "Aether Engineer",
            "9": "Aether Artificer",
            "10": "Clockwork Engineer",
        }
        for key, value in archetypes.items():
            print(f"[{key}] {value}")
        choice = input("> ").strip()
        while choice not in archetypes:
            choice = input("Choose a listed chassis number: ").strip()
        player = Player(name, archetypes[choice])

    try:
        while True:
            sector = ProceduralWorld.get_sector(player.x, player.y)
            render_dashboard(player, sector)
            action = input("\nAction: ").strip().lower()
            if action == "w":
                player.y += 1
            elif action == "s":
                player.y -= 1
            elif action == "a":
                player.x -= 1
            elif action == "d":
                player.x += 1
            elif action == "travel":
                direction = input("Direction (north/south/east/west): ").strip().lower()
                directions = {
                    "north": (0, 1), "n": (0, 1),
                    "south": (0, -1), "s": (0, -1),
                    "east": (1, 0), "e": (1, 0),
                    "west": (-1, 0), "w": (-1, 0),
                }
                if direction not in directions:
                    print("Choose north, south, east, or west.")
                    input("Press Enter to continue.")
                    continue
                distance_text = input("How many coordinates? ").strip()
                if not distance_text.isdigit() or int(distance_text) < 1:
                    print("Enter a positive whole-number distance.")
                    input("Press Enter to continue.")
                    continue
                distance = int(distance_text)
                dx, dy = directions[direction]
                print(f"Traveling {distance} coordinates {direction}...")
                time.sleep(distance / 25)
                player.x += dx * distance
                player.y += dy * distance
                print(f"You arrive at coordinates {player.x}, {player.y}.")
                input("Press Enter to continue.")
            elif action == "1":
                CombatEngine.battle(player, sector)
                input("Press Enter to continue.")
            elif action == "2":
                if sector["type"] in ("Town", "Village", "Capital"):
                    if sector["type"] == "Capital" and sector["mechanic"]:
                        print("A rare mechanic is operating in this capital.")
                    TownShop.enter(
                        player, sector["faction"], player.x, player.y,
                        sector["type"] == "Capital" and sector["mechanic"],
                    )
                else:
                    print("There is no shop out here.")
                    input("Press Enter to continue.")
            elif action == "3":
                result = CombatEngine.battle(player, sector)
                if result == "lost" and not resolve_chassis_death(player):
                    save_game(player)
                    return
                quest_key = ProceduralWorld.quest_key(player.x, player.y)
                if quest is None:
                    print("There is no quest board in the wilderness.")
                elif quest_key in player.completed_quests:
                    print("You have already completed this settlement's quest.")
                else:
                    print(f"Quest: {quest['title']}")
                    print(f"Reward: {quest['gold']} gold, {quest['exp']} XP, 25 faction standing")
                    if input("Accept and fight? (y/n) ").strip().lower() == "y":
                        battle_result = CombatEngine.battle(player, sector)
                        if battle_result == "won":
                            player.gold += quest["gold"]
                            player.lifetime_gold += quest["gold"]
                            player.gain_experience(quest["exp"])
                            player.factions[quest["faction"]] = min(
                                200, player.factions[quest["faction"]] + quest["rep_gain"]
                            )
                            player.completed_quests.append(quest_key)
                            print("Quest complete. Your standing with the faction has improved.")
                        elif battle_result == "lost" and not resolve_chassis_death(player):
                            save_game(player)
                            return
                input("Press Enter to continue.")
            elif action == "4":
                rest(player, sector)
                input("Press Enter to continue.")
            elif action in ("inv", "char"):
                show_character_sheet(
                    player,
                    sector["type"] == "Capital" and sector["mechanic"],
                )
            elif action == "q":
                save_game(player)
                print("Your adventure is saved. Goodbye!")
                return
            else:
                print("Unknown action. Use W/A/S/D, Travel, 1, 2, 3, 4, Inv, Char, or Q.")
                input("Press Enter to continue.")
    except (EOFError, KeyboardInterrupt):
        print("\nSaving your adventure before exit.")
        save_game(player)


def create_run_bundle():
    """Create a folder with the game, Windows launcher, and Termux README."""
    source_dir = os.path.dirname(os.path.abspath(__file__))
    bundle_dir = os.path.join(source_dir, "Infinite_RPG_bundle")
    if os.path.abspath(source_dir) == os.path.abspath(bundle_dir):
        return

    os.makedirs(bundle_dir, exist_ok=True)
    shutil.copy2(__file__, os.path.join(bundle_dir, "Infinite_RPG.py"))
    with open(os.path.join(bundle_dir, "start.bat"), "w", encoding="utf-8", newline="\r\n") as launcher:
        launcher.write('@echo off\npython "%~dp0Infinite_RPG.py"\npause\n')

    readme = """# Infinite RPG

## Windows

Install Python 3 and enable the option to add Python to PATH. Double-click
`start.bat` to launch the game. The save file is stored beside the game script.

## Android with Termux

1. Install Termux from F-Droid or the official Termux GitHub releases.
2. Open Termux and install Python: `pkg update && pkg install python`.
3. To access shared storage, run `termux-setup-storage` and grant permission.
   Use `cd` to enter this folder, for example:
   `cd ~/storage/shared/Download/Infinite_RPG_bundle`.
4. Launch the game with `python Infinite_RPG.py`.

Use the game's `Q` action to save and exit. Keep `infinite_factions_rpg.json`
beside the script to preserve your save between sessions.
"""
    with open(os.path.join(bundle_dir, "README.md"), "w", encoding="utf-8", newline="\n") as readme_file:
        readme_file.write(readme)


if __name__ == "__main__":
    create_run_bundle()
    main()

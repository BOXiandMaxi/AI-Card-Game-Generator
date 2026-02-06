import random
from numpy.random import choice

class GameLogic:
    def __init__(self):
        # --- Database สัตว์ ---
        self.animals = [
            "Dragon", "Phoenix", "Fenrir", "Griffin", "Chimera", 
            "Hydra", "Cerberus", "Kraken", "Pegasus", "Leviathan",
            "Behemoth", "Valkyrie", "Basilisk", "Wyvern", "Golem",
            "Yeti", "Minotaur", "Kitsune", "Thunderbird", "Serpent",
            "Werewolf", "Vampire", "Dullahan", "Siren", "Cyclops",
            "Bahamut", "Tiamat", "Ifrit", "Shiva", "Odin", "Zeus", "Hades",
            "Abomination", "Demon Lord", "Seraphim", "World-Eater"
        ]
        
        self.prefixes = [
            "Ancient", "Crimson", "Shadow", "Divine", "Cursed", 
            "Eternal", "Savage", "Mystic", "Infernal", "Celestial",
            "Abyssal", "Radiant", "Chaos", "Frozen", "Void",
            "Storm", "Iron", "Spectral", "Noble", "Dark",
            "Hollow", "Primeval", "Azure", "Golden", "Blood",
            "Apocalyptic", "God-Slayer", "Forbidden", "Omnipotent", "Cataclysmic"
        ]
        
        self.titles = [
            "the Destroyer", "the Guardian", "the Slayer", "Prime", 
            "the Conqueror", "of Doom", "of Light", "Walker", 
            "Sentinel", "Overlord", "Reaper", "Champion", 
            "Avenger", "the Wise", "King", "Lord", "Titan",
            "Emperor", "Bringer", "Prophet", "the Eternal", "the Calamity", "the Creator",
            "of the End Times"
        ]

        # --- คลังคำศัพท์แบ่งตามธาตุ (เพิ่ม Light / Dark) ---
        self.actions = {
            'Fire': {
                'weak': ["Burns", "Ignites", "Heats", "Singes"],
                'normal': ["Incinerates", "Scorches", "Blasts", "Erupts"],
                'epic': ["Obliterates with hellfire", "Summons an apocalypse of", "Unleashes the supernova of", "Forges a star from"]
            },
            'Water': {
                'weak': ["Splashes", "Wets", "Chills", "Sprays"],
                'normal': ["Floods", "Freezes", "Crushes with waves", "Drowns"],
                'epic': ["Summons the absolute zero", "Unleashes the oceanic cataclysm", "Control the tides of", "Engulfs the world in"]
            },
            'Wind': {
                'weak': ["Blows", "Pushes", "Gusts", "Breezes"],
                'normal': ["Slices", "Tears", "Summons tornados", "Suffocates"],
                'epic': ["Rips the dimension with", "Summons the eternal storm of", "Moves faster than light using", "Shatters the sky with"]
            },
            'Earth': {
                'weak': ["Throws rocks", "Digs", "Hits", "Blocks"],
                'normal': ["Crushes", "Quakes", "Petrifies", "Smashes"],
                'epic': ["Reshapes the tectonic plates with", "Summons the wrath of Gaia", "Turns enemies to dust with", "Meteor strike of"]
            },
            # --- เพิ่มธาตุใหม่ ---
            'Light': {
                'weak': ["Glows at", "Flashes", "Shines on", "Beams"],
                'normal': ["Purifies", "Blinds", "Sanctifies", "Smites"],
                'epic': ["Calls down the Heaven's judgment on", "Unleashes the Genesis light upon", "Erases darkness with", "Baptizes the world with"]
            },
            'Dark': {
                'weak': ["Dims", "Haunts", "Shades", "Glooms"],
                'normal': ["Curses", "Corrupts", "Devours", "Possesses"],
                'epic': ["Plunges the world into Eternal Night", "Summons the Void's hunger", "Rends the fabric of reality with", "Drags into the abyss"]
            }
        }

        self.targets = ["the enemy", "a single target", "the opponent", "nearby foes", "the unworthy"]
        self.adjectives = ["raging", "violent", "swift", "heavy", "sharp", "burning", "frozen", "merciless", "holy", "cursed"]
        self.epic_adjectives = ["catastrophic", "god-killing", "infinite", "forbidden", "dimension-breaking", "absolute", "eternal", "world-ending"]

        self.secondary_effects = {
            'Fire': [ "leaving them burning eternally.", "melting their armor instantly.", "turning the area into a volcanic wasteland.", "and causing a massive explosion." ],
            'Water': [ "freezing their soul instantly.", "drowning them in deep pressure.", "washing away all their buffs.", "and healing all allies fully." ],
            'Wind': [ "ignoring all defense and shields.", "slicing the very air itself.", "creating a vacuum that suffocates all.", "and granting max speed to the user." ],
            'Earth': [ "stunning them for eternity.", "crushing their bones to dust.", "creating an unbreakable fortress.", "burying them alive instantly." ],
            'Light': [ "blinding all enemies permanently.", "resurrecting all fallen allies.", "granting absolute immunity.", "purging all evil from existence." ],
            'Dark': [ "stealing their life force.", "inducing eternal nightmare.", "decaying their flesh instantly.", "trapping their soul in the void." ]
        }

        self.god_tier_lines = [
            "\"Behold the death of stars; the Era of Silence begins.\"",
            "\"Thy existence is an insult to the Void; perish.\"",
            "\"I am the Entropy that devours the foundations of Reality.\"",
            "\"Tremble, for I am the Nightmare that God forgot.\"",
            "\"Not even Death can save thee from my wrath.\"",
            "\"The Seventh Seal is broken; the Universe weeps in terror.\"",
            "\"Bow down, mortal, for Judgment has arrived.\"",
            "\"I am the Beginning of the End, and the Silence that follows.\"",
            "\"All dimensions shatter before my Absolute Authority.\"",
            "\"Witness the final extinction of all hope.\"",
            "\"The Abyss gazes back, and it hungers for thy soul.\""
        ]

    def random_card_pack(self, pack_type):
        if pack_type == 'random':
            items = ["bronze", "silver", "gold", "diamond"]
            probabilities = [0.5, 0.3, 0.18, 0.02]
            return choice(items, p=probabilities)
        return pack_type

    def get_random_animal(self):
        return random.choice(self.animals)

    def generate_unique_name(self, animal, job_class):
        prefix = random.choice(self.prefixes)
        title = random.choice(self.titles)
        return f"{prefix} {animal} {title}"

    # -------------------------------------------------------------------------
    # [LOGIC UPDATE] เพิ่มเงื่อนไข Gold/Diamond ถึงจะมีสิทธิ์ได้ Light/Dark
    # -------------------------------------------------------------------------
    def generate_stats(self, card_type):
        ranges = { 'bronze': (10, 49), 'silver': (50, 69), 'gold': (70, 89), 'diamond': (90, 100) }
        r_min, r_max = ranges.get(card_type, (10, 49))
        
        # ธาตุพื้นฐาน
        base_elements = ['Earth', 'Water', 'Wind', 'Fire']
        # ธาตุหายาก
        rare_elements = ['Light', 'Dark']
        
        # ถ้าการ์ดเป็น Gold หรือ Diamond ให้รวมธาตุหายากเข้าไปในกองสุ่ม
        if card_type in ['gold', 'diamond']:
            all_elements = base_elements + rare_elements
        else:
            all_elements = base_elements # ถ้า Bronze/Silver เอาแค่พื้นฐาน

        # สลับลำดับธาตุ
        random.shuffle(all_elements)
        
        if card_type == 'diamond':
            active_elements = all_elements 
        else:
            # สุ่มมา 2 หรือ 3 ธาตุ
            pool_size = len(all_elements)
            num_elements = random.choice([2, min(3, pool_size)])
            active_elements = random.sample(all_elements, num_elements)

        stats = {el: 0 for el in all_elements}
        for el in active_elements:
            stats[el] = random.randint(r_min, r_max)

        items = list(stats.items())
        # สลับอีกรอบก่อนเรียงลำดับ
        random.shuffle(items) 
        
        sorted_elements = sorted(items, key=lambda x: x[1], reverse=True)
        
        # ส่งค่ากลับ: dict สเตตัส, (ชื่อธาตุหลัก, ค่าพลัง), (ชื่อธาตุรอง, ค่าพลัง)
        return stats, sorted_elements[0], sorted_elements[1]

    def generate_ability_desc(self, element, card_type, power):
        if element not in self.actions: element = 'Earth'
        desc = "Attacks the enemy."

        if card_type == 'bronze':
            action = random.choice(self.actions[element]['weak'])
            target = random.choice(self.targets)
            desc = f"{action} {target}."
        elif card_type == 'silver':
            action = random.choice(self.actions[element]['normal'])
            adj = random.choice(self.adjectives)
            target = random.choice(self.targets)
            desc = f"{action} {target} with {adj} power."
        elif card_type == 'gold':
            action = random.choice(self.actions[element]['normal'])
            adj = random.choice(self.adjectives)
            effect = random.choice(self.secondary_effects[element])
            desc = f"{action} enemies with {adj} {element} magic, {effect}"
        elif card_type == 'diamond':
            action = random.choice(self.actions[element]['epic'])
            epic_adj = random.choice(self.epic_adjectives)
            effect = random.choice(self.secondary_effects[element])
            templates = [
                f"{action} {epic_adj} energy, {effect}",
                f"Channels {epic_adj} {element} force that {effect}",
                f"A forbidden technique that {action} reality, {effect}"
            ]
            desc = random.choice(templates)
        
        if power == 100:
            god_line = random.choice(self.god_tier_lines)
            return f"{desc}\n{god_line}"
        
        return desc

    # -------------------------------------------------------------------------
    # [PROMPT UPDATE] เพิ่ม Background สำหรับ Light และ Dark
    # -------------------------------------------------------------------------
    def create_prompt(self, animal, card_class, weapon, element, card_type):
        rarity = card_type

        # 1. เช็คอาวุธ
        weapon_lower = weapon.lower()
        if "shield" in weapon_lower or "buckler" in weapon_lower:
            weapon_desc = f"holding a {weapon} shield in defensive stance, heavy armor, no sword"
        elif "staff" in weapon_lower or "wand" in weapon_lower or "orb" in weapon_lower or "grimoire" in weapon_lower:
            weapon_desc = f"casting magic spell with a {weapon}, glowing magic runes"
        elif "bow" in weapon_lower or "crossbow" in weapon_lower:
            weapon_desc = f"aiming a {weapon}, archery combat pose"
        else:
            weapon_desc = f"wielding a {weapon}, dynamic combat pose"

        # 2. เช็คฉากหลัง (Background Logic) - เพิ่ม Light / Dark
        backgrounds = {
            "Fire": "volcanic wasteland, flowing lava rivers, dark smoke, embers in the air, apocalyptic atmosphere",
            "Water": "stormy dark ocean, crushing waves, deep underwater abyss, bioluminescent coral, mysterious aura",
            "Wind": "high mountain peaks above clouds, thunderstorms, swirling tornado, lightning strikes, cold atmosphere",
            "Earth": "ancient overgrown forest, deep rocky canyon, roots and vines, mystical ruins, dust particles",
            "Light": "heavenly kingdom, golden gates, divine cathedral, bright clouds, aurora borealis, holy rays of light, ethereal atmosphere",
            "Dark": "twisted shadow realm, dark void dimension, eclipse, black fog, gothic horror necropolis, purple aura, nightmare world"
        }
        bg_prompt = backgrounds.get(element, "ancient dungeon ruins, dark fantasy atmosphere, mysterious fog")

        # 3. ระดับความเทพ (Rarity)
        if rarity == "diamond":
            rarity_prompt = "god-tier mythical creature, majestic aura, ornate golden armor, ethereal glow, imposing presence"
        elif rarity == "gold":
            rarity_prompt = "legendary beast, intricate armor details, heroic lighting, powerful stance"
        elif rarity == "silver":
            rarity_prompt = "battle-hardened warrior, scarred texture, weathered armor, realistic dirt and grit"
        else: # Bronze
            rarity_prompt = "wild creature, rough texture, simple leather gear, natural lighting"

        # 4. Style Tags
        style_tags = (
            "dark fantasy art style, oil painting texture, realistic fantasy illustration, "
            "intricate details, dramatic lighting, volumetric fog, "
            "rugged texture, grit and dirt, sharp details, "
            "trending on artstation, style of magic the gathering, Greg Rutkowski style"
        )

        # 5. รวมร่าง Prompt
        full_prompt = (
            f"A hyper-realistic painting of a {animal} as a {card_class}, {weapon_desc}, {element} element. "
            f"{rarity_prompt}. "
            f"Background is {bg_prompt}. "
            f"{style_tags}, full shot, wide angle, centered composition."
        )

        return full_prompt
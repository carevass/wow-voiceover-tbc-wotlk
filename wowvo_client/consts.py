# https://wowpedia.fandom.com/wiki/RaceId
RACE_DICT = {
    -1: 'narrator',
    1: 'human',
    2: 'orc',
    3: 'dwarf',
    4: 'nightelf',
    5: 'scourge',
    6: 'tauren',
    7: 'gnome',
    8: 'troll',
    9: 'goblin',
    10: 'bloodelf',
    11: 'draenei',
    12: 'felorc',
    13: 'naga',
    14: 'broken',
    15: 'skeleton',
    16: 'vrykul',
    17: 'tuskarr',
    18: 'foresttroll',
    19: 'taunka',
    20: 'northrendskeleton',
    21: 'icetroll',
    22: 'worgen',
    23: 'human',
    24: 'pandaren',
    25: 'pandaren',
    26: 'pandaren',
    27: 'nightborne',
    28: 'highmountaintauren',
    29: 'voidelf',
    30: 'lightforgeddraenei',
    31: 'zandalari',
    32: 'kultiran',
    33: 'thinhuman',
    34: 'darkirondwarf',
    35: 'vulpera',
    36: 'magharorc',
    37: 'mechagnome',
    38: 'ethereal', #added not in website
    39: 'giant', #added not in website
    40: 'demon', #added not in website
    41: 'nerubian', #added not in website
    42: 'arakkoa', #added not in website
    43: 'furbolg', #added not in website
    44: 'wolvar', #added not in website
    45: 'gorloc', #added not in website
    52: 'dracthyr',
    70: 'dracthyr',
    -77:'custom'
}

GENDER_DICT = {0: 'male',
               1: 'female',
               -77: 'custom'}

RACE_DICT_INV = {v: k for k, v in RACE_DICT.items()}
GENDER_DICT_INV = {v: k for k, v in GENDER_DICT.items()}

def race_gender_tuple_to_strings(race_gender_tuple):
    race_gender_strings = []

    for race_id, gender_id in race_gender_tuple:
        race = RACE_DICT.get(race_id, 'unknown')
        gender = GENDER_DICT.get(gender_id, 'unknown')
        race_gender_strings.append(f"{race}_{gender}")

    return race_gender_strings

REPLACE_DICT = {
                '$b': '\n', '$B': '\n', '$n': 'adventurer', '$N': 'Adventurer',
                '$C': 'Adventurer', '$c': 'adventurer', '$R': 'Traveler', '$r': 'traveler', '$t citizen : citizen': 'citizen',
                '$T Civvy : Civvy;': '',
                '<name>': 'adventurer', '<Name>': 'Adventurer',
                '<race>': 'traveler', '<Race>': 'Traveler',
                '<class>': 'adventurer', '<Class>': 'Adventurer',
                 '—':',', '--':',', " - ":", ",
                 
                 # Factions / Regions
                 "Draenei": "Dray-nai",
                "Lordaeron": "Lor-deron",
                "Quel'Thalas": "Kwel-tha-las",
                "Dalaran": "Dalah-ran",
                "Naxxramas": "Nax-ramas",
                "Scholomance": "Skolo-mance",
                "Stratholme": "Strath-holm",
                "Atal'ai":"Ata-lai",
                "Naaru":"Naroo",
                "Dragonflight": "Dragon-flight",
                "Necrolord":"necro-lord",
                "bloodmage":"blood-mage",
                "taunka'le":"taunka-lay",
                "wyrm":"werm",
                "Oneqwah":"Ohnay-kwah",
                "vrykul":"vrye-kool",
                "thor modan":"thormoe-dhaan",
                "ursoc":"ursok",
                "dun argol":"duunar-goll",
                "earthen":"ehrrthin",
                "gryphon":"griffon",
                "tyrannus":"tyerannus",

                # Bosses / NPCs
                "Malygos": "Maali-goss",
                "Kel'Thuzad": "Kel-thu-zahd",
                "Anub'arak": "Anoobah-raak",
                "Kael'thas": "Kale-thoss",
                "Mok'Nathal":"Mockna-tholl",
                "orcish":"orkish",
                "Kil'jaeden": "Kil-jayden",
                "Archimonde": "Arki-mond",
                "C'Thun": "Kuh-thoon",
                "Yogg-Saron": "Yog-suh-ron",
                "Gjalerbron": "Yal-er-bron",
                "Heb'Drakkar": "Hebdrah-kar",
                "Rageclaw": "Rage-claw",
                "Ragemane": "Rage-mane",
                "Verna":"Vur-nah",
                "Pathaleon":"Pathalion",
                "Demetrian":"Deh-mee-tree-ahn",
                "Zul'Marosh": "Zool-marosh",
                "Medivh":"Medaeve",
                "Dar'Khan":"DarKahn",
                "Stormrage": "Storm-rayge",
                "Gul'dan":"Gool dan",
                "undead":"on-ded",
                "undeath":"on-deth",
                "Lok'tar ogar":"Loktaro garr",
                'mrgl-mrgl':"mergle-mergle",
                "sseratus":'seratus',
                "sargeras":"sargheras",
                "mac'aree":"macka-ree",
                "ata'mal":"atah-maal",
                # Places
                "Icecrown": "Ice crown",
                "Dragonshrine": "Dragon-shrine",
                "Auchindoun": "Aw-kin-doon",
                "Hyjal": "High-jahl",
                "Mathystra": "Mathis-trah",
                "Ulduar": "Ool-dwar",
                "Utgarde": "Oot-guard",
                "Zul'Aman": "Zool-ahmaan",
                "Zul'Drak": "Zool-drak",
                "Ahn'kahet": "On-ka-het",
                "Gundrak": "Gun-drak",
                "Modan":"Moe-dahn",
                "Ahn'Qiraj":"On-kee-rahj",
                "Elwynn":"Elwin",
                "Arcatraz":"Arc-a-traz",
                "Stonetalon":"stone-talon",
                "Kalimdor":"Kaalim-dor",

                # Titans / Lore
                "Tyr": "Teer",
                "Freya": "Frayah",
                "Hodir": "Ho-deer",
                "mimir":"mimeer",
                "Ymiron": "Yee-miron",
                "Elune":"Ehloon",
                "ymirheim":"yeemir-heim",
                "midrealm":"mid-relm",
                "mechagnomes":"mecca-nomes",
                "mechazod":"mecca-zod",
                "dragonblight":"dragon-blight",
                # Misc
                "Felwood": "Fell-wood",
                "Ashenvale": "Ashen-veil",
                "Sha'naar":"Shanar",
                "Sin'dorei":"Sindoh-rye",
                "Gorefiend":"Gorfeend",
                "Indu'le": "Indu-lay",
                "goretalon": "gorr-talon",
                "shan'do":"shan'doe",


}

REUSE_AUDIO_MAP = {
    "fire_elemental": "demon_male",
    "water_elemental": "demon_male",
    "earth_elemental": "demon_male",
    "wind_elemental": "demon_male",
    "wolf": "rexxar",
    "banshee": "forsaken_female",
    "mountain_giant": "ancient",
    "orc_hero": "felorc_male",
    "girl":"goblin_female",
    "ethereal_stalker":"draenei_male",
    "naga_male":"broken_male",
}
VOICE_MODEL_MAP = {
    # sholazar
    "wolvar_male": "rexxar",
    "gorloc_male": "furbolg_male",
    "cairne":"big_creature",

    #dragon
    "dragon_female":"tauren_female",
    "dragon_male":"demon_male",

    # big creature shared model
    "tooga":"big_creature",
    "giant_male": "big_creature",
    "vrykul_male": "orc_male",
    "ogre_male": "felorc_male",
    "abomination":"felorc_male",
    "mountain_giant": "felorc_male",
    "mountain_giant_dk": "felorc_male", #for rune giants, e.g., Gavrock
    #other
    "giant_female":"forsaken_female",
    "giant_female_dk":"forsaken_female",
    "bone_witch":"forsaken_female",
    "titan_male":"varian",
    "matador":"ethereal_stalker",
    "ogrila_ogre":'khadgar',
    "earthen":"tuskarr_male",
    "naaru":"tauren_female",
    "murloc":"demon_female",
    "naga_male":"demon_female",
    "naga_male_dk":"demon_female",
    "fire_elemental":"demon_male",
    "water_elemental":"demon_male",
    "earth_elemental":"demon_male",
    "wind_elemental":"demon_male",
    "wolf":"rexxar",
    "bear":"rexxar",
    "mammoth":"big_creature",
    "cat":"tauren_female",
    "rhino":"tauren_male",
    "serpent":"demon_female",
    "banshee":"forsaken_female",
    "geist":"arakkoa_male",
    "demon_boy":"boy",
    "sanlayn":"bloodelf_male",
    "sporeggar":"furbolg_male",
    "akama":"broken_male",
}


# maps questgiver IDs to effect types
NPC_EFFECTS = {
    302: "ghost",
    392: "ghost",
    2076:"bubbles",
    2227:"ghost",
    2278:"ghost",
    4606:"ghost",
    6491:"ghost",
    5397:"giant",
    9598:"ghost",
    10666:"undead",
    10684:"ghost",
    10926:"ghost",
    1733:"demon",
    18261:"demon",
    12238:"ghost",
    13716:"ghost",
    14470:"demon",
    14902:"giant",
    10929:"demon", #Haleh
    10976:"demon", #Jeziba
    15362:"ghost", #malfurion stormrage
    14347:"demon", #highlord demetrian
    180642:"underwater", #inconspicuous crate (gnome_male)
    16015:"demon",
    14354:"demon",
    16201: "ghost",
    16388: "ghost",
    16813: "ghost",
    16814: "ghost",
    16815: "ghost",
    17712: "ghost",
    17674:"ghost",
    17877:"ancient",
    187565:"ghost", #elder atkanok
    18369:"small", #corki
    18445:"small", #corki
    18687:"ghost",
    20812:"small", #corki
    21797:"demon",
    21318:"ghost",
    185126:"ghost", #crimson sigil crystal prison
    22103:"demon",
    23778:"undead",
    24137:"undead",
    25425:"ghost",
    22113:"demon", #mordenai
    23433:"demon", #barthamus
    23141:"demon", #yarzill the merc
    26117:"demon", #raelorasz
    27658:"demon", #belgaristrasz
    28012:"ghost", #image of belgaristrasz stage 1
    27657:"demon", #verdisa
    27659:"demon", #eternos
    30227:"demon", #penumbrius
    32548:"demon", #corastrasza
    26206:"demon",
    24910:"ghost",
    26501:"ghost",
    26471:"ghost",
    27337:"ghost",
    29047:"ghost",
    31135:"ghost",
    19456:"ghost",
    19644:"ghost",
    27229:"ghost", #forgotten footman
    27224:"ghost", #forgotten knight
    27225:"ghost", #forgotten rifleman
    27226:"ghost", #forgotten peasant
    23730:"underwater", #harold lagras
    29455:"underwater", #gerk
    19488:"undead", #custodian dieworth
    19489:"undead", #lieutenant-sorcerer morran
    20463:"undead", #apprentice andrethan
    20464:"undead", #thadell
    20482:"comms", #image of commander ameer
    20154:"undead", #shrouded figure
    20110:"demon", #tyri
    20518:"comms",
    20084:"comms",
    19698:"ghost", #greatfather aldrimus
    20130:"demon", #andormu (boy)
    18723:"demon", #erozion (old hillsbrad)
    19935:"demon", #soridormi
    20201:"demon", #sa'at (black morass)
    27915:"demon", #chromie (cot by strath)
    38589:"demon", #valithria dreamwalker
    19937:"ghost",
    29259:"ghost",
    24027:"undead",
    24956:"ghost",
    24261:"wolf", #ulfang
    27275:"bear", #kodian
    27274:"bear", #orsonn
    28030:"serpent", #quetz'lun's spirit
    28401:"cat", #har'koa
    28561:"bear", #spirit of rhunok
    25862:"mammoth", #khu'nok
    27350:"demon",
    26443:"demon",
    27950:"demon",
    26917:"demon",
    27575:"demon",
    27990:"demon",
    27785:"demon",
    27506:"demon", #ceristrasz
    16816:"ghost", #echo of medivh
    26673:"ghost", #image of archmage modera
    17468:"undead", #prophet velen
    29481:"giant", #lok'lira the crone (inside)
    30395:"ghost", #chieftain swiftspear
    30074:"undead", #the leaper
    29579:"comms", #brann bronzbeard (via communicator)
    28666:"undead", #gorebag
    28589:"demon", #gristlegut
    26527:"demon", #chromie (purging of stratholme)
    27856:"demon", #chromie (wyrmrest)
    27765:"demon", #nalice
    26593:"demon", #serinar
    26983:"demon", #aurastrasza
    27763:"demon", #vargastrasz
    26653:"undead", #kilix the unraveler
    188419:"ghost", #elder mana'loa
    26500:"ghost", #image of drakuru
    26543:"ghost", #image of drakuru
    26701:"ghost", #image of drakuru
    26787:"ghost", #image of drakuru
    26924:"ghost", #gan'jo
    31848:"demon", #zidormi
    37779:"undead", #dark ranger loralen
    37780:"undead", #dark ranger vorel
    30304:"undead", #imhadria
    32404:"ghost", #matthias lehner
    31237:"ghost", #matthias lehner
    32408:"ghost", #matthias lehner
    32423:"ghost", #matthias lehner
    32497:"ghost", #matthias lehner
    40429:"demon", #sanctum guardian xerestrasza

}

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

VOICE_MODEL_MAP = {
    # sholazar
    "wolvar_male": "orc_male",
    "gorloc_male": "furbolg_male",

    #dragon
    "dragon_female":"demon_male",
    "dragon_male":"demon_male",


    # big creature shared model
    "giant_male": "big_creature",
    "vrykul_male": "orc_male",
    "ogre_male": "felorc_male",

    #other
    "giant_female":"forsaken_female",
    "titan_male":"varian",
    "medivh":"khadgar",
    "ogrila_ogre":'khadgar',

    "earthen":"dwarf_male",
    "naaru":"tauren_female",

    # defaults map to themselves (if not overridden)
}


# maps questgiver IDs to effect types
NPC_EFFECTS = {
    302: "ghost",
    392: "ghost",
    2227:"ghost",
    2278:"ghost",
    4606:"ghost",
    5397:"giant",
    10684:"ghost",
    1733:"demon",
    18261:"demon",
    14470:"demon",
    14902:"giant",
    16201: "ghost",
    17712: "ghost",
    17674:"ghost",
    18369:"small",
    18445:"small",
    20812:"small",
    21700:"demon",
    21797:"demon",
    21318:"ghost",
    21330:"demon",
    22103:"demon",
    24910:"ghost",
    26501:"ghost",
    27337:"ghost",
    29047:"ghost",
    31135:"ghost",
    19456:"ghost",
    19644:"ghost",
    19488:"undead",
    19489:"undead",
    20463:"undead",
    20464:"undead",
    20482:"comms",
    20518:"comms",
    20084:"comms",
    28377:"undead",
    28907:"undead",
    28911:"undead",
    19937:"ghost",

}

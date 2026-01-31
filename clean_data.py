from wowvo_client.consts import race_gender_tuple_to_strings
from wowvo_client import utils
import numpy as np
import pandas as pd
from corrections.corrections import apply_corrections, add_new_entries
from data_prep.sql_queries import query_dataframe_for_all_quests_and_gossip


def clean_quest_data(tts_processor):

    language_code = "enUS"
    language_number = utils.language_code_to_language_number(language_code)
    print(f"Selected language: {language_code}")

    #Load data from our SQL query with tbc/wotlk data
    df = query_dataframe_for_all_quests_and_gossip(language_number)
    print("Data query OK.", flush = True)

    #mark custom models with -77 for sex and gender so code doesn't break when hashing
    mask = df['DisplayRaceID'].isna() & df['DisplaySexID'].isna()
    df.loc[mask, ['DisplayRaceID', 'DisplaySexID']] = -77

    #caterogize quests and gossip by expansion...roughly since there is no clear cutoff

    #create expansion category
    conditions = [
        (df['id'] >= 1) & (df['id'] < 15278),
        (df['id'] >= 15278) & (df['id'] < 23728),
        (df['id'] >= 23728) & (df['id'] < 80000)
    ]

    # Values for each condition
    choices = [0, 1, 2]  # 0: Vanilla, 1: TBC, 2: WotLK

    df['expansion'] = np.select(conditions, choices, default=-1)

    # Mask to identify rows where expansion == -1
    mask = df['expansion'] == -1

    # Subset the DataFrame
    df_subset = df[mask]

    # Conditions for just that subset
    conditions2 = [
        (df_subset['id'] >= 89931) & (df_subset['id'] < 180918),
        (df_subset['id'] >= 180918) & (df_subset['id'] < 186585),
        (df_subset['id'] >= 186585)
    ]

    # Apply np.select just to the subset
    new_expansion_values = np.select(conditions2, choices, default=-1)

    # Assign result back to the original DataFrame
    df.loc[mask, 'expansion'] = new_expansion_values

    # recategorize expansion from corrections file before filtering, this will eliminate some vanilla npcs that are being
    # wrongly categorized as tbc in the logic above

    #filter out vanilla observations to avoid overlap with original VO
    #we know that original VO only missed custom models and item/gameobject quests
    #filtering the rest out should do the trick

    df = df[
        (df['expansion'] != 0) |
        (df['type'].isin(['item','gameobject'])) |
        (df['DisplayRaceID'] == -77) |
        ((df['DisplayRaceID'] == 8) & (df['DisplaySexID'] == 0)) # specifically keeping troll males from vanilla to add that in
    ]
    #add missing quest entries from excel; note all columns must be filled out

    df = add_new_entries(df,"corrections/new_entries.xlsx")
    print("Applying new entries ...", flush = True)


    #add the new columns
    df = tts_processor.preprocess_dataframe(df)


    #do corrections
    df = apply_corrections(df, "corrections/corrections.xlsx")
    print("Applying corrections ...", flush = True)


    # Define the mapping of old values to new values
    replace_map = {
        'scourge_male': 'forsaken_male',
        'scourge_female': 'forsaken_female',
        'icetroll_male': 'troll_male',
        'narrator_male': 'narrator',
        'taunka_male': 'tauren_male',
        'naga_female':'demon_female'
    }

    # Apply the replacement
    df['voice_name'] = df['voice_name'].replace(replace_map)


    #correct some gossips that have nan for quest and quest_title
    df['quest'] = df.quest.fillna('')
    df['quest_title'] = df.quest_title.fillna('')

    # Get unique race-gender combinations
    unique_race_gender_combos = df[[
        'DisplayRaceID', 'DisplaySexID']].drop_duplicates().values
    # Convert the unique race-gender combinations to a tuple
    race_gender_tuple = tuple(map(tuple, unique_race_gender_combos))


    selected_voice_names = race_gender_tuple_to_strings(
            race_gender_tuple)

    # Add the new values if not already in the list
    for new_value in replace_map.values():
        if new_value not in selected_voice_names:
            selected_voice_names.append(new_value)
    #append other race-gender combos that were not in the list for some reason
    selected_voice_names.append('ogre_male')
    selected_voice_names.append('rexxar')
    selected_voice_names.append('tirion')
    selected_voice_names.append('jaina')
    selected_voice_names.append('mechanical')
    selected_voice_names.append('demon_male')
    selected_voice_names.append('big_creature')
    selected_voice_names.append('varian')
    selected_voice_names.append('khadgar')
    selected_voice_names.append('arthas')
    selected_voice_names.append('thrall')
    selected_voice_names.append('boy')
    selected_voice_names.append('girl')
    selected_voice_names.append('sylvanas')
    selected_voice_names.append('furbolg_male')
    selected_voice_names.append('arakkoa_male')
    selected_voice_names.append('ancient')
    selected_voice_names.append('satyr')
    selected_voice_names.append('dryad')
    selected_voice_names.append('naaru')
    selected_voice_names.append('tuskarr_male')
    selected_voice_names.append('wolvar_male')
    selected_voice_names.append('gorloc_male')
    selected_voice_names.append('keeper')
    selected_voice_names.append('lich_king')
    selected_voice_names.append('human_necro')
    selected_voice_names.append('ogrila_ogre')
    selected_voice_names.append('titan_male')
    selected_voice_names.append('earthen')
    selected_voice_names.append('giant_male')
    selected_voice_names.append('dragon_male')
    selected_voice_names.append('arthas_dk')
    selected_voice_names.append('draenei_female_dk')
    selected_voice_names.append('draenei_male_dk')
    selected_voice_names.append('troll_male_dk')
    selected_voice_names.append('bloodelf_female_dk')
    selected_voice_names.append('bloodelf_male_dk')
    selected_voice_names.append('draenei_female_dk')
    selected_voice_names.append('orc_male_dk')
    selected_voice_names.append('nightelf_female_dk')
    selected_voice_names.append('forsaken_male_dk')
    selected_voice_names.append('gnome_female_dk')
    selected_voice_names.append('human_male_dk')
    selected_voice_names.append('human_necro_dk')


    del df_subset

    return "Quest and gossip data cleaning complete.", df

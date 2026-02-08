import requests
import os
import pandas as pd
from tqdm import tqdm
import hashlib
from concurrent.futures import ThreadPoolExecutor
import re
from wowvo_client.consts import RACE_DICT, GENDER_DICT, VOICE_MODEL_MAP, NPC_EFFECTS
from wowvo_client.length_table import write_sound_length_table_lua
from wowvo_client.utils import get_first_n_words, get_last_n_words, replace_dollar_bs_with_space
from slpp import slpp as lua
from wowvo_client.audio_effects import *
from pydub import AudioSegment
import io
from wowvo_client.tts_engine import TTSEngine
import subprocess

DATAMODULE_TABLE_GUARD_CLAUSE = 'if not VoiceOver or not VoiceOver.DataModules then return end'
REPLACE_DICT = {'$b': '\n', '$B': '\n', '$n': 'adventurer', '$N': 'Adventurer',
                '$C': 'Adventurer', '$c': 'adventurer', '$R': 'Traveler', '$r': 'traveler', '$t citizen : citizen': 'citizen',
                '$T Civvy : Civvy;': '',
                 '—':',', '--':',', " - ":", ",
                 # Factions / Regions
                 "Draenei": "Dray-nai",
                "Lordaeron": "Lord-air-on",
                "Quel'Thalas": "Kwel-tha-las",
                "Dalaran": "Dal-ah-ran",
                "Naxxramas": "Nax-ramas",
                "Scholomance": "Skolo-mance",
                "Stratholme": "Strath-holm",
                "Atal'ai":"Ata-lai",
                "Naaru":"Naroo",
                "Dragonflight": "Dragon-flight",



                # Bosses / NPCs
                "Malygos": "Mal-ee-goss",
                "Kel'Thuzad": "Kel-thu-zahd",
                "Anub'arak": "Anub-araak",
                "Kael'thas": "Kale-thoss",
                "Mok'Nathal":"Mockna-tholl",
                "orcish":"orkish",
                "Kil'jaeden": "Kil-jay-den",
                "Archimonde": "Ark-i-mond",
                "C'Thun": "Kuh-thoon",
                "Yogg-Saron": "Yog-suh-ron",
                "Gjalerbron": "Yal-er-bron",
                "Heb'Drakkar": "Heb-drah-kar",
                "Rageclaw": "Rage-claw",
                "Ragemane": "Rage-mane",
                "Verna":"Vur-nah",
                "Pathaleon":"Pathalion",
                "Demetrian":"Deh-mee-tree-ahn",
                "Zul'Marosh": "Zool-marosh",
                "Medivh":"Meh-deev",
                "Dar'Khan":"DarKahn",
                "Stormrage": "Storm-rayge",
                "Gul'dan":"Gool dan",


                # Places
                #"Azeroth":"Ah-ze-roth",
                "Icecrown": "Ice crown",
                "Dragonshrine": "Dragon-shrine",
                "Auchindoun": "Aw-kin-doon",
                "Hyjal": "High-jahl",
                "Mathystra": "Math-is-trah",
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

                # Titans / Lore
                "Tyr": "Teer",
                "Freya": "Fray-ah",
                "Thorim": "Thor-rim",
                "Hodir": "Ho-deer",
                "Loken": "Low-ken",
                "Ymiron": "Yee-miron",
                "Elune":"Ehloon",

                # Misc
                "Felwood": "Fell-wood",
                "Ashenvale": "Ash-en-vale",
                "Grizzly Hills": "Grizz-lee Hills",
                "Stranglekelp":"Strangle-kelp",
                "Sha'naar":"Shanar",
                "Sin'dorei":"Sindoh-rye",
                "Gorefiend":"Gorfeend",


}
VOICE_SAMPLE_FOLDER = "voices"


def get_hash(text):
    hash_object = hashlib.md5(text.encode())
    return hash_object.hexdigest()


def prune_quest_id_table(quest_id_table):
    def is_single_quest_id(nested_dict):
        if isinstance(nested_dict, dict):
            if len(nested_dict) == 1:
                return is_single_quest_id(next(iter(nested_dict.values())))
            else:
                return False
        else:
            return True

    def single_quest_id(nested_dict):
        if isinstance(nested_dict, dict):
            return single_quest_id(next(iter(nested_dict.values())))
        else:
            return nested_dict

    pruned_table = {}
    for source_key, source_value in quest_id_table.items():
        pruned_table[source_key] = {}
        for title_key, title_value in source_value.items():
            if is_single_quest_id(title_value):
                pruned_table[source_key][title_key] = single_quest_id(title_value)
            else:
                pruned_table[source_key][title_key] = {}
                for npc_key, npc_value in title_value.items():
                    if is_single_quest_id(npc_value):
                        pruned_table[source_key][title_key][npc_key] = single_quest_id(npc_value)
                    else:
                        pruned_table[source_key][title_key][npc_key] = npc_value

    return pruned_table


def clean_folder(df, expansions=[0, 1, 2], module_name="AI_VoiceOverData_TBC"):
    # Filter DF by expansion
    df = df[df['expansion'].isin(expansions)]

    # Collect all expected filenames
    expected_files = set()
    for _, row in df.iterrows():
        quest_id = str(row.get("quest", "")).strip()
        source = str(row.get("source", "")).strip().lower()

        if quest_id:  # quest dialogue
            base_name = f"{quest_id}-{source}.mp3"
            subfolder = "quests"
        else:  # gossip dialogue
            base_name = f"{row['templateText_race_gender_hash']}.mp3"
            subfolder = "gossip"

        # If gender is specified, add gendered versions
        if row.get("player_gender") in ["m", "f"]:
            filename = f"{row['player_gender']}-{base_name}"
            expected_files.add(os.path.join(subfolder, filename))
        else:
            # Add both gendered and non-gendered, just in case
            expected_files.add(os.path.join(subfolder, base_name))
            expected_files.add(os.path.join(subfolder, f"m-{base_name}"))
            expected_files.add(os.path.join(subfolder, f"f-{base_name}"))

    # Define base sound folder
    sound_folder = os.path.join(module_name, "generated", "sounds")

    # Walk through quests & gossip folders and clean up
    for subfolder in ["quests", "gossip"]:
        folder_path = os.path.join(sound_folder, subfolder)
        if not os.path.isdir(folder_path):
            continue  # skip missing subfolders

        for fname in os.listdir(folder_path):
            fpath = os.path.join(subfolder, fname)  # relative path
            full_path = os.path.join(folder_path, fname)

            if fpath not in expected_files:
                print(f"🗑️ Deleting extra file: {full_path}")
                os.remove(full_path)

    print("✅ Folder cleanup complete.")
def clean_brackets(s):
    if pd.isna(s):
        return s

    # If ENTIRE string is just <...>, keep inside
    m = re.fullmatch(r'<\s*(.*?)\s*>', s)
    if m:
        return m.group(1)   # return only inner text

    # Otherwise remove <...> completely
    return re.sub(r'<.*?>', '', s)

class TTSProcessor(TTSEngine):
    def __init__(self, module_name='AI_VoiceOverData_TBC'):
        self.module_name = module_name
        self.output_folder = os.path.join(self.module_name, 'generated')
        self.sound_output_folder = os.path.join(self.output_folder, 'sounds')
        super().__init__()

    def create_output_subdirs(self, subdir: str):
        output_subdir = os.path.join(self.sound_output_folder, subdir)
        os.makedirs(output_subdir, exist_ok=True)

    def tts(self, text, voice_name, output_name, output_subfolder, forceGen=True, questgiver_id=None,
                          temperature = 0.75, length_penalty = 1.0, repetition_penalty = 10.0,
                          top_k = 1, top_p = 1.0, speed = 1.05, f0_up_key = 0, f0_method = "rmvpe",
                          index_rate = 0.70, filter_radius = 3, resample_sr = 0, rms_mix_rate = 1,
                          protect = 0.25
                          ):

        SOUND_OUTPUT_FOLDER = os.path.join(self.sound_output_folder, output_subfolder)
        VOICE_SAMPLE_FOLDER = "voices"

        outpath = os.path.join(SOUND_OUTPUT_FOLDER, output_name)
        # Keep original voice_name for effects further below
        voice_key = voice_name

        #remode dk suffix from dk so model search matches with the corresponding
        #race-gender model on file
        if voice_name.endswith("_dk"):
            voice_name = voice_name[:-3]

        mapped_voice = VOICE_MODEL_MAP.get(voice_name, voice_name)

        if os.path.isfile(outpath) and not forceGen:
            print("duplicate generation, skipping")
            return

        voice_path = os.path.join(VOICE_SAMPLE_FOLDER, f"{voice_name}.wav")
        if not os.path.isfile(voice_path):
            print(f"Voice sample not found: {voice_path}")
            return
        # Set model_dir based on mapped voice, or voice_name
        model_dir = f"fine_tuned/{mapped_voice}"


        if not os.path.isdir(model_dir):
            model_dir = None  # fallback in FastAPI will handle this

        files = {
            "speaker_wav": voice_path
        }
        data = {
            "text": text,
            "language": "en",
            "model_dir": model_dir or "",  # If None, FastAPI treats it as base
            "voice_name":mapped_voice
        }


        response = self.synthesize(
            text = data["text"],
            speaker_wav = files["speaker_wav"],
            language = data["language"],
            model_dir = data["model_dir"],
            voice_name = mapped_voice,


            # XTTS params
            temperature = temperature,
            length_penalty = length_penalty,
            repetition_penalty = repetition_penalty,
            top_k = top_k,
            top_p = top_p,
            speed = speed,
            #RVC Params
            f0_up_key = f0_up_key,
            f0_method = f0_method,
            index_rate = index_rate,
            filter_radius = filter_radius,
            resample_sr = resample_sr,
            rms_mix_rate = rms_mix_rate,
            protect = protect
        )
        os.makedirs(os.path.dirname(outpath), exist_ok=True)

        # Convert response.content (which is WAV) into an MP3
        audio = AudioSegment.from_file(self.output_path, format="wav")

        audio.export(outpath, format="mp3", bitrate = "64k")

        #after voice generation, apply sfx based on certain race-gender combos
        if voice_key.endswith("_dk"):
            print(f"DK post-processing for {outpath}")
            dk_effects(outpath)
        elif voice_key in ("sylvanas", "forsaken_male", "forsaken_female"):
            print(f"Undead post-processing for {outpath}")
            undead_effects(outpath)
        elif voice_key in ("mechanical", "titan_male"):
            print(f"Robot post-processing for {outpath}")
            robot_effects(outpath)
        elif voice_key in ("demon_male", "keeper", "dragon_male", "dragon_female"):
            print(f"Demon post-processing for {outpath}")
            demon_effects(outpath)
        elif voice_key in ("giant_male", "ogre_male", "ogrila_ogre","ancient"):
            print(f"Giant post-processing for {outpath}")
            giant_effects(outpath, voice_key)
        elif voice_key in ("wolvar_male", "gorloc_male"):
            print(f"Small creature post-processing for {outpath}")
            small_effects(outpath)
        elif voice_key in ("earthen"):
            print(f"Earthen creature post-processing for {outpath}")
            earthen_effects(outpath)
        elif voice_key in ("naaru"):
            print(f"Naaru creature post-processing for {outpath}")
            naaru_effects(outpath)
        elif voice_key in ("ethereal_male"):
            print(f"Ethereal creature post-processing for {outpath}")
            ethereal_effects(outpath)
        # Apply questgiver-specific effects that don't conform to race_gender categories
        if questgiver_id and questgiver_id in NPC_EFFECTS:
            effect_type = NPC_EFFECTS[questgiver_id]
            if effect_type == "ghost":
                print("Doing ghost effects", flush = True)
                ghost_effects(outpath)
            elif effect_type == "demon":
                print("Doing demon effects", flush = True)
                demon_effects(outpath)
            elif effect_type == "giant":
                print("Doing giant effects", flush = True)
                giant_effects(outpath, voice_key)
            elif effect_type == "undead":
                print("Doing undead effects", flush = True)
                undead_effects(outpath)
            elif effect_type == "small":
                print(f"Small creature effects", flush = True)
                small_effects(outpath)
            elif effect_type == "comms":
                print(f"Telephone effects ...", flush = True)
                comms_effects(outpath)
        print(f"Audio saved and processed: {outpath}")



    def handle_gender_options(self, text):
        pattern = re.compile(r'\$[Gg]\s*([^:;]+?)\s*:\s*([^:;]+?)\s*;')

        male_text = pattern.sub(r'\1', text)
        female_text = pattern.sub(r'\2', text)

        return male_text, female_text

    def preprocess_dataframe(self, df):
        df = df.copy() # prevent mutation on original df for safety
        df['race'] = df['DisplayRaceID'].map(RACE_DICT)
        df['gender'] = df['DisplaySexID'].map(GENDER_DICT)
        df['voice_name'] = df['race'] + '_' + df['gender']

        df['templateText_race_gender'] = df['original_text'] + df['race'] + df['gender']
        df['templateText_race_gender_hash'] = df['templateText_race_gender'].apply(get_hash)

        df['cleanedText'] = df['text'].copy()

        for k, v in REPLACE_DICT.items():
            df['cleanedText'] = df['cleanedText'].str.replace(k, v, regex=False, flags=re.IGNORECASE)

        #deal with text in brackets: if its all the text for that NPC, keep the text, otherwise remove it

        df['cleanedText'] = df['cleanedText'].apply(clean_brackets)

        # Remove quotes
        df['cleanedText'] = df['cleanedText'].str.replace(r'(?<!^)"(?!$)', '', regex=True)

        #Removes commas
        df['cleanedText'] = df['cleanedText'].str.replace(
            r',\s+(and|but|you|he|she|they|we|i)\b',
            r' \1',
            regex=True
        )

        # Remove appositive commas (optional)
        df['cleanedText'] = df['cleanedText'].str.replace(
            r',\s*([^,]{1,60}?)\s*,',
            r' \1',
            regex=True
        )
        #no commas for short sentences
        df['cleanedText'] = df['cleanedText'].apply(lambda x: x.replace(",", "") if len(x) <= 50 else x)

        #deal with ellipses
        # normalize spaced ellipses like ". . ." or ". ." into "..."
        df['cleanedText']  = df['cleanedText'].str.replace(r"\.\s+\.\s+\.", "...",regex=True)  # ". . ." → "..."
        df['cleanedText']  = df['cleanedText'].str.replace(r"\.\s+\.", "...", regex=True)       # ". ."   → "..."


        # "..." inside a sentence → ","
        df['cleanedText'] = df['cleanedText'].str.replace(r"\.\.\.(\w)", r", \1", regex=True)
        # "..." at the end → "."
        df['cleanedText'] = df['cleanedText'].replace(r"\.\.\.$", ".", regex=True)

        # Remove newlines and normalize spaces
        df['cleanedText'] = df['cleanedText'].str.replace(r'\n+', ' ', regex=True)  # remove newlines
        df['cleanedText'] = df['cleanedText'].str.replace(r'\s+', ' ', regex=True)  # normalize multiple spaces
        df['cleanedText'] = df['cleanedText'].str.strip()  # remove leading/trailing spaces

        #remove illegal characters
        df["cleanedText"] = (
            df["cleanedText"]
            .str.replace(r"<.*?>|\*\*.*?\*\*|\*.*?\*", "", regex=True)
            .str.replace(r"\s+", " ", regex=True)  # collapse leftover spaces
            .str.strip()
        )

        #Remove binary characters (for the punchographs in Gnomeregan)
        df["cleanedText"] = df["cleanedText"].str.replace(r'(?:\b[01]{8}\b\s*)+', '', regex = True)

        df['player_gender'] = None
        rows = []
        for _, row in df.iterrows():
            if re.search(r'\$[Gg]', row['cleanedText']):
                male_text, female_text = self.handle_gender_options(row['cleanedText'])

                row_male = row.copy()
                row_male['cleanedText'] = male_text
                row_male['player_gender'] = 'm'

                row_female = row.copy()
                row_female['cleanedText'] = female_text
                row_female['player_gender'] = 'f'

                rows.extend([row_male, row_female])
            else:
                rows.append(row)

        new_df = pd.DataFrame(rows)
        new_df.reset_index(drop=True, inplace=True)

        return new_df


    def process_row(
            self,
            row_tuple,
            temperature=0.75,
            length_penalty=1.0,
            repetition_penalty=10.0,
            top_k=1,
            top_p=1.0,
            speed=1.05,
            f0_up_key=0,
            f0_method="rmvpe",
            index_rate=0.70,
            filter_radius=3,
            resample_sr=0,
            rms_mix_rate=1,
            protect=0.25
    ):
        row = pd.Series(row_tuple[1:], index=row_tuple._fields[1:])
        #if row['voice_name'].endswith("_dk"):
        #    voice_name = f'{row["voice_name"][:-3]}'
        #else:
        voice_name = f'{row["voice_name"]}'

        custom_message = ""
        if "$" in row["cleanedText"] or "<" in row["cleanedText"] or ">" in row["cleanedText"]:
            custom_message = f'skipping due to invalid chars: {row["cleanedText"]}'
        elif voice_name not in self.selected_voice_names:
            custom_message = f'skipping due to voice being unselected or unavailable: {voice_name}'
        elif row['source'] == "progress": # skip progress text (progress text is usually better left unread since its always played before quest completion)
            custom_message = f'skipping progress text: {row["quest"]}-{row["source"]}'
        else:
            self.tts_row(row, voice_name, temperature = temperature, length_penalty = length_penalty,
            repetition_penalty = repetition_penalty, top_k = top_k, top_p = top_p, speed = speed,
            f0_up_key = f0_up_key, f0_method = f0_method, index_rate = index_rate, filter_radius = filter_radius,
            resample_sr = resample_sr, rms_mix_rate = rms_mix_rate, protect = protect)
        return custom_message

    def tts_row(
                self, row, voice_name, **kwargs
                ):
        tts_text = row['cleanedText']
        file_name =  f'{row["quest"]}-{row["source"]}' if row['quest'] else f'{row["templateText_race_gender_hash"]}'
        if row['player_gender'] is not None:
            file_name = row['player_gender'] + '-'+ file_name
        file_name = file_name + '.mp3'
        subfolder = 'quests' if row['quest'] else 'gossip'
        questgiver_id = row['id'] if row['id'] else None
        self.tts(tts_text, voice_name, file_name, subfolder, questgiver_id = questgiver_id,
            **kwargs)

    def create_output_dirs(self):
        self.create_output_subdirs('')
        self.create_output_subdirs('quests')
        self.create_output_subdirs('gossip')

    def process_rows_in_parallel(self, df, row_proccesing_fn, selected_voice_names: list[str], max_workers=1, **kwargs):

        total_rows = len(df)
        bar_format = '{l_bar}{bar}| {n_fmt}/{total_fmt} [{elapsed}<{remaining}, {rate_fmt}] {postfix}'
        self.selected_voice_names = set(selected_voice_names)

        with tqdm(total=total_rows, unit='rows', ncols=100, desc='Generating Audio', ascii=False, bar_format=bar_format, dynamic_ncols=True) as pbar:
            with ThreadPoolExecutor(max_workers=max_workers) as executor:
                for row, custom_message in zip(df.iterrows(), executor.map(row_proccesing_fn, df.itertuples())):
                    pbar.set_postfix_str(custom_message)
                    pbar.update(1)


    def write_gossip_file_lookups_table(self, df, module_name, type, table, filename):
        output_file = self.output_folder + f"/{filename}.lua"
        gossip_table = {}

        accept_df = df[(df['quest'] == '') & (df['type'] == type)]

        for i, row in tqdm(accept_df.iterrows()):
            if row['id'] not in gossip_table:
                gossip_table[row['id']] = {}

            escapedText = row['text'].replace('"', '\'').replace('\r',' ').replace('\n',' ')

            gossip_table[row['id']][escapedText] = row['templateText_race_gender_hash']

        with open(output_file, "w", encoding="UTF-8") as f:
            f.write(DATAMODULE_TABLE_GUARD_CLAUSE + "\n")
            f.write(f"{module_name}.{table} = ")
            f.write(lua.encode(gossip_table))
            f.write("\n")

        print(f"Finished writing {filename}.lua")


    def write_questlog_npc_lookups_table(self, df, module_name, type, table, filename):
        output_file = self.output_folder + f"/{filename}.lua"
        questlog_table = {}

        accept_df = df[(df['source'] == 'accept') & (df['type'] == type)]

        for i, row in tqdm(accept_df.iterrows()):
            questlog_table[int(row['quest'])] = row['id']

        with open(output_file, "w", encoding="UTF-8") as f:
            f.write(DATAMODULE_TABLE_GUARD_CLAUSE + "\n")
            f.write(f"{module_name}.{table} = ")
            f.write(lua.encode(questlog_table))
            f.write("\n")

        print(f"Finished writing {filename}.lua")

    def write_npc_name_lookup_table(self, df, module_name, type, table, filename):
        output_file = self.output_folder + f"/{filename}.lua"
        npc_name_table = {}

        accept_df = df[df['type'] == type]

        for i, row in tqdm(accept_df.iterrows()):
            npc_name_table[row['id']] =  row['name']

        with open(output_file, "w", encoding="UTF-8") as f:
            f.write(DATAMODULE_TABLE_GUARD_CLAUSE + "\n")
            f.write(f"{module_name}.{table} = ")
            f.write(lua.encode(npc_name_table))
            f.write("\n")

        print(f"Finished writing {filename}.lua")

    def write_quest_id_lookup(self, df, module_name):
        output_file = self.output_folder + "/quest_id_lookups.lua"
        quest_id_table = {}

        quest_df = df[df['quest'] != '']

        for i, row in tqdm(quest_df.iterrows()):
            quest_source = row['source']
            if quest_source == 'progress': # skipping progress text for now
                continue

            quest_id = int(row['quest'])
            quest_title = row['quest_title']
            quest_text = get_first_n_words(row['text'], 25) + ' ' +  get_last_n_words(row['text'], 25)
            escaped_quest_text = replace_dollar_bs_with_space(quest_text.replace('"', '\'').replace('\r',' ').replace('\n',' '))
            escaped_quest_title = quest_title.replace('"', '\'').replace('\r',' ').replace('\n',' ')
            npc_name = row['name']
            escaped_npc_name = npc_name.replace('"', '\'').replace('\r',' ').replace('\n',' ')

            # table[source][title][npcName][text]
            if quest_source not in quest_id_table:
                quest_id_table[quest_source] = {}

            if escaped_quest_title not in quest_id_table[quest_source]:
                quest_id_table[quest_source][escaped_quest_title] = {}

            if escaped_npc_name not in quest_id_table[quest_source][escaped_quest_title]:
                quest_id_table[quest_source][escaped_quest_title][escaped_npc_name] = {}

            if quest_text not in quest_id_table[quest_source][escaped_quest_title][escaped_npc_name]:
                quest_id_table[quest_source][escaped_quest_title][escaped_npc_name][escaped_quest_text] = quest_id

        pruned_quest_id_table = prune_quest_id_table(quest_id_table)

        # UTF-8 Encoding is important for other languages!
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(DATAMODULE_TABLE_GUARD_CLAUSE + "\n")
            f.write(f"{module_name}.QuestIDLookup = ")
            f.write(lua.encode(pruned_quest_id_table))
            f.write("\n")

    def write_npc_name_gossip_file_lookups_table(self, df, module_name, type, table, filename):
        output_file = self.output_folder + f"/{filename}.lua"
        gossip_table = {}

        accept_df = df[(df['quest'] == '') & (df['type'] == type)]

        for i, row in tqdm(accept_df.iterrows()):
            npc_name = row['name']
            escaped_npc_name = npc_name.replace('"', '\'').replace('\r',' ').replace('\n',' ')

            if escaped_npc_name not in gossip_table:
                gossip_table[escaped_npc_name] = {}

            escapedText = row['text'].replace('"', '\'').replace('\r',' ').replace('\n',' ')

            gossip_table[escaped_npc_name][escapedText] = row['templateText_race_gender_hash']

        with open(output_file, "w", encoding="UTF-8") as f:
            f.write(DATAMODULE_TABLE_GUARD_CLAUSE + "\n")
            f.write(f"{module_name}.{table} = ")
            f.write(lua.encode(gossip_table))
            f.write("\n")

        print(f"Finished writing {filename}.lua")



    def tts_dataframe(self, df, selected_voices, expansions=[0, 1, 2], module_name=None,
              temperature = 0.75, length_penalty = 1.0, repetition_penalty = 10.0,
              top_k = 1, top_p = 1.0, speed = 1.05, f0_up_key = 0, f0_method = "rmvpe",
              index_rate = 0.70, filter_radius = 3, resample_sr = 0, rms_mix_rate = 1,
              protect = 0.25):
       #Add specific codes for quests that need to be in the module search table so the audio for certain quests with the same name is found properly.
        exp_for_audio = expansions

        if 0 in expansions:
            expansions.append(-77)
        if 1 in expansions:
            expansions.append(-88)
        if 2 in expansions:
            expansions.append(-99)

        df = df[df['expansion'].isin(exp_for_audio)]
        df.sort_values("voice_name")

        if module_name:
            self.module_name = module_name
            self.output_folder = os.path.join(self.module_name, 'generated')
            self.sound_output_folder = os.path.join(self.output_folder, 'sounds')

        self.create_output_dirs()
        self.process_rows_in_parallel(df, self.process_row, selected_voices, max_workers=1,
        temperature = temperature, length_penalty = length_penalty,
        repetition_penalty = repetition_penalty, top_k = top_k, top_p = top_p, speed = speed,
        f0_up_key = f0_up_key, f0_method = f0_method, index_rate = index_rate, filter_radius = filter_radius,
        resample_sr = resample_sr, rms_mix_rate = rms_mix_rate, protect = protect)
        print("Audio finished generating.")

    def generate_lookup_tables(self, df, expansions=[0, 1, 2], module_name=None):
        if module_name:
            self.module_name = module_name
            self.output_folder = os.path.join(self.module_name, 'generated')
            self.sound_output_folder = os.path.join(self.output_folder, 'sounds')

        self.create_output_dirs()

        if 0 in expansions:
            expansions.append(-77)
        if 1 in expansions:
            expansions.append(-88)
        if 2 in expansions:
            expansions.append(-99)

        df = df[df['expansion'].isin(expansions)]
        self.create_output_dirs()
        self.write_gossip_file_lookups_table(df, module_name, 'creature',   'GossipLookupByNPCID',    'npc_gossip_file_lookups')
        self.write_gossip_file_lookups_table(df, module_name, 'gameobject', 'GossipLookupByObjectID', 'object_gossip_file_lookups')

        self.write_quest_id_lookup(df, module_name)
        print("Finished writing quest_id_lookups.lua")

        self.write_npc_name_gossip_file_lookups_table(df, module_name, 'creature',   'GossipLookupByNPCName',    'npc_name_gossip_file_lookups')
        self.write_npc_name_gossip_file_lookups_table(df, module_name, 'gameobject', 'GossipLookupByObjectName', 'object_name_gossip_file_lookups')

        self.write_questlog_npc_lookups_table(df, module_name, 'creature',   'NPCIDLookupByQuestID',    'questlog_npc_lookups')
        self.write_questlog_npc_lookups_table(df, module_name, 'gameobject', 'ObjectIDLookupByQuestID', 'questlog_object_lookups')
        self.write_questlog_npc_lookups_table(df, module_name, 'item',       'ItemIDLookupByQuestID',   'questlog_item_lookups')

        self.write_npc_name_lookup_table(df, module_name, 'creature',   'NPCNameLookupByNPCID',       'npc_name_lookups')
        self.write_npc_name_lookup_table(df, module_name, 'gameobject', 'ObjectNameLookupByObjectID', 'object_name_lookups')
        self.write_npc_name_lookup_table(df, module_name, 'item',       'ItemNameLookupByItemID',     'item_name_lookups')

        write_sound_length_table_lua(module_name, self.sound_output_folder, self.output_folder)
        print("Updated sound_length_table.lua")

        return "Lookup tables complete."

    def tts_quest(self, df, quest_id : str, module_name="AI_VoiceOverData_TBC", spec : list = ['accept', 'complete'],
              temperature = 0.75, length_penalty = 1.0, repetition_penalty = 10.0,
              top_k = 1, top_p = 1.0, speed = 1.05, f0_up_key = 0, f0_method = "rmvpe",
              index_rate = 0.70, filter_radius = 3, resample_sr = 0, rms_mix_rate = 1,
              protect = 0.25):

        quest_id = str(quest_id)

        if isinstance(spec, str):
            spec = [spec]
        """
        Regenerate audio for a specific quest id (overwrites existing audio).
        """
        if module_name:
            self.module_name = module_name
            self.output_folder = os.path.join(self.module_name, 'generated')
            self.sound_output_folder = os.path.join(self.output_folder, 'sounds')

        self.create_output_dirs()

        quest_id = str(quest_id)

        df_filtered = df[(df['quest'] == quest_id) & (df['expansion'] >= 0) & df['source'].isin(spec)]

        expansions = df_filtered['expansion'].drop_duplicates().tolist()
        if 0 in expansions:
            expansions.append(-77)
        if 1 in expansions:
            expansions.append(-88)
        if 2 in expansions:
            expansions.append(-99)

        if df_filtered.empty:
            print(f"No rows found for quest {quest_id}", flush = True)
            return
        print(f"Regenerating {len(df_filtered)} rows for quest {quest_id}...", flush = True)

        for _, row in df_filtered.iterrows():
            file_name = f'{row["quest"]}-{row["source"]}' if row['quest'] else f'{row["templateText_race_gender_hash"]}'
            if row['player_gender'] is not None:
                file_name = row['player_gender'] + '-' + file_name
            file_name = file_name + '.mp3'

            subfolder = 'quests' if row['quest'] else 'gossip'
            tts_text = row['cleanedText']
            voice_name = row['voice_name']


            questgiver_id = row['id']
            self.tts(tts_text, voice_name, file_name, subfolder, forceGen=True,
                     questgiver_id=questgiver_id, temperature = temperature, length_penalty = length_penalty,
                     repetition_penalty = repetition_penalty, top_k = top_k, top_p = top_p, speed = speed,
                     f0_up_key = f0_up_key, f0_method = f0_method, index_rate = index_rate, filter_radius = filter_radius,
                     resample_sr = resample_sr, rms_mix_rate = rms_mix_rate, protect = protect)
        audio = self.output_path
        return "Generation complete.", expansions, audio  # Return both info message and expansions

    def tts_gossip(self, df, module_name="AI_VoiceOverData_TBC", npc_name=None,
              temperature = 0.75, length_penalty = 1.0, repetition_penalty = 10.0,
              top_k = 1, top_p = 1.0, speed = 1.05, f0_up_key = 0, f0_method = "rmvpe",
              index_rate = 0.70, filter_radius = 3, resample_sr = 0, rms_mix_rate = 1,
              protect = 0.25):

        """
        Regenerate audio for a specific gossip, either specific npc or race_gender (overwrites existing audio).
        """
        if module_name:
            self.module_name = module_name
            self.output_folder = os.path.join(self.module_name, 'generated')
            self.sound_output_folder = os.path.join(self.output_folder, 'sounds')

        self.create_output_dirs()

        if npc_name:
            spec = str(npc_name)
        else:
            return "No specification given to produce audio on."

        df_filtered = df[(df['name'] == spec) & (df['expansion'] >= 0) & (df['source'] == 'gossip')]

        expansions = df['expansion'].drop_duplicates().tolist()
        if 0 in expansions:
            expansions.append(-77)
        if 1 in expansions:
            expansions.append(-88)
        if 2 in expansions:
            expansions.append(-99)

        if df_filtered.empty:
            print(f"No rows found for NPC {npc_name}", flush = True)
            return
        print(f"Regenerating {len(df_filtered)} rows for NPC {npc_name}...", flush = True)

        for _, row in df_filtered.iterrows():
            file_name = f'{row["quest"]}-{row["source"]}' if row['quest'] else f'{row["templateText_race_gender_hash"]}'
            if row['player_gender'] is not None:
                file_name = row['player_gender'] + '-' + file_name
            file_name = file_name + '.mp3'

            subfolder = 'quests' if row['quest'] else 'gossip'
            tts_text = row['cleanedText']
            voice_name = row['voice_name']


            questgiver_id = row['id']
            self.tts(tts_text, voice_name, file_name, subfolder, forceGen=True,
                     questgiver_id=questgiver_id, temperature = temperature, length_penalty = length_penalty,
                     repetition_penalty = repetition_penalty, top_k = top_k, top_p = top_p, speed = speed,
                     f0_up_key = f0_up_key, f0_method = f0_method, index_rate = index_rate, filter_radius = filter_radius,
                     resample_sr = resample_sr, rms_mix_rate = rms_mix_rate, protect = protect)
        audio = self.output_path
        return "Generation complete.", expansions, audio  # Return both info message and expansions

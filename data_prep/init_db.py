from data_prep.env_vars import MYSQL_HOST, MYSQL_PORT, MYSQL_PASSWORD, MYSQL_USER, MYSQL_DATABASE
import pymysql
import io
import zipfile
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import os
from tqdm import tqdm
import shutil
import gzip
import subprocess
import pandas as pd

def init_db():
    ACORE_DB_DUMP_URL = "https://github.com/azerothcore/azerothcore-wotlk/archive/refs/heads/master.zip"

    #  Temporary directories
    TEMP_DIR = "temp_wotlk_db"
    EXTRACTED_DIR = os.path.join(TEMP_DIR, "extracted")

    #  MySQL Config (Update if needed)
    MYSQL_CONTAINER = MYSQL_HOST  # MySQL Docker container name
    DB_NAME = MYSQL_DATABASE          # Database name
    DB_USER = MYSQL_USER                  # MySQL user
    DB_PASSWORD = MYSQL_PASSWORD              # MySQL root password

    TEMP_DIR = "temp_wotlk_db"
    EXTRACTED_DIR = os.path.join(TEMP_DIR, "extracted")
    os.makedirs(EXTRACTED_DIR, exist_ok=True)

    url = ACORE_DB_DUMP_URL
    # --- Step 1: Download ---
    print(f"📥 Downloading {url} ...", flush = True)
    session = requests.Session()
    retries = Retry(total=5, backoff_factor=1, status_forcelist=[502, 503, 504])
    session.mount("https://", HTTPAdapter(max_retries=retries))

    resp = session.get(url, stream=True, timeout=30)
    resp.raise_for_status()
    zip_path = os.path.join(TEMP_DIR, "dump.zip")
    with open(zip_path, "wb") as f:
        for chunk in resp.iter_content(8192):
            f.write(chunk)

    # --- Step 2: Extract ---
    print("📂 Extracting...", flush = True)
    with zipfile.ZipFile(zip_path, "r") as zf:
        zf.extractall(EXTRACTED_DIR)
    print("✅ Extracted", flush = True)

    # --- Step 3: Detect structure ---
    root_candidates = [d for d in os.listdir(EXTRACTED_DIR) if os.path.isdir(os.path.join(EXTRACTED_DIR, d))]
    if not root_candidates:
        raise RuntimeError("❌ No extracted folder found")

    root_dir = os.path.join(EXTRACTED_DIR, root_candidates[0])

    # Check if it's AzerothCore (many .sql files) or vMaNGOS (one .gz)
    ac_path = os.path.join(root_dir, "data", "sql", "base", "db_world")
    mangos_path = os.path.join(root_dir, "Full_DB")

    sql_files = []

    if os.path.isdir(ac_path):
        # --- AzerothCore ---
        print(" Detected AzerothCore structure")
        for root, _, files in os.walk(ac_path):
            for f in sorted(files):
                if f.endswith(".sql"):
                    sql_files.append(os.path.join(root, f))
    elif os.path.isdir(mangos_path):
        # --- vMaNGOS ---
        print(" Detected MaNGOS structure")
        for f in os.listdir(mangos_path):
            if f.lower().endswith(".sql.gz"):
                sql_files.append(os.path.join(mangos_path, f))
    else:
        raise RuntimeError("❌ Unknown DB layout — no db_world or Full_DB found")

    if not sql_files:
        raise RuntimeError("❌ No SQL files located")

    print(f"✅ Found {len(sql_files)} SQL file(s)")
    # Combine drop + create into one command
    cmd = (
        f'mysql -h {MYSQL_HOST} -u {MYSQL_USER} -p{MYSQL_PASSWORD} '
        f'-e "DROP DATABASE IF EXISTS {MYSQL_DATABASE}; CREATE DATABASE {MYSQL_DATABASE};"'
    )

    try:
        subprocess.run(cmd, shell=True, check=True)
        print(f"✅ Dropped and recreated database '{MYSQL_DATABASE}'")
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to reset database: {e}")

    # --- Step 4: Import ---
    for sql_file in sql_files:
        print(f"📥 Importing {sql_file}")

        # Extract gzip if needed
        if sql_file.endswith(".gz"):
            unzipped = sql_file[:-3]
            with gzip.open(sql_file, "rb") as gz_in, open(unzipped, "wb") as out_f:
                shutil.copyfileobj(gz_in, out_f)
            sql_file = unzipped

        import_cmd = (f'mysql -h {MYSQL_CONTAINER} -u {DB_USER} -p{DB_PASSWORD} {DB_NAME} < "{sql_file}"')

        try:
            subprocess.run(import_cmd, shell=True, check=True)
            print(f"✅ Imported {os.path.basename(sql_file)}")
        except subprocess.CalledProcessError as e:
            print(f"❌ Import failed for {sql_file}: {e}")

    # --- Step 5: Cleanup ---
    if os.path.exists(TEMP_DIR):
        shutil.rmtree(TEMP_DIR, ignore_errors=True)
    print("🧹 Cleanup complete.", flush = True)


    #step 7: Add creaturedisplayinfo and creaturedisplayinfoextra to the database

    # Load CSV
    df = pd.read_csv("wotlk-db/DBFilesClient/CreatureDisplayInfo.csv", header=None, skiprows=1)
    df.fillna(0, inplace=True)
    df2 = pd.read_csv("wotlk-db/DBFilesClient/CreatureDisplayInfoExtra.csv", header=None, skiprows=1)
    df2.fillna(0, inplace=True)


    # Load CSV
    df3 = pd.read_csv("wotlk-db/DBFilesClient/CreatureDisplayInfo2.csv", header=None, skiprows=1)
    df3.fillna(0, inplace=True)
    df4 = pd.read_csv("wotlk-db/DBFilesClient/CreatureDisplayInfoExtra2.csv", header=None, skiprows=1)
    df4.fillna(0, inplace=True)

    # Connect to MySQL
    conn = pymysql.connect(
        host=MYSQL_HOST,
        user=MYSQL_USER,
        password=MYSQL_PASSWORD,
        database=MYSQL_DATABASE,
        client_flag=pymysql.constants.CLIENT.MULTI_STATEMENTS

    )


    cursor = conn.cursor()


    cursor.execute("""
        CREATE TABLE IF NOT EXISTS CreatureDisplayInfo (
      `ID` int NOT NULL DEFAULT '0',
      `ModelID` int NOT NULL DEFAULT '0',
      `SoundID` int NOT NULL DEFAULT '0',
      `ExtendedDisplayInfoID` int NOT NULL DEFAULT '0',
      `CreatureModelScale` float NOT NULL DEFAULT '0',
      `CreatureModelAlpha` int NOT NULL DEFAULT '0',
      `TextureVariation_1` text,
      `TextureVariation_2` text,
      `TextureVariation_3` text,
      `PortraitTextureName` text,
      `BloodLevel` int NOT NULL DEFAULT '0',
      `BloodID` int NOT NULL DEFAULT '0',
      `NPCSoundID` int NOT NULL DEFAULT '0',
      `ParticleColorID` int NOT NULL DEFAULT '0',
      `CreatureGeosetData` int NOT NULL DEFAULT '0',
      `ObjectEffectPackageID` int NOT NULL DEFAULT '0',
      PRIMARY KEY (`ID`)
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS CreatureDisplayInfoExtra (
      `ID` int NOT NULL DEFAULT '0',
      `DisplayRaceID` int NOT NULL DEFAULT '0',
      `DisplaySexID` int NOT NULL DEFAULT '0',
      `SkinID` int NOT NULL DEFAULT '0',
      `FaceID` int NOT NULL DEFAULT '0',
      `HairStyleID` int NOT NULL DEFAULT '0',
      `HairColorID` int NOT NULL DEFAULT '0',
      `FacialHairID` int NOT NULL DEFAULT '0',
      `NPCItemDisplay_1` int NOT NULL DEFAULT '0',
      `NPCItemDisplay_2` int NOT NULL DEFAULT '0',
      `NPCItemDisplay_3` int NOT NULL DEFAULT '0',
      `NPCItemDisplay_4` int NOT NULL DEFAULT '0',
      `NPCItemDisplay_5` int NOT NULL DEFAULT '0',
      `NPCItemDisplay_6` int NOT NULL DEFAULT '0',
      `NPCItemDisplay_7` int NOT NULL DEFAULT '0',
      `NPCItemDisplay_8` int NOT NULL DEFAULT '0',
      `NPCItemDisplay_9` int NOT NULL DEFAULT '0',
      `NPCItemDisplay_10` int NOT NULL DEFAULT '0',
      `NPCItemDisplay_11` int NOT NULL DEFAULT '0',
      `Flags` int NOT NULL DEFAULT '0',
      `BakeName` text,
      PRIMARY KEY (`ID`)
        )
    """)

    # Insert each row

    cursor.executemany("""
        INSERT IGNORE CreatureDisplayInfo VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """, [tuple(row[:16]) for row in df.itertuples(index=False)])
    conn.commit()

    cursor.executemany("""
        INSERT IGNORE CreatureDisplayInfoExtra VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """, [tuple(row[:21]) for row in df2.itertuples(index=False)])
    conn.commit()



    cursor2 = conn.cursor()

    cursor2.execute("""
        CREATE TABLE IF NOT EXISTS CreatureDisplayInfo2 (
      `ID` int NOT NULL DEFAULT '0',
      `ModelID` int NOT NULL DEFAULT '0',
      `SoundID` int NOT NULL DEFAULT '0',
      `ExtendedDisplayInfoID` int NOT NULL DEFAULT '0',
      `CreatureModelScale` float NOT NULL DEFAULT '0',
      `CreatureModelAlpha` int NOT NULL DEFAULT '0',
      `TextureVariation_1` text,
      `TextureVariation_2` text,
      `TextureVariation_3` text,
      `PortraitTextureName` text,
      `BloodLevel` int NOT NULL DEFAULT '0',
      `BloodID` int NOT NULL DEFAULT '0',
      `NPCSoundID` int NOT NULL DEFAULT '0',
      `ParticleColorID` int NOT NULL DEFAULT '0',
      `CreatureGeosetData` int NOT NULL DEFAULT '0',
      `ObjectEffectPackageID` int NOT NULL DEFAULT '0',
      PRIMARY KEY (`ID`)
        )
    """)

    cursor2.execute("""
        CREATE TABLE IF NOT EXISTS CreatureDisplayInfoExtra2 (
      `ID` int NOT NULL DEFAULT '0',
      `DisplayRaceID` int NOT NULL DEFAULT '0',
      `DisplaySexID` int NOT NULL DEFAULT '0',
      `SkinID` int NOT NULL DEFAULT '0',
      `FaceID` int NOT NULL DEFAULT '0',
      `HairStyleID` int NOT NULL DEFAULT '0',
      `HairColorID` int NOT NULL DEFAULT '0',
      `FacialHairID` int NOT NULL DEFAULT '0',
      `NPCItemDisplay_1` int NOT NULL DEFAULT '0',
      `NPCItemDisplay_2` int NOT NULL DEFAULT '0',
      `NPCItemDisplay_3` int NOT NULL DEFAULT '0',
      `NPCItemDisplay_4` int NOT NULL DEFAULT '0',
      `NPCItemDisplay_5` int NOT NULL DEFAULT '0',
      `NPCItemDisplay_6` int NOT NULL DEFAULT '0',
      `NPCItemDisplay_7` int NOT NULL DEFAULT '0',
      `NPCItemDisplay_8` int NOT NULL DEFAULT '0',
      `NPCItemDisplay_9` int NOT NULL DEFAULT '0',
      `NPCItemDisplay_10` int NOT NULL DEFAULT '0',
      `NPCItemDisplay_11` int NOT NULL DEFAULT '0',
      `Flags` int NOT NULL DEFAULT '0',
      `BakeName` text,
      PRIMARY KEY (`ID`)
        )
    """)

    # Insert each row
    cursor2.executemany("""
        INSERT IGNORE CreatureDisplayInfo2 VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """, [tuple(row[:16]) for row in df3.itertuples(index=False)])
    conn.commit()

    cursor2.executemany("""
        INSERT IGNORE CreatureDisplayInfoExtra2 VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """, [tuple(row[:21]) for row in df4.itertuples(index=False)])
    conn.commit()

     #Step 8: add some modifications to the data that need to be here I think to match doing it when the import is done


    # Use a single cursor
    cursor3 = conn.cursor()

    # Each statement separately
    print("Adding CompletionText to quest template...", flush = True)

    # Add CompletionText column if missing
    cursor3.execute("ALTER TABLE quest_template ADD COLUMN CompletionText TEXT")

    # Copy values into CompletionText
    cursor3.execute("""
        UPDATE quest_template qt
        JOIN quest_request_items qri ON qt.ID = qri.ID
        SET qt.CompletionText = qri.CompletionText
    """)
    conn.commit()

    print("Adding RewardText to quest template...", flush = True)

    # Add RewardText column if missing
    cursor3.execute("ALTER TABLE quest_template ADD COLUMN RewardText TEXT")

    # Copy values into RewardText
    cursor3.execute("""
        UPDATE quest_template qt
        JOIN quest_offer_reward qor ON qt.ID = qor.ID
        SET qt.RewardText = qor.RewardText
    """)
    conn.commit()

    print("✅ Added and updated CompletionText and RewardText successfully.", flush = True)



    conn.close()

    return "WoTLK database initialized successfully."

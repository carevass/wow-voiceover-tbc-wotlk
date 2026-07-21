import pymysql
import pandas as pd
from data_prep.env_vars import MYSQL_HOST, MYSQL_PORT, MYSQL_PASSWORD, MYSQL_USER, MYSQL_DATABASE


def make_connection():
    return pymysql.connect(
        host=MYSQL_HOST,
        port=3306,
        user=MYSQL_USER,
        password=MYSQL_PASSWORD,
        database=MYSQL_DATABASE
    )




def query_dataframe_for_all_quests_and_gossip(lang: int = 0, langStr = None):
    db = make_connection()
    sql_query = '''
WITH RECURSIVE
creature_quest_relations AS (
    SELECT 'accept' as source, qr.quest, ct.entry as creature_id
    FROM creature_template ct
    JOIN creature_queststarter qr ON qr.id = ct.entry
        UNION ALL
    SELECT 'accept' as source, qr.quest, ct.entry as creature_id
    FROM creature_template ct
    JOIN game_event_creature_quest qr ON qr.id = ct.entry
        UNION ALL
    SELECT 'complete' as source, qr.quest, ct.entry as creature_id
    FROM creature_template ct
    JOIN creature_questender qr ON qr.id = ct.entry
        UNION ALL
    SELECT 'progress' as source, qr.quest, ct.entry as creature_id
    FROM creature_template ct
    JOIN creature_questender qr ON qr.id = ct.entry
),
gameobject_quest_relations AS (
    SELECT 'accept' as source, qr.quest, gt.entry as gameobject_id
    FROM gameobject_template gt
    JOIN gameobject_queststarter qr ON qr.id = gt.entry
        UNION ALL
    SELECT 'complete' as source, qr.quest, gt.entry as gameobject_id
    FROM gameobject_template gt
    JOIN gameobject_questender qr ON qr.id = gt.entry
        UNION ALL
    SELECT 'progress' as source, qr.quest, gt.entry as gameobject_id
    FROM gameobject_template gt
    JOIN gameobject_questender qr ON qr.id = gt.entry
),
item_quest_relations AS (
    SELECT 'accept' as source, it.startquest as quest, it.entry as item_id
    FROM item_template it
    WHERE it.startquest
),
collected_gossip_menus (base_menu_id, menu_id, text_id, action_menu_id) AS (
    WITH gossip_menu_and_options AS (
        SELECT gm.MenuID, gm.TextID, NULL as action_menu_id
            FROM gossip_menu gm
        UNION DISTINCT
        SELECT gm.MenuID, gm.TextID, gmo.ActionMenuID
            FROM gossip_menu gm
            LEFT JOIN gossip_menu_option gmo on gmo.MenuID = gm.MenuID
    )
    SELECT gm.MenuID as base_menu_id, gm.MenuID, gm.TextID, gm.action_menu_id
        FROM gossip_menu_and_options gm
    UNION DISTINCT
    SELECT cgm.base_menu_id, gm.MenuID, gm.TextID, gm.action_menu_id
        FROM gossip_menu_and_options gm
        INNER JOIN collected_gossip_menus cgm ON cgm.action_menu_id = gm.MenuID
),
creature_data AS (
    SELECT
        ct.entry as id,
        ct.name,
        cgm.text_id,
        cdie.DisplaySexID,
        cdie.DisplayRaceID
    FROM creature_template ct
   	    JOIN creature_template_model ctm ON ct.entry = ctm.CreatureID
        JOIN CreatureDisplayInfo2 cdi ON ctm.CreatureDisplayID = cdi.ID
        LEFT JOIN CreatureDisplayInfoExtra2 cdie ON cdi.ExtendedDisplayInfoID = cdie.ID
        LEFT JOIN collected_gossip_menus cgm ON cgm.base_menu_id = ct.gossip_menu_id
),
gameobject_data AS (
    SELECT
        gt.entry as id,
        gt.name,
        cgm.text_id
    FROM gameobject_template gt
        LEFT JOIN collected_gossip_menus cgm ON cgm.base_menu_id =
            CASE gt.type
                WHEN 2  THEN data3  -- GAMEOBJECT_TYPE_QUESTGIVER (type 2) has property "gossipID" in data3 field
                WHEN 8  THEN data10 -- GAMEOBJECT_TYPE_SPELL_FOCUS (type 8) has property "gossipID" in data10 field
                WHEN 10 THEN data19 -- GAMEOBJECT_TYPE_GOOBER (type 10) has property "gossipID" in data19 field
            END
    WHERE gt.type IN (2, 10)
),
numbers AS (
    SELECT 0 AS n
    UNION ALL SELECT 1
    UNION ALL SELECT 2
    UNION ALL SELECT 3
    UNION ALL SELECT 4
    UNION ALL SELECT 5
    UNION ALL SELECT 6
    UNION ALL SELECT 7
),
ALL_DATA AS (

-- Creature QuestGivers

SELECT
    distinct
    qr.source,
    qr.quest,
    qt.LogTitle as quest_title,
    CASE
        WHEN qr.source = 'accept' THEN qt.QuestDescription
        WHEN qr.source = 'progress' THEN qt.CompletionText
        ELSE qt.RewardText
    END as "text",
    0 as broadcast_text_id,
    cdie.DisplayRaceID,
    cdie.DisplaySexID,
    ct.name,
    'creature' as type,
    qr.creature_id as id
FROM
    creature_quest_relations qr
JOIN quest_template qt ON qr.quest = qt.ID
JOIN creature_template ct ON qr.creature_id = ct.entry
JOIN creature_template_model ctm ON ct.entry = ctm.CreatureID
JOIN CreatureDisplayInfo2 cdi ON ctm.CreatureDisplayID = cdi.ID
LEFT JOIN CreatureDisplayInfoExtra2 cdie ON cdi.ExtendedDisplayInfoID = cdie.ID

WHERE
    (
        (qr.source = 'accept' AND qt.QuestDescription IS NOT NULL AND qt.QuestDescription != '')
        OR (qr.source = 'progress' AND qt.CompletionText IS NOT NULL AND qt.CompletionText != '')
        OR (qr.source = 'complete' AND qt.RewardText IS NOT NULL AND qt.RewardText != '')
    )

-- GameObject QuestGivers

UNION ALL
SELECT
    distinct
    qr.source,
    qr.quest,
    qt.LogTitle as quest_title,
    CASE
        WHEN qr.source = 'accept' THEN qt.QuestDescription
        WHEN qr.source = 'progress' THEN qt.CompletionText
        ELSE qt.RewardText
    END as "text",
    0 as broadcast_text_id,
    -1 as DisplayRaceID,
    0 as DisplaySexID,
    gt.name,
    'gameobject' as type,
    qr.gameobject_id as id
FROM
    gameobject_quest_relations qr
JOIN quest_template qt ON qr.quest = qt.ID
JOIN gameobject_template gt ON qr.gameobject_id = gt.entry

WHERE
   (
        (qr.source = 'accept' AND qt.QuestDescription IS NOT NULL AND qt.QuestDescription != '')
       OR (qr.source = 'progress' AND qt.CompletionText IS NOT NULL AND qt.CompletionText != '')
       OR (qr.source = 'complete' AND qt.RewardText IS NOT NULL AND qt.RewardText != '')
  )

-- Item QuestGivers

UNION ALL
SELECT
    distinct
    qr.source,
    qr.quest,
    qt.LogTitle as quest_title,
    qt.QuestDescription as "text",
    0 as broadcast_text_id,
    -1 as DisplayRaceID,
    0 as DisplaySexID,
    it.name,
    'item' as type,
    qr.item_id as id
FROM
    item_quest_relations qr
JOIN quest_template qt ON qr.quest = qt.ID
JOIN item_template it ON qr.item_id = it.entry

WHERE
    (
        (qr.source = 'accept' AND qt.QuestDescription IS NOT NULL AND qt.QuestDescription != '')
    )

-- Creature Gossip

UNION ALL
SELECT
    distinct
    'gossip' as source,
    '' as quest,
    '' as quest_title,
    CASE
     WHEN creature_data.DisplaySexID = 0 THEN bt.MaleText
     WHEN creature_data.DisplaySexID = 1 THEN bt.FemaleText
     ELSE COALESCE(NULLIF(bt.MaleText, ''), NULLIF(bt.FemaleText, ''), '')
	END AS TEXT,
    bt.ID as broadcast_text_id,
    creature_data.DisplayRaceID,
    creature_data.DisplaySexID,
    creature_data.name,
    'creature' as type,
    creature_data.id
FROM creature_data
    CROSS JOIN numbers
    JOIN npc_text nt ON nt.ID = creature_data.text_id
    JOIN broadcast_text bt ON
        CASE numbers.n
            WHEN 0 THEN nt.BroadcastTextID0
            WHEN 1 THEN nt.BroadcastTextID1
            WHEN 2 THEN nt.BroadcastTextID2
            WHEN 3 THEN nt.BroadcastTextID3
            WHEN 4 THEN nt.BroadcastTextID4
            WHEN 5 THEN nt.BroadcastTextID5
            WHEN 6 THEN nt.BroadcastTextID6
            WHEN 7 THEN nt.BroadcastTextID7
        END = bt.ID

WHERE
    (DisplaySexID = 0 AND bt.MaleText IS NOT NULL AND bt.MaleText != '')
    OR (DisplaySexID = 1 AND bt.FemaleText IS NOT NULL AND bt.FemaleText != '')
    OR (DisplaySexID IS NULL AND bt.FemaleText IS NOT NULL AND bt.FemaleText != '')
    OR (DisplaySexID IS NULL AND bt.MaleText IS NOT NULL AND bt.MaleText != '')


-- GameObject Gossip

UNION ALL
SELECT
    distinct
    'gossip' as source,
    '' as quest,
    '' as quest_title,
    IF(bt.MaleText IS NOT NULL AND bt.MaleText != '', bt.MaleText, bt.FemaleText) AS text,
    bt.ID as broadcast_text_id,
    -1 as DisplayRaceID,
    0 as DisplaySexID,
    gameobject_data.name,
    'gameobject' as type,
    gameobject_data.id
FROM gameobject_data
    CROSS JOIN numbers
    JOIN npc_text nt ON nt.ID = gameobject_data.text_id
    JOIN broadcast_text bt ON
        CASE numbers.n
            WHEN 0 THEN nt.BroadcastTextID0
            WHEN 1 THEN nt.BroadcastTextID1
            WHEN 2 THEN nt.BroadcastTextID2
            WHEN 3 THEN nt.BroadcastTextID3
            WHEN 4 THEN nt.BroadcastTextID4
            WHEN 5 THEN nt.BroadcastTextID5
            WHEN 6 THEN nt.BroadcastTextID6
            WHEN 7 THEN nt.BroadcastTextID7
        END = bt.ID

WHERE
    bt.MaleText IS NOT NULL AND bt.MaleText != '' OR
    bt.FemaleText IS NOT NULL AND bt.FemaleText != ''

-- Creature QuestGreetings

UNION ALL
SELECT
    distinct
    'gossip' as source,
    '' as quest,
    '' as quest_title,
    qg.Greeting AS text,
    0 as broadcast_text_id,
    creature_data.DisplayRaceID,
    creature_data.DisplaySexID,
    creature_data.name,
    'creature' as type,
    creature_data.id
FROM creature_data
    JOIN quest_greeting qg ON qg.ID=creature_data.id AND type=0

-- GameObject QuestGreetings

UNION ALL
SELECT
    distinct
    'gossip' as source,
    '' as quest,
    '' as quest_title,
    qg.Greeting AS text,
    0 as broadcast_text_id,
    -1 AS DisplayRaceID,
    0 AS DisplaySexID,
    gameobject_data.name,
    'gameobject' as type,
    gameobject_data.id
FROM gameobject_data
    JOIN quest_greeting qg ON qg.ID=gameobject_data.id AND type=1

)
    '''

    if lang == 0:
        sql_query += '''
SELECT
    source,
    quest,
    quest_title,
    text,
    DisplayRaceID,
    DisplaySexID,
    name,
    type,
    id,
    text as original_text
FROM ALL_DATA
        '''
    else:
        sql_query += f'''
SELECT
    source,
    quest,
    IFNULL(NULLIF(lq.title, ''), quest_title) as quest_title,
    IFNULL(NULLIF(CASE source
        WHEN 'gossip' THEN (CASE
            WHEN broadcast_text_id = 0 THEN qg.Greeting
            WHEN ALL_DATA.type = 'creature' THEN IF(DisplaySexID = 0, lbt.MaleText, lbt.FemaleText)
            ELSE IFNULL(NULLIF(lbt.MaleText, ''), lbt.FemaleText)
        END)
        WHEN 'accept'   THEN lq.Details
        WHEN 'progress' THEN qril.CompletionText
        WHEN 'complete' THEN qorl.RewardText
        
        
        ELSE NULL
    END, ''), text) as text,
    DisplayRaceID,
    DisplaySexID,
    IFNULL(NULLIF(CASE ALL_DATA.type
        WHEN 'creature'   THEN lc.Name
        WHEN 'gameobject' THEN lg.Name
        WHEN 'item'       THEN li.Name
        
        ELSE NULL
    END, ''), ALL_DATA.name) as name,
    ALL_DATA.type,
    ALL_DATA.id,
    ALL_DATA.text as original_text
FROM ALL_DATA
    LEFT JOIN wotlk_mangos.quest_template_locale    lq  ON lq.ID = ALL_DATA.quest AND lq.locale = %(langStr)s
    LEFT JOIN wotlk_mangos.quest_request_items_locale    qril  ON qril.ID = ALL_DATA.quest AND qril.locale = %(langStr)s
    LEFT JOIN wotlk_mangos.quest_offer_reward_locale    qorl  ON qorl.ID = ALL_DATA.quest AND qorl.locale = %(langStr)s
    
    LEFT JOIN wotlk_mangos.broadcast_text_locale lbt ON lbt.ID = broadcast_text_id AND lbt.locale = %(langStr)s 
    
    LEFT JOIN wotlk_mangos.creature_template_locale lc  ON lc.entry = ALL_DATA.id AND type = 'creature' AND lc.locale = %(langStr)s 
    
    LEFT JOIN wotlk_mangos.gameobject_template_locale     lg  ON lg .entry = ALL_DATA.id AND type = 'gameobject' AND lg.locale = %(langStr)s
    
    LEFT JOIN wotlk_mangos.item_template_locale           li  ON li .ID = ALL_DATA.id AND type = 'item' AND li.locale = %(langStr)s
    
    LEFT JOIN wotlk_mangos.quest_greeting_locale         qg  ON qg.ID = ALL_DATA.id AND qg.type = (CASE ALL_DATA.type WHEN 'creature' THEN 0 WHEN 'gameobject' THEN 1 ELSE -1 END) AND qg.locale = %(langStr)s
    
        '''

    with db.cursor() as cursor:
        cursor.execute(sql_query, {'langStr': langStr})
        data = cursor.fetchall()
        columns = [desc[0] for desc in cursor.description]

    db.close()
    df = pd.DataFrame(data, columns=columns)

    return df

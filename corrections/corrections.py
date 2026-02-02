import pandas as pd

def recode_expansions(df, corrections_path):

    # Load the corrections Excel file
    quest_corrections = pd.read_excel(corrections_path, sheet_name = 'quest', dtype={"quest": str})
    quest_corrections = quest_corrections[['quest','expansion']][~quest_corrections['expansion'].isnull()]


    id_corrections = pd.read_excel(corrections_path, sheet_name = 'npc', dtype={"id": int, "source":str})
    id_corrections = id_corrections[['id','expansion']][~id_corrections['expansion'].isnull()]

    #make a copy of the dataframe we pass initially
    merged = df.copy()

    # --- Apply corrections by id ---
    #if there are corrections by id (the df is not empty)
    if not id_corrections.empty:
        #merge original df with id corrections df, left join suffixing columns from the id corrections with _corr
        merged = merged.merge(
            id_corrections,
            on='id',
            how='left',
            suffixes=('', '_corr')
        )

        #iterate over columns in the corrections dataframe
        for col in id_corrections.columns:
            #skip over the id column when iterating for the subsequent operations
            if col != 'id':
                #replace value of the original column with the one from the corrections df
                merged[col] = merged[f"{col}_corr"].combine_first(merged[col])
                #drop the corrections column from the final dataset when finished
                merged.drop(columns=[f"{col}_corr"], inplace=True)
    # --- Apply recode by quest(not specific) ---
    if not quest_corrections.empty:
        merged = merged.merge(
            quest_corrections,
            on='quest',
            how='left',
            suffixes=('', '_corr')
        )
        for col in quest_corrections.columns:
            if col != 'quest':
                merged[col] = merged[f"{col}_corr"].combine_first(merged[col])
                merged.drop(columns=[f"{col}_corr"], inplace=True)
    return merged

def apply_corrections(df, corrections_path):
    # Load the corrections Excel file
    quest_corrections = pd.read_excel(corrections_path, sheet_name = 'quest', dtype={"quest": str}).drop(["expansion"], axis=1)
    #split quest correction on those that have source defined and those that do not
    #we will do two merges for general quest corrections (like expansion recoding) and one for quest specific stuff (like editing the text)

    #subset id corrections with sourc empty i.e., corrections are made for all parts of the quest
    q_corrections_all = quest_corrections[quest_corrections['source'].isna()]

    #subset id corrections with source populated, i.e., corrections are made for either complete or accept (or both)
    q_corrections_spec = quest_corrections[quest_corrections['source'].notna()]

    #corrections by npc; dropping the expansion label because we are separating that from the other corrections
    id_corrections = pd.read_excel(corrections_path, sheet_name = 'npc', dtype={"id": int, "source":str}).drop(["expansion"], axis=1)

    #make a copy of the dataframe we pass initially
    merged = df.copy()

    # --- Apply corrections by id ---
    #if there are corrections by id (the df is not empty)
    if not id_corrections.empty:
        #merge original df with id corrections df, left join suffixing columns from the id corrections with _corr
        merged = merged.merge(
            id_corrections,
            on='id',
            how='left',
            suffixes=('', '_corr')
        )

        #iterate over columns in the corrections dataframe
        for col in id_corrections.columns:
            #skip over the id column when iterating for the subsequent operations
            if col != 'id':
                #replace value of the original column with the one from the corrections df
                merged[col] = merged[f"{col}_corr"].combine_first(merged[col])
                #drop the corrections column from the final dataset when finished
                merged.drop(columns=[f"{col}_corr"], inplace=True)

    # --- Apply corrections by quest(not specific) ---
    if not q_corrections_all.empty:
        merged = merged.merge(
            q_corrections_all,
            on='quest',
            how='left',
            suffixes=('', '_corr')
        )
        for col in q_corrections_all.columns:
            if col != 'quest':
                merged[col] = merged[f"{col}_corr"].combine_first(merged[col])
                merged.drop(columns=[f"{col}_corr"], inplace=True)
    # --- Apply corrections by quest (specific) ---

    if not q_corrections_spec.empty:
        merged = merged.merge(
            q_corrections_spec,
            on=['source','quest'],
            how='left',
            suffixes=('', '_corr')
        )
        for col in q_corrections_spec.columns:
            if col not in ['source','quest']:
                merged[col] = merged[f"{col}_corr"].combine_first(merged[col])
                merged.drop(columns=[f"{col}_corr"], inplace=True)

    return merged


def add_new_entries(df, xlsx_path):
    # Load the new rows from Excel
    new_rows = pd.read_excel(xlsx_path, keep_default_na = False, dtype={"quest": str})
    #new_rows['quest'] = new_rows['quest'].astype(str)


    # Check for fully duplicated rows
    duplicates = new_rows[new_rows.isin(df.to_dict(orient='list')).all(axis=1)]

    if not duplicates.empty:
        raise ValueError(f"{len(duplicates)} duplicate row(s) found in the Excel file that already exist in the DataFrame: \n {duplicates['quest']}-{duplicates['source']} ")
    # Concatenate and return the updated DataFrame

    updated_df = pd.concat([df, new_rows], ignore_index=True)

    return updated_df

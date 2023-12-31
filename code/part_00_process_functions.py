# mike babb
# 2021 02 20
# functions used to find anagrams

# standard libraries
import collections
import datetime
import os
import pickle
import sqlite3

# external
import numpy as np
import pandas as pd

# custom
from part_00_file_db_utils import build_db_conn

def get_values(wg_id:int, 
               wchar_matrix:np.ndarray,
              word_group_id_list:np.ndarray):
    """ FIND ANAGRAMS FOR A SPECIFIC USING word_group_id AND MATRIX COMPARISONS    
    This is the simplest technique
    """ 

    outcome = wchar_matrix - wchar_matrix[wg_id, ]
    
    # compute the score by finding where rows, across all columns, are GTE 0
    outcome_indices = np.all(outcome >= 0, axis = 1)
    outcome = None        
    
    # extract anagrams based on index values
    outcome_word_id_list = word_group_id_list[outcome_indices]    
    
    output_list = np.zeros(shape = (outcome_word_id_list.shape[0], 2),  dtype=int)
    
    # update the output list with the word_id_list - these are from/parent words    
    output_list[:, 0] = outcome_word_id_list
    
    # update with the word_id - this is the to/child word
    output_list[:, 1] = wg_id
        
    return output_list


def get_values_better(wg_id:int,
                      letter_selector:str,
                      letter_selector_matrix_dict:dict):

    # this is the submatrix by letter selector
    ls_wg_id_list, ls_wchar_matrix, ls_wg_id_set = letter_selector_matrix_dict[letter_selector]

    new_word_id = ls_wg_id_list==wg_id    
    
    # now, perform the comparison    
    outcome = ls_wchar_matrix - ls_wchar_matrix[new_word_id, ]

    # compute the score by finding where rows, across all columns, are GTE 0
    outcome_indices = np.all(outcome >= 0, axis = 1)
    outcome = None        
    
    # extract anagrams based on index values
    outcome_word_id_list = ls_wg_id_list[outcome_indices]    
    
    output_list = np.zeros(shape = (outcome_word_id_list.shape[0], 2),  dtype=int)
    
    # update the output list with the word_id_list - these are from/parent words    
    output_list[:, 0] = outcome_word_id_list
    
    # update with the word_id - this is the to/child word
    output_list[:, 1] = wg_id

    return output_list


def get_values_even_better(wg_id:int,
                           nc_ls_tuple:tuple,                           
                           nc_ls_matrix_dict:dict):

    # this is the submatrix by letter selector
    nc_ls_wg_id_list, nc_ls_wchar_matrix, nc_ls_wg_id_set = nc_ls_matrix_dict[nc_ls_tuple]

    
    new_word_id = nc_ls_wg_id_list==wg_id    
    
    # now, perform the comparison    
    outcome = nc_ls_wchar_matrix - nc_ls_wchar_matrix[new_word_id, ]

    # compute the score by finding where rows, across all columns, are GTE 0
    outcome_indices = np.all(outcome >= 0, axis = 1)
    outcome = None        
    
    # extract anagrams based on index values
    outcome_word_id_list = nc_ls_wg_id_list[outcome_indices]    
    
    output_list = np.zeros(shape = (outcome_word_id_list.shape[0], 2),  dtype=int)
    
    # update the output list with the word_id_list - these are from/parent words    
    output_list[:, 0] = outcome_word_id_list
    
    # update with the word_id - this is the to/child word
    output_list[:, 1] = wg_id

    return output_list
    

def estimate_total_pairs(word_df:pd.DataFrame, wg_df:pd.DataFrame, nc_ls_matrix_dict:dict):

    # list of the number of characters per word
    n_char_list = sorted(word_df['n_chars'].unique().tolist())
    
    # enumerate and sample
    output_list = []
    for n_char in n_char_list:
        # this will get all words that are n_char in length.        
        curr_id_list = wg_df.loc[wg_df['n_chars']==n_char, 'word_group_id'].to_numpy()        
        # sample with replacement, 10 words per length of word
        sample_id_list = np.random.choice(a = curr_id_list, size = 10, replace = True)
        sample_df = wg_df.loc[wg_df['word_group_id'].isin(sample_id_list), ['word_group_id', 'nc_ls_tuple']]        
        
        for s_wg_id, nc_ls_tuple in zip(sample_df['word_group_id'], sample_df['nc_ls_tuple']):
            

            # get the values
            output = get_values_even_better(wg_id = s_wg_id,
                           nc_ls_tuple = nc_ls_tuple,                           
                           nc_ls_matrix_dict=nc_ls_matrix_dict)
            
            curr_from_words = output.shape[0]
            curr_output = [n_char, curr_from_words]
            output_list.append(curr_output)    
    
    # make a dataframe from the possibilities
    pos_df = pd.DataFrame(data = output_list, columns = ['n_chars', 'n_from_words'])
    
    # minimum, max, and mean number of from words
    agg_pos_df = pos_df.groupby('n_chars').agg(["min", "max", "mean"])    
       
    agg_pos_df.columns = ['min_n_from_words', 'max_n_from_words', 'mean_n_from_words']
    
    # let's aggregate by number of letters per word, and then join
    n_word_length_df = word_df['n_chars'].groupby(word_df['n_chars']).agg(np.size).to_frame()
    n_word_length_df.columns = ['n_words']
    
    n_pos_df = pd.merge(left = n_word_length_df, right = agg_pos_df, left_index = True,
                       right_index = True)
    
    n_pos_df['n_tot_max_anagrams'] = n_pos_df['n_words'] * n_pos_df['max_n_from_words']
    n_pos_df['n_tot_mean_anagrams'] = n_pos_df['n_words'] * n_pos_df['mean_n_from_words']
    
    # set the upper bound of anagrams as the midway point
    # between the mean and the max of the estimated number of anagrams
    n_possible_anagrams = (n_pos_df['n_tot_mean_anagrams'].sum() + n_pos_df['n_tot_max_anagrams'].sum()) / 2
    
    # round and convert to integer
    n_possible_anagrams = int(np.round(n_possible_anagrams, 0))
    
    # this number will be used to create an array that will hold the from/to pairs
    n_possible_anagrams_formatted = '{:,}'.format(n_possible_anagrams)    
    print('...estimated number of from/to pair word pairs:', n_possible_anagrams_formatted )               
    
    return n_possible_anagrams


def store_anagram_pairs(
    output_list: np.array, db_path: str, db_name: str, cut_size: int = 1000000):
    # create database connection objects
    db_conn = build_db_conn(db_path=db_path, db_name=db_name)
    db_cursor = db_conn.cursor()

    # let's write to the SQLite database in chunks of 1M records
    cut_size = 1000000
    n_total_anagrams = len(output_list)
    break_point_list = list(range(0, n_total_anagrams, cut_size))
    # add the last bit of records
    if break_point_list[-1] < n_total_anagrams:
        break_point_list.append(n_total_anagrams)

    # drop the anagrams table if it previously exists
    sql = "drop table if exists anagram_groups;"

    print("...dropping previous table...")
    # send the sql statement to the database and commit the changes
    db_cursor.execute(sql)
    db_conn.commit()

    # create the anagrams table
    sql = "create table anagram_groups ( from_word_group_id integer, to_word_group_id integer);"

    # execute the statement and commit changes
    db_cursor.execute(sql)
    db_conn.commit()

    # objects to record write time
    db_write_time_list = []
    db_write_time_start = datetime.datetime.now()

    # create a sql statement that we'll use to insert values.
    print("...beginning to add anagram word group pairs...")
    base_sql = "insert into anagram_groups values (?,?)"

    curr_db_write_time_start = datetime.datetime.now()
    for i_bp, bp in enumerate(break_point_list[:-1]):
        # slice the output list of word id pairs, convert to a python list
        # the numpy.int data type is not compatable with sqlite.
        # the cursor.executemany() is a quick way to write a lot of data.
        next_bp = break_point_list[i_bp + 1]

        # converting the entire output_list to a python list adds too much overheard.
        curr_output_list = output_list[bp:next_bp,].tolist()

        # use the executemany() function to write records
        # https://docs.python.org/3/library/sqlite3.html#sqlite3.Cursor.executemany
        db_cursor.executemany(base_sql, curr_output_list)

        # commit changes every 10M records
        if next_bp % 10000000 == 0:
            print("...commiting changes:", "{:,}".format(next_bp), "records")
            db_conn.commit()
            # calculate the current time to write 10M records
            curr_db_write_time_end = datetime.datetime.now()
            curr_db_write_time_proc = curr_db_write_time_end - curr_db_write_time_start
            curr_db_write_time_proc = curr_db_write_time_proc.total_seconds()

            # save this value
            db_write_time_list.append(curr_db_write_time_proc)

            # compute average write time, display after 1M writes
            mean_write_time = np.mean(db_write_time_list)

            # compute ETA
            n_seconds = (n_total_anagrams / 10000000) * mean_write_time
            add_seconds = datetime.timedelta(seconds=n_seconds)
            eta_write_complete = db_write_time_start + add_seconds
            eta_write_complete = eta_write_complete.strftime(
                format="%m/%d/%Y, %H:%M:%S"
            )

            mean_write_time = round(mean_write_time, 3)
            print(
                "...average write time per 10M records:", mean_write_time, "seconds..."
            )
            print("...estimated write complete time:", eta_write_complete)

            # restart the current write time
            curr_db_write_time_start = datetime.datetime.now()

    # commit the last round of changes
    print("...commiting changes:", "{:,}".format(len(curr_output_list)), "records")
    db_conn.commit()

    # compute total write times
    db_write_time_end = datetime.datetime.now()
    db_write_time_proc = db_write_time_end - db_write_time_start
    db_write_time_proc = db_write_time_proc.total_seconds() / 60
    db_write_time_proc = round(db_write_time_proc, 2)
    print("...writing to db took", db_write_time_proc, "minutes")

    del curr_output_list

    # close connection objects
    db_cursor.close()
    db_conn.close()

    return None


def store_anagaram_processing_time(
    output_list: np.array,
    proc_time_df_list: pd.DataFrame,
    word_df: pd.DataFrame,
    wg_df: pd.DataFrame,
    matrix_extraction_option: int,
    db_path: str,
    db_name: str,
    total_time_start: datetime.datetime,
):
    # create database connection objects
    db_conn = build_db_conn(db_path=db_path, db_name=db_name)

    # the count of to words
    to_word_counter = collections.Counter(output_list[:, 0])

    # create a dataframe with the processing times
    proc_time_df = pd.concat(proc_time_df_list)

    # drop columns related to data processing
    drop_col_names = [
        "letter_selector",
        "word_id_n_char_matrix_key",
        "word_id_n_char_matrix_key_hash",
    ]
    curr_col_names = word_df.columns.tolist()
    for dcn in drop_col_names:
        if dcn in curr_col_names:
            word_df = word_df.drop(dcn, axis=1)

    # merge the word_df and the proc_time_df dataframes to get the processing time per word
    word_df = pd.merge(left=word_df, right=proc_time_df)

    # now, use the map function to get the number of from/to words and the number of
    # candidate words for each word
    word_df["n_to_word_groups"] = word_df["word_group_id"].map(to_word_counter)

    # rearrange columns
    col_names = [
        "word",
        "lcase",
        "n_chars",
        "first_letter",
        "word_id",
        "word_group_id",
        "letter_group",
        "letter_group_ranked",
        "n_seconds",
        "n_from_word_groups",
        "n_to_word_groups",
        "n_candidates",
    ]
    word_df = word_df[col_names]

    # let's include a field to indicate which word was actually used from the candidate groups
    word_df["word_processed"] = int(0)

    word_df.loc[word_df["word_id"].isin(wg_df["word_id"]), "word_processed"] = int(1)

    # add a matrix extraction option
    word_df["matrix_extraction_option"] = int(matrix_extraction_option)

    # output table name
    table_name = f"words_me_{str(matrix_extraction_option).zfill(2)}"

    # write the processing option table
    word_df.to_sql(name=table_name, con=db_conn, if_exists="replace", index=False)

    # close the connection
    db_conn.close()

    anagram_discovery_time = word_df.loc[
        word_df["word_processed"] == 1, "n_seconds"
    ].sum()
    anagram_discovery_time = anagram_discovery_time / 60
    anagram_discovery_time = round(anagram_discovery_time, 2)

    print("...anagram discovery time:", anagram_discovery_time, "minutes")

    # record the total time
    total_time_end = datetime.datetime.now()
    total_time_proc = total_time_end - total_time_start
    total_time_proc = total_time_proc.total_seconds()
    total_time_proc = total_time_proc / 60
    total_time_proc = round(total_time_proc, 2)

    print("...total processing time:", total_time_proc, "minutes")

    return None


def query_db(sql, db_path, db_name, params=None):
    """QUERY A SQLITE DATABASE, RETURN A PANDAS DATAFRAME"""
    # https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.read_sql.html
    db_conn = build_db_conn(db_path=db_path, db_name=db_name)

    s_time = datetime.datetime.now()

    df = pd.read_sql(sql=sql, con=db_conn, params=params)
    db_conn.close()

    e_time = datetime.datetime.now()
    p_time = e_time - s_time
    p_time = p_time.total_seconds()
    print("...query execution took:", round(p_time, 7), "seconds...")

    return df

if __name__ == "__main__":
    # simple test, query the first 10 words
    print('The dean? hellos')
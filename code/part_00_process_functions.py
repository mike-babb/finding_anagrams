# mike babb
# 2021 02 20
# functions used to find anagrams

# standard libraries
import collections
import datetime
import os
import string

# external
import numpy as np
import pandas as pd

# custom
from part_00_file_db_utils import *


def load_input_data(db_path: str, db_name: str, in_file_path: str) -> pd.DataFrame:

    # load the word_df, the words from Part 1
    print("...loading words into a dataframe...")
    sql = "select * from words;"
    word_df = query_db(sql=sql, db_path=db_path, db_name=db_name)

    # load the word group df
    print("...loading word groups into a dataframe...")
    sql = "select * from word_groups;"
    wg_df = query_db(sql=sql, db_path=db_path, db_name=db_name)

    # load the letter dictionary from part 1
    print("...loading the letter dictionary...")
    in_file_name = "letter_dict.pkl"
    letter_dict = load_pickle(in_file_path=in_file_path, in_file_name=in_file_name)

    # load the char matrix from part 1
    print("...loading the char matrix...")
    in_file_name = "char_matrix.npy"
    ipn = os.path.join(in_file_path, in_file_name)
    char_matrix = np.load(file=ipn)

    # get the word group ids
    print("...subsetting the char matrix...")
    word_group_id_list = wg_df["word_group_id"].to_numpy()
    # and the associated word_id
    word_id_list = wg_df["word_id"].to_numpy()

    # trim the char matrix by word id and not the word_group id
    wchar_matrix = char_matrix[word_id_list, :]

    return (
        word_df,
        wg_df,
        letter_dict,
        char_matrix,
        word_group_id_list,
        word_id_list,
        wchar_matrix,
    )


####
# SPLIT MATRIX PLACEHOLDER
####

def format_output_list(outcome_word_id_list: np.ndarray, wg_id: int) -> np.ndarray:
    output_list = np.zeros(shape=(outcome_word_id_list.shape[0], 2), dtype=int)

    # update the output list with the word_id_list - these are from/parent words
    output_list[:, 0] = outcome_word_id_list

    # update with the word_id - this is the to/child word
    output_list[:, 1] = wg_id

    return output_list


def format_demo_output(demo_word: str, word_df: pd.DataFrame, demo_output: np.ndarray):
    # how many parent/from words were found for the word 'quiet'?
    print(
        "There are",
        demo_output.shape[0],
        "parent/from word groups for the word",
        demo_word,
    )

    # and those words are...
    word_list = word_df.loc[word_df["word_group_id"].isin(demo_output[:, 0]), "lcase"]
    print("There are", word_list.shape[0], "parent/from words for the word", demo_word)

    print("The first five words are:")
    print(word_list.head())
    print("The last five words are:")
    print(word_list.tail())

    return None


def get_values_full_matrix(
    wg_id: int, wchar_matrix: np.ndarray, word_group_id_list: np.ndarray
):
    """FIND ANAGRAMS FOR A SPECIFIC USING word_group_id AND MATRIX COMPARISONS
    This is the simplest technique
    """

    outcome = wchar_matrix - wchar_matrix[wg_id,]

    # compute the score by finding where rows, across all columns, are GTE 0
    outcome_indices = np.all(outcome >= 0, axis=1)
    outcome = None

    # extract anagrams based on index values
    outcome_word_id_list = word_group_id_list[outcome_indices]

    output_list = format_output_list(
        outcome_word_id_list=outcome_word_id_list, wg_id=wg_id
    )

    return output_list


def get_values_n_char(wg_id: int, n_char: int, n_char_matrix_dict: dict):
    nc_wg_id_list, nc_sub_wchar_matrix, nc_wg_id_set = n_char_matrix_dict[n_char]
    new_word_id = nc_wg_id_list == wg_id

    # now, perform the comparison
    outcome = nc_sub_wchar_matrix - nc_sub_wchar_matrix[new_word_id,]

    # compute the score by finding where rows, across all columns, are GTE 0
    outcome_indices = np.all(outcome >= 0, axis=1)
    outcome = None

    # extract anagrams based on index values
    outcome_word_id_list = nc_wg_id_list[outcome_indices]

    output_list = format_output_list(
        outcome_word_id_list=outcome_word_id_list, wg_id=wg_id
    )

    return output_list


def get_values_single_letter(
    wg_id: int, single_letter_id: str, single_letter_matrix_dict: dict
):
    # this is the submatrix by single letter
    (
        single_letter_word_group_id_list,
        single_letter_wchar_matrix,
        single_letter_word_group_id_set,
    ) = single_letter_matrix_dict[single_letter_id]

    new_word_id = single_letter_word_group_id_list == wg_id

    # now, peform the comparison
    outcome = single_letter_wchar_matrix - single_letter_wchar_matrix[new_word_id,]

    # compute the score by finding where rows, across all columns, are GTE 0
    outcome_indices = np.all(outcome >= 0, axis=1)
    outcome = None

    # extract anagrams based on index values
    outcome_word_id_list = single_letter_word_group_id_list[outcome_indices]

    output_list = format_output_list(
        outcome_word_id_list=outcome_word_id_list, wg_id=wg_id
    )

    return output_list


def get_values_letter_selector(
    wg_id: int, letter_selector_id: str, letter_selector_matrix_dict: dict
):
    # this is the submatrix by letter selector
    ls_wg_id_list, ls_wchar_matrix, ls_wg_id_set = letter_selector_matrix_dict[
        letter_selector_id
    ]

    new_word_id = ls_wg_id_list == wg_id

    # now, perform the comparison
    outcome = ls_wchar_matrix - ls_wchar_matrix[new_word_id,]

    # compute the score by finding where rows, across all columns, are GTE 0
    outcome_indices = np.all(outcome >= 0, axis=1)
    outcome = None

    # extract anagrams based on index values
    outcome_word_id_list = ls_wg_id_list[outcome_indices]

    output_list = format_output_list(
        outcome_word_id_list=outcome_word_id_list, wg_id=wg_id
    )

    return output_list


def get_values_n_char_letter_selector(
    wg_id: int, nc_ls_id: tuple, nc_ls_matrix_dict: dict
):
    # this is the submatrix by letter selector
    nc_ls_wg_id_list, nc_ls_wchar_matrix, nc_ls_wg_id_set = nc_ls_matrix_dict[nc_ls_id]

    new_word_id = nc_ls_wg_id_list == wg_id

    # now, perform the comparison
    outcome = nc_ls_wchar_matrix - nc_ls_wchar_matrix[new_word_id,]

    # compute the score by finding where rows, across all columns, are GTE 0
    outcome_indices = np.all(outcome >= 0, axis=1)
    outcome = None

    # extract anagrams based on index values
    outcome_word_id_list = nc_ls_wg_id_list[outcome_indices]

    output_list = format_output_list(
        outcome_word_id_list=outcome_word_id_list, wg_id=wg_id
    )

    return output_list


def estimate_total_pairs(wg_df: pd.DataFrame, nc_ls_matrix_dict: dict) -> int:
    # Sample 10 words of each word length, compute the number of from/parent
    # anagrams for each word in the sample, compute the min, mean, and max,
    # and apply those values to the numbers of words by length and multiply
    # accordingly this will give us (very generous) upper bounds of anagram pairs

    # sample 10 words from each word based on word length.
    # words are anywhere from 1 character to 24 characters, 240 samples
    sample_df = wg_df.groupby(["n_chars"]).sample(n=10, replace=True, random_state=123)

    # enumerate using itertuples in order to capture the output
    output_list = []
    for row in sample_df.itertuples():
        # get the values using the get_values_n_char_letter_selector() function.
        output = get_values_n_char_letter_selector(
            wg_id=row.word_group_id,
            nc_ls_id=row.nc_ls_id,
            nc_ls_matrix_dict=nc_ls_matrix_dict,
        )

        curr_from_words = output.shape[0]
        curr_output = [row.n_chars, curr_from_words]
        output_list.append(curr_output)

    # make a dataframe from the sample possibilities
    pos_df = pd.DataFrame(data=output_list, columns=["n_chars", "n_from_words"])

    # minimum, maximum, and mean number of from words
    agg_pos_df = (
        pos_df.groupby("n_chars")
        .agg(
            min_n_from_words=("n_from_words", "min"),
            max_n_from_words=("n_from_words", "max"),
            mean_n_from_words=("n_from_words", "mean"),
        )
        .reset_index()
    )

    # count the number of words by letter size
    word_size_counter = collections.Counter(wg_df["n_chars"])

    # add this to the aggregated possibility dataframe
    agg_pos_df["n_words"] = agg_pos_df["n_chars"].map(word_size_counter)

    agg_pos_df["n_tot_max_anagrams"] = (
        agg_pos_df["n_words"] * agg_pos_df["max_n_from_words"]
    )
    agg_pos_df["n_tot_mean_anagrams"] = (
        agg_pos_df["n_words"] * agg_pos_df["mean_n_from_words"]
    )

    # set the upper bound of anagrams as the midway point
    # between the mean and the max of the estimated number of anagrams
    n_possible_anagrams = (
        agg_pos_df["n_tot_mean_anagrams"].sum() + agg_pos_df["n_tot_max_anagrams"].sum()
    ) / 2

    # round and convert to integer
    n_possible_anagrams = int(np.round(n_possible_anagrams, 0))

    # this number will be used to create an array that will hold the from/to pairs
    n_possible_anagrams_formatted = "{:,}".format(n_possible_anagrams)
    print(
        "...estimated number of from/to pair word pairs:", n_possible_anagrams_formatted
    )

    return n_possible_anagrams


####
# generate_from_to_word_group_pairs placeholder
####
def generate_from_to_word_group_pairs(
    wg_df: pd.DataFrame,
    n_possible_anagrams: int,
    matrix_extraction_option: int,
    wchar_matrix: np.ndarray,
    word_group_id_list: np.ndarray,
    n_char_matrix_dict: dict,
    single_letter_matrix_dict: dict,
    letter_selector_matrix_dict: dict,
    nc_ls_matrix_dict: dict,
    letter_subset_list: str = None,
):
    # use numpy to pre-allocate an array that will be updated while enumerating.
    # this eliminates list.append() calls which are fine in small amounts, but
    # hundreds of thousands of append calls add a lot of overhead.

    output_list = np.full(shape=(n_possible_anagrams, 2), fill_value=-1, dtype=int)

    # this dictionary will store the calculations for each word
    proc_time_dict = {}

    if letter_subset_list == "SAMPLE":
        # generate 100 samples within each n_chars and first_letter group combination
        curr_wg_df = (
            wg_df.groupby(["n_chars", "first_letter"])
            .sample(n=100, replace=True, random_state=123)
            .drop_duplicates()
        )
    elif isinstance(letter_subset_list, str) or isinstance(letter_subset_list, list):
        # subset by a specific set of letters or a single letter
        curr_wg_df = wg_df.loc[
            wg_df["first_letter"].isin(set(letter_subset_list)), :
        ].copy()
    else:
        curr_wg_df = wg_df.copy()

    # display counts
    curr_word_count = curr_wg_df.shape[0]

    n_curr_words = "{:,}".format(curr_word_count)
    print("...finding parent anagrams for", n_curr_words, "words...")

    # establish counters for record keeping
    row_count = 0
    anagram_pair_count = 0
    # enumerate by word id, working with integers is faster than words
    for row in curr_wg_df.itertuples(index=False):
        # start timing to record processing for each word
        s_time = datetime.datetime.now()

        # word group id
        wg_id = row.word_group_id

        # get the current word length, from the word id

        # get the tuple associated with the word id
        # much faster to look up stored values for the hash value than it is to
        # only look up if the hash value has changed

        # get the possible candidate word_group_ids and char matrix

        if matrix_extraction_option == 1:
            # option 1: full matrix
            outcome_word_id_list = get_values_full_matrix(
                wg_id=wg_id,
                wchar_matrix=wchar_matrix,
                word_group_id_list=word_group_id_list,
            )
        elif matrix_extraction_option == 2:
            # option 2: word length
            outcome_word_id_list = get_values_n_char(
                wg_id=wg_id,
                n_char=row.n_chars,
                n_char_matrix_dict=n_char_matrix_dict,
            )
        elif matrix_extraction_option == 3:
            # option 3: first character
            outcome_word_id_list = get_values_single_letter(
                wg_id=wg_id,
                single_letter_id=row.first_letter_id,
                single_letter_matrix_dict=single_letter_matrix_dict,
            )
        elif matrix_extraction_option == 4:
            # option 4: single least common letter
            outcome_word_id_list = get_values_single_letter(
                wg_id=wg_id,
                single_letter_id=row.single_letter_id,
                single_letter_matrix_dict=single_letter_matrix_dict,
            )
        elif matrix_extraction_option == 5:
            # option 5: letter selector / focal letter
            outcome_word_id_list = get_values_letter_selector(
                wg_id=wg_id,
                letter_selector_id=row.letter_selector_id,
                letter_selector_matrix_dict=letter_selector_matrix_dict,
            )
        else:
            # option 6: word length and letter selector
            outcome_word_id_list = get_values_n_char_letter_selector(
                wg_id=wg_id,
                nc_ls_id=row.nc_ls_id,
                nc_ls_matrix_dict=nc_ls_matrix_dict,
            )

        # if the outcome is greater than or equal to zero, then the current word is an
        # anagram of the other word
        # a value  >= 0 means that the current word contains the exact same number of focal letters
        # mite --> time or miter --> time
        # a value >= 1 means that current word contains at least the same number of focal letters
        # terminator --> time
        # a value of <= -1 means that the current word does not have the
        # correct number of letters and is therefore not an anagram.
        # trait <> time

        # number of parent words found
        n_from_words = outcome_word_id_list.shape[0]

        if n_from_words > 1:
            # we have matches
            # the focal word

            # enumerate the from/parent words
            new_anagram_pair_count = anagram_pair_count + n_from_words

            output_list[
                anagram_pair_count:new_anagram_pair_count, :
            ] = outcome_word_id_list

            # set the anagram pair count
            anagram_pair_count = new_anagram_pair_count

        # delete the intermediate list
        del outcome_word_id_list

        # record the time for the word
        e_time = datetime.datetime.now()
        p_time = e_time - s_time
        p_time = round(p_time.total_seconds(), 8)

        proc_time_dict[wg_id] = (p_time, n_from_words)

        row_count += 1
        if row_count % 1e4 == 0:
            print("...found parent anagrams for", "{:,}".format(row_count), "words...")

    # last update
    print("...found parent anagrams for", "{:,}".format(row_count), "words...")
    # create a dataframe from the proc_time_dict
    proc_time_df = pd.DataFrame.from_dict(data=proc_time_dict, orient="index")
    proc_time_df = proc_time_df.reset_index()
    proc_time_df.columns = ["word_group_id", "n_seconds", "n_from_word_groups"]

    # display processing time for the current letter
    total_proc_time_s = round(proc_time_df["n_seconds"].sum(), 4)
    total_proc_time_m = round(proc_time_df["n_seconds"].sum() / 60, 4)
    print(
        "...finding parent anagrams for",
        n_curr_words,
        "words took",
        total_proc_time_s,
        "seconds |",
        total_proc_time_m,
        "minutes...",
    )

    # truncate the output array to only include rows with a from/to word pair
    # this removes any row that has a value of -1
    print("...truncating output list...")
    output_indices = np.all(output_list >= 0, axis=1)
    output_list = output_list[output_indices,]
    del output_indices

    # how many anagram pairs were found?
    n_total_anagrams = output_list.shape[0]
    n_total_anagrams_formatted = "{:,}".format(n_total_anagrams)
    print("...total anagrams:", n_total_anagrams_formatted)

    return proc_time_df, output_list


def store_anagram_pairs(
    output_list: np.array, db_path: str, db_name: str, cut_size: int = 1000000
) -> None:
    # elapsed time
    elapsed_time = 0

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
            elapsed_time += n_seconds
            add_seconds = datetime.timedelta(seconds=elapsed_time)

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


def format_anagaram_processing(
    output_list: np.array,
    proc_time_df: pd.DataFrame,
    word_df: pd.DataFrame,
    wg_df: pd.DataFrame,
    matrix_extraction_option: int,
) -> None:
    # the count of to/child words, and in order to do that,
    # we need to count the number of times each word_group_id
    # exists in the from/parent column
    # count the number of to words
    # seems little counter-intuitive... but we're counting the number of
    # to-words from each from-word. So, this is the number of child words
    # from each parent word.
    # https://docs.python.org/3/library/collections.html#collections.Counter

    print("...populating the count of from-words...")
    n_from_word_counter = collections.Counter(output_list[:, 1])
    print(len(n_from_word_counter))

    print("...populating the count of to-words...")
    n_to_word_counter = collections.Counter(output_list[:, 0])
    print(len(n_to_word_counter))

    # get the processed word id
    processed_word_id = wg_df.loc[
        wg_df["word_group_id"].isin(n_to_word_counter.keys()), "word_id"
    ].to_numpy()

    # remove columns that will be duplicated, this is necessary for a
    # subsequent join to the word_df
    drop_col_names = [
        "word",
        "lcase",
        "n_chars",
        "first_letter",
        "word_id",
        "letter_group",
        "letter_group_ranked",
    ]

    wg_df = wg_df.drop(labels=drop_col_names, axis=1)

    # merge the word_df and wg_df, this has the processing times and the number of candidates.
    word_df = pd.merge(left=word_df, right=wg_df)

    # now, use the map function to get the number of from/to words and the number of
    # candidate words for each word
    proc_time_df["n_to_word_groups"] = proc_time_df["word_group_id"].map(
        n_to_word_counter
    )

    # indicate which words were used in the data processing
    # here we are counting the to words
    word_df["word_processed"] = int(0)
    word_df.loc[word_df["word_id"].isin(processed_word_id), "word_processed"] = 1

    # select and re-order columns
    col_names = [
        "word",
        "lcase",
        "n_chars",
        "first_letter",
        "word_id",
        "word_group_id",
        "letter_group",
        "letter_group_ranked",
        "letter_selector",
        "me_01_full_matrix_lookup",
        "me_02_n_char_lookup",
        "me_03_first_letter_lookup",
        "me_04_single_letter_lookup",
        "me_05_letter_selector_lookup",
        "me_06_nc_ls_lookup",
        "word_processed",
    ]

    word_df = word_df[col_names]

    # add a matrix extraction option
    proc_time_df["matrix_extraction_option"] = int(matrix_extraction_option)
    # proc_time_df['lookup_check_from'] = proc_time_df['word_group_id'].map(n_from_word_counter)
    # proc_time_df['lookup_check_to'] = proc_time_df['word_group_id'].map(n_to_word_counter)

    return proc_time_df, word_df


def store_anagram_processing(
    proc_time_df: str,
    word_df: str,
    matrix_extraction_option: str,
    db_path: str,
    db_name: str,
) -> None:
    # create database connection objects
    db_conn = build_db_conn(db_path=db_path, db_name=db_name)

    # write the processing option table
    table_name = f"words_me_{str(matrix_extraction_option).zfill(2)}"
    print("...now writing", table_name, "...")
    proc_time_df.to_sql(name=table_name, con=db_conn, if_exists="replace", index=False)

    # write the word df to disk
    table_name = f"words_processed_me_{str(matrix_extraction_option).zfill(2)}"
    print("...now writing", table_name, "...")
    word_df.to_sql(name=table_name, con=db_conn, if_exists="replace", index=False)

    # close the connection
    db_conn.close()

    return None


def display_total_processing_time(
    proc_time_df: pd.DataFrame, total_time_start: datetime.datetime
) -> None:
    anagram_discovery_time_seconds = proc_time_df["n_seconds"].sum()
    anagram_discovery_time_minutes = anagram_discovery_time_seconds / 60

    anagram_discovery_time_seconds = round(anagram_discovery_time_seconds, 4)
    anagram_discovery_time_minutes = round(anagram_discovery_time_minutes, 4)

    print(
        "...anagram discovery time:",
        anagram_discovery_time_seconds,
        "seconds |",
        anagram_discovery_time_minutes,
        "minutes",
    )

    # record the total time
    total_time_end = datetime.datetime.now()
    total_time_proc = total_time_end - total_time_start
    total_time_proc = total_time_proc.total_seconds()
    total_time_proc = total_time_proc / 60
    total_time_proc = round(total_time_proc, 2)

    print("...total processing time:", total_time_proc, "minutes")

    return None


if __name__ == "__main__":
    # simple test, query the first 10 words
    print("The dean? hellos")

# mike babb
# TODO: HOLD FOR DATE
# functions used to find anagrams

# standard libraries
import collections
import datetime
import os
from time import perf_counter_ns

# external
import numpy as np
import pandas as pd

# custom
import _run_constants as rc
from part_00_file_db_utils import *



def load_input_data(data_path: str = rc.data_output_file_path, db_path = rc.db_path, db_name: str = rc.db_name, in_file_path: str = rc.in_file_path) -> pd.DataFrame:

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
    letter_dict = load_pickle(
        in_file_path=data_path, in_file_name=in_file_name)

    # load the char matrix from part 1
    print("...loading the char matrix...")
    in_file_name = "char_matrix.npy"
    ipn = os.path.join(data_path, in_file_name)
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
# SPLIT MATRIX
####


def split_matrix(
    letter_dict: dict,
    word_group_id_list: np.ndarray,
    wg_df: pd.DataFrame,
    wchar_matrix: np.ndarray,
    n_subset_letters: int,
    matrix_extraction_option: int = 0
):

    # the different matrix extraction options
    # Option 0: Return all of the different types of matrix extraction options
    # Option 1: Full matrix - no objects are returned
    # Option 2: Word-length - returns matrices split by the number of characters
    # Option 3: First letter - returns matrices split by each letter
    # Option 4: Single-least common letter - return matrices split by each letter
    # Option 5: n least common letters - return matrices split by least common letters
    # Option 6: word-length and n least common letters - return matrices split by least common letters and word length.

    s_time = perf_counter_ns()

    # create the letter selector and determine the max number
    # of sub-matrices to makes
    wg_df["letter_selector"] = wg_df["letter_group_ranked"].str[:n_subset_letters]
    wg_df["first_letter_id"] = wg_df["first_letter"].map(letter_dict)
    wg_df["single_letter_id"] = wg_df["letter_selector"].str[0].map(
        letter_dict)

    # build the letter selector id list and dict
    letter_selector_list = wg_df["letter_selector"].unique()
    letter_selector_list.sort()
    letter_selector_id_dict = {ls: i_ls for i_ls,
                               ls in enumerate(letter_selector_list)}

    wg_df["letter_selector_id"] = wg_df["letter_selector"].map(
        letter_selector_id_dict)

    nc_ls_df = wg_df[
        ["n_chars", "letter_selector_id", "letter_selector"]
    ].drop_duplicates()
    nc_ls_df["nc_ls_id"] = range(0, nc_ls_df.shape[0])

    wg_df = pd.merge(left=wg_df, right=nc_ls_df)

    # only proceed if matrix_extraction_option != 1:
    if matrix_extraction_option != 1:

        # word length dictionary
        # used in matrix extraction option: 2
        n_char_matrix_dict = {}

        # single letter matrix dict
        # used in matrix extraction option: 3 and 4
        single_letter_matrix_dict = {}

        # letter selector dictionary
        # used in matrix extraction option: 5
        letter_selector_matrix_dict = {}

        # word length and lettor selector dictionary
        # used in matrix extraction option: 6
        nc_ls_matrix_dict = {}

        # create dictionaries to hold sets - these will only exist in the context of this function
        n_char_set_dict = {}
        single_letter_set_dict = {}
        letter_selector_set_dict = {}

        # enumerate these combinations only once
        # reduce the number of times we have to compute ids and sub-matrices

        # we have created some ids, but we don't need to enumerate for all of the
        # matrix extraction options.
        # but because of the way enumeration and creation of dictionaries is
        # setup, we're over-enumerating for options 2 through 5.
        # this is trade off between minimizing code, code reuse, and data enumeration
        n_records = nc_ls_df.shape[0]

        print("...enumerating", "{:,}".format(n_records), "records...")

        loop_count = 0
        for row in nc_ls_df.itertuples(index=False):
            nc = row.n_chars
            ls = row.letter_selector
            ls_id = row.letter_selector_id

            if matrix_extraction_option in (0, 6):
                nc_ls_id = row.nc_ls_id

            ####
            # MATRIX EXTRACTION OPTION 1: NO SUB-MATRICES ARE CREATED.
            ####
            # (Block left here for convenience)

            ####
            # MATRIX EXTRACTION OPTION 2: DICTIONARY BY NUMBER OF CHARACTERS
            ####
            if nc not in n_char_matrix_dict:
                nc_wg_id_list = wg_df.loc[
                    (wg_df["n_chars"] >= nc), "word_group_id"
                ].to_numpy()
                nc_wg_id_set = set(nc_wg_id_list)
                n_char_set_dict[nc] = nc_wg_id_set

                # subset the wchar_matrix to get the sub-matrix
                nc_sub_wchar_matrix = wchar_matrix[nc_wg_id_list,]

                n_char_matrix_dict[nc] = (nc_wg_id_list, nc_sub_wchar_matrix)

            else:                
                nc_wg_id_list, nc_sub_wchar_matrix = n_char_matrix_dict[nc]
                nc_wg_id_set = n_char_set_dict[nc]

            ####
            # MATRIX EXTRACTION OPTION 3 AND 4: DICTIONARY BY SINGLE-LETTER
            ####
            ll = ls[0]
            ll_id = letter_dict[ll]

            # check to see if the sub-matrix with the first letter has already been created
            if ll_id not in single_letter_matrix_dict:
                # the submatrix has not been created, let's do it.
                column_selector = [ll_id]
                outcome = wchar_matrix[:, column_selector] > 0
                outcome_indices = np.all(outcome > 0, axis=1)

                # these indices match with the word_id_list, extract the subset
                single_letter_word_group_id_list = word_group_id_list[outcome_indices]

                # the set of ids
                single_letter_word_group_id_set = set(
                    single_letter_word_group_id_list)
                single_letter_set_dict[ll_id] = single_letter_word_group_id_set

                # subset the wchar_matrix to get the sub-matrix
                single_letter_wchar_matrix = wchar_matrix[single_letter_word_group_id_list, ]

                single_letter_matrix_dict[ll_id] = (
                    single_letter_word_group_id_list,
                    single_letter_wchar_matrix
                )

            else:
                # query the sub-matrices split by individual letter to then get the smaller matrices
                (
                    single_letter_word_group_id_list,
                    single_letter_wchar_matrix,
                ) = single_letter_matrix_dict[ll_id]

                single_letter_word_group_id_set = single_letter_set_dict[ll_id]

            ####
            # MATRIX EXTRACTION OPTION 5: DICTIONARY BY LETTER SELECTOR
            ####
            if ls_id not in letter_selector_matrix_dict:
                # build a column selector
                column_selector = [letter_dict[curr_letter]
                                   for curr_letter in ls]

                # get the indices of the single_letter_wchar_matrix that feature the n least common letters
                outcome = single_letter_wchar_matrix[:, column_selector] > 0
                outcome_indices = np.all(outcome > 0, axis=1)

                # these are now the ids
                ls_wg_id_list = single_letter_word_group_id_list[outcome_indices]

                # the set of ids
                ls_wg_id_set = set(ls_wg_id_list)
                letter_selector_set_dict[ls_id] = ls_wg_id_set

                # subset the wchar_matrix to get the sub-matrix - this contains the N least common letters for a group of words
                ls_wchar_matrix = wchar_matrix[ls_wg_id_list,]
                letter_selector_matrix_dict[ls_id] = (
                    ls_wg_id_list,
                    ls_wchar_matrix
                )

            else:
                # this is the submatrix by letter selector
                ls_wg_id_list, ls_wchar_matrix = letter_selector_matrix_dict[
                    ls_id
                ]

                ls_wg_id_set = letter_selector_set_dict[ls_id]

            ####
            # MATRIX EXTRACTION OPTION 6: DICTIONARY BY NUMBER OF CHARACTERS AND LETTER SELECTOR
            ####

            ##
            # We need to find the intersection of the word_group_id by number of characters
            # and the word_group_id by letter selector. The fastest way to do that
            # is to use the set().intersection() method. It blows other methods out of the water.
            # But...

            # THERE IS A LOT OF OVERHEAD IN THIS PART - THE set() INTERSECTION AND THEN CONVERTING THE
            # RESULTING SET TO A NUMPY ARRAY. THIS TAKES ABOUT 33% OF THE TOTAL
            # RUNTIME OF THIS FUNCTION
            # LEAVING THESE SNIPPETS OF ALTERNATIVES IN FOR REFERENCE AND LEARNING
            ##

            # 2024 02 05: USE np.intersect1d(): This is very slow
            # nc_ls_wg_id_list = np.intersect1d(ar1 = nc_wg_id_list, ar2=ls_wg_id_list, assume_unique=True)

            # 2024 02 05: use a pandas join: This is very slow
            # df_ls = pd.DataFrame(data = ls_wg_id_list, columns = ['word_group_id'])
            # df_nc = pd.DataFrame(data = nc_wg_id_list, columns = ['word_group_id'])
            # df_out = pd.merge(left = df_ls, right = df_nc)
            # nc_ls_wg_id_set = None
            # nc_ls_wg_id_list = df_out['word_group_id'].to_numpy()

            # 2024 02 06: use a collections.Counter(). This is also sloooooooow!
            # this_counter = collections.Counter(nc_wg_id_list)
            # this_counter.update(ls_wg_id_list)
            # this_array = np.array(list(this_counter.items()))
            # outcome = this_array[:, 1] == 2
            # nc_ls_wg_id_list = this_array[outcome, 0]
            # nc_ls_wg_id_set = None

            # This is the fastest implementation
            if matrix_extraction_option in (0, 6):
                nc_ls_wg_id_set = nc_wg_id_set.intersection(ls_wg_id_set)
                nc_ls_wg_id_list = np.fromiter(iter=nc_ls_wg_id_set, dtype=int)

                # now, get the rows
                nc_ls_wchar_matrix = wchar_matrix[nc_ls_wg_id_list,]
                nc_ls_matrix_dict[nc_ls_id] = (
                    nc_ls_wg_id_list,
                    nc_ls_wchar_matrix
                )

            # get the right loop count
            loop_count += 1
            if loop_count % 1000 == 0:
                print("...{:,}".format(loop_count), "records enumerated...")

        # display the final count
        if matrix_extraction_option == 2:
            n_sub_matrices = len(n_char_matrix_dict)

        if matrix_extraction_option in (3, 4):
            n_sub_matrices = len(single_letter_matrix_dict)

        if matrix_extraction_option == 5:
            n_sub_matrices = len(letter_selector_matrix_dict)

        if matrix_extraction_option in (0, 6):
            n_sub_matrices = len(nc_ls_matrix_dict)
    else:
        n_sub_matrices = 0

    print("...{:,}".format(n_sub_matrices), "sub-matrices created...")
    p_time = calc_time(time_start=s_time)
    print("Total extraction time:", p_time, "seconds.")

    # set things to None so that we can free up memory and reduce overhead
    # these objects are no longer needed
    # only return objects specific to the particular matrix extraction option
    if matrix_extraction_option not in (0, 2):
        # option 2
        n_char_matrix_dict = None

    if matrix_extraction_option not in (0, 3, 4):
        # option 3 and 4
        single_letter_matrix_dict = None

    if matrix_extraction_option not in (0, 5):
        # option 5
        letter_selector_matrix_dict = None

    if matrix_extraction_option not in (0, 6):
        # option 6
        nc_ls_matrix_dict = None

    return (
        wg_df,
        n_char_matrix_dict,
        single_letter_matrix_dict,
        letter_selector_matrix_dict,
        nc_ls_matrix_dict,
        p_time
    )


def test_matrix_extraction_option(wg_df: pd.DataFrame,
                                  letter_dict: dict,
                                  word_group_id_list: np.ndarray,
                                  wchar_matrix: np.ndarray,
                                  n_subset_letters: int):

    output_list = []
    for meo in range(0, 7):
        print('*** matrix extraction option:', meo, '***')

        wg_df, n_char_matrix_dict, single_letter_matrix_dict, letter_selector_matrix_dict, nc_ls_matrix_dict, p_time = split_matrix(
            letter_dict=letter_dict,
            word_group_id_list=word_group_id_list,
            wg_df=wg_df,
            wchar_matrix=wchar_matrix,
            n_subset_letters=n_subset_letters,
            matrix_extraction_option=meo
        )

        if n_char_matrix_dict is None:
            n_char_matrix_dict_items = -1
        else:
            n_char_matrix_dict_items = len(n_char_matrix_dict)

        if single_letter_matrix_dict is None:
            single_letter_matrix_dict_items = -1
        else:
            single_letter_matrix_dict_items = len(single_letter_matrix_dict)

        if letter_selector_matrix_dict is None:
            letter_selector_matrix_dict_items = -1
        else:
            letter_selector_matrix_dict_items = len(
                letter_selector_matrix_dict)

        if nc_ls_matrix_dict is None:
            nc_ls_matrix_dict_items = -1
        else:
            nc_ls_matrix_dict_items = len(nc_ls_matrix_dict)

        temp_dict = {
            'matrix_extraction_option': meo,
            'n_char_matrix_dict_type': str(type(n_char_matrix_dict)),
            'single_letter_matrix_dict_type': str(type(single_letter_matrix_dict)),
            'letter_selector_matrix_dict_type': str(type(letter_selector_matrix_dict)),
            'nc_ls_matrix_dict_type': str(type(nc_ls_matrix_dict)),
            'n_char_matrix_dict_items': n_char_matrix_dict_items,
            'single_letter_matrix_dict_items': single_letter_matrix_dict_items,
            'letter_selector_matrix_dict_items': letter_selector_matrix_dict_items,
            'nc_ls_matrix_dict_items': nc_ls_matrix_dict_items,
            'process_time': p_time
        }
        output_list.append(temp_dict)

    # create an output dataframe
    output_df = pd.DataFrame(output_list)

    return output_df


def compute_lookups(wg_df: pd.DataFrame,
                    n_char_matrix_dict: dict,
                    single_letter_matrix_dict: dict,
                    letter_selector_matrix_dict: dict,
                    nc_ls_matrix_dict: dict):

    # time to count some stuff!

    # count the number of look ups for a single letter
    n_char_lu_dict = {nc: nc_items[0].shape[0]
                      for nc, nc_items in n_char_matrix_dict.items()}

    # count the number of look ups
    single_letter_lu_dict = {sl: sl_items[0].shape[0]
                             for sl, sl_items in single_letter_matrix_dict.items()}

    # count the number of possible values for a given letter select
    letter_selector_lu_dict = {ls: ls_items[0].shape[0]
                               for ls, ls_items in letter_selector_matrix_dict.items()}

    # count the number of lookups
    nc_ls_lu_dict = {nc_ls: nc_ls_items[0].shape[0]
                     for nc_ls, nc_ls_items in nc_ls_matrix_dict.items()}

    col_names = ['word_id', 'word_group_id', 'n_chars', 'first_letter_id',
                 'single_letter_id', 'letter_selector_id', 'nc_ls_id']

    wg_lu_df = wg_df[col_names].copy()

    # count the look-ups!
    # matrix extraction option 1
    wg_lu_df["me_01_full_matrix_lookup"] = wg_df.shape[0]
    # matrix extraction option 2
    wg_lu_df["me_02_n_char_lookup"] = wg_lu_df["n_chars"].map(n_char_lu_dict)
    # matrix extraction option 3
    wg_lu_df["me_03_first_letter_lookup"] = wg_lu_df["first_letter_id"].map(
        single_letter_lu_dict
    )
    # matrix extraction option 4
    wg_lu_df["me_04_single_letter_lookup"] = wg_lu_df["single_letter_id"].map(
        single_letter_lu_dict
    )
    # matrix extraction option 5
    wg_lu_df["me_05_letter_selector_lookup"] = wg_lu_df["letter_selector_id"].map(
        letter_selector_lu_dict
    )
    # matrix extraction option 6
    wg_lu_df["me_06_nc_ls_lookup"] = wg_lu_df["nc_ls_id"].map(nc_ls_lu_dict)    

    return wg_lu_df


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
    word_list = word_df.loc[word_df["word_group_id"].isin(
        demo_output[:, 0]), "lcase"]
    print("There are", word_list.shape[0],
          "parent/from words for the word", demo_word)

    print("The first five words are:")
    print(word_list.head())
    print("The last five words are:")
    print(word_list.tail())

    return None


def get_values_full_matrix(
    wg_id: int, wchar_matrix: np.ndarray, word_group_id_list: np.ndarray
):
    # matrix extraction option 1

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

    # matrix extraction option 2

    nc_wg_id_list, nc_sub_wchar_matrix = n_char_matrix_dict[n_char]
    new_word_id = nc_wg_id_list == wg_id

    # perform the comparison
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
    # matrix extraction option 3 and 4
    (
        single_letter_word_group_id_list,
        single_letter_wchar_matrix
    ) = single_letter_matrix_dict[single_letter_id]

    new_word_id = single_letter_word_group_id_list == wg_id

    # now, peform the comparison
    outcome = single_letter_wchar_matrix - \
        single_letter_wchar_matrix[new_word_id,]

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
    # matrix extraction option 5
    ls_wg_id_list, ls_wchar_matrix = letter_selector_matrix_dict[
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
    # matrix extraction option 6
    nc_ls_wg_id_list, nc_ls_wchar_matrix = nc_ls_matrix_dict[nc_ls_id]

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


def estimate_total_pairs(wg_df: pd.DataFrame, letter_selector_matrix_dict: dict) -> int:
    # Sample 10 words of each word length, compute the number of from/parent
    # anagrams for each word in the sample, compute the min, mean, and max,
    # and apply those values to the numbers of words by length and multiply
    # accordingly. this will give us (very generous) upper bounds of anagram pairs

    # sample 10 words from each word based on word length.
    # words are anywhere from 1 character to 24 characters, 240 samples
    sample_df = wg_df.groupby(["n_chars"]).sample(
        n=10, replace=True, random_state=123)

    # enumerate using itertuples in order to capture the output
    output_list = []
    for row in sample_df.itertuples():
        # get the values using the get_values_n_char_letter_selector() function.
        output = get_values_letter_selector(
            wg_id=row.word_group_id,
            letter_selector_id=row.letter_selector_id,
            letter_selector_matrix_dict=letter_selector_matrix_dict,
        )

        curr_from_words = output.shape[0]
        curr_output = [row.n_chars, curr_from_words]
        output_list.append(curr_output)

    # make a dataframe from the sample possibilities
    pos_df = pd.DataFrame(data=output_list, columns=[
                          "n_chars", "n_from_words"])

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
        agg_pos_df["n_tot_mean_anagrams"].sum(
        ) + agg_pos_df["n_tot_max_anagrams"].sum()
    ) / 2

    # round and convert to integer
    n_possible_anagrams = int(np.round(n_possible_anagrams, 0))

    # this number will be used to create an array that will hold the from/to pairs
    n_possible_anagrams_formatted = "{:,}".format(n_possible_anagrams)
    print(
        "...estimated number of from/to pair word pairs:", n_possible_anagrams_formatted
    )

    return n_possible_anagrams, agg_pos_df


def load_possible_anagrams(db_path: str, db_name: str) -> pd.DataFrame:

    sql = 'select * from n_possible_anagrams;'
    agg_pos_df = query_db(sql=sql, db_path=db_path, db_name=db_name)
    n_possible_anagrams = (
        agg_pos_df["n_tot_mean_anagrams"].sum(
        ) + agg_pos_df["n_tot_max_anagrams"].sum()
    ) / 2

    # round and convert to integer
    n_possible_anagrams = int(np.round(n_possible_anagrams, 0))

    return n_possible_anagrams


####
# generate_from_to_word_group_pairs placeholder
####
def generate_from_to_word_group_pairs_simple(
    wg_df: pd.DataFrame,
    n_possible_anagrams: int,
    matrix_extraction_option: int,
    wchar_matrix: np.ndarray,
    word_group_id_list: np.ndarray,
    n_char_matrix_dict: dict,
    single_letter_matrix_dict: dict,
    letter_selector_matrix_dict: dict,
    nc_ls_matrix_dict: dict,
    letter_subset_list: str = None
):

    # use numpy to pre-allocate an array that will be updated while enumerating.
    # this eliminates list.append() calls which are fine in small amounts, but
    # hundreds of thousands of append calls are very slow.

    output_list = np.full(shape=(n_possible_anagrams, 2),
                          fill_value=-1, dtype=int)

    # this dictionary will store the calculations for each word
    proc_time_dict = {}

    if letter_subset_list == 'SAMPLE':
        # generate 100 samples within each n_chars and first_letter group combination
        curr_wg_df = wg_df.groupby(['n_chars', 'first_letter']).sample(
            n=100, replace=True, random_state=123).drop_duplicates()
    elif isinstance(letter_subset_list, str) or isinstance(letter_subset_list, list):
        # subset by a specific set of letters or a single letter
        curr_wg_df = wg_df.loc[wg_df['first_letter'].isin(
            set(letter_subset_list)), :].copy()
    else:
        curr_wg_df = wg_df.copy()

    # display counts
    curr_word_count = curr_wg_df.shape[0]

    n_curr_words = "{:,}".format(curr_word_count)
    print(
        "...finding parent anagrams for",
        n_curr_words,
        "words..."
    )

    # establish counters for record keeping
    row_count = 0
    anagram_pair_count = 0
    intmerdiate_to_word_count = collections.Counter()
    # enumerate by word id, working with integers is faster than words
    for row in curr_wg_df.itertuples(index=False):
        # start timing to record processing for each word
        s_time = perf_counter_ns()

        # word group id
        wg_id = row.word_group_id

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

            output_list[anagram_pair_count:new_anagram_pair_count,
                        :] = outcome_word_id_list
            

            #n_to_word_counter = collections.Counter(output_list[:, 0])
            intmerdiate_to_word_count.update(outcome_word_id_list[:, 0])


            # set the anagram pair count
            anagram_pair_count = new_anagram_pair_count

        # delete the intermediate list
        del outcome_word_id_list

        # record the time for the word
        p_time = calc_time(time_start=s_time, round_digits=-1)

        proc_time_dict[wg_id] = (p_time, n_from_words)

        row_count += 1
        if row_count % 1e4 == 0:
            print('...found parent anagrams for',
                  "{:,}".format(row_count), 'words...')

    # last update
    print('...found parent anagrams for', "{:,}".format(row_count), 'words...')
    # create a dataframe from the proc_time_dict
    proc_time_df = pd.DataFrame.from_dict(data=proc_time_dict, orient="index")
    proc_time_df = proc_time_df.reset_index()
    proc_time_df.columns = ["word_group_id", "n_seconds", "n_from_word_groups"]

    # display processing time for the current letter
    total_proc_time_s = round(proc_time_df["n_seconds"].sum(), 2)
    total_proc_time_m = round(proc_time_df["n_seconds"].sum() / 60, 2)
    print(
        "...finding parent anagrams for",
        n_curr_words,
        "words took",
        total_proc_time_s,
        "seconds |",
        total_proc_time_m,
        "minutes..."
    )

    # truncate the output array to only include rows with a from/to word pair
    # this removes any row that has a value of -1
    print('...truncating output list...')
    output_indices = np.all(output_list >= 0, axis=1)
    output_list = output_list[output_indices,]
    del output_indices

    # initialize Counters to hold the count of found pairs for a given word
    # for the count of to/child words, we need to count the number of times
    # each word_group_id
    # exists in the from/parent column
    # count the number of to words
    # seems little counter-intuitive... but we're counting the number of
    # to-words from each from-word. So, this is the number of child words
    # from each parent word.
    # https://docs.python.org/3/library/collections.html#collections.Counter

    # we do not need the count of from-word, but leaving in for convenience
    # print("...populating the count of from-words...")
    # n_from_word_counter = collections.Counter(output_list[:, 1])

    print("...populating the count of to-words...")
    #big_count_start_time = perf_counter_ns()
    #n_to_word_counter = collections.Counter(output_list[:, 0])
    #print(calc_time(time_start = big_count_start_time))
    #outcome_test = intmerdiate_to_word_count == n_to_word_counter
    #print(outcome_test)

    # now, use the map function to get the number of from/to words and the number of
    # candidate words for each word
    proc_time_df["n_to_word_groups"] = proc_time_df["word_group_id"].map(
        intmerdiate_to_word_count
    )

    # record the matrix extraction option
    proc_time_df['matrix_extraction_option'] = matrix_extraction_option

    # how many anagram pairs were found?
    n_total_anagrams = output_list.shape[0]
    n_total_anagrams_formatted = "{:,}".format(n_total_anagrams)
    print("...total anagram pairs:", n_total_anagrams_formatted)

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

            mean_write_time = round(mean_write_time, 2)
            print(
                "...average write time per 10M records:", mean_write_time, "seconds..."
            )
            print("...estimated write complete time:", eta_write_complete)

            # restart the current write time
            curr_db_write_time_start = datetime.datetime.now()

    # commit the last round of changes
    print("...committing changes:", "{:,}".format(
        len(curr_output_list)), "records")
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


def store_anagram_processing(
    proc_time_df: str,
    matrix_extraction_option: str,
    db_path: str,
    db_name: str,
) -> None:

    # create database connection objects
    db_conn = build_db_conn(db_path=db_path, db_name=db_name)

    # write the processing option table
    table_name = f"words_me_{str(matrix_extraction_option).zfill(2)}"
    write_data_to_sqlite(df=proc_time_df,
                         table_name=table_name,
                         db_path=db_path,
                         db_name=db_name)

    # close the connection
    db_conn.close()

    return None


def display_total_processing_time(
    proc_time_df: pd.DataFrame, total_time_start: datetime.datetime
) -> None:
    anagram_discovery_time_seconds = proc_time_df["n_seconds"].sum()
    anagram_discovery_time_minutes = anagram_discovery_time_seconds / 60

    anagram_discovery_time_seconds = round(anagram_discovery_time_seconds, 2)
    anagram_discovery_time_minutes = round(anagram_discovery_time_minutes, 2)

    print(
        "...anagram discovery time:",
        anagram_discovery_time_seconds,
        "seconds |",
        anagram_discovery_time_minutes,
        "minutes",
    )

    # record the total time
    total_time_seconds = calc_time(
        time_start=total_time_start, round_digits=-1)
    total_time_minutes = total_time_seconds / 60
    # round for display
    total_time_seconds = round(total_time_seconds, 2)
    total_time_minutes = round(total_time_minutes, 2)

    print("...total processing time:", total_time_seconds,
          "seconds |",  total_time_minutes, "minutes")

    return None


if __name__ == "__main__":
    # gotta do something...
    print("The dean? hellos")

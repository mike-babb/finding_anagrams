# standard libraries - installed by default
import collections
import datetime
import os

# external libraries - not installed by default
import numpy as np
import pandas as pd


from part_00_file_db_utils import *
from part_00_process_functions import *


def split_matrix(
    letter_dict: dict,
    word_group_id_list: np.ndarray,
    wg_df: pd.DataFrame,
    wchar_matrix: np.ndarray,
    n_subset_letters: int
):
    s_time = datetime.datetime.now()

    # create the letter selector and determine the max number
    # of sub-matrices to makes

    wg_df["letter_selector"] = wg_df["letter_group_ranked"].str[:n_subset_letters]
    wg_df["first_letter_id"] = wg_df["first_letter"].map(letter_dict)
    wg_df["single_letter_id"] = wg_df["letter_selector"].str[0].map(letter_dict)

    # build the letter selector id
    letter_selector_list = wg_df["letter_selector"].unique()
    letter_selector_list.sort()
    letter_selector_id_dict = {ls: i_ls for i_ls, ls in enumerate(letter_selector_list)}

    wg_df["letter_selector_id"] = wg_df["letter_selector"].map(letter_selector_id_dict)

    nc_ls_df = wg_df[
        ["n_chars", "letter_selector_id", "letter_selector"]
    ].drop_duplicates()
    nc_ls_df["nc_ls_id"] = range(0, nc_ls_df.shape[0])

    wg_df = pd.merge(left=wg_df, right=nc_ls_df)

    n_sub_matrices = nc_ls_df.shape[0]
    print("...creating", "{:,}".format(n_sub_matrices), "sub-matrices...")

    # word length dictionary
    # used in matrix extraction option: 2
    n_char_matrix_dict = {}
    n_char_lu_dict = dict.fromkeys(wg_df["n_chars"].unique())

    # single letter matrix dict
    # used in matrix extraction option: 3 and 4
    single_letter_matrix_dict = {}
    single_letter_lu_dict = dict.fromkeys(wg_df["first_letter_id"].unique())

    # letter selector dictionary
    # used in matrix extraction option: 5
    letter_selector_matrix_dict = {}
    letter_selector_lu_dict = dict.fromkeys(nc_ls_df["letter_selector_id"].unique())

    # word length and lettor selector dictionary
    # used in matrix extraction option: 6
    nc_ls_matrix_dict = {}
    # nc_ls_lu_dict = dict.fromkeys(nc_ls_df['nc_ls_id'].to_numpy())
    nc_ls_lu_dict = collections.Counter()

    # enumerate these combinations only once
    # reduce the number of times we have to compute sets of ids
    loop_count = 0

    for nc, ls, ls_id, nc_ls_id in zip(
        nc_ls_df["n_chars"].to_numpy(),
        nc_ls_df["letter_selector"].to_numpy(),
        nc_ls_df["letter_selector_id"].to_numpy(),
        nc_ls_df["nc_ls_id"].to_numpy(),
    ):
   
        ####
        # MATRIX EXTRACTION OPTION 2: DICTIONARY BY NUMBER OF CHARACTERS
        ####
        if nc not in n_char_matrix_dict:
            nc_wg_id_list = wg_df.loc[
                (wg_df["n_chars"] >= nc), "word_group_id"
            ].to_numpy()
            nc_wg_id_set = set(nc_wg_id_list)

            # subset the wchar_matrix to get the sub-matrix
            nc_sub_wchar_matrix = wchar_matrix[nc_wg_id_list,]

            n_char_matrix_dict[nc] = (nc_wg_id_list, nc_sub_wchar_matrix, nc_wg_id_set)

            # count the number of look ups for a letter
            n_char_lu_dict[nc] = nc_wg_id_list.shape[0]
        else:
            nc_wg_id_list, nc_sub_wchar_matrix, nc_wg_id_set = n_char_matrix_dict[nc]

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
            single_letter_word_group_id_set = set(single_letter_word_group_id_list)

            # subset the wchar_matrix to get the sub-matrix
            single_letter_wchar_matrix = wchar_matrix[single_letter_word_group_id_list,]

            single_letter_matrix_dict[ll_id] = (
                single_letter_word_group_id_list,
                single_letter_wchar_matrix,
                single_letter_word_group_id_set,
            )

            # count the number of look ups
            single_letter_lu_dict[ll_id] = single_letter_word_group_id_list.shape[0]
        else:
            # query the sub-matrices split by individual letter to then get the smaller partitions
            (
                single_letter_word_group_id_list,
                single_letter_wchar_matrix,
                single_letter_word_group_id_set,
            ) = single_letter_matrix_dict[ll_id]

        ####
        # MATRIX EXTRACTION OPTION 5: DICTIONARY BY LETTER SELECTOR
        ####
        if ls_id not in letter_selector_matrix_dict:
            # build a column selector
            column_selector = [letter_dict[curr_letter] for curr_letter in ls]

            # get the indices of the single_letter_wchar_matrix that feature the n least common letters
            outcome = single_letter_wchar_matrix[:, column_selector] > 0
            outcome_indices = np.all(outcome > 0, axis=1)

            # these are now the ids
            ls_wg_id_list = single_letter_word_group_id_list[outcome_indices]
            ls_wg_id_set = set(ls_wg_id_list)

            # subset the wchar_matrix to get the sub-matrix - this contains the N least common letters for a group of words
            ls_wchar_matrix = wchar_matrix[ls_wg_id_list,]
            letter_selector_matrix_dict[ls_id] = (
                ls_wg_id_list,
                ls_wchar_matrix,
                ls_wg_id_set,
            )

            # count the number of possible values for a given letter select
            letter_selector_lu_dict[ls_id] = ls_wg_id_list.shape[0]
        else:
            # this is the submatrix by letter selector
            ls_wg_id_list, ls_wchar_matrix, ls_wg_id_set = letter_selector_matrix_dict[
                ls_id
            ]

        
        ####
        # MATRIX EXTRACTION OPTION 5: DICTIONARY BY NUMBER OF CHARACTERS AND LETTER SELECTOR
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

        # 2024 02 06: user a collections.Counter(). This is also sloooooooow!
        # this_counter = collections.Counter(nc_wg_id_list)
        # this_counter.update(ls_wg_id_list)
        # this_array = np.array(list(this_counter.items()))
        # outcome = this_array[:, 1] == 2
        #nc_ls_wg_id_list = this_array[outcome, 0]
        # nc_ls_wg_id_set = None

        # This is the fastest implementation
        # it takes about 33% of the total time        
        nc_ls_wg_id_set = nc_wg_id_set.intersection(ls_wg_id_set)
        nc_ls_wg_id_list = np.fromiter(iter=nc_ls_wg_id_set, dtype=int)

        # now, get the rows
        nc_ls_wchar_matrix = wchar_matrix[nc_ls_wg_id_list,]
        nc_ls_matrix_dict[nc_ls_id] = (
            nc_ls_wg_id_list,
            nc_ls_wchar_matrix,
            nc_ls_wg_id_set,
        )
        # count the number of lookups
        nc_ls_lu_dict[nc_ls_id] = nc_ls_wg_id_list.shape[0]        
        
        loop_count = len(nc_ls_lu_dict)
        if loop_count % 1000 == 0:
            print("...{:,}".format(loop_count), "sub-matrices created...")
            
    # display the final count
    print("...{:,}".format(len(nc_ls_lu_dict)), "sub-matrices created...")
    e_time = datetime.datetime.now()
    p_time = e_time - s_time
    p_time = round(p_time.total_seconds(), 2)
    print("Total extraction time:", p_time, "seconds.")

    # count the look-ups!
    wg_df["me_01_full_matrix_lookup"] = wchar_matrix.shape[0]
    wg_df["me_02_n_char_lookup"] = wg_df["n_chars"].map(n_char_lu_dict)
    wg_df["me_03_first_letter_lookup"] = wg_df["first_letter_id"].map(
        single_letter_lu_dict
    )
    wg_df["me_04_single_letter_lookup"] = wg_df["single_letter_id"].map(
        single_letter_lu_dict
    )
    wg_df["me_05_letter_selector_lookup"] = wg_df["letter_selector_id"].map(
        letter_selector_lu_dict
    )
    wg_df["me_06_nc_ls_lookup"] = wg_df["nc_ls_id"].map(nc_ls_lu_dict)    

    return (
        wg_df,
        n_char_matrix_dict,
        single_letter_matrix_dict,
        letter_selector_matrix_dict,
        nc_ls_matrix_dict,
    )


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


def do_it(matrix_extraction_option: int, letter_subset_list: str):
    # start a timer to record the entire operation
    total_time_start = datetime.datetime.now()

    # base file path
    base_file_path = "/project/finding_anagrams"

    # input path
    in_file_path = "data"
    in_file_path = os.path.join(base_file_path, in_file_path)

    # output db path and name
    db_path = "db"
    db_path = os.path.join(base_file_path, db_path)

    if os.path.exists(db_path):
        pass
    else:
        os.makedirs(db_path)

    db_name = "words.db"

    # Use numpy to perform matrix opertions and determine from/to and exact anagram relationships
    # Option 1: Full matrix
    # Option 2: Word-length
    # Option 3: First letter
    # Option 4: Single-least common letter
    # Option 5: n least common letters
    # Option 6: word-length and n least common letters

    # max number of letters to slice to use for the generation of sub-matrices for
    # options 5 and 6. More letters means more sub-matrices
    # 3 seems to be the sweet spot
    n_subset_letters = 3

    (
        word_df,
        wg_df,
        letter_dict,
        char_matrix,
        word_group_id_list,
        word_id_list,
        wchar_matrix,
    ) = load_input_data(db_path=db_path, db_name=db_name, in_file_path=in_file_path)

    (
        wg_df,
        n_char_matrix_dict,
        single_letter_matrix_dict,
        letter_selector_matrix_dict,
        nc_ls_matrix_dict,
    ) = split_matrix(
        letter_dict=letter_dict,
        word_group_id_list=word_group_id_list,
        wg_df=wg_df,
        wchar_matrix=wchar_matrix,
        n_subset_letters=n_subset_letters
    )

    n_possible_anagrams = estimate_total_pairs(
        wg_df=wg_df, nc_ls_matrix_dict=nc_ls_matrix_dict
    )

    # set things to None so that we can free up memory and reduce overhead
    # these objects are no longer needed
    if matrix_extraction_option != 2:
        # option 2
        n_char_matrix_dict = None

    if matrix_extraction_option not in (3, 4):
        # option 3 and 4
        single_letter_matrix_dict = None

    if matrix_extraction_option != 5:
        # option 5
        letter_selector_matrix_dict = None

    if matrix_extraction_option != 6:
        # option 6
        nc_ls_matrix_dict = None
    
    proc_time_df, output_list = generate_from_to_word_group_pairs_simple(
        wg_df=wg_df,
        n_possible_anagrams=n_possible_anagrams,
        matrix_extraction_option=matrix_extraction_option,
        wchar_matrix=wchar_matrix,
        word_group_id_list=word_group_id_list,
        n_char_matrix_dict=n_char_matrix_dict,
        single_letter_matrix_dict=single_letter_matrix_dict,
        letter_selector_matrix_dict=letter_selector_matrix_dict,
        nc_ls_matrix_dict=nc_ls_matrix_dict,
        letter_subset_list=letter_subset_list,
    )

    proc_time_df, word_df = format_anagaram_processing(
        output_list=output_list,
        proc_time_df=proc_time_df,
        word_df=word_df,
        wg_df=wg_df,
        matrix_extraction_option=matrix_extraction_option,
    )

    store_anagram_processing(
        proc_time_df=proc_time_df,
        word_df=word_df,
        matrix_extraction_option=matrix_extraction_option,
        db_path=db_path,
        db_name=db_name,
    )

    display_total_processing_time(
        proc_time_df=proc_time_df, total_time_start=total_time_start
    )

    return None


if __name__ == "__main__":
    # specify extraction options
    matrix_extraction_option = 6
    letter_subset_list = None
    #letter_subset_list = ['x']

    for meo in range(5, 6):
        do_it(
            matrix_extraction_option=meo,
            letter_subset_list=letter_subset_list,
        )

# standard libraries - installed by default
import collections
import datetime
import os

# external libraries - not installed by default
import numpy as np
import pandas as pd

# custom
from part_00_file_db_utils import *
from part_00_process_functions import *


def find_from_to_word_pairs(matrix_extraction_option: int, letter_subset_list: str):
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
        n_subset_letters=n_subset_letters,
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
    # letter_subset_list = ['x']

    for meo in range(5, 6):
        find_from_to_word_pairs(
            matrix_extraction_option=meo,
            letter_subset_list=letter_subset_list,
        )

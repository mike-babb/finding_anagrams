#!/usr/bin/env python
# coding: utf-8
# Mike Babb
# babb.mike@outlook.com
# Find Anagrams Part 3: Generate and store the anagrams


# standard libraries
from time import perf_counter_ns

# external libraries

# custom libraries
from _run_constants import *
from part_00_file_db_utils import *
from part_00_process_functions import *


def run_part_03(matrix_extraction_option: int, n_subset_letters: int, write_data: bool, letter_subset_list: None,
                db_path: str, db_name: str, in_file_path:str):

    # start a timer to record the entire operation
    total_time_start = perf_counter_ns()

    # load input data

    word_df, wg_df, letter_dict, char_matrix, \
        word_group_id_list, word_id_list, wchar_matrix = load_input_data(
            db_path=db_path, db_name=db_name,
            in_file_path=in_file_path)

    # subset the matrix
    wg_df, n_char_matrix_dict, single_letter_matrix_dict, letter_selector_matrix_dict, nc_ls_matrix_dict, p_time = split_matrix(
        letter_dict=letter_dict,
        word_group_id_list=word_group_id_list,
        wg_df=wg_df,
        wchar_matrix=wchar_matrix,
        n_subset_letters=n_subset_letters,
        matrix_extraction_option=matrix_extraction_option
    )

    # get the total number of from/to word pairs from the previous steps
    n_possible_anagrams = load_possible_anagrams(
        db_path=db_path, db_name=db_name)

    # discover from/to word group id pairs
    proc_time_df, output_list = \
        generate_from_to_word_group_pairs_simple(wg_df=wg_df,
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

    # write the anagram pairs to the database
    if write_data:
        store_anagram_pairs(output_list=output_list,
                            db_path=db_path, db_name=db_name)

    # store number of from/to word pairs and time related to processing
    store_anagram_processing(proc_time_df=proc_time_df,
                             matrix_extraction_option=matrix_extraction_option, db_path=db_path, db_name=db_name)

    display_total_processing_time(
        proc_time_df=proc_time_df, total_time_start=total_time_start)


if __name__ == '__main__':

    # start a timer to record the entire operation
    total_time_start = perf_counter_ns()

    ####
    # process control flags
    ####

    # Use numpy to perform matrix opertions and determine from/to and exact anagram relationships
    # Option 1: Full matrix
    # Option 2: Word-length
    # Option 3: First letter
    # Option 4: Single-least common letter
    # Option 5: n least common letters
    # Option 6: word-length and n least common letters

    matrix_extraction_option = 6


    # max number of letters to slice to use for the generation of sub-matrices for
    # options 5 and 6. More letters means more sub-matrices
    # 3 seems to be the sweet spot
    n_subset_letters = 3

    # set write_data to True to store the generated list of anagrams
    write_data = False

    # Testing options
    # NoneL to include all letters
    # ['q', 'x'] or a different set of letters to test a specific letter
    # 'SAMPLE' to take a 10% sample by word length group
    # letter_subset_list = ['x']
    # letter_subset_list = 'SAMPLE'
    letter_subset_list = None

    run_part_03(matrix_extraction_option=matrix_extraction_option,
                n_subset_letters=n_subset_letters,
                letter_subset_list=letter_subset_list,
                write_data=write_data, db_path=rc.db_path, db_name=rc.db_name, 
                in_file_path=rc.in_file_path)

    compute_total_time(total_time_start=total_time_start)

#!/usr/bin/env python
# coding: utf-8

# # Mike Babb
# # babb.mike@outlook.com
# # Find anagrams
# ## Part 2: Demonstrate extraction timing techniques


# standard libraries - installed by default
from itertools import product
import timeit


# external libraries - not installed by default
import numpy as np
import pandas as pd


# custom, user-defined functions
import _run_constants as rc
from part_00_file_db_utils import *
from part_00_process_functions import *


def demo_extraction_techniques(word_df: pd.DataFrame, wg_df: pd.DataFrame,
                               wchar_matrix: np.ndarray, word_group_id_list: np.ndarray,
                               n_char_matrix_dict: dict,
                               single_letter_matrix_dict: dict,
                               letter_selector_matrix_dict: dict, nc_ls_matrix_dict: dict,
                               demo_word: str = 'achiever',
                               n_trials: int = 100):

    wg_id = word_df.loc[word_df['lcase'] == demo_word, 'word_group_id'].iloc[0]

    demo_wg_df = wg_df.loc[wg_df['word_group_id'] == wg_id, :]

    # option 1 - Full matrix
    # No additional data needed

    # option 2 -  Number of characters
    n_char = demo_wg_df['n_chars'].iloc[0]

    # option 3 - First letter
    first_letter_id = demo_wg_df['first_letter_id'].iloc[0]

    # option 4 - Least common letter
    single_letter_id = demo_wg_df['single_letter_id'].iloc[0]

    # option 5 - Multiple least common letters
    letter_selector_id = demo_wg_df['letter_selector_id'].iloc[0]

    # option 6 - Number of characters and multiple least common letters
    nc_ls_id = demo_wg_df['nc_ls_id'].iloc[0]

    # Demontrate that the different matrix extraction options return identical results

    # Select on the full matrix: option 1

    # demo the full matrix selection
    output = get_values_full_matrix(wg_id=wg_id,
                                    wchar_matrix=wchar_matrix,
                                    word_group_id_list=word_group_id_list)

    # this is an array of from words to the word 'achiever'
    format_demo_output(demo_word=demo_word,
                       word_df=word_df,
                       demo_output=output)

    # Select on the matrices split by word-length: option 2

    # demo the n char selection
    output = get_values_n_char(wg_id=wg_id,
                               n_char=n_char,
                               n_char_matrix_dict=n_char_matrix_dict)

    # this is an array of from words to the word 'achiever'
    format_demo_output(demo_word=demo_word,
                       word_df=word_df,
                       demo_output=output)

    # Select on the matrices split by the first letter: option 3

    # demo the first letter selection
    output = get_values_single_letter(wg_id=wg_id, single_letter_id=first_letter_id,
                                      single_letter_matrix_dict=single_letter_matrix_dict)

    # this is an array of from words to the word 'achiever'
    format_demo_output(demo_word=demo_word,
                       word_df=word_df,
                       demo_output=output)

    # Select on the matrices split by the single least common letter: option 4

    # demo the first letter selection
    output = get_values_single_letter(wg_id=wg_id, single_letter_id=single_letter_id,
                                      single_letter_matrix_dict=single_letter_matrix_dict)

    # this is an array of from words to the word 'achiever'
    format_demo_output(demo_word=demo_word,
                       word_df=word_df,
                       demo_output=output)

    # Select on the matrices split by the letter selector: option 5

    # demo with the letter selector
    output = get_values_letter_selector(wg_id=wg_id,
                                        letter_selector_id=letter_selector_id,
                                        letter_selector_matrix_dict=letter_selector_matrix_dict)

    # this is an array of from words to the word 'achiever'
    format_demo_output(demo_word=demo_word,
                       word_df=word_df,
                       demo_output=output)

    # Select on the matrices split by word-length and the letter selector: option 6

    # demo with the n_char letter selector
    output = get_values_n_char_letter_selector(wg_id=wg_id,
                                               nc_ls_id=nc_ls_id,
                                               nc_ls_matrix_dict=nc_ls_matrix_dict)

    # this is an array of from words to the word 'achiever'
    format_demo_output(demo_word=demo_word,
                       word_df=word_df,
                       demo_output=output)

    # we've tested with one word, let's time many evaluations to get a sense of how quickly
    # the different matrix extraction options work
    # use the timeit() function to evaluate how long, on average, a single operation
    # takes to complete
    # we do this by writing python code encapsulated in quotes which is then sent to the function
    # we can store the quoted code in a dictionary and then enumerate.
    # we'll run each code chunk 100 times and then compute the average

    code_snippet_dict = {
        'Matrix Selection Option 1: Selecting by full matrix':
        """get_values_full_matrix(wg_id = wg_id, wchar_matrix = wchar_matrix, word_group_id_list = word_group_id_list)""",
        'Matrix Selection Option 2: Selecting by word length':
        """get_values_n_char(wg_id = wg_id, n_char = n_char, n_char_matrix_dict = n_char_matrix_dict)""",
        'Matrix Selection Option 3: Selecting by first letter':
        """get_values_single_letter(wg_id = wg_id, single_letter_id = first_letter_id, single_letter_matrix_dict = single_letter_matrix_dict)""",
        'Matrix Selection Option 4: Selecting by single least common letter':
        """get_values_single_letter(wg_id = wg_id, single_letter_id = single_letter_id, single_letter_matrix_dict = single_letter_matrix_dict)""",
        'Matrix Selection Option 5: Selecting by letter selector':
        """get_values_letter_selector(wg_id = wg_id, letter_selector_id = letter_selector_id, letter_selector_matrix_dict = letter_selector_matrix_dict)""",
        'Matrix Selection Option 6: Selecting by word length and letter selector':
        """get_values_n_char_letter_selector(wg_id = wg_id, nc_ls_id = nc_ls_id, nc_ls_matrix_dict=nc_ls_matrix_dict)"""
    }

    item_dictionary = {'wg_id': wg_id, 'wchar_matrix': wchar_matrix,
                       'word_group_id_list': word_group_id_list, 'n_char': n_char,
                       'n_char_matrix_dict': n_char_matrix_dict,                       
                       'first_letter_id': first_letter_id,
                       'single_letter_id': single_letter_id,
                       'single_letter_matrix_dict': single_letter_matrix_dict,
                       'letter_selector_id': letter_selector_id,
                       'letter_selector_matrix_dict': letter_selector_matrix_dict,
                       'nc_ls_id': nc_ls_id, 'nc_ls_matrix_dict': nc_ls_matrix_dict}

    setup_statement = 'from part_00_process_functions import ' \
        'get_values_full_matrix, get_values_n_char, get_values_single_letter, ' \
        'get_values_letter_selector, get_values_n_char_letter_selector, ' \
        'format_output_list'

    timing_list = []
    for csd, cs in code_snippet_dict.items():
        print(csd)

        # here we time the code execution
        total_time = timeit.timeit(
            stmt=cs, number=n_trials, setup=setup_statement, globals=item_dictionary)
        timing_list.append([csd, total_time])

        # total time
        total_time_formatted = '{:,}'.format(round(total_time, 2))

        # average time
        avg_time = total_time / n_trials
        avg_time_formatted = '{:,}'.format(round(avg_time, 2))

        # average number of seconds per trial
        print('Total time:', total_time_formatted,
              'seconds. Average time:', avg_time_formatted, 'seconds.')

        # add a line break to make it easier to read
        print()

    # Calculate the ratios amongst different timing techniques

    # matrix extraction option 6 - the combination of the word length and letter selector - is the fastest
    # but how much faster is it compared to option 5 or option 3?

    # these numbers are orders of magnitude different and therefore hard to interpret.
    # let's rescale.

    # we'll use product() to compute the cartesian product of the list of timings
    # from the timing list, we can compute the ratio of one timing to another
    # we can then build a dataframe and cross-tab

    expanded_timing_list = []
    for me_source, me_target in product(timing_list, repeat=2):
        # let's unpack this
        me_source_option, me_source_timing = me_source
        me_target_option, me_target_timing = me_target

        me_source_option = me_source_option[17:25]
        me_target_option = me_target_option[17:25]
        me_source_target_timing_ratio = me_source_timing / me_target_timing

        # add to the list
        expanded_timing_list.append([me_source_option, me_target_option,
                                    me_source_timing, me_target_timing, me_source_target_timing_ratio])

    col_names = ['source', 'target', 'source_timing',
                 'target_timing', 'timing_ratio']

    timing_df = pd.DataFrame(data=expanded_timing_list, columns=col_names)

    print(timing_df.head())

    # use the pd.pivot_table() function to display the ratios
    # we computed the product so all cells will be filled
    # but we only need to look at the top diagonal
    # the bottom diagonal is the inverse of the top diagonal
    # from left to right: we can see how much faster option 5 is than option 1
    # or how much faster option 4 is than option 3
    timing_table = timing_df.pivot_table(index=['source'], columns=['target'],
                                         values=['timing_ratio']).reset_index(drop=False, names='Matrix Extraction')

    # use a list comprehension to clean up the column names
    col_names = [''.join(cn).replace('timing_ratio', '')
                 for cn in timing_table.columns.tolist()]

    timing_table.columns = col_names

    print(timing_table)

    # write to sqlite
    write_data_to_sqlite(df=timing_table, table_name='matrix_extraction_timing', db_path=rc.db_path,
                         db_name=rc.db_name)

    return timing_list


def run_part_02(db_path: str, db_name: str, data_output_file_path,
           n_subset_letters: str, demo_word: str = 'achiever'):

    ####
    # LOAD THE INPUT DATA
    ####
    word_df, wg_df, letter_dict, char_matrix, word_group_id_list, word_id_list, wchar_matrix = load_input_data(db_path=db_path,
                                                                                                               db_name=db_name,
                                                                                                               in_file_path=data_output_file_path)
    ####
    # Test the different matrix splitting techniques
    ####

    # There are 7 different matrix extraction techniques:
    # Option 0: Prepare matrix extraction techniques 1 through 6
    # Option 1: No sub-matrices
    # Option 2: Word-length - matrices split by the number of characters
    # Option 3: First letter - matrices split by each letter
    # Option 4: Single-least common letter - matrices split by each letter
    # Option 5: n least common letters - matrices split by N least common letters
    # Option 6: matrices split by word-length and N least common letters
    # See split_matrix() for a more elaborate description.
    # test_matrix_extraction_option() invokes the split_matrix() function 7 times to demonstrate the differences in timing and split_matrix() function output.

    ####
    # TEST THE DIFFERENT MATRIX EXTRACTION OPTIONS
    ####
    mat_ext_df = test_matrix_extraction_option(wg_df=wg_df,
                                               letter_dict=letter_dict,
                                               word_group_id_list=word_group_id_list,
                                               wchar_matrix=wchar_matrix,
                                               n_subset_letters=n_subset_letters)

    print(mat_ext_df.head(n=7))

    # save to sqlite for future reference
    write_data_to_sqlite(df=mat_ext_df, table_name='matrix_extraction_technique_timing',
                         db_path=db_path, db_name=db_name)

    ####
    # CREATE ALL MATRIX EXTRACTION OPTIONS
    ####
    # Leaving the matrix extracton blank defaults to option 0: prepare all outputs
    wg_df, n_char_matrix_dict, single_letter_matrix_dict, letter_selector_matrix_dict, nc_ls_matrix_dict, p_time = split_matrix(
        letter_dict=letter_dict,
        word_group_id_list=word_group_id_list,
        wg_df=wg_df,
        wchar_matrix=wchar_matrix,
        n_subset_letters=n_subset_letters
    )
    # demonstrate the different matrix extraction techniques using the word 'achiever'
    demo_extraction_techniques(word_df=word_df, wg_df=wg_df, wchar_matrix=wchar_matrix,
                               word_group_id_list=word_group_id_list, n_char_matrix_dict=n_char_matrix_dict,
                               single_letter_matrix_dict=single_letter_matrix_dict,
                               letter_selector_matrix_dict=letter_selector_matrix_dict,
                               nc_ls_matrix_dict=nc_ls_matrix_dict,demo_word=demo_word)

    ####
    # Compute the search space for each matrix extraction option.
    ####
    # The search space is how many candidates have to be evaluated
    # when finding parent/child word relationships.
    # The smaller the search space for a given word, the faster the
    # parent/child relationship determination.
    # compute_lookups() calculates this using the number of rows in each of the different matrices and sub-matrices

    wg_lu_df = compute_lookups(wg_df=wg_df,
                               n_char_matrix_dict=n_char_matrix_dict,
                               single_letter_matrix_dict=single_letter_matrix_dict,
                               letter_selector_matrix_dict=letter_selector_matrix_dict,
                               nc_ls_matrix_dict=nc_ls_matrix_dict)
    
    # write this to disk
    write_data_to_sqlite(df=wg_lu_df, table_name='word_group_lookup_counts',
                         db_path=db_path, db_name=db_name)

    ####
    # Esimate total number of pairs
    ####

    # how many parent/child relationships are there?
    # let's estimate the number of anagrams by assuming that the number of
    # parent/from words is a function of word length.
    # estimate_total_pairs() estimates the total number of from/to word pairs
    # the reason for estimating the upper bound is that it is both just interesting
    # to know but it also means that we can use the estimated values to allocate an
    # object in memory as opposed to incrementally appending to a list - this is faster
    # the object in memory is a NumPy Array that will store integers: from word group id | to word group id

    n_possible_anagrams, agg_pos_df = estimate_total_pairs(
        wg_df=wg_df, letter_selector_matrix_dict=letter_selector_matrix_dict)

    # save this to disk for future reference
    write_data_to_sqlite(df=agg_pos_df, table_name='n_possible_anagrams', db_path=db_path, db_name=db_name,
                         if_exists_option='replace',
                         index_option=False, verbose=True)


if __name__ == "__main__":

    run_part_02(db_path=rc.db_path, db_name=rc.db_name,
           data_output_file_path=rc.data_output_file_path,
           n_subset_letters=3)

    # wow. So, based on this analysis of the different
    # matrix extraction options using the word 'achiever':
    # options 5 and 6 are the fastest, each over 100 times faster than option 1
    # option 4 - just using the single least common letter - is 10X faster than option 1
    # and 6X faster than option 3 - using the starting the letter of the word.

#!/usr/bin/env python
# coding: utf-8
# Find anagrams - Part 04
# Run part 01, part 02, and part 03
# Mike Babb
# babb.mike@outlook.com


# standard libraries
from time import perf_counter_ns

# external libraries
# import numpy as np
# import pandas as pd

# custom libraries
import _run_constants as rc
from part_00_file_db_utils import compute_total_time
from part_01_structure_data import run_part_01
from part_02_demonstrate_extraction_timing_techniques import run_part_02
from part_03_generate_and_store_anagrams import run_part_03


def run_part_04(in_file_path: str, in_file_name: str, base_output_file_path: str, db_path: str,
                db_name: str, data_output_file_path: str, matrix_extraction_option: int,
                n_subset_letters: int, letter_subset_list: None, write_data: bool):
    
    # Part 01
    run_part_01(
        in_file_path=in_file_path,
        in_file_name=in_file_name,
        base_output_file_path=base_output_file_path,
        db_name=db_name,
    )

    # Part 02
    run_part_02(db_path=db_path, db_name=db_name,
                data_output_file_path=data_output_file_path,
                n_subset_letters=n_subset_letters)

    # Part 03
    run_part_03(matrix_extraction_option=matrix_extraction_option, n_subset_letters=n_subset_letters, letter_subset_list=letter_subset_list,
                write_data=write_data, db_path=db_path, db_name=db_name, in_file_path=in_file_path)


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

    matrix_extraction_option = 5

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
    run_part_04(in_file_path=rc.IN_FILE_PATH, in_file_name=rc.IN_FILE_NAME, base_output_file_path=rc.BASE_OUTPUT_FILE_PATH,
                db_path=rc.DB_PATH, db_name=rc.DB_NAME, data_output_file_path=rc.DATA_OUTPUT_FILE_PATH,
                matrix_extraction_option=matrix_extraction_option, n_subset_letters=n_subset_letters,
                letter_subset_list=None, write_data=False)

    compute_total_time(total_time_start=total_time_start)

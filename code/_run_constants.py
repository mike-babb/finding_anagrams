#!/usr/bin/env python
# coding: utf-8
# Mike Babb
# babb.mike@outlook.com
# Find Anagrams: Part 00: define run constants


# standard libraries
import os

# external libraries

# custom libraries

# path and name of input data
in_file_path = "/git/finding_anagrams/data/"
in_file_name = "words.txt"

# output paths
base_output_file_path = "/project/finding_anagrams"
data_output_file_path = os.path.join(base_output_file_path, 'data')
tabulation_output_file_path = os.path.join(base_output_file_path, 'tabulations')

# words
word_output_file_path = os.path.join(base_output_file_path, 'words')

# database name
db_path = data_output_file_path
db_name = "words.db"
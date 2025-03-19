#!/usr/bin/env python
# coding: utf-8
# Find Anagrams: run constants
# Mike Babb
# babb.mike@outlook.com


# standard libraries
import os

# external libraries

# custom libraries

# path and name of input data
IN_FILE_PATH = "/git/finding_anagrams/data/"
IN_FILE_NAME = "words.txt"

# output paths
BASE_OUTPUT_FILE_PATH = "/project/finding_anagrams"
DATA_OUTPUT_FILE_PATH = os.path.join(BASE_OUTPUT_FILE_PATH, 'data')
TABULATION_OUTPUT_FILE_PATH = os.path.join(BASE_OUTPUT_FILE_PATH, 'tabulations')

# words
WORD_OUTPUT_FILE_PATH = os.path.join(BASE_OUTPUT_FILE_PATH, 'words')

# database name
DB_PATH = DATA_OUTPUT_FILE_PATH
DB_NAME = "words.db"
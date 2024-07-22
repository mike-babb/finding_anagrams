# constants used across the various files for finding anagrams
# this cuts down on the total number of lines of code AND increases code re-useability
# 2024 06 06

# standard libraries
import os

# external

# custom


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
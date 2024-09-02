#!/usr/bin/env python
# coding: utf-8
# Mike Babb
# babb.mike@outlook.com
# Find Anagrams: Part 1: Structure the data

# standard libraries
import collections
import os
import string
from time import perf_counter_ns

# external libraries
import numpy as np
import pandas as pd

# custom
import _run_constants as rc
from part_00_file_db_utils import *


def import_and_format_words(in_fpn: str):
    # use pandas to load the data
    print("...Reading in list of words...")
    word_df = pd.read_csv(
        filepath_or_buffer=in_fpn, sep=",", header=None, names=["word"]
    )

    # how many words are we working with?
    n_words = len(word_df)
    print("...found", "{:,}".format(n_words),
          "words to find relationships for...")

    # convert the only column to a string - just to be safe.
    # 'nan' is a word in the dictionary. nan is an internal python value.
    # same with 'null'
    word_df["word"] = word_df["word"].astype(str)

    # create lower case values of the words
    word_df["lcase"] = word_df["word"].str.lower()

    # remove hyphens
    word_df["lcase"] = word_df["lcase"].str.replace("-", "")

    # and now drop duplicates, based on the lowercase version of each word
    word_df = word_df.drop_duplicates("lcase")

    # find word length
    word_df["n_chars"] = word_df["lcase"].str.len()

    # extract the first letter of each word
    word_df["first_letter"] = word_df["lcase"].str[:1]

    # create a word id
    word_df["word_id"] = range(0, word_df.shape[0])

    return word_df


def compute_word_group_id(word_df: pd.DataFrame) -> pd.DataFrame:
    print("...computing the word group id...")
    # add a hash id to capture the sorted letters in each word
    word_df["hash_id"] = word_df["lcase"].map(
        lambda x: hash("".join(sorted(x))))

    # create a dataframe of the unique, hashed values
    word_id_hash_id_df = word_df["hash_id"].drop_duplicates().to_frame()

    # add a unique id
    word_id_hash_id_df["word_group_id"] = range(0, word_id_hash_id_df.shape[0])

    # join to get the word group id and the hash id
    word_df = pd.merge(left=word_df, right=word_id_hash_id_df)

    # drop the hash id, no longer needed
    word_df = word_df.drop(labels="hash_id", axis=1)
    # use dictionary comprehension to store the letter
    # we'll import the letters from string.ascii_lowercase
    # index of the letter for fast look ups
    letter_dict = {l: li for li, l in enumerate(string.ascii_lowercase)}

    # get the unique letters in each word and then sort those letters
    word_df["letter_group"] = word_df["lcase"].map(
        lambda x: "".join(sorted(set(x))))
    return word_df, letter_dict


def count_letter_frequency(word_df: pd.DataFrame):
    print("...counting letter frequencies...")
    # several versions of the anagram determination technique require subsetting by letters in each word.
    # generate those data and use a ranking technique to help with anagram group identification

    # use a counter object to count the total occurences of each letter AND
    # a counter to count the number of words that feature each letter
    # counters are a special type of dictionary.
    # https://docs.python.org/3/library/collections.html#collections.Counter
    # very fast
    total_letter_counter = collections.Counter()
    single_letter_counter = collections.Counter()

    # enumerate each word and then each letter
    for curr_word in word_df["lcase"].to_numpy():
        total_letter_counter.update(list(curr_word))

    for curr_letter_group in word_df["letter_group"].to_numpy():
        single_letter_counter.update(list(curr_letter_group))
    # make a dataframe from the counter object and then order from low to high
    letter_count_df = pd.DataFrame.from_dict(
        data=total_letter_counter, orient="index", columns=["total_letter_count"]
    ).reset_index(names=["letter"])
    letter_count_df["single_letter_count"] = letter_count_df["letter"].map(
        single_letter_counter
    )

    # compute the total letter rank and the single_letter_count
    letter_count_df["total_letter_rank"] = (
        letter_count_df["total_letter_count"].rank(ascending=False).astype(int)
    )
    letter_count_df["single_letter_rank"] = (
        letter_count_df["single_letter_count"].rank(
            ascending=False).astype(int)
    )

    # sort by letter count
    letter_count_df = letter_count_df.sort_values(
        by="total_letter_count", ascending=False
    )

    letter_count_df["total_letter_percent"] = (
        letter_count_df["total_letter_count"]
        / letter_count_df["total_letter_count"].sum()
    )
    # note the denomiantor - we are computing which words have a letter, most words have multiple letters.
    letter_count_df["single_letter_percent"] = (
        letter_count_df["single_letter_count"] / word_df.shape[0]
    )
    # join with the count of words that start with a focal letter.
    fl_count_df = (
        word_df["first_letter"]
        .groupby(word_df["first_letter"])
        .agg(np.size)
        .to_frame(name="first_letter_word_count")
        .reset_index(names=["letter"])
    )

    fl_count_df["first_letter_word_percent"] = (
        fl_count_df["first_letter_word_count"]
        / fl_count_df["first_letter_word_count"].sum()
    )

    fl_count_df["first_letter_rank"] = (
        fl_count_df["first_letter_word_count"].rank(
            ascending=False).astype(int)
    )

    # joins
    letter_count_df = pd.merge(left=letter_count_df, right=fl_count_df)

    # sort the records
    letter_count_df = letter_count_df.sort_values(by="letter")

    # reorder columns: count, percent, rank
    col_names = [
        "letter",
        "total_letter_count",
        "single_letter_count",
        "first_letter_word_count",
        "total_letter_percent",
        "single_letter_percent",
        "first_letter_word_percent",
        "total_letter_rank",
        "single_letter_rank",
        "first_letter_rank",
    ]

    letter_count_df = letter_count_df[col_names]
    print("...creating letter groups...")
    # place the letter and its rank into a dictionary
    # as well as the rank and the corresponding letter
    # {'k':21, 21:'k'}
    letter_count_rank_dict = {}
    for cl, clr in zip(letter_count_df["letter"], letter_count_df["total_letter_rank"]):
        letter_count_rank_dict[cl] = clr
        letter_count_rank_dict[clr] = cl

    # write a function to order the unique letters in each word by
    # least common letter to most common letter
    def get_least_common_letters(letter_group):
        if len(letter_group) == 1:
            lcl = letter_group
        else:
            # ranking of each letter
            rank_list = [
                letter_count_rank_dict[curr_letter] for curr_letter in letter_group
            ]
            # sort the ranking
            rank_list = sorted(rank_list, reverse=True)
            # generate the letters sorted by rank
            rank_list = [
                letter_count_rank_dict[curr_letter] for curr_letter in rank_list
            ]
            # concatenate the letters together
            lcl = "".join(rank_list)
        return lcl

    # extract letters by ranking
    word_df["letter_group_ranked"] = word_df["letter_group"].map(
        get_least_common_letters
    )
    return word_df, letter_count_df


def generate_character_matrix(word_df: pd.DataFrame, letter_dict: dict) -> np.ndarray:
    # count the occurences of each letter in each word and store the results in a matrix named char_matrix
    # populate the char_matrix and the word_id dictionary
    # Apply a function to each row in the dataframe to accomplish this
    # https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.DataFrame.apply.html
    print("...populating the character matrix...")

    # Upon intialization, the char_matrix has shape (234370, 26) and is zero-filled.
    # Each row in the char_matrix corresponds to a word.
    # The char_matrix is 26 columns wide. Each column corresponds to a letter.
    # ['a','b','c','d','e','f','g','h','i','j','k','l','m','n','o','p','q','r','s','t','u','v','w','x','y','z']
    # Each cell is a count of the number of times each letter occurs in each word.
    # the entry for emit (as do the entriees for time, mite, item) has the following value:
    # [0, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0]
    # we need to find all words that have matching rows with at least these values.
    # for example, 'terminator'.
    # ['a','b','c','d','e','f','g','h','i','j','k','l','m','n','o','p','q','r','s','t','u','v','w','x','y','z']
    # [1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1, 1, 1, 0, 0, 2, 0, 2, 0, 0, 0, 0, 0, 0]
    # the letters in the word 'emit' is a subset of the letters in the word 'terminator'

    # the zero-filled matrix will be populated once the
    # fill_char_matrix() function is applied to the word_df
    char_matrix = np.zeros(shape=(len(word_df), 26), dtype=int)

    def fill_char_matrix(row):
        # get a word from the current row
        curr_word = row["lcase"]
        ri = row["word_id"]  # row index / word index
        # populate the char matrix
        for i_letter, letter in enumerate(curr_word):
            if letter in letter_dict:
                # find the corresponding column index of that letter
                li = letter_dict[letter]
                # increment the count of letters in the current row and current column
                char_matrix[ri, li] += 1
        return None

    # catch the output from the function and delete
    output = word_df.apply(fill_char_matrix, 1)
    del output
    return char_matrix


def create_word_group_df(word_df: pd.DataFrame) -> pd.DataFrame:
    print("...creating the word group dataframe...")
    # drop duplicates based on the word group.
    # by default, this will only keep the first record and it will drop all others
    wg_df = word_df.drop_duplicates(subset=["word_group_id"]).copy()
    # count how many times each word group appears - a word group is a perfect anagram.
    word_group_counter = collections.Counter(word_df["word_group_id"])

    wg_df["word_group_count"] = wg_df["word_group_id"].map(word_group_counter)
    return wg_df


def save_objects(
    char_matrix: np.ndarray,
    letter_dict: dict,
    word_df: pd.DataFrame,
    wg_df: pd.DataFrame,
    letter_count_df: pd.DataFrame,
    output_file_path: str,
    db_name: str,
) -> None:
    # save data to disk - first the char matrix and the letter dictionary
    # save the char matrix in the numpy format
    print("...saving the character matrix...")
    output_name = "char_matrix.npy"
    opn = os.path.join(output_file_path, output_name)
    np.save(file=opn, arr=char_matrix)

    # letter dictionary
    print("...saving the letter dictionary...")
    output_name = "letter_dict.pkl"
    save_pickle(file_path=output_file_path,
                file_name=output_name, obj=letter_dict)
    print("...saving tables to database...")
    # save the word df to sqlite db
    write_data_to_sqlite(
        df=word_df, table_name="words", db_path=output_file_path, db_name=db_name
    )
    # save the word_groups
    write_data_to_sqlite(
        df=wg_df, table_name="word_groups", db_path=output_file_path, db_name=db_name
    )

    # now, the word / letter count
    write_data_to_sqlite(
        df=letter_count_df,
        table_name="letter_count",
        db_path=output_file_path,
        db_name=db_name,
    )
    return None


def run_part_01(
    in_file_path: str, in_file_name: str, base_output_file_path: str, db_name: str
):
    # construct the input file path
    in_fpn = os.path.join(in_file_path, in_file_name)

    # paths to output directories
    output_file_path = os.path.join(base_output_file_path, "data")
    db_name = "words.db"

    # setup the data output path
    if os.path.exists(output_file_path):
        pass
    else:
        os.makedirs(output_file_path)
    # import the list of words as a pandas dataframe
    word_df = import_and_format_words(in_fpn=in_fpn)
    # compute the word group id and create the letter dict lookup
    word_df, letter_dict = compute_word_group_id(word_df=word_df)

    # count letter frequencies
    word_df, letter_count_df = count_letter_frequency(
        word_df=word_df
    )
    # build the character matrix
    char_matrix = generate_character_matrix(
        word_df=word_df, letter_dict=letter_dict)
    # create the word group dataframe - removes all exact word groups
    wg_df = create_word_group_df(word_df=word_df)
    # save everything to disk
    save_objects(
        char_matrix=char_matrix,
        letter_dict=letter_dict,
        word_df=word_df,
        wg_df=wg_df,
        letter_count_df=letter_count_df,
        output_file_path=output_file_path,
        db_name=db_name,
    )


if __name__ == "__main__":

    # start a timer to record the entire operation
    total_time_start = perf_counter_ns()

    run_part_01(
        in_file_path=rc.in_file_path,
        in_file_name=rc.in_file_name,
        base_output_file_path=rc.base_output_file_path,
        db_name=rc.db_name,
    )

    compute_total_time(total_time_start=total_time_start)

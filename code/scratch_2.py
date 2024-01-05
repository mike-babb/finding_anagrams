print("here")
# initialize counters to count the number of to (child words) from a focal word.
# we could do this in post-processing, but the data are already in memory and it's a simple
# calculation to make.
# we want to minimize the number of trips through our data.

# the number of candidate words examined for each focal word

# a list to hold the dataframes generated for each letter
proc_time_df_list = []

# subset the list of leters
if letter_subset_list:
    letters = letter_subset_list[:]
else:
    letters = sorted_first_letters

anagram_pair_count = 0
# use numpy to pre-allocate an array that will be updated while enumerating.
# this eliminates list.append() calls

output_list = np.full(shape=(n_possible_anagrams, 2), fill_value=-1, dtype=int)

wg_count = 0

for curr_letter in letters:
    # enumerate by each letter
    # this isn't absolutely necessary, we could just enumerate by word id,
    # but for testing and development, letters are a handy way to chunk up the data.

    # this dictionary will store the calculations for each letter
    proc_time_dict = {}

    # the list of words that start with the focal letter
    curr_wg_df = wg_df.loc[wg_df["first_letter"] == curr_letter, :]

    # sort the dataframe by n_chars and letter_selector, if it exists.
    # this will cut down on dictionary lookups for matrix_extraction_types 3 and 4.
    curr_wg_df = curr_wg_df.sort_values(by=["n_chars", "letter_selector"])
    curr_word_group_id_list = curr_wg_df["word_group_id"].to_numpy()
    curr_nc_ls_tuple_list = curr_wg_df["nc_ls_tuple"].to_numpy()

    wg_count += len(curr_word_group_id_list)

    n_curr_words = "{:,}".format(curr_wg_df.shape[0])
    print(
        "...finding parent anagrams for",
        n_curr_words,
        "words that start with",
        curr_letter,
    )

    # enumerate by word id, working with integers is faster than words
    for wg_id, nc_ls_tuple in zip(curr_word_group_id_list, curr_nc_ls_tuple_list):
        # start timing to record processing for each word
        s_time = datetime.datetime.now()

        # get the current word length, from the word id
        # to_word, to_word_length, curr_first_letter, clg, clgr = word_dict[word_group_id]
        to_word_length = word_dict[wg_id][1]

        # get the tuple associated with the word id
        # much faster to look up stored values for the hash value than it is to
        # only look up if the hash value has changed

        # get the possible candidate word_group_ids and char matrix
        ####
        ## TODO: CODE
        # go with option 4 for now
        outcome_word_id_list = get_values_n_char_letter_selector(
            wg_id=wg_id, nc_ls_tuple=nc_ls_tuple, nc_ls_matrix_dict=nc_ls_matrix_dict
        )

        # how many candidates?
        n_possible_words = 0

        # if the outcome is greater than or equal to zero, then the current word is an
        # anagram of the other word
        # a value  >= 0 means that the current word contains the exact same number of focal letters
        # mite --> time or miter --> time
        # a value >= 1 means that current word contains at least the same number of focal letters
        # terminator --> time
        # a value of <=-1 means that the current word does not have the
        # correct number of letters and is therefore not an anagram.
        # trait <> time

        # number of parent words found
        n_from_words = outcome_word_id_list.shape[0]

        if n_from_words > 1:
            # we have matches
            # the focal word

            # enumerate the from/parent words
            new_anagram_pair_count = anagram_pair_count + n_from_words
            # the from words
            # print(anagram_pair_count)
            # print(new_anagram_pair_count)
            # print(len(outcome_word_id_list))
            # print(output_list.shape)
            output_list[
                anagram_pair_count:new_anagram_pair_count, 0
            ] = outcome_word_id_list[:, 0]

            # the to word
            output_list[
                anagram_pair_count:new_anagram_pair_count, 1
            ] = outcome_word_id_list[:, 0]

            # set the anagram pair count
            anagram_pair_count = new_anagram_pair_count

        del outcome_word_id_list

        # record the time for the word
        e_time = datetime.datetime.now()
        p_time = e_time - s_time
        p_time = p_time.total_seconds()

        proc_time_dict[wg_id] = (p_time, n_from_words, n_possible_words)

    # create a dataframe from the proc_time_dict
    proc_time_df = pd.DataFrame.from_dict(data=proc_time_dict, orient="index")
    proc_time_df = proc_time_df.reset_index()
    proc_time_df.columns = [
        "word_group_id",
        "n_seconds",
        "n_from_word_groups",
        "n_candidates",
    ]

    # display processing time for the current letter
    total_proc_time = round(proc_time_df["n_seconds"].sum(), 2)
    print(
        "...finding parent anagrams for",
        curr_letter,
        "words took",
        total_proc_time,
        "seconds...",
    )

    proc_time_df_list.append(proc_time_df)

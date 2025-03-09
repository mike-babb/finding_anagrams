# Finding Anagrams: v2.0
# March 1, 2025
Find and store from/to word relationships using Python, NumPy, Pandas, and SQLite

# Introduction
This workshop uses python and the NumPy, Pandas, and SQLite libraries to discover and store anagrams found in a list of English words. The main focus of this workshop is to show how NumPy's arrays and other python objects can be used to Extract, Transform, and Load (ETL) data into a SQLite database. In addition, there is an R-script showcasing how to use R to connect to a SQLite database, gather data, and create several simple visualizations.

While version 1.0 of this workshop made use of individual words, version 2.0 makes use of word groups. There are approximately 234K unique words and approximately 216K unique word groups in the initial dataset. A word group is defined as a group of words all containing the same letters: 'emit', 'item', 'mite', and 'time', for example. 

This workshop is built for beginners - people very new to python - and progresses to demonstrations of advanced data processing techniques. To that end, there are six different data processing techniques - referred to as matrix extraction options throughout the workshop - that demonstrate how processing the same data can take 90+ minutes or as little five minutes. Each of the six different processing techniques produce the same output: the discovery of over 73M parent/child word pairs. The difference between each of the processing techniques is how the data processing and retrieval are subdivided. 

Where applicable, there are Jupyter Notebooks and python scripts that demonstrate the same process flow. The notebooks are more interactive while the python scripts can be run from the command line. The notebooks for parts 1, 2, and 3 make use of functions written in the corresponding scripts for parts 1, 2, and 3. In general, the notebooks and scripts start out less complex and become more complex. For example, part_01 features more interactivity (calls to `print` and `pd.DataFrame.head()`) and descriptions of operations and objects(dictionaries and arrays, for example) than part_03. Each part builds upon the previous part(s). 

# THE TECHNIQUE - SUBDIVIDING A MATRIX
Broadly, this workshop finds parent/child word pairs by representing words as numeric vectors and performing various vector and matrix operations on each word-stored-as-numeric vector. The differences in processing time orginate from reducing the number of matrix comparisons to be made (in effect, reducing the size of the search space). For example, comparing a [1, 26] vector with another [1, 26] vector is a lot faster than comparing a [1, 26] vector with a [500, 26] matrix. While the time it takes to perform a single vector comparison operation is trivial, ~216K vector comparison operations is less so. 

Each of the six different matrix extraction options implements a different way of sub-dividing a 215,842 row by 26 column matrix. Referred to as the `char_matrix` throughout this document. Each row represents a different word and each column indicates the number of occurences of a letter in the ordinal position. By equating the letter 'a' with 0 and the letter 'z' with 25, we can replace each letter in a word with each letter's ordinal position in the the English alphabet. For example, the word `achiever` features the following letters by zero-index position:  
```python
[0, 2, 7, 8, 4, 21, 4, 17]
```  
By replacing the ordinal positions of each letter with the count of each letter in each letter's oridinal position, we can represent the word `achiever` as a numeric vector with length 26:  
``` python
[1, 0, 1, 0, 2, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 0]
```  
Doing this for each word enables the rapid comparison of a focal word with *all other words*. This is accomplished by subtracting the focal vector from the `char_matrix`. Calling [`numpy.min(axis=1)`](https://numpy.org/doc/stable//reference/generated/numpy.min.html) generates a vector of length ~216K with the smallest value in each row. The resulting vector features a combination of positive, negative, and zero values. Negative values indicate that the focal word has letters not found in other words. A value GTE zero means that the letters in the focal word are found in other words. A boolean operation is then used to select which indices are greater than or equal to 0. These indices correspond to parent words of the focal word. For example, `archdetective` is a parent word of `achiever`:
``` python
archdetective = np.array([1, 0, 2, 1, 3, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 2, 0, 1, 0, 0, 0, 0])
achiever = np.array([1, 0, 1, 0, 2, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 0])
archdetective - achiever
>> array([0, 0, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 0, 0, 0, 0, 0, 0])
```

Each matrix extraction option is described in greater detail below. Where applicable, graphics are included to illustrate the intuition and reasoning behind each technique. 

## Matrix Extraction Option 1 - No subdivision of the `char_matrix`
By subtracting each row (a focal word) of the `char_matrix` from every other row of the `char_matrx` and finding non-negative values for each operation (as described above), the parent words for a focal word are identified. This is the simplest option to implement and the slowest because each word is compared against 215,842 other words. This effectively peforming ~216K**2 comparison. Accordingly, this option takes approximately 90 minutes to complete. While the `char_matrix` makes each word have a standard output, there are latent structures in our list of words that we can leverage. To that end, [part_01_structure_data.ipynb](/code/part_01_structure_data.ipynb) uncovers these latent structures: the number of characters in each word and the frequency of each character in our list of words. Matrix extraction options 2 through 6 leverage these latent structures by splitting the `char_matrix` into smaller matrices. 

## Matrix Extraction Option 2 - Subdivision by word length
A logical starting point for dividing the `char matrix` is by character length. This produces 24 seperate matrices. Words that are *N* characters in length are only compared to other words that are at least *N* characters in length. For example, the word 'achiever' is 8 characters in length and there are 170,056 words are at least 8 characters in length. This plot shows the number of candidates for each word length.  
![Matrix Extraction Option 2: Number of Candidates](/graphics/meo_2_ss.png)  
Not surprisingly, as the number of the characters in a word increases, the number of candidate words decreases. This option takes approximately 52 minutes to complete. 

## Matrix Extraction Option 3 - Subdivision by first letter
The `char_matrix` is subdivided by each letter of the alphabet: 26 seperate matrices. The list of candidate words is generated for a focal word if the first letter of the focal word is found anywhere in each of the condidate words. For example, the word 'achiever' begins with the letter 'a' and it is compared against the 133,001 words that contain the letter 'a'. Not all letters are used at the same frequency: the plot below showcases the number of candidates by starting letter.  
![Matrix Extraction Option 3: Number of Candidates](/graphics/meo_3_ss.png)  
We can see from the plot that there are fewer words that feature the letter 'q' or the letter 'j' than words that feature the letter 'a' or the letter 't'. By leveraging these differences, matrix extraction option 3 takes approximately 31 minutes to complete. Matrix extraction option 4 more effectively leverages this distribution in letter frequency. 

## Matrix Extraction Option 4: Subdivision by single-least common letter.
The `char_matrix` is again subdivided by each letter of the alphabet: 26 seperate matrices. This is the same division as option 3, but the least common letter in each word is used to suggest candidates. The plot above gives some indication of letter ranking, but a better way to express the ranking is to compute the total number of occurences of each letter across all words. The graph below showcases the count of each letter across all 215,842 words, plotted in descending order:  
![Letter Frequency](/graphics/meo_4_letter_rank.png)  
This chart should be somewhat familiar to anyone who has investigated the frequency distribution of letters in the English language. The letter 'e' is the most commonly used letter while the letter 'j' is the least commonly used letter. With matrix extraction option 3, for every word that starts with 'a', the search space includes ALL words with the letter 'a'. For the word 'achiever', the search space using matrix extraction option 3 is 133,001 words and the search space for matrix extraction 4 is 18,391 words. The search space for the word 'achiever' using matrix extraction option 4 is 7.2 times smaller than the search space for the word 'achiever' using matrix extraction 3. This is because the least common letter in 'achiever' is the letter 'v'. Using only the least common letter in each word to winnow down the search space for each word decreases processing to 17 minutes. A 82-percent improvment just by leveraging an innate component in the data. 

One way of expressing the relationship between the starting letter of a word and the least common letter in the word and therefore the reduction in procesing time is to compute the distribution of words by starting letter and least common letter. The heatmap below showcases this distribution:  
![First letter and starting letter commonality](/graphics/meo_4_first_letter_starting_letter.png)  
To highlight interesting trends, cells framed in yellow feature a frequency greater than 1,000. About 20% of cells feature frequencies greater than 1,000. Cells in the diagonal are framed in green. The row totals on the left indicate the number of words that start with a given letter. For example, there are 16,513 words that start with the letter 'a'. For words that start with the letter 'a', 869 of those words feature a least common letter of 'v'. Using matrix extraction option 4 means that there will be 869 checks of the 18,391 word search space (words that feature the letter 'v') as opposed to 869 checks of the 133,001 word space (words that feature the letter 'a') using matrix extraction option 3. For words that start with the letter 'r', 7,558, there are only 12 words that feature the letter 'r' as the least common letter. This means that there are 12 checks of a search space that includes 118,135 words as opposed to 7,558 checks of the 118,135 word search space. Lower values indicate a more rare pairing of starting letter and least common letter indicating fewer checks of a given search search space. We can graph the relationship between the reduction in the size of the search space by starting letter and the least common letter as follows. 
![Reduction in search space between option 3 and option 4](/graphics/meo_4_letter_lookup_diff.png).  
By leveraging least common letters, we see large average reductions for the vowels and the letters 'r', 's', and 't'. There is no reduction for the letters 'j' and 'q' as those letters are used so infrequently. This reduction in comparisons of large search spaces is why matrix extraction option 4 is 14 minutes faster than matrix extraction option 3: from 31 minutes to 17 minutes.

## Matrix Extraction Option 5: Matrices are sub-divided by groups of least common letters. 
Option 4 showed quite an improvement over option 3. And this was accomplished by using a single least common letter in a focal word. Option 5 uses groups of least common letters. Returning to the word 'achiever', the ranks of each letter are as follows: `[3, 10, 15, 2, 1, 20, 1, 5]`. Selecting the three least common - and unique - letters from the word 'achiever' we have the following: `['v', 'h', 'c']`. Based on this unique letter grouping - referred to as a letter selector for convenience - there are 489 candidate words. To put that in perspective, option 3 featured a search space of 133,001 letters, option 4 featured a search space of 18,391 words, and now option 5 features a search space of 489 words: 272 times smaller than option 3 and 38 times smaller than option 4. 

Repeating this process of selecting the three least common letters for each of the ~216K words, we can generate 2,387 unique letter selector groups:
* 26 One letter groups
* 111 Two letter groups
* 2,250 Three letter groups  

The letter selector groups range in size from a single word to over 145K words. We can get a better sense of the distribution of the sizes of the letter selector groups by examining the plot comparing the number of letter selector groups by the size of the letter selector group:  
![Letter selector difference](/graphics/meo_5_letter_selector_group_size.png)
For ease of interpretation, the x-axis is log-transformed. Most letter groups are small: 25-percent of the 2,387 distinct letter groups feature 340 words or fewer and 50-percent of the 2,387 letter groups feature 1,665 words or fewer. The average group size is a little over 7.4K words. Grouping by least common letters is an efficient way to sub-divide the initial `char_matrix`. In fact, it is so efficient that matrix extraction option 5 executes in under four minutes. This is over 7 times faster when compared to option 3 (31 minutes) and over 4 times faster than option 4 (17 minutes). And this is because of the reduction in the search spaces of candidate words. When compared with option 3, the average percent reduction in the search space of candidate words is [92-percent](/graphics/meo_5_letter_selector_lookup_diff.png).
  
## Matrix Extraction Option 6: Matrices are sub-divided by groups of least common letters and number of characters
Of the five previous matrix extraction options, option 5 is currently in first place. Can we improve on option 5? The answer is a resounding *"yes, but..."* More on that in a bit, but first the method behind option 6: a combination of word length and groups of least common letters. Option 6 performs additional subdivision by finding the set of words common between words that are at least *N* characters in length *and* the groups of least common letters. This generates 16,101 sub-matrices. Again, focusing on the word `achiever`, we can intersect the set of 489 words that feature the three least common letters of `['v', 'h', 'c']` with the set of candidate words that are at least 8 characters in length - 170,056 words - to produce a list of 449 candidate words. This process is repeated for all words. Just like for option 5, we can get a sense of the distibution of the search space by examining the sizes of the letter-selector-number-of-characters groups.   
![Letter selector difference](/graphics/meo_6_nc_ls_group_size.png)  

Again, note the log-transformation on the x-axis. While the general shapes of the distribution directly above and the graph of the distribution for [option 5](/graphics/meo_5_letter_selector_group_size.png) are similar, note the differences in the magnitude of the y-axis: for option 6, some of the largest groups are greater than 600 in number. The groups of letter-selector-number-of-characters range in size from a single word to over 145K words. The average group size is approximately 4.5K words and 50-percent of groups have a size of 789 or fewer. Effectively, with matrix extraction option 6, there are more, smaller groups of candidate words when compared to matrix extraction option 5. As the previous five matrix extraction techniques have shown, reductions in the search space lead to decreases in processing time. And because of this reduced search space, option 6 also completes in under 4 minutes.

So, why is the answer to "is matrix extraction option 6 faster than matrix extraction option 5" a resounding "yes, but..."? There are several reasons for this and to unpack that qualified statement, let's focus on the word 'achiever' and the average time it takes to find the parent words for 'achiever' for 1000 runs of each matrix extraction technique:

|Matrix Extraction Technique| Total Seconds| Average Seconds|
|------|-----|-----|
|Option 1|26.531|0.026531|
|Option 2|21.912|0.021912|
|Option 3|16.238|0.016238|
|Option 4|2.607|0.002607|
|Option 5|0.228|0.000228|
|Option 6|0.201|0.000201|

When comparing extraction times for a single word, 'achiever', matrix extraction option 6 *IS* faster. And because those numbers are orders of magnitude different, computing the ratio of each extraction technique's execution time to each other extraction technique's execution time will better showcase the differences in execution time. The heatmap below visualizes those ratios. 

!['achiever' comp times](/graphics/meo_all_comp_times.png)  

The bottom diagonal is not shown as those numbers are the inverse of the top diagonal. Most striking is that both option 5 and 6 are over 100 times faster than option 1! Using the least common letter, option 4, is 11 times faster than using the first letter of a word. Examining this heat map, we can see that matrix extraction technique 6 is 10% faster than matrix extraction technique 5. But again, this is just for a single word. 

Comparing the total processing time for all words for all techinques we have the following:

|Matrix Extraction Technique| Hours| Minutes| Seconds|
|------|------|------|------|
|Option 1|1|31|3.43|
|Option 2|0|52|15.51|
|Option 3|0|30|32.36|
|Option 4|0|16|48.57|
|Option 5|0|2|57.23|
|Option 6|0|3|36.32|
 
And again, because those numbers are orders of magnitude different, we can compute the ratio of processing times as follows:

![all words proc times](/graphics/meo_all_comp_times_all_words.png)  

Looking at the ratios of the different processing times, we see that option 5 is approximately 34 times faster than option 1 while option 6 is approxiately 25 times faster than option 1. So, why is matrix extraction option 6 slower than matrix extraction 5? In short, the number of keys used to correspond to the sub-matrices. This, too, is a search space. There are 2,387 sub-matrices created for matrix extraction option 5 and 16,101 matrices created for matrix extraction option 6: approximately 6.7 times as many sub-matrices. When processing each word, there are now an initial 16,101 comparisons to make (to find the right sub-matrix) before making the comparisons that find the parent words for a focal word. These extra comparisons add to the time it takes to find the parent words of a given word. By carefully curating the number and size of the sub-matrices, we can reduce the processing time. Below is a graphic featuring a boxplot of the distribution of sub-matrix size for options 2 through 6. Option 1 is omitted as there is no sub-matrix.
![sub-matrix size](/graphics/meo_all_box_plot_distribution.png)  
As the sizes of sub-matrices decrease, the number of sub-matrices increase. This has diminishing returns as can be seen in the [previously mentioned heatmap](/graphics/meo_all_comp_times_all_words.png) comparing the ratios of extraction above. To  urther illustrate this concept of diminishing returns, I will suggest setting `n_subset_letters = 4` in  [part_02_demonstrate_extraction_timing_techniques.ipynb](/code/part_02_demonstrate_extraction_timing_techniques.ipynb) or [part_02_demonstrate_extraction_timing_techniques.py](/code/part_02_demonstrate_extraction_timing_techniques.py) and running the notebook or script.

As a final comment, up until this point, I have not have mentioned any timing related to generating the sub-matrices. For options 2 through 4, it takes about 2 seconds to generate the sub-matrices. Generating the sub-matrices for option 5 takes about 10 seconds and it takes about a minute to generate the sub-matrices for option 6. In other words, for option 5, an extra 8 seconds of pre-processing results in a time savings of 88 minutes when compared with matrix extraction option 1.

# AN ETL PIPELINE
This section describes each script in the ETL pipeline and the various scripts used to analyze different processing times. Parts 01, 02, and 03 form the ETL pipeline while other parts feature various components for code reuse and analyses.

## SETUP
The scripts in this portion define contstants and functions used throughout subsequent processes.
* `_run_constants.py` - Input and output file names and paths. All subsequent scripts reference the paths defined in this file. Paths and names only need to be set once, in this file. 

## UTILIES
* `part_00_file_db_utils.py` - Code reuse for parts 1 through 7. These are mostly I/O and utility functions.
* `part_00_process_functions.py` - Code reuse for parts 1 through 7. These functions peform the data processing and are called in subsequent parts. The reason for this structure is for code reuse, efficient optimization and debugging, and generally writing less code. Effectively, we can efine the function once and import it.

## EXTRACT
* `part_01_structure_data.ipynb` and `part_01_structure_data.py`
Load a list of words, perform several calculations and data creation steps, and store the results. This step creates the objects that faciliate the different extraction techniques.

## TRANSFORM
* `part_02_demonstrate_extraction_timing_techniques.ipynb` and `part_02_demonstrate_extraction_timing_techniques.py`
The scripts in this section demonstrate the techniques - and crucial differences - in the different matrix extraction techniques.

## LOAD
* `part_03_generate_and_store_anagrams.ipynb` and 
`part_03_generate_and_store_anagrams.py*`
This script and notebook find the parent words for all words in the list of focal words using one of the user specified extraction options. The data can optionally be written to a SQLite DB.

Each of the six techniques in part_03 will produce the same data using different data structuring and access techniques. 

## ETL
* `part_04_run_parts_01_02_and_03.ipynb` and `part_04_run_parts_01_02_and_03.py` can be used to run parts 01, 02, and 03 from one notebook / script. This is helpful in showcasing the overall time it takes to run one matrix extraction technique.

## QUERY

* `part_05_query_anagram_database.ipynb` - query the anagram database. Shows how to crosswalk from `word_group_id` to `word`.
* `part_06_add_database_indices.ipynb` - adds indices to tables in the anagarm database. This showcases how database indices can dramatically speed up data retrieval times: from minutes to query for a single word to sub-second access. This notebook only needs to be run afterthe `anagram_groups` table is (re)created. 

## ANALYSIS
* `part_07_build_a_graph.ipynb` - build a graph of the parent/child word relationships after for the word `terminator`. 

# VISUALIZATION
* `part_08_plot_counts_of_search_spaces.ipynb` - use [`matplotlib`](https://matplotlib.org/) and [`seaborn`](https://seaborn.pydata.org/) to plot counts of search spaces and processing times. This file generates the `meo_*_.png` images.

* `part_08_visualize_processing_time.R` - Make graphics using [`R`](https://www.r-project.org/)! Because the data generated in parts 01, 02, and 03 are stored in a SQLiteDB, we can connect to the database using the [RSQLite](https://rsqlite.r-dbi.org) library and in turn load the data as a [data.table](https://rdatatable.gitlab.io/data.table/) object. From there, we can then use the [ggplot2](https://ggplot2.tidyverse.org/) library to produce several plots showcasing different aspects of the processing times. This graphic below showcases the total time it takes to find all parent words by letter length:
![total time by word length](/graphics/tot_proc_time_by_word_length.png). Additional graphics generated in R include the following:


avg_from_to_words_by_word_length_v2.png
avg_proc_time_by_word_length.png
avg_search_candidates_by_word_length_v2.png
number_of_candidates_to_words_by_word_length.png
tot_proc_time_by_word_length.png




# call graphs


# profiling
run_part_01_structure_data.bat
run_part_02_demonstrate_extraction_timing_techniques.bat
run_part_03_generate_and_store_anagrams.bat








### EXTRA VISUALS
two graphs: one by word length, one by starting character
For each technique: the average difference between the search space and the number of candidates

We also need to compare the reduction in search when compared to MEO 1


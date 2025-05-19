# Finding Anagrams: v2.0
## March 27, 2025
Find and store parent/child word relationships using Python, NumPy, Pandas, and SQLite

# Introduction
This workshop uses [python](https://www.python.org/downloads/) and the [NumPy](https://numpy.org/), [Pandas](https://pandas.pydata.org/), and [SQLite](https://docs.python.org/3/library/sqlite3.html) libraries to discover and store parent/child word relationships found in a list of English words. The main focus of this workshop is to show how NumPy's arrays and other python objects can be used to [Extract, Transform, and Load (ETL)](https://en.wikipedia.org/wiki/Extract,_transform,_load) data into a SQLite database. In addition, there is an R-script showcasing how to use the [R programming language](https://www.r-project.org/) to connect to a SQLite database, use the data generated in python, and create several simple visualizations.

A previous version of this workshop made use of individual words. This version makes use of word groups. A word group is defined as a group of words (an [anagram](https://en.wikipedia.org/wiki/Anagram)!) all containing the same letters: `emit`, `item`, `mite`, and `time`, for example. In the supplied [dataset](/data/words.txt), there are approximately $234K$ unique words and approximately $216K$ unique word groups in the initial dataset. 

This workshop is built for people new to python and progresses to demonstrations of advanced data processing techniques. To that end, there are six different data processing techniques - referred to as matrix extraction options throughout the workshop - that demonstrate how processing the same data can take over $90$ minutes or about $3$ minutes. Each of the six different processing techniques produce the same output: the discovery of over $73M$ parent/child word pairs. 

As as example of these relationships, see [word group grid](https://mike-babb.github.io/media/finding_anagrams/word_grid.html) for the top 5 parent words and top 5 child words by word length.**

Where applicable, there are Jupyter Notebooks and python scripts that demonstrate the same process flow. The notebooks are more interactive while the python scripts can be run from the command line. The notebooks for parts 01, 02, and 03 make use of functions written in the corresponding scripts for parts 01, 02, and 03. In general, the notebooks and scripts start out less complex and become more complex. For example, part 01 features more interactivity (calls to `print()` and `pd.DataFrame.head()`) and descriptions of operations and objects ([python dictionaries](https://docs.python.org/3/tutorial/datastructures.html) and [NumPy arrays](https://numpy.org/doc/stable/reference/generated/numpy.array.html), for example) than part 03. Each part builds upon the previous part(s).

# The Technique - Subdividing a matrix
Broadly, this workshop finds parent/child word pairs by representing words as numeric vectors and performing various vector and matrix operations on each word-stored-as-numeric vector. The differences in processing time originate from reducing the size of a focal word's candidate search space. For example, comparing a $[1,26]$ vector with another $[1, 26]$ vector is a lot faster than comparing a $[1, 26]$ vector with a $[500, 26]$ matrix. While the time it takes to perform a single vector comparison operation is trivial, approximately $216K$ vector comparison operations is less so. 

Each of the six different matrix extraction options implements a different way of sub-dividing a $215,842$ row by $26$ column matrix into matrices of size $[M, 26]$. This $[~216K, 26]$ focal matrix is referred to as the `char_matrix` throughout this document. In the `char_matrix`, each row represents a different word and each column indicates the number of occurrences of a letter in the ordinal position. By equating the letter `a` with index position $0$ and the letter `z` with index position $25$, we can replace each letter in a word with each letter's ordinal position in the the English alphabet. For example, the word `achiever` features the following letters by zero-index position:  
```python
[0, 2, 7, 8, 4, 21, 4, 17]
```  
By replacing the ordinal positions of each letter with the count of each letter in each letter's ordinal position - and include counts for letters not present - we can represent the word `achiever` as a numeric vector with length 26:  
``` python
[1, 0, 1, 0, 2, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 0]
```  
Doing this for each word enables the rapid comparison of a focal word with *all other words*. This is accomplished by subtracting the focal vector from the `char_matrix`. Calling [`np.min(axis=1)`](https://numpy.org/doc/stable//reference/generated/numpy.min.html) generates a vector of length approximatley $216K$ that contains the smallest value in each row. The resulting vector features a combination of positive, negative, and zero values. Negative values indicate that the focal word has letters not found in other words. A value GTE zero means that the letters in the focal word are found in other words. A boolean operation is then used to select which indices are greater than or equal to $0$. These indices correspond to parent words of the focal word. For example, `archdetective` is a parent word of `achiever`:
``` python
>>> import numpy as np
>>> archdetective = np.array([1, 0, 2, 1, 3, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 2, 0, 1, 0, 0, 0, 0])
>>> achiever = np.array([1, 0, 1, 0, 2, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 0])
>>> archdetective - achiever
array([0, 0, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 0, 0, 0, 0, 0, 0])
```
As all values in the resulting array are GTE $0$, we can conclude that `archdetective` is indeed a parent word of `achiever`.

Each matrix extraction option is described in greater detail below. Where applicable, graphics are included to illustrate the intuition and reasoning behind each technique. As there are six matrix extraction techniques, I am using a specific color to identify each extraction technique. 

| Matrix Extraction Option | Subdivision Description | Color |
| -----:|:-----|:-----|
| 1 | No subdivision | <span style="width: 20px; height: 20px; background-color: #1b9e77;"> Technique 1</span> |
| 2 | Word length | <span style="width: 20px; height: 20px; background-color: #d95f02;"> Technique 2</span> |
| 3 | First letter| <span style="width: 20px; height: 20px; background-color: #7570b3;"> Technique 3</span> |
| 4 | Single least common letter | <span style="width: 20px; height: 20px; background-color: #e7298a;"> Technique 4</span> |
| 5 | Three least common letters | <span style="width: 20px; height: 20px; background-color: #66a61e;"> Technique 5</span> |
| 6 | Three least common letters and word length | <span style="width: 20px; height: 20px; background-color: #e6ab02;"> Technique 6</span> |

These colors were created by [Professor Cynthia Brewer](https://www.geog.psu.edu/directory/cynthia-brewer) and originate from the [Dark2 color theme](https://colorbrewer2.org/#type=qualitative&scheme=Dark2&n=3).  

## Matrix Extraction Option 1 - No subdivision
By subtracting each row (a focal word) of the `char_matrix` from every other row of the `char_matrix` and finding non-negative values for each operation, the parent words for a focal word are identified. This is the simplest option to implement and the slowest because each word is compared against $215,842$ other words. This is effectively performing $~216K * ~216K$ comparisons. Accordingly, this option takes approximately $90$ minutes to complete. While the `char_matrix` creates a standard format for each word, there are latent structures in our list of words that we can leverage. To that end, [part_01_structure_data.ipynb](/code/part_01_structure_data.ipynb) uncovers these latent structures: the number of characters in each word and the frequency of each character in our list of words. Matrix extraction options `2` through `6` leverage these latent structures by splitting the `char_matrix` into smaller $[M, 26]$ matrices. 

## Matrix Extraction Option 2 - Subdivision by word length
A logical starting point for dividing the `char matrix` is by character length. This produces $24$ separate matrices. Words that are $N$ characters in length are only compared to other words that are at least $N$ characters in length. For example, the word `achiever` is $8$ characters in length and there are $170,056$ words are at least $8$ characters in length. This plot shows the number of candidates by word length.  
![Matrix Extraction Option 2: Number of Candidates](/graphics/meo_2_ss.png)  
The dashed, horizontal, red line is the average number of candidates, approximately $89K$ words. Not surprisingly, as the number of the characters in a word increases, the number of candidate words decreases. This option takes approximately $52$ minutes to complete. 

## Matrix Extraction Option 3 - Subdivision by first letter
The `char_matrix` is subdivided by each letter of the alphabet to produce $26$ sub-matrices. The list of candidate words is generated for a focal word if the first letter of the focal word is found anywhere in each of the candidate words. For example, the word `achiever` begins with the letter `a` and it is compared against the $133,001$ words that contain the letter `a`. Across the $~216K$ words, not all letters are used at the same frequency. The plot below shows the counts of the words featuring each letter in the English language.  
![Matrix Extraction Option 3: Number of Candidates](/graphics/meo_3_ss.png)  
The dashed, horizontal, red line is the average number of candidates, approximately $64K$ words.
We can see from the plot that there are fewer words that feature the letter `q` or the letter `j` than words that feature the letter `a` or the letter `t`. By leveraging these differences, matrix extraction option `3` takes approximately $35$ minutes to complete. Matrix extraction option `4` more effectively leverages this distribution in letter frequency. 

## Matrix Extraction Option 4: Subdivision by single-least common letter
The `char_matrix` is again subdivided by each letter of the alphabet: $26$ separate matrices. This is the same division as option `3`, but the least common letter in each word is used to suggest candidates. The plot above gives some indication of letter ranking, but a better way to express the ranking is to compute the total number of occurrences of each letter across all words. The graph below showcases the count of each letter across all $215,842$ words, plotted in descending order:  
![Letter Frequency](/graphics/meo_4_letter_rank.png)  
This chart should be somewhat familiar to anyone who has investigated the frequency distribution of letters in the English language. The letter `e` is the most commonly used letter while the letter `j` is the least commonly used letter. With matrix extraction option `3`, for every word that starts with `a`, the search space includes *ALL* words with the letter `a`. For the word `achiever`, the search space using matrix extraction option `3` is $133,001$ words and the search space for matrix extraction `4` is $18,391$ words. The search space for the word `achiever` using matrix extraction option `4` is $7.2$ times smaller than the search space for the word `achiever` using matrix extraction `3`. This is because the least common letter in `achiever` is the letter `v`. Using only the least common letter in each word to winnow down the search space for each word decreases processing to less than $16$ minutes. An $82$ -percent improvement just by leveraging an innate component in the input data

One way of expressing the relationship between the starting letter of a word and the least common letter in the word is to compute the distribution of words by starting letter and least common letter. The heatmap below showcases this distribution:  
![First letter and starting letter commonality](/graphics/meo_4_first_letter_starting_letter.png)  

Any cell with a value greater than $1,000$ is assigned the same shade of red: about $20$ -percent of cells feature frequencies greater than $1,000$. Cells in the diagonal are framed in yellow.  The row totals on the left indicate the number of words that start with a given letter. For example, there are $16,513$ words that start with the letter `a` and $11,420$ words that start with the letter `m`. The two rows at the bottom are the total number of words sent to a given search space (second row from the bottom) and the size of that search space (bottom-most row). Using matrix extraction option `3`, $16,513$ words are sent to the search space with all words containing the letter `a` - $133,001$ - at least once. Identifying the least common letter in each word that starts with the letter `a`, those $16,513$ words are more efficiently sent to smaller search spaces. For example, $869$ of these $16,513$ words feature a least common letter of `v`. Using matrix extraction option `4` means that there will be $869$ checks of the $18,391$ word search space (words that feature the letter `v`). For words that start with the letter `r`, $7,558$, there are only $12$ words that feature the letter `r` as the least common letter. This means that there are $12$ checks of a search space that features $118,135$ words with the letter `r`. Lower values indicate a more rare pairing of starting letter and least common letter indicating fewer checks of a given search search space. While the bottom two rows of the heatmap above display the counts of the number of words by search space, we can plot those counts separately for both option `3` and option `4`.

![Differences in the count of search space submissions](/graphics/meo_4_search_space_letter_lookup_diff.png)  

The x-axis in the above plot is the search space size and the y-axis is the number of checks in that search space. Each dot corresponds to a letter. The pink lines are the number of words sent to search spaces of specific sizes by matrix extraction option `4` and the purple lines are the number of words sent to search spaces of specific by matrix extraction option `3`. Only points for option `4` are labeled, however each set of vertically-aligned points is for the same letter. This graphic is showing that for option `4`, more words are being sent to smaller search spaces and fewer words are being sent to larger search spaces. To further highlight this relationship, I can graph the reduction in the size of the search space by starting letter and the least common letter. 
![Reduction in search space between option 3 and option 4](/graphics/meo_4_letter_lookup_diff.png)  
By leveraging least common letters, we see large average reductions for the vowels and the letters `r`, `s`, and `t`. There is no visible reduction for the letters `j` and `q` as those letters are used infrequently. Even though this is using the same data as Matrix Extraction `3`, *how* the data are being are used - optimizing look ups of search space sizes - is driving improvement. This reduction in comparisons of large search spaces is why matrix extraction option `4` is $20$ minutes faster than matrix extraction option `3`: from $35$ minutes to $15$ minutes.

## Matrix Extraction Option 5: Matrices are sub-divided by groups of least common letters. 
Option `4` showed quite an improvement over option `3`. And this was accomplished by using a single least common letter in a focal word. Option `5` continues this trend by using groups of least common letters. Returning to the word `achiever`, the ranks of each letter are as follows: `[3, 10, 15, 2, 1, 20, 1, 5]`. Selecting the three least common - and unique - letters from the word `achiever` we have the following: `['v', 'h', 'c']`. Based on this unique letter grouping - referred to as a letter selector for convenience - there are $489$ candidate words. To put that in perspective, option `3` featured a search space of $133,001$ letters, option `4` featured a search space of $18,391$ words, and now option `5` features a search space of $489$ words: $272$ times smaller than option `3` and $38$ times smaller than option `4`. 

Repeating this process of selecting the three least common letters for each of the approximately $216K$ words, we can generate $2,387$ unique letter groupings:
* $26$ One letter groups
* $111$ Two letter groups
* $2,250$ Three letter groups  

The letter selector groups range in size from a single word to over $145K$ words. We can get a better sense of the distribution of the sizes of the letter selector groups by examining the plot comparing the number of letter selector groups by the size of the letter selector group:  
![Letter selector difference](/graphics/meo_5_letter_selector_group_size.png)
For ease of interpretation, the x-axis is log-transformed. Most letter groups are small: $25$ -percent of the $2,387$ distinct letter groups feature $340$ words or fewer and $50$ -percent of the $2,387$ letter groups feature $1,665$ words or fewer. The average group size is a little over $7.4K$ words. Grouping by least common letters is an efficient way to sub-divide the initial `char_matrix`. In fact, it is so efficient that matrix extraction option `5` executes in under four minutes. This is over $10$ times faster when compared to Option `3` ($31$ minutes) and over $5$ times faster than option `4` ($15$ minutes). And this is because of the reduction in the search spaces of candidate words: when comparing option `5` with option `3`, there is a [92-percent](/graphics/meo_5_letter_selector_lookup_diff.png) reduction in the size of the search spaces.
  
## Matrix Extraction Option 6: Matrices are sub-divided by groups of least common letters and number of characters
Of the five previous matrix extraction options, option `5` is currently in first place. Can we improve on option `5`? The answer is a resounding *"yes, but..."* More on that in a bit, but first the method behind option `6`: a combination of word length and groups of least common letters. Option `6` performs additional subdivision by finding the set of words common between words that are at least $N$ characters in length *and* the groups of least common letters. This generates $16,101$ sub-matrices. Again, focusing on the word `achiever`, we can intersect the set of $489$ words that feature the three least common letters of `['v', 'h', 'c']` with the set of candidate words that are at least $8$ characters in length - $170,056$ words - to produce a list of $449$ candidate words. This process is repeated for all words. Just like for option `5`, we can get a sense of the distribution of the search space by examining the sizes of the letter-selector-number-of-characters groups.   
![Letter selector difference](/graphics/meo_6_nc_ls_group_size.png)  

Again, note the log-transformation on the x-axis. While the general shape of the distribution directly above and the graph of the distribution for [option `5`](/graphics/meo_5_letter_selector_group_size.png) are similar, note the differences in the magnitude of the y-axis: for option `6`, some of the histogram groups are greater than 600 in number. The groups of letter-selector-number-of-characters range in size from a single word to over $145K$ words. The average number-of-characters-letter-selector group size is approximately $4.5K$ words and $50$ -percent of number-of-characters-letter-selector groups have a size of $789$ or fewer. Effectively, with matrix extraction option `6`, there are more, smaller groups of candidate words when compared to matrix extraction option `5`. As the previous five matrix extraction techniques have shown, reductions in the search space lead to decreases in processing time. And because of this reduced search space, option `6` also completes in under $4$ minutes.

So, why is the answer to "is matrix extraction option `6` faster than matrix extraction option `5`" a resounding "yes, but..."? There are several reasons for this and to unpack that qualified statement, let's focus on the word `achiever` and the average time it takes to find the parent words for `achiever` for $1,000$ runs of each matrix extraction technique:

|Matrix Extraction Technique| Total Seconds| Average Seconds|
|------|-----|-----|
|Option 1|22.65677|0.02266|
|Option 2|18.92866|0.01893|
|Option 3|15.76573|0.01577|
|Option 4|2.1044|0.0021|
|Option 5|0.15909|0.00016|
|Option 6|0.15185|0.00015|

When comparing extraction times for a single word, `achiever`, matrix extraction option `6` *IS* ever so slightly faster. And because those numbers for all extraction techniques are orders of magnitude different, computing the ratio of each extraction technique's execution time to each other extraction technique's execution time will better showcase the differences in execution time. The heatmap below visualizes those ratios. 

![`achiever` comp times](/graphics/meo_all_comp_times.png)  

The bottom diagonal is not shown as those numbers are the inverse of the top diagonal. Most striking is that both option `5` and `6` are over `140` times faster than option `1`! Using the least common letter, option `4`, is over $7$ times faster than using the first letter of a word (option `3`). Examining this heat map, we can see that matrix extraction technique `6` is marginally faster than matrix extraction technique `5`. But again, this is just for a single word. 

Comparing the total processing time for all words for all six techniques we have the following:

|Matrix Extraction Technique| Hours| Minutes| Seconds|
|------:|:------:|------:|------:|
|1|1|33|50|
|2|0|49|33|
|3|0|35|27|
|4|0|15|29|
|5|0|3|2|
|6|0|3|39|

And again, because those numbers are orders of magnitude different, we can compute the ratio of processing times as follows:
![all words proc times](/graphics/meo_all_comp_times_all_words.png)  

Looking at the ratios of the different processing times, we see that option `5` is approximately $34$ times faster than option `1` while option `6` is approximately $26$ times faster than option `1`. So, why is matrix extraction option `6` slower, on average, than matrix extraction 5? In short, the number of keys used to correspond to the sub-matrices. This, too, is a search space. There are $2,387$ sub-matrices created for matrix extraction option `5` and $16,101$ matrices created for matrix extraction option `6`: approximately $6.7$ times as many sub-matrices. When processing each word, there are now an initial $16,101$ comparisons to make (to find the right sub-matrix) before making the comparisons that find the parent words for a focal word. These extra comparisons - in the form of [dictionary](https://en.wikipedia.org/wiki/Associative_array) keys - add to the time it takes to find the parent words of a given word. By carefully curating the number and size of the sub-matrices, we can reduce the processing time. But, too much curation adds additional search time. Below is a graphic featuring a boxplot of the distribution of sub-matrix size by matrix extraction technique. Note that there is not a distribution for matrix extraction technique `1` as each word is compared against the same matrix.
![sub-matrix size](/graphics/meo_all_box_plot_distribution.png)  
As the sizes of sub-matrices decrease, the number of sub-matrices increase. This has diminishing returns as can be seen in the [previously mentioned heatmap](/graphics/meo_all_comp_times_all_words.png) comparing the ratios of extraction above. To further illustrate this concept of diminishing returns, I will suggest setting `n_subset_letters = 4` in  [part_02_demonstrate_extraction_timing_techniques.ipynb](/code/part_02_demonstrate_extraction_timing_techniques.ipynb) or [part_02_demonstrate_extraction_timing_techniques.py](/code/part_02_demonstrate_extraction_timing_techniques.py) and running the notebook or script. This will take an additional minute to complete.

As a final comment, up until this point, I have not have mentioned any timing related to generating the sub-matrices. For options `2` through `4`, it takes about $2$ seconds to generate the sub-matrices. Generating the sub-matrices for option `5` takes about $10$ seconds and it takes about a minute to generate the sub-matrices for option `6`. In other words, for option `5`, an extra $8$ seconds of pre-processing results in a time savings of $90$ minutes when compared with matrix extraction option `1`.

# An ETL Pipeline
This section describes each script in the ETL pipeline and the various scripts used to analyze different processing times. Parts 01, 02, and 03 form the ETL pipeline while other parts feature various components for code reuse and analyses.

## Setup
The scripts in this portion define constants and functions used throughout subsequent processes.
* [`_run_constants.py`](/code/_run_constants.py) - Input and output file names and paths. All subsequent scripts reference the paths defined in this file. Paths and names only need to be set once, in this file. 

## Utilities
* [`part_00_file_db_utils.py`](/code/part_00_file_db_utils.py) - Code reuse for parts 01 through 07. These are mostly I/O and utility functions.
* [`part_00_process_functions.py`](/code/part_00_process_functions.py) - Code reuse for parts 01 through 07. These functions perform the data processing and are called in subsequent parts. The reason for this structure is for code reuse, efficient optimization and debugging, and generally writing less code. Effectively, we can define the function once and import it.

## Extract
* [`part_01_structure_data.ipynb`](/code/part_01_structure_data.ipynb) and [`part_01_structure_data.py`](/code/part_01_structure_data.py) - 
Load a list of words, perform several calculations and data creation steps, and store the results. This step creates the objects that facilitate the different extraction techniques. In these notebooks, the word groups are determined. The input list of [words](/data/words.txt) features approximately $234K$ unique words. Of these $234K$ words, approximately $201K$ do not belong to a word group while approximately $14K$ words do belong a word group. Most words in the word groups belong to groups of size $2$. The words `abactor` and `acrobat` are anagrams of each other. There are two words groups of size 10: 

## Transform
* [`part_02_demonstrate_extraction_timing_techniques.ipynb`](/code/part_02_demonstrate_extraction_timing_techniques.ipynb) and [`part_02_demonstrate_extraction_timing_techniques.py`](/code/part_02_demonstrate_extraction_timing_techniques.py) - The scripts in this section demonstrate the techniques - and crucial differences - in the different matrix extraction techniques in subsequent scripts.

## Load
* [`part_03_generate_and_store_anagrams.ipynb`](/code/part_04_run_parts_01_02_and_03.ipynb) and 
[`part_03_generate_and_store_anagrams.py`](/code/part_03_generate_and_store_anagrams.py) - This notebook and script find the parent words for all words in the list of focal words using one of the user specified extraction options. The data can optionally be written to a SQLite DB.

Each of the six techniques in part_03 will produce the same data - approximately $73M$ parent-child word pairs. 

## Complete ETL
* [`part_04_run_parts_01_02_and_03.ipynb`](/code/part_04_run_parts_01_02_and_03.ipynb) and [`part_04_run_parts_01_02_and_03.py`](/code/part_04_run_parts_01_02_and_03.py) can be used to run parts 01, 02, and 03 from one notebook / script. This is helpful in showcasing the overall time it takes to run one matrix extraction technique.

## Query
* [`part_05_query_anagram_database.ipynb`](/code/part_05_query_anagram_database.ipynb) - query the anagram database. Show how to crosswalk from `word_group_id` to `word`.
* [`part_06_add_database_indices.ipynb`](/code/part_06_add_database_indices.ipynb) - adds indices to tables in the anagram database. This showcases how database indices can dramatically speed up data retrieval times: from minutes to query for a single word to sub-second access. This notebook only needs to be run after the `anagram_groups` table is (re)created. 

## Analysis
* [`part_07_build_a_graph.ipynb`](/code/part_07_build_a_graph.ipynb) - build a graph of the parent/child word relationships after for the word `terminator`. 

# Visualization
Both python (part 08) and R (part 09) are used to plot aspects of the search space and process times by matrix extraction technique. Parts 10 and 11 prepare data for use in a webpage. 

## Search Spaces and Processing Times
* [`part_08_plot_counts_of_search_spaces.ipynb`](/code/part_08_plot_counts_of_search_spaces.ipynb) - use [`matplotlib`](https://matplotlib.org/) and [`seaborn`](https://seaborn.pydata.org/) to plot counts of search spaces and processing times. This file generates the `meo_*_.png` images, referenced and shown in the sections above

* [`part_09_visualize_processing_time.R`](/code/part_09_visualize_processing_time.R) - Make graphics using the [`R programming language`](https://www.r-project.org/)! Because the data generated in parts 01, 02, and 03 are stored in a SQLiteDB, we can connect to the database using the [RSQLite](https://rsqlite.r-dbi.org) library and in turn load the data as a [data.table](https://rdatatable.gitlab.io/data.table/) object. From there, we can then use the [ggplot2](https://ggplot2.tidyverse.org/) library to produce several plots showcasing different aspects of the processing times and search space. In this case, all plots feature statistics by word length. As an example, the graphic below showcases the total time it takes to find all parent words by word length:
![total time by word length](/graphics/wl_time_tot_proc_time.png). Additional graphics generated in R include the following:

* [wl_from_to_words_avg.png](/graphics/wl_from_to_words_avg.png) - the average count of parent words and child words by word length  
* [wl_from_to_words_distribution.png](/graphics/wl_from_to_words_distribution.png) - boxplots of parent words and child words by word length  
These two plots show how as the number of letters in a word increases, the number of child words increases and the number of parent words decreases. This is to be expected. 

* [wl_search_space_avg.png](/graphics/wl_search_space_avg.png) - the average size of the search space by word length and matrix extraction technique.
* [wl_search_space_number_of_candidate_words.png](/graphics/wl_search_space_number_of_candidate_words.png) - boxplots of the size of the search space by word length and matrix extraction technique.  
This last plot is similar to the graphic showing [sub-matrix size](/graphics/meo_all_box_plot_distribution.png) the search spaces by technique.
* [wl_time_avg_proc_time.png](/graphics/wl_time_avg_proc_time.png) - the average processing time by word length and matrix extraction technique. 

## Word Relationships
* [part_10_create_word_counts.ipynb](/code/part_10_create_word_counts.ipynb) - generate the data for a web page showing a grid of words with the greatest number of parent/child words by word length. Up until this point, I have only mentioned the words as a corpus but I have not really focused on any specific word. We have graphed search spaces and the number of parent/child words but we haven't looked any specific words. To that end, I have ranked each word based on the number of parent words and the number of child words by word length. I then selected the five words with the greatest number of parent words and the greatest number of child words by word length. As the words range in length of $1$ through $24$ letters, there are $120$ words showing the count of parent words and $120$ words showing the count of child words. There are $240$ words in total. This script generates one part of the data for the word group grid.  

* [part_11_export_data_for_grids.ipynb](/code/part_11_export_data_for_grids.ipynb) - This notebook generates the parent and child words for the 240 words on the word grid. Clicking on each grid cell takes a user to the formatted list of parent or child words. This script generates that list. And here is the word group grid:
* [word group grid](/media/finding_anagrams/word_grid.html) - Top 5 word groups by parent/child word count by word length. The counts of `from` words are on the left in shades of blue and the counts of `to` words are on the right in shades red. In general, as the word length increases, more child words can be created and a focal word can be found in fewer parent words. For example, the letter `e` can be found in over $157K$ words: over $67$ -percent of the words in the word list. In total, there are approximately $233K$ unique words identified in the list of $120$ child words, over $99$ -percent of all words. There are $101K$ parent words identified in the parent words section, about $43$ -percent of all words. Across the $120$ parent words, all but the letters `k` and `w` are present. Across the $120$ child words, all but the letters `q` and `w` are present. The word with the greatest number of child words is [pseudolamellibranchia](https://www.merriam-webster.com/dictionary/Pseudolamellibranchia). The letters in this $23$ -character word describing a group of bivalve mollusks can be rearranged to spell a whopping $32,456$ words. 

# Introspection
This section focuses on tools to understand how the functions are referenced from one another and the time it takes to execute various functions. How do the functions in parts 00, 01, 02, and 03 come together? How long do the various components of each function take to execute? We can answer each question, respectively, by creating static call graphs and profiling.

## Call Graphs
According to [wikipedia](https://en.wikipedia.org/wiki/Call_graph), a call graph "is a control-flow graph which represents calling relationships between subroutines in a computer program." A static call graph represents the idealized flow of the program while a dynamic call graph represents what is *actually* called during a program's execution.

* [part_12_generate_call_graphs.bat](/code/part_12_generate_call_graphs.bat) generates static call graphs. One in the *.svg format:
![static call graph](/graphics/all_parts_call_graph.svg)  
The other format is an interactive [html page](/graphics/all_parts_call_graph.html) call graph where each node can be clicked.  

Note: A different version of python is needed to create the call graph so I recommend creating a different conda environment and installing the following libraries:
``` shell
conda create -n py38 python==3.8
pip install pydot
pip install graphviz
conda install graphviz
# yes, it is necessary to install graphviz using both pip and conda
pip install pyan3==1.1.1
```
After this environment has been created, activate the `py38` environment and run the batch file listed above. 

## Profiling
[Profiling](https://en.wikipedia.org/wiki/Profiling_(computer_programming)) measures execution time and complexity. This is exceptionally useful when looking at which parts of a program are taking longer than expected or just understanding how long things take. The three batch files below can be executud from the Anaconda Powershell prompt with the same activated environment as the environment used to run parts 01, 02, and 03.

* [profile_part_01_structure_data.bat](/code/profile_part_01_structure_data.bat)
* [profile_part_02_demonstrate_extraction_timing_techniques.bat](/code/profile_part_02_demonstrate_extraction_timing_techniques.bat)
* [profile_part_03_generate_and_store_anagrams.bat](/code/profile_part_03_generate_and_store_anagrams.bat)

In python, profiling makes use of the [cProfile](https://docs.python.org/3/library/profile.html) library. The general format to profile a program takes the following form:
``` shell
python -m cProfile -o ..\graphics\part_01.prf part_01_structure_data.py
```
The profile output is saved to a file - `part_01.prf` - and can then be viewed using [snakeviz](https://pypi.org/project/snakeviz/)

```shell 
pip install snakeviz
snakeviz ..\graphics\part_01.prf
```

I have already done a fair amount of optimizing on each part so most of the easy fixes have already been implemented. Plus, as this project is written to be a quasi-tutorial, there are sections in the code that are not as efficient as they could be - for loops that could be vectorized, for example - but are left in for explanatory purposes. That being said, a good example of how to interpret the output from profiling can be seen in the image below:
![part 02 profile](/graphics/part_02_profile_example.png)  
This image shows the time taken to perform [set intersections](https://docs.python.org/3/library/stdtypes.html#frozenset.intersection) in the split_matrix() function. This corresponds to matrix extraction option `6`: sub-matrices are split by word-length and three least common letters. Finding the word ids of words that at least $N$ letters in length and feature a specific set of three least common letters is accomplished through the `set().intersection` method. This method is very fast: it's just being called thousands of times.

# Version 3.0
If you've made it this far, first, thank you. Second, if you see some room for improvement, please do let me know. I would love to hear from you if you have any thoughts on an additional matrix extraction technique or suggestions on how to improve the existing matrix extraction techniques. I do wonder if it would be possible to get the parent-child word determination down to under a minute. That might be a wholly different technique or a different hardware implementation such as using a [GPU-accelerated version of NumPy](https://cupy.dev/).

# Update, May 10, 2025
I decided to see if I could make the parent/child word relationship determination faster. Yes, I was able to make the process faster with a very simple addition to the code: explicitly setting the NumPy array data types. After some trial-and-error in which I learned a great deal, I was able to get the process down to less than $90$ seconds on my main computer and about $35$ seconds on a more powerful computer. I tried four different experiments, in the following order: processing data on a GPU using [CuPy](https://cupy.dev/), using [Numba](https://numba.pydata.org/), splitting up the search spaces, and explicitly setting [NumPy data types](https://numpy.org/doc/stable/user/basics.types.html). However, for the ease of narrative and setting a fast baseline, I have structured the experiments in the following order: setting the NumPy data types, using a GPU, splitting the search spaces, and using Numba. The only reduction in data processing time was from setting the NumPy data types. Using a GPU was mixed, splitting the search spaces, and using Numba did not decrease the processing time. In fact, those three techniques increased the processing time. For the sake of consistency, I implemented a modified version of Matrix Extraction Technique `5`: splitting matrices by groups of least common letters to test out the four different techniques.
    
* [Exp_01_demo_numpy_data_types.ipynb](code/Exp_01_demo_numpy_data_types.ipynb): This is the last experiment I tried, but I'm setting this first as it featured the biggest speed ups. Explicitly setting the data types on NumPy objects resulted in some operations being upwards of twice as fast. The largest integer value in use in this project is $234,370$. This is larger than the signed $16$-bit integer $2^{16} = [-32768, 32767]$ and smaller than a signed $32$-bit integer $2^{32} = [-21474836482, 2147483647]$. By setting the NumPy data types as small as possible, significant reductions in processing time can be achieved. Some objects could even be set to smaller data types: the `char_matrix` and the `wchar_matrix` could be set to the `np.int8` data type. In truth, I was pleasantly surprised to see this. I knew that smaller data types were generally faster, but I didn't realize it would be that much faster. Because of these gains, I set this experiment as first in the narrative so that subsequent experiments could improve on these impressive gains. This small addition to the code base also had the benefit of adding modest amounts of new code. Usually, this took the form of typing `dtype = np.int32` when creating an array. 

* [Exp_02_demo_cupy_part.ipynb](code/Exp_02_demo_cupy.ipynb): My first experiment in making this process faster. I tried using CuPy on a computer with an Nvidia GPU. I first implemented the naive, full matrix comparison approach: matrix extraction technique `1`. Using NumPy on the machine with the GPU, this takes about an hour. Using the GPU through CuPy, this takes a little more than 3 minutes. About 17 times faster! Using a modified version of matrix extraction `5` - sub-dividing the `char_matrix` by groups of three-least common letters - takes about $35$ seconds. But using matrix extraction technique `5` with CuPy takes a little less than two minutes. Using a GPU proved to be sometimes faster, but not always. The gains from a GPU occur from operations on large matrices consisting of many rows and many columns. That being said, while NumPy is faster in this case, CuPy is incredible. It's effectively a drop in replacement for NumPy - nearly identical function syntax and the [installation](https://docs.cupy.dev/en/stable/install.html) was very easy.

* [Exp_03_plot_search_space_sizes.ipynb](code/Exp_03_plot_search_space_sizes.ipynb) Not so much of an approach, but further investigation into what's driving the time it takes to find parent/child word relationships. With this modified version of matrix extraction technique `5`, there are $2,387$ letter selectors. However, each sub-matrix by letter selector is created only once and the relevant look-ups are carried out accordingly. What this means is that I can time how long it takes for each letter/selector operation to complete. Some letter-selectors are queried only once, some are queried over $2,500$ times. On average, each letter-selector is queried $90$ times and $50$-percent of letter-selectors are queried $14$ times. Long tail! The plot that is created in [Exp_03_plot_search_space_sizes.ipynb](code/Exp_03_plot_search_space_sizes.ipynb) shows how as the total number of comparisons by letter-selector increases (number of queries * search space size), the total time to process each letter-selector increases. 
![total number of comparisons](/graphics/exp_02_total_time_by_total_comps.png) What's really driving this shape is the size of the search space - not how many times it is queried. Larger search spaces, naturally, take longer to query. Note that in this plot, the $26$ single-character and $111$ two-character letter selectors were removed from this plot to better highlight the relationship between total comparisons and time. Given this relationships, it would make sense to break up the large search spaces into smaller search spaces. An issue with that, however, is that too many search spaces - regardless of size - also increases processing time. 

* [Exp_04_compute_sizes_of_all_search_spaces.ipynb](code/Exp_04_compute_sizes_of_all_search_spaces.ipynb)
The default letter selector is three characters. In this example, I compute the number of letter selectors for all letter selectors up to and including those of $16$ characters. In the list of words, the longest word is $24$ characters. Letter selectors use unique characters and so this means that the largest letter selector is $16$ unique characters. Just for fun, I decided to compute the number of letter selectors using both a CPU and a GPU. This is a great example of the performance boost that comes with a GPU. Using the CPU this takes about $30$ minutes while producing the same data using a GPU takes about $3$ minutes or so. 

* [Exp_05_try_modified_search_spaces.ipynb](code/Exp_05_try_modified_search_spaces.ipynb): 
Using the data generated in the previous experiment, I identified the largest letter-selector by search space size and split them. A three character limit on the letter selector produces 2,387 letter selectors. A four character limit on the letter selector produces $10,222$ letter selectors. Previous work demonstrated that a four character limit resulted in a slower overall time even though the search spaces were smaller. The hypothesis driving this section is that there is an optimal way to split up some of the largest letter selectors in order to decrease the processing time. There are values in the beginning of the notebook that modifies the different search cut-offs and letter selector splits. Splitting letter selectors greater than $40,000$ words by one extra character creates an additional $16$ letter selectors. However, decreasing the size of a search space increases the number of search spaces so there wasn't any gain from splitting the search spaces.

* [Exp_06_demo_numba.ipynb](code/Exp_06_demo_numba.ipynb): I placed some of the operations in this notebook into `njit()` decorated functions. Briefly, Numba creates just-in-time compiled versions of functions. This can make big, multi-step operations faster. I watched this [Numba how-to video](https://www.youtube.com/watch?v=x58W9A2lnQc&t=35s&ab_channel=JackofSome) and it shows some advantages of using using Numba. In this case, however, using Numba proved to be slower than not. This is not an indictment of Numba, rather, it suggests that this is not the correct problem for Numba. Two of the "big" operations in the workflow involve using `np.all`. and since Numba, is not compatible with `np.all`. The operations where I could use Numba were already vectorized. Even after taking into consideration the time spent compiling the functions, there was no speed up. Again, this is not a recommendation against Numba, I just think that this task is not suited for it. 

* [Exp_07_plot_search_spaces.R](code/Exp_07_plot_search_spaces.R): Not an experiment, just an excuse to work with `R` and the `data.table` package and make a few plots. While I think Python is great and it's incredibly versatile, I love R. I made three plots using `ggplot()`. Each plot showcases a different aspect of the letter selectors as created in [Exp_04_compute_sizes_of_all_search_spaces.ipynb](code/Exp_04_compute_sizes_of_all_search_spaces.ipynb). What's really interesting is that these plots show how the rate of change plateaus after increasing the number of characters in the letter selector to six or so. The additional plots created by this process are:
    * [ls_01_n_letter_selectors.png](/graphics/ls_01_n_letter_selectors.png): Barplot showing the number of letter selectors by number of characters in the letter selector.
    * [ls_02_n_lookups.png](/graphics/ls_02_n_lookups.png): Boxplot showing the number of lookups by number of characters in the letter selector.
    * [ls_03_letter_selector_size.png](/graphics/ls_03_letter_selector_size.png): Boxplot showing the number of elements in the letter selector by number of characters in the letter selector.

So, to conclude, set your `NumPy` data types.
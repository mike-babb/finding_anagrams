# Finding Anagrams: v2.0
# September 2, 2024
Find and store from/to word relationships using Python, NumPy, Pandas, and SQLite

# Introduction
This workshop uses python and the NumPy, Pandas, and SQLite libraries to discover and store anagrams found in a list of English words. The main focus of this workshop is to show how NumPy's arrays and other python objects can be used to Extract, Transform, and Load (ETL) data into a SQLite database. In addition, there is an R-script showcasing how to use R to connect to a SQLite database, gather data, and create several simple visualizations.

While version 1.0 of this workshop made use of individual words, version 2.0 makes use of word groups. There are approximately 234K unique words and approximately 216K unique word groups in the initial dataset. A word group is defined as a group of words all containing the same letters: 'emit', 'item', 'mite', and 'time', for example. 

This workshop is built for beginners - people very new to python - and progresses to demonstrations of advanced data processing techniques. To that end, there are six different data processing techniques - referred to as matrix extraction options throughout the workshop - that demonstrate how processing the same data can take 90+ minutes or as little five minutes. Each of the six different processing techniques produce the same output, the difference between each of the processing techniques is how the data processing and retrieval is subdivided. 

Where applicable, there are Jupyter Notebooks and python scripts that demonstrate the same process flow. The notebooks are more interactive while the python scripts can be run from the command line. The notebooks for parts 1, 2, and 3 make use of functions written in the corresponding scripts for parts 1, 2, and 3. In general, the notebooks and scripts start out less complex and become more complex. For example, part_01 features more interactivity (calls to `print` and `pd.DataFrame.head()`) and descriptions of operations and objects(dictionaries and arrays, for example) than part_03. Each part builds upon the previous part(s). 

# THE TECHNIQUE - SUBDIVIDING A MATRIX
Broadly, this workshop finds parent/child word pairs by representing words as numeric vectors and performing various vector and matrix operations on each word vector. The differences in processing time orginate from reducing the number of matrix comparisons to be made (in effect, reducing size the search space). For example, comparing a [1, 26] vector with another [1, 26] vector is a lot faster than comparing a [1, 26] vector with a [500, 26] matrix. While the time it takes to perform a single vector comparison operation is trivial, ~216K vector comparison operations is less so. 

Each of the six different matrix extraction options implements a different way of sub-dividing a 215,842 row by 26 column matrix: the `char_matrix`. Each row represents a different word and each column indicates the number of occurences of a letter in the ordinal position. By equating the letter 'a' with 0 and the letter 'z' with 25, we can replace each letter in a word with each word's ordinal position in the the English alphabet. For example, the word `achiever` features the following letters by zero-index position:  
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
array([0, 0, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 0, 0, 0, 0, 0, 0])
```

Each matrix extraction option is described in greater detail below. Where applicable, graphics are included to illustrate the intuition behind each technique. 

## Matrix Extraction Option 1 - No subdivision of the `char_matrix`
By subtracting each row (a focal word) of the `char_matrix` from every other row of the `char_matrx` and finding non-negative values for each operation (as described above), the parent words for a focal word are identified. This is the simplest option to implement and the slowest because each word is compared against 215,842 other words. Accordingly, this option takes approximately 90 minutes to complete. While the `char_matrix` makes each word have a standard output, there are latent structures in our list of words that we can leverage. Indeed, [part_01_structure_data.ipynb](/code/part_01_structure_data.ipynb) uncovers these latent structures: the number of characters in each word and the frequency of each character in our list of words. Matrix extraction options 2 through 6 leverage these latent structures by splitting the `char_matrix` into smaller matrices. 

## Matrix Extraction Option 2 - Subdivision by word length
A logical starting point for dividing the `char matrix` is by character length. This produces 24 seperate matrices. Words that are *N* characters in length are only compared to other words that are at least *N* characters in length. For example, the word 'achiever' is 8 characters in length and there are 170,056 words are at least 8 characters in length. This plot shows the number of candidates for each word length.  
![Matrix Extraction Option 2: Number of Candidates](/assets/meo_2_ss.png)  
Not surprisingly, as the number of the characters in a word increases, the number of candidate words decreases. This option takes approximately 52 minutes to complete. 

## Matrix Extraction Option 3 - Subdivision by first letter
The `char_matrix` is subdivided by each letter of the alphabet: 26 seperate matrices. The list of candidate words is generated for a focal word if the first letter of the focal word is found anywhere in each of the condidate words. For example, the word 'achiever' begins with the letter 'a' and it is compared against the 133,001 words that contain the letter 'a'. Not all letters are used at the same frequency: the plot below showcases the number of candidates by starting letter.  
![Matrix Extraction Option 3: Number of Candidates](/assets/meo_3_ss.png)  
We can see from the plot that there are fewer words that feature the letter 'q' or the letter 'j' than words that feature the letter 'a' or the letter 't'. By leveraging these differences, matrix extraction option 3 takes approximately 31 minutes to complete. Matrix extraction option 4 more effectively leverages this distribution in letter frequency. 

## Matrix Extraction Option 4: Subdivision by single-least common letter.
The `char_matrix` is subdivided by each letter of the alphabet: 26 seperate matrices. This is the same division as option 3, but the least common letter in each word is used to suggest candidates. The plot above gives some indication of letter ranking, but a better way to express the ranking is to compute the total number of occurences of each letter across all words. The graph below showcases the count of each letter across all 215,842 words, plotted in descending order:  
![Letter Frequency](/assets/meo_4_letter_rank.png)  
This chart should be somewhat familiar to anyone who has investigated the frequency distribution of letters in the English language. The letter 'e' is the most commonly used letter while the letter 'j' is the least commonly used letter. With matrix extraction option 3, for every word that starts with 'a', the search space includes ALL words with the letter 'a'. For the word 'achiever', the search space using matrix extraction option 3 is 133,001 words and the search space for matrix extraction 4 is 18,391 words. The search space for matrix extraction 4 is 7.2 times smaller than the search space for matrix extraction 3. This is because the least common letter in 'achiever' is the letter 'v'. Ranking every letter in the word 'achiever' gives us the following vector: `[3, 10, 15, 2, 1, 20, 1, 5]`. One way of expressing the relationship between the starting letter of a word and the least common letter in the word is the compute the distribution for each group of words by starting letter. The heatmap below showcases this distribution:  
![First letter and starting letter commonality](/assets/meo_4_first_letter_starting_letter.png)  
To better highlight interesting trends, cells framed in red feature a frequency greater than 10-percent and cells framed in orange feature a frequency between 5- and 10-percent. For words that start with the letter 'a', 5.3-percent of those words feature a least common letter of 'v'. In other words, if a focal word starts with the letter 'a' and contains the letter 'v', it is more efficient to look at words grouped by containing the letter 'v'. For words that start with the letter 'r', only 0.2-percent of those words feature the letter 'r' as the least common letter. In the graph above cells highlighted in black are the matrix diagonal. In some cases, the starting letter of a word is the least common letter - letters 'j' and 'k', for example. For words that start with the letters 'f', 'g', and 'h', those letters are the least common letters in the word 78.3-percent, 70.4-percent, and 33.3-percent, respectively, of the time.  Finally, 100-percent of words that start with the letter 'j' feature the letter 'j' as the least common letter. This is because the letter 'j' is the least commonly used letter. Of the ~2.2M letters used across the ~216K words, the letter 'j' is used only 3,112 times. By leveraging these differences in the frequency of letter usage, we can improve our processing time considerably: matrix extraction option 4 takes approximately 17 minutes to execute.

## Matrix Extraction Option 5: Matrices are sub-divided by groups of least common letters. 
Option 4 showed quite an improvement over option 3. And this was accomplished by using a single least common letter in a focal word. Option 5 uses groups of least common letters. Returning to the word 'achiever', the ranks of each letter are as follows: [3, 10, 15, 2, 1, 20, 1, 5]. Selecting the three least common - and unique - letters from the word 'achiever' we have the following: `['v', 'h', 'c']`. Based on this unique letter grouping - referred to as a letter selector for convenience - there are 489 candidate words.

Repeating this for each of the ~216K words, we can generate 2,387 unique letter selector groups:
* 26 One letter groups
* 111 two letter groups
* 2,250 three letter groups  
The letter selector groups range in size from a single word to over 145K words. We can get a better sense of the distribution of the sizes of the letter selector groups by examining the plot comparing the number of letter selector groups by the size of the letter selector group:  
![Letter selector difference](/assets/meo_5_letter_selector_group_size.png)
For ease of interpretation, the x-axis is log-transformed. Most letter groups are small: 25-percent of the 2,387 distinct letter groups feature 340 words or fewer and 50-percent of the 2,387 letter groups feature 1,665 words or fewer. The average group size is a little over 7.4K words. Grouping by least common letters is an efficient way to sub-divide the initial `char_matrix`. In fact, it is so efficient that matrix extraction option 5 executes in under four minutes. 
 
## Matrix Extraction Option 6: Matrices are sub-divided by groups of least common letters and number of characters
Of the five previous matrix extraction options, option 5 is currently in first place. Can we improve on option 5? The answer is a resounding "yes, but..." More on that in a bit, but first the method behind option 6: a combination of word length and groups of least common letters. Option 6 performs additional subdivision by finding the set of words common between words that are at least *N* characters in length *and* the groups of least common letters. This generates 16,101 sub-matrices. Again, focusing on the word `achiever`, we can intersect the set of 489 words with the three least common letters of `['v', 'h', 'c']` with the set of candidate words that are at least 8 characters in length - 170,056 words - to produce a list of 449 candidate words. This process is repeated for all words. Just like for option 5, we can get a sense of the distibution of the search space by examining the sizes of the letter-group-number-of-characters groups.   
![Letter selector difference](/assets/meo_6_nc_ls_group_size.png)  
Again, note the log-transformation on the x-axis. While the general shape of the two distributions is similar, note the differences in the magnitude of the y-axis: some of the largest groups are greater than 600 in number. The groups of letter-group-number-of-characters range in size from a single word to over 145K words. The average group size is approximately 4.5K words and 50-percent of groups have a size of 789 or fewer. Effectively, with matrix extraction option 6, there are more, smaller groups of candidate words when compared to matrix extraction option 5. As the previous five matrix extraction techniques have shown, reductions in the search space lead to decreases in processing time. And because of this reduced search space, option 6 also completes in under 4 minutes.

So, why is the answer to "is matrix extraction option 6 faster than matrix extraction option 5" a resounding "yes, but..."? There are several reasons for this and to unpack that qualified statement, let's focus on the word 'achiever' and the average time it takes to find the parent words for 'achiever' for 100 runs of each matrix extraction technique:

|Matrix Extraction Technique| Seconds|
|------|-----|
|Option 1|2.751|
|Option 2|2.279|
|Option 3|1.656|
|Option 4|0.237|
|Option 5|0.018|
|Option 6|0.015|

When comparing extraction times for a single word, 'achiever', matrix extraction option 6 *IS* faster. And because those numbers are orders of magnitude different, computing the ratio of each extraction technique execution time to each other extraction technique execution time will better showcase the differences in execution time. The heatmap below visualizes those ratios. 

!['achiever' comp times](/assets/meo_x_comp_times.png)  

The bottom diagonal is not shown as those numbers are the inverse of the top diagonal. Most striking is that option 6 is over 180 times faster than option 1! Using the least common letter, option 4, is 7 times faster than using the first letter of a word. While those are exciting numbers, these are the differences for a single word as opposed to all words. For that, we can perfom an additional tabulation to compare the ratios of total times for each time.  
![all words comp times](/assets/meo_x_comp_times_all_words.png)  
Examining this heat map, we can see that matrix extraction technique 6 is 20% slower than matrix extraction technique 5. The total time for each extraction technique is as follows:

|Matrix Extraction Technique| Seconds| Minutes| Hours|
|------|------|------|------|
|Option 1|5463.43|91.06|1.52|
|Option 2|3135.51|52.26|0.87|
|Option 3|1832.36|30.54|0.51|
|Option 4|1008.57|16.81|0.28|
|Option 5|177.23|2.95|0.05|
|Option 6|216.32|3.61|0.06|

















. On the other hand, this is only measuring the time it takes to find parent words. None of the timings reported above include the time it takes to build the sub-matrices *or* query for the sub-matrices. Accordingly, it takes longer to extract the sub-matrices for matrix extraction 6 than it does for matrix extraction 5: about 60 seconds versus 9 seconds, respectively, but to performing the set intersections. But, there is also an additional layer of complexity built into this via the search space for the specific sub-matrix of candidates for each focal word. For each word, the search space of sub-matrices is 2,387 for matrix extraction option 5 and 16,101 sub-matrices for matrix extraction option 6. This 6.75X increase in sub-matrix search space equates to an in 


 In total, including the time it takes to extract the sub-matrices, matrix extraction option 5 is faster than matrix extraction option 6: XXX versus YYY, respectively.

The following tables summarize the differences in the size of search spaces, comparison time for the word achiever, and comparison time for all words. 











## SETUP
The scripts in this portion define contstants and functions used throughout subsequent processes.
* `_run_constants.py` - Input and output file names and paths. All subsequent scripts reference the paths defined in this file. Paths and names only need to be set once, in this file. 

### Part 00 utilies
* `part_00_file_db_utils.py` - Code reuse for parts 1 through 7. These are mostly I/O and utility functions.
* `part_00_process_functions.py` - Code reuse for parts 1 through 7. These functions peform the data processing and are called in subsequent parts. The reason for this structure is for code reuse, efficient optimization and debugging, and generally writing less code. Effectively, we can efine the function once and import it.

## EXTRACT
The scripts and notebooks in this section shape the data and introduce the matrix extraction techniques. 

### Part 01: Structure Data
* `part_01_structure_data.ipynb` and `part_01_structure_data.py`
Load a list of words, perform several calculations and data creation steps, and store the results.

### Part 02: Demonstrate Matrix Extraction Techniques
* `part_02_demonstrate_extraction_timing_techniques.ipynb` and `part_02_demonstrate_extraction_timing_techniques.py`

This script and notebook demonstrate the six different matrix extraction techniques. 

















# Option 6: word-length and n least common letters


# Option 1: Full matrix - no objects are returned
    # Option 2: Word-length - returns matrices split by the number of characters
    # Option 3: First letter - returns matrices split by each letter
    # Option 4: Single-least common letter - return matrices split by each letter
    # Option 5: n least common letters - return matrices split by least common letters
    # Option 6: word-length and n least common letters - return matrices split by least common letters and word length.














represents the count of letters 





## TRANSFORM




AND LOAD
Each of the four techniques in part_02 v1 will produce the same data using different data structuring and access techniques. Part_02 v2 will use the same techinuqe in v1, but will examine groups of words. NumPy is incredibly versatile and can do many things. These vignettes showcase how to take advantage of its tools and optimize data processing. The result is that technique 1 takes about 120 minutes to complete while technique 4 takes about 6 minutes to complete. The technique in v2 takes a little over 2 minutes to complete. Each technique in v1 will generate approximately 124M from word / to word pairs. The technique in v2 will generate approximately 73M from word group / to word group pairs, a reduction in storage by 41-percent.
3. part_02_generate_and_store_anagrams_v1.0.ipynb - Use NumPy to perform matrix opertions and determine from/to word relationships. Four different processing techniques are available, growing in complexity with option 1 being the least complex and taking the most time to complete while option 4 is the most complex and completes in the shortest amount of time. 
Processing Technique 1: Perform calculations on the entire matrix.
Processing Technique 2: Create sub-matrices split by word length.
Processing Technique 3: Create sub-matrices split by word-length and presence of a focal letter.
Processing Technique 4: Create sub-matrices split by word-length and presence of two (or more) least common letters.
4. part_02_generate_and_store_anagrams_v2.0.ipynb - Use NumPy to perform matrix opertions and determine from/to word group relationships. The techniques creates sub-matrices similar to processing technique 4 in version 1.0, but uses word groups instead of individual words. For example, by identifying the 'emit' word group (emit, item, mite, and time), and the parent words for 'emit', the parent words are simultaneously determined for 'item', 'mite', and 'time'. 
## Query the stored data
5. part_03_query_anagram_database_v1.0.ipynb - Query the SQLite database to extract a set of anagrams. Makes use of words.
6. part_03_query_anagram_database_v2.0.ipynb - Query the SQLite database to extract a set of anagrams. Makes use of word groups.
7. part_04_add_database_indices_v1.0.ipynb - Add indices to the anagrams table to decrease data access time.
8. part_04_add_database_indices_v2.0.ipynb - Add indices to the anagram_groups table to decrease data access time.
9. part_05_build_a_graph_v1.0.ipynb - Create a graph object using the NetworkX python library, save to a Gephi graph file format for visualization.
10. part_05_build_a_graph_v2.0.ipynb - Create a graph object using the NetworkX python library, save to a Gephi graph file format for visualization.
11. part_06_visualize_processing_time_v1.0.R - Use R to connect to a SQLite db, query data, and plot data. 
12. part_06_visualize_processing_time_v2.0.R - Use R to connect to a SQLite db, query data, and plot data. Limits the visualization to only examine words unique word groups.


_run_constants.py
part_00_file_db_utils.py
part_00_process_functions.py


part_02_demonstrate_extraction_timing_techniques.ipynb
part_02_demonstrate_extraction_timing_techniques.py*

part_03_generate_and_store_anagrams.ipynb
part_03_generate_and_store_anagrams.py*

part_04_query_anagram_database.ipynb
part_05_add_database_indices.ipynb
part_06_build_a_graph.ipynb
part_07_run_parts_01_02_and_03.ipynb
part_07_run_parts_01_02_and_03.py*
part_08_visualize_processing_time_v2.1.R
run_part_01_structure_data.bat
run_part_02_demonstrate_extraction_timing_techniques.bat
run_part_03_generate_and_store_anagrams.bat


### EXTRA VISUALS
two graphs: one by word length, one by starting character
For each technique: the average difference between the search space and the number of candidates

We also need to compare the reduction in search when compared to MEO 1


## EXTRA TEXT
Another way to express the efficiency gains from using the least common letter as opposed to the starting letter is to count the total number of comparisons by method by starting letter. 
![Letter difference](/assets/meo_4_letter_lookup_diff.png)
For words that start with letter 'a', there are approximatelhy 2/3 fewer comparisons when implementing matrix extraction option 4 over matrix extraction option 3.

# Finding Anagrams: v2.0
# September 2, 2024
Find and store from/to word relationships using Python, NumPy, Pandas, and SQLite

# Introduction
This workshop uses python and the NumPy, Pandas, and SQLite libraries to discover and store anagrams found in a list of English words. The main focus of this workshop is to show how NumPy's arrays and other python objects can be used to Extract, Transform, and Load (ETL) data into a SQLite database. In addition, there is an R-script showcasing how to use R to connect to a SQLite database, gather data, and create several simple visualizations.

While version 1.0 of this workshop made use of individual words, version 2.0 makes use of word groups. There are approximately 234K unique words and approximately 215K unique word groups in the initial dataset. A word group is defined as a group of words all containing the same letters: emit, item, mite, and time, for example. 

This workshop was built for beginners - people very new to python - and progresses to demonstrations advanced data processing techniques. To that end, there are six different data processing techniques - referred to as matrix extraction options throughout the workshop - that demonstrate how processing the same data can take 90+ minutes or as little five minutes. Each of the six different processing techniques produce the same output, the difference is how the data processing and retrieval is subdivided. 

Where applicable, there are Jupyter Notebooks and python scripts that demonstrate the same process flow. The notebooks are more interactive while the python scripts can be run from the command line. In general, the notebooks and scripts start out less complex and become more complex. For example, part_01 features more interactivity (calls to `print` and `pd.DataFrame.head()`) and descriptions of operations and objects(dictionaries and matrices, for example) than part_03. Each part builds upon the previous part(s). 

## SETUP
0. _run_constants.py - Input and output file names and paths. All subsequent scripts reference the paths defined in this file. Paths and names only need to be set once, in this file. 
1. part_00_file_db_utils.py - Code reuse for parts 1 through 7. These are mostly I/O and utility functions.
2. part_00_process_functions.py - Code reuse for parts 1 through 7. These functions peform the data processing and are called in subsequent parts. The reason for this structure is for code reuse, efficient optimization and debugging, and generally writing less code. Effectively, we can efine the function once and import it.


## EXTRACT



0. part_00_process_functions.py
1. part_01_generate_char_matrix_v1.0.ipynb - load a list of words, perform several calculations and data creation steps, and store the results.
2. part_01_generate_char_matrix_v2.0.ipynb - load a list of words, perform several calculations and data creation steps, and store the results. Fixes a bug in v1 that generated incorrect word_group_id values and updates several sqlite tables. 
## TRANSFORM AND LOAD
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

part_01_structure_data.ipynb
part_01_structure_data.py*

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

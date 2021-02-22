# finding_anagrams
# February 22, 2021
Find and store from/to word relationships using Python, NumPy, Pandas, and SQLite

# Introduction
This workshop uses python and the NumPy, pandas, and SQLite libraries to discover and store anagrams found in a list of English words. The main focus of this workshop is to show how NumPy's arrays and other python objects can be used to Extract, Transform, and Load (ETL) data into a SQLite database. In addition, there is an R-script showcasing how to use R to connect to a SQLite database, gather data, and create several simple visualizations. Finally, there is an additional python script showcasing how to use NumPy and PIL to produce a VERY SIMPLE visualization of the Mandelbrot set. 

## EXTRACT
0. part_00_process_functions.py - Code reuse for parts 1 through 5.
Several functions are called in multiple scripts. Define the function once and import it.
1. part_01_generate_char_matrix.ipynb - load a list of words, perform several calculation and data creation steps, and store the results.
## TRANSFORM AND LOAD
Each of the four techniques in part_02 will produce the same data using different data structuring and access techniques. NumPy is incredibly versatile and can do many things. These vignettes showcase how to take advantage of its tools and optimize data processing. The result is that technique 1 takes ~120 minutes to complete while option 4 takes ~6 minutes to complete. 
2. part_02_generate_and_store_anagrams_v1.0.ipynb - Use NumPy to perform matrix opertions and determine from/to and words relationships. Four different processing techniques to chose from, growing in complexity with option 1 being the least complex and taking the most time to complete while option 4 is the most complex and completes in the shortest amount of time. 
Processing Technique 1: Perform calculations on the entire matrix.
Processing Technique 2: Create sub-matrices split by word length.
Processing Technique 3: Create sub-matrices by word-length and presence of a focal letter.
Processing Technique 4: Create sub-matrices by word-length and presence of two (or more) least common letters.
## Query the stored data
3. part_03_query_anagram_database.ipynb - Query the SQLite database to extract a set of anagrams.
4. part_04_add_database_indices.ipynb - Add indices to the anagram table to decrease data access time.
5. part_05_build_a_graph.ipynb - Create a graph object using the NetworkX python library, save to a Gephi graph file format for visualization.
6. part_06_visualize_processing_time.R - Use R to connect to a SQLite db, query data, and plot data.
## Extra
7. simple_fractal.ipynb - Use NumPy and PIL to create a simple visualization of the Mandelbrot set.

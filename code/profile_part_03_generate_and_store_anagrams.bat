rem: Windows batch file to profile the functions for part 03
rem: Mike Babb  
rem: babb.mike@outlook.com

rem: USE THE SAME CONDA ENVIRONMENT YOU USED TO CREATE THE FUNCTIONS FOR PART 01

rem: use cProfile to view how long things take to execute
python -m cProfile -o ..\graphics\part_03.prf part_03_generate_and_store_anagrams.py

rem: load the viewer
snakeviz ..\graphics\part_03.prf

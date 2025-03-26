rem: Windows batch file to profile the functions for part 02
rem: Mike Babb  
rem: babb.mike@outlook.com

rem: USE THE SAME CONDA ENVIRONMENT YOU USED TO CREATE THE FUNCTIONS FOR PART 01

rem: use cProfile to view how long things take to execute
python -m cProfile -o ..\graphics\part_02.prf part_02_demonstrate_extraction_timing_techniques.py

rem: load the viewer
snakeviz ..\graphics\part_02.prf


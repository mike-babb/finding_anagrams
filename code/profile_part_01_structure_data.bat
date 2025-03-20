rem: Windows batch file to profile the functions for part 01
rem: Mike Babb  
rem: babb.mike@outlook.com

rem: USE THE SAME CONDA ENVIRONMENT YOU USED TO CREATE THE FUNCTIONS FOR PART 01

rem: use cProfile to view how long things take to execute
python -m cProfile -o ..\graphics\part_01.prf part_01_structure_data.py

rem: load the viewer
snakeviz ..\graphics\part_01.prf

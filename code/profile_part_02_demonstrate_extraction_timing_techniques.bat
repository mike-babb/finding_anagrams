rem: Windows batch file to profile the functions for part 02
rem: Mike Babb  
rem: babb.mike@outlook.com


rem: use cProfile to view how long things take to execute
C:\Users\babbm\Anaconda3\envs\analysis\python.exe -m cProfile -o part_02.prf part_02_demonstrate_extraction_timing_techniques.py

rem: load the viewer
snakeviz part_02.prf


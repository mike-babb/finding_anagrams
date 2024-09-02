rem: use cProfile to view how long things take to execute
C:\Users\babbm\Anaconda3\envs\analysis\python.exe -m cProfile -o part_03.prf part_03_generate_and_store_anagrams.py

rem: load the viewer
snakeviz part_03.prf

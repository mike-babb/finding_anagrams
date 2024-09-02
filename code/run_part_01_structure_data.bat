rem: use cProfile to view how long things take to execute
C:\Users\babbm\Anaconda3\envs\analysis\python.exe -m cProfile -o part_01.prf part_01_structure_data.py

rem: load the viewer
snakeviz part_01.prf

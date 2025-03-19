rem: Windows batch file to generate call graphs of the functions across parts all *.py scripts
rem: Mike Babb  
rem: babb.mike@outlook.com

rem: generate a call graph as an SVG image
pyan3 *.py --uses --no-defines --colored --grouped --annotated --dot-rankdir "LR" --svg > "H:\git\finding_anagrams\graphics\all_parts_call_graph.svg"

rem: generate a call graph as an interactive html file
pyan3 *.py --uses --no-defines --colored --grouped --annotated --dot-rankdir "LR" --html > "H:\git\finding_anagrams\graphics\all_parts_call_graph.html"
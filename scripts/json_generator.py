import json 
import sys
import gzip 
from distutils import util
from pathlib import Path
import random
import string
if __name__ == '__main__':
    file_name = sys.argv[1]
    file_num = (int) (sys.argv[2])
    folder_name = Path(sys.argv[3])
    with open(file_name, 'r') as input: 
        input = input.read()
        lang = "cpp" if file_name[-6:] != 'MASK.c' else "c_obfuscated"
        
        x = {
            "repo_name": f"anghabench{file_num}/{''.join(random.choice(string.ascii_lowercase) for i in range(5))} ",
            "path": file_name,  
            "language": lang,
            "content": input
        }
        y = json.dumps(x) 
        
        json_file_name = folder_name.joinpath(f"{lang}/{lang}.{'{:03d}'.format(file_num)}.json.gz")
        # if not json_file_name.is_dir():
        #     print("alksndfandkaln klfand")
        #     outF = gzip.open(json_file_name, "wt")
        # else: 
        outF = gzip.open(json_file_name, "a")
        outF.write((y+'\n').encode())
        # outF.write()
        outF.close()
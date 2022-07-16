import gzip
import json
import os 
import subprocess
from pathlib import Path
from multiprocessing import Pool, Manager
import multiprocessing
import time
split_json_file_num = 10000 
def compile(i, c_name): 
    if i % split_json_file_num == 0: 
        print(f"we r on {i} index",flush=True)
    c_name = str(c_name)
    assert os.path.isfile(c_name), c_name
    llvm_name = c_name[:-2]+'.ll'
    result = subprocess.run(f"clang {c_name} -w -femit-all-decls -S -emit-llvm -o {llvm_name}", shell=True, 
                            stdout=subprocess.PIPE, stderr=subprocess.PIPE, executable='/bin/bash')
    if result.stdout.decode('UTF-8') != '': 
        print(result.stdout.decode('UTF-8'), flush=True)
    if result.stderr.decode('UTF-8').find("error:") != -1: 
        print(result.stderr.decode('UTF-8')[:result.stderr.decode('UTF-8').index('\n')], flush=True)
        return 1
    else: 
        result = subprocess.run(f"python /home/carl/TransCoder/scripts/json_generator.py {c_name} placeholder {(int)(i/split_json_file_num)} 1 anghabench", shell=True, 
                                stdout=subprocess.PIPE, stderr=subprocess.PIPE, executable='/bin/bash')
        if result.stderr.decode('UTF-8') != '': 
            print(result.stderr.decode('UTF-8'), flush=True)
        result = subprocess.run(f"python /home/carl/TransCoder/scripts/json_generator.py {llvm_name} placeholder {(int)(i/split_json_file_num)} 0 anghabench", shell=True, 
                stdout=subprocess.PIPE, stderr=subprocess.PIPE, executable='/bin/bash')
        if result.stderr.decode('UTF-8') != '': 
            print(result.stderr.decode('UTF-8'), flush=True)
        if result.stdout.decode('UTF-8') != '': 
            print(result.stdout.decode('UTF-8'), flush=True)
        return 0 
        

if __name__ == '__main__':
    file_names = Path('/home/carl/AnghaBench').rglob('*.c')
    file_names = list(file_names)
    print(f"total number{len(file_names)}")
    for i,file in enumerate(file_names): 
        print(file)
        if i == 5: 
            break
    folder_name = Path(f"/home/carl/TransCoder/data/anghabench/")
    for lang in ['cpp','llvm']:
        if not folder_name.is_dir(): 
            folder_name.mkdir()
        if not folder_name.joinpath(lang).is_dir():
            folder_name.joinpath(lang).mkdir()
        for i in range(int(len(file_names)/split_json_file_num) + 1):
            outF = gzip.open(folder_name.joinpath(f"{lang}/{lang}.{'{:03d}'.format(i)}.json.gz"), "w") 
            outF.close()
    
    with Pool(processes=60) as pool:
        results = pool.starmap(compile,enumerate(file_names))
        # results = [result.get() for result in results]
        # fail_count = 0
        # for each in results: 
        #     fail_count += each
        # print(f"fail count {fail_count}")
        # print(f"successful count {len(list(file_names)) - fail_count}")
        
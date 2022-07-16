import gzip
import json
import os 
import subprocess
from pathlib import Path
from multiprocessing import Pool, Manager
import multiprocessing
import time
import psutil
split_json_file_num = 20000 
folder_name = Path(f"/home/carl/CodeGen/data/anghabench3")
def compile(i, c_name): 
    if i % split_json_file_num == 0: 
        print(f"we r on {i} index",flush=True)
    c_name = str(c_name)
    if c_name[-7:] == '_MASK.c':
        return 0
    #print(psutil.Process().cpu_num(), c_name, flush=True)
    cpu_num = multiprocessing.current_process().name.split('-')[1]
    result = subprocess.run(f"python /home/carl/CodeGen/scripts/json_generator.py {c_name} {cpu_num} {folder_name}", shell=True, 
                            stdout=subprocess.PIPE, stderr=subprocess.PIPE, executable='/bin/bash')
    if result.stderr.decode('UTF-8') != '': 
            print(result.stderr.decode('UTF-8'), flush=True)

    obs_name = c_name.replace("AnghaBench","AnghaBench_pre_masked")[:-2]+"_MASK.c"
    result = subprocess.run(f"python /home/carl/CodeGen/scripts/json_generator.py {obs_name} {cpu_num} {folder_name}", shell=True, 
                            stdout=subprocess.PIPE, stderr=subprocess.PIPE, executable='/bin/bash')
    if result.stderr.decode('UTF-8') != '': 
            print(result.stderr.decode('UTF-8'), flush=True)
    return 0 
        

if __name__ == '__main__':
    file_names = set(Path('/home/carl/AnghaBench').rglob('*.c'))
    print(len(file_names))
    file_names = list(file_names  - set(Path('/home/carl/AnghaBench').rglob('*MASK*')))
    print(len(file_names))
    # count = 0 
    # count2 = 0 
    # for file in file_names: 
        
    #     if str(file)[-7:] == '_MASK.c':
    #         print(file)
    #         count +=1 
    #     name = str(file).replace("AnghaBench","AnghaBench_pre_masked")[:-2]+"_MASK.c"
    #     if  not os.path.isfile(name): 
    #         count2+=1 
    # print(count, count2)   
    # assert count == count2

    print(f"total number{len(file_names)}")
    for i,file in enumerate(file_names): 
        print(file_names[i])
        # print(masked_file_names[i])
        # assert(os.path.exists(masked_file_names[i]))
        if i == 5: 
            break
    for lang in ['cpp','c_obfuscated']:
        if not folder_name.is_dir(): 
            folder_name.mkdir()
        if not folder_name.joinpath(lang).is_dir():
            folder_name.joinpath(lang).mkdir()
        for i in range(multiprocessing.cpu_count()):
            outF = gzip.open(folder_name.joinpath(f"{lang}/{lang}.{'{:03d}'.format(i)}.json.gz"), "w") 
            outF.close()
    
    with Pool(processes=multiprocessing.cpu_count()) as pool:
        results = pool.starmap(compile,enumerate(file_names))


    # #    results = pool.starmap(compile,enumerate(masked_file_names))
    # #     # results = [result.get() for result in results]
    # #     # fail_count = 0
    #     # for each in results: 
    #     #     fail_count += each
    #     # print(f"fail count {fail_count}")
    #     # print(f"successful count {len(list(file_names)) - fail_count}")
        
import gzip
import json
import os 
import subprocess
from pathlib import Path
from multiprocessing import Pool, Manager
import multiprocessing
import time
import numpy as np
import re

def find(llvm_names): 
    #print(f"llvm_names{llvm_names}", flush=True)
    d = dict()
    for i in range(len(llvm_names)):
        with open(llvm_names[i], 'r') as p: 
            p = p.read()
            array = re.findall('(?<= load\s)(\w+)',p)
            #print(f"array{array}",flush=True)
            for word in array:
                if word in set(['kernel','DMA','map','address','journal','firmware']):
                    print(p)
                if word not in set(['half', 'bfloat', 'float', 'double', 
                    'fp128', 'x86_fp80', 'ppc_fp128', 'x86_amx', 'x86_mmx','void']) and re.fullmatch("i\d+", word) == None: 
                    if word not in d.keys():
                        d[word] = 1
                    else:
                        d[word] += 1
    d = sorted(d.items(), key=lambda x: x[1], reverse=True)
    print(f"dict{d}",flush=True)

if __name__ == '__main__':
    file_names = Path('/home/carl/AnghaBench').rglob('*.ll')
    file_names = np.array(list(file_names))
    # print(f"total number{len(file_names)}")
    file_names = np.array_split(file_names, 60)
   # print(file_names)
    folder_name = Path(f"/home/carl/TransCoder/data/anghabench/")
    with Pool(processes=60) as pool:
        results = pool.map(find,file_names)

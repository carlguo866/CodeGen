import gzip
import json
import os 
import subprocess
from pathlib import Path
from multiprocessing import Pool, Manager
import multiprocessing
import time
def execute(json_file): 
    with gzip.open(json_file, "r") as f:
        data = f.readlines()
        i = 0 
        success_count = 0 
        print(f"{json_file} in total {len(data)}",flush=True)
        json_file_string = json_file.stem[:json_file.stem.index('.')]
        json_folder = f"temp/{json_file_string}"
        if not os.path.exists(json_folder): 
            os.mkdir(json_folder)
        
        fail_dict = dict()
        for i in range(200):
            item = data[i].decode("utf-8")
            item = json.loads(item)
            try: 
                file_name = f"temp/{json_file_string}/{item['path'][item['path'].rindex('/'):]}"
            except: 
                file_name = f"temp/{json_file_string}/{item['path']}"
            writer = open(file_name, "w")
            try: 
                writer.write(item['content'])
            except: 
                print(f"dont have any content {item}")
            writer.close()
            result = subprocess.run(f"clang {file_name} -w -s -I/home/carl/linux-5.10.85/include", shell=True, 
                                stdout=subprocess.PIPE, stderr=subprocess.PIPE, executable='/bin/bash')
            
            if result.stderr.decode('UTF-8') != '': 
                error_msg = result.stderr.decode('UTF-8')
                error_msg = error_msg[:error_msg.index('\n')]
                if error_msg.find('fatal error: ') != -1 and error_msg.find('file not found') != -1:
                    file_needed = error_msg[error_msg.index('fatal error: ')+14:error_msg.index(' file not found')-1]
                    if file_needed == 'config.h': 
                        print(open(file_name,'r').read())
                    if file_needed in fail_dict.keys(): 
                        fail_dict[file_needed] +=1 
                    else: 
                        fail_dict[file_needed] = 1
            else: 
                success_count += 1
            if i % 1000 == 0: 
                print(f"index: {i}",flush=True)
        print(f"{json_file} success_count{success_count}",flush=True)
        result = sorted(fail_dict.items(), key=lambda x: x[1], reverse=True) 
        print(f"file_dict{result}", flush=True)
        with open('result.txt','a') as p:
            p.write(f"{file_name} {result}\n") 
        return success_count, result
if __name__ == '__main__':
    data_folder = Path('/home/carl/datasets/')
    json_files = list(data_folder.glob("withstar*"))
    total_dict = dict()
    print(json_files)
    with Pool(processes=60) as pool:
        results = [pool.apply_async(execute, args=(json_file,)) for json_file in json_files]
        total_success_count = 0 
        dicts = list()
        for result in results: 
            result = result.get()
            total_success_count += result[0]
            dicts.append(result[1])
        

        print("done with compiling; summarizing results",flush=True)
        start = time.time()
        for file_dict in dicts:
            print(f"file_dict{file_dict}",flush=True)
            for k,v in file_dict: 
                if k in total_dict.keys(): 
                    total_dict[k] += v
                else: 
                    total_dict[k] = v
        end = time.time()
        print(f"time: {end-start}",flush=True)
        print(f"total_success_count{total_success_count}")
    total_dict = sorted(total_dict.items(), key=lambda x: x[1], reverse=True) 
    print(total_dict)
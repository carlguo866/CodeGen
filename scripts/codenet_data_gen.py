import csv 
import os 
import subprocess 
import time 
if __name__ == '__main__': 
    row_num = {
        'submission_id': 0, 
        'problem_id': 1, 
        'language': 4, 
        'status': 7
    }
    num_in_json_file = 1
    json_num = 1
    start = time.time()
    for num in range(0, 4053):
        print(num)
        with open(f'/home/carl/Project_CodeNet/metadata/p{"{:05d}".format(num)}.csv') as csv_file:   
            csv_reader = csv.reader(csv_file, delimiter=',')
            for row in csv_reader: 
                if row[row_num['language']] == 'C' and row[row_num['status']] == 'Accepted': 
                    c_name = f"/home/carl/Project_CodeNet/data/{row[row_num['problem_id']]}/C/{row[row_num['submission_id']]}.c" 
                    assert os.path.isfile(c_name), c_name
                    llvm_name = c_name.replace('.c', '.ll')
                    result = subprocess.run(f"python /home/carl/TransCoder/csmith_wrapper.py {c_name}", shell=True, 
                                stdout=subprocess.PIPE, stderr=subprocess.PIPE, executable='/bin/bash')
                    if result.stdout.decode('UTF-8') != '': 
                        print(result.stdout.decode('UTF-8'), flush=True)
                    if result.stderr.decode('UTF-8') != '': 
                        print(result.stderr.decode('UTF-8'), flush=True)
                    result = subprocess.run(f"clang {c_name} -w -femit-all-decls -S -emit-llvm -o {llvm_name}", shell=True, 
                            stdout=subprocess.PIPE, stderr=subprocess.PIPE, executable='/bin/bash')
                    if result.stderr.decode('UTF-8') == '': 
                        result = subprocess.run(f"python /home/carl/TransCoder/preprocessing/src/json_generator.py {c_name} {num_in_json_file} {json_num} 1 codenet {row[row_num['problem_id']]} {row[row_num['submission_id']]}", shell=True, 
                                stdout=subprocess.PIPE, stderr=subprocess.PIPE, executable='/bin/bash')
                        if result.stdout.decode('UTF-8') != '': 
                            print(result.stdout.decode('UTF-8'), flush=True)
                        if result.stderr.decode('UTF-8') != '': 
                            print(result.stderr.decode('UTF-8'), flush=True)
                        result = subprocess.run(f"python /home/carl/TransCoder/preprocessing/src/json_generator.py {llvm_name} {num_in_json_file} {json_num} 0 codenet {row[row_num['problem_id']]} {row[row_num['submission_id']]}", shell=True, 
                                stdout=subprocess.PIPE, stderr=subprocess.PIPE, executable='/bin/bash')
                        if result.stdout.decode('UTF-8') != '': 
                            print(result.stdout.decode('UTF-8'), flush=True)
                        if result.stderr.decode('UTF-8') != '': 
                            print(result.stderr.decode('UTF-8'), flush=True)
                        num_in_json_file+=1 
                        if num_in_json_file >= 5000: 
                            num_in_json_file = 1
                            json_num +=1
                    else:
                        print(result.stderr.decode('UTF-8'), flush=True)
    end = time.time()
    print(f"time: {end-start}")

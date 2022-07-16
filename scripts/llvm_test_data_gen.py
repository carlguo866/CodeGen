import os 
import subprocess
if __name__ == '__main__': 
    llvm_files = list()
    for (dirpath, dirnames, filenames) in os.walk('/home/carl/llvm-project-tok/llvm/test'):
        llvm_files += [os.path.join(dirpath, file) for file in filenames if file[-3:] == '.ll']
    print(f"len(llvm_files){len(llvm_files)}")


    c_codegen_files = list()
    for (dirpath, dirnames, filenames) in os.walk('/home/carl/llvm-project-tok/clang/test/CodeGen'):
        c_codegen_files += [os.path.join(dirpath, file) for file in filenames if file[-2:] == '.c']
    print(f"len(c_codegen_files){len(c_codegen_files)}")

    c_files = list()
    for (dirpath, dirnames, filenames) in os.walk('/home/carl/llvm-project-tok/clang/test'):
        c_files += [os.path.join(dirpath, file) for file in filenames if file[-2:] == '.c']
    print(f"len(c_files){len(c_files)}")

    test_suite_files = list()
    for (dirpath, dirnames, filenames) in os.walk('/home/carl/test-suite'):
        test_suite_files += [os.path.join(dirpath, file) for file in filenames if file[-2:] == '.c']
    print(f"len(test_suite_files){len(test_suite_files)}")

    count = 0
    for c_name in test_suite_files:
        llvm_name= f'/home/carl/TransCoder/playground/llvm/{c_name[c_name.rindex("/"):-2]}.ll'
        result = subprocess.run(f"clang {c_name} -w -femit-all-decls -S -emit-llvm -o {llvm_name}", shell=True, 
                            stdout=subprocess.PIPE, stderr=subprocess.PIPE, executable='/bin/bash')
        if result.stderr.decode('UTF-8') != '': 
            print(result.stderr.decode('UTF-8'), flush=True)
            count +=1
    print(count)
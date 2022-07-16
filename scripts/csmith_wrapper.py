import sys
import re
if __name__ == '__main__': 
    fn = open(sys.argv[1], 'r').read()
    # fn = fn.replace("int ", "int32_t ")
    outF = open(sys.argv[1], "w")
    if fn.find("stdint.h") == -1: 
        fn = "#include <stdint.h>\n" + fn
    int_count = 0
    for i in range(len(fn)-4): 
        if fn[i:i+4] == 'int ': 
            int_count += 1
            if i > 5 and fn[i-5:i] == 'long ': 
                "avoid replacement long"
            elif i > 6 and fn[i-6:i] == 'short ':
                "avoid replacement short"
            elif i > 8 and fn[i-9:i] == 'unsigned ':
                "avoid replacement unsigned"
            elif i+8<len(fn)-4 and fn[i+4:i+8] == 'main': 
                "avoid main"
            elif i+5<len(fn)-4 and fn[i+4:i+8] == 'long': 
                "avoid long"
            elif i > 1 and fn[i-1] == '_': 
                "variable"
            elif i > 1 and fn[i-1] in set([' ','{','(',';',')']): 
                fn= fn[:i] + fn[i:].replace('int ', 'int32_t ', 1)
            elif i == 0: 
                fn= fn[:i] + fn[i:].replace('int ', 'int32_t ', 1)
    outF.write(fn)
    outF.close()

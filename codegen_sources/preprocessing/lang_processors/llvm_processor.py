from codegen_sources.preprocessing.lang_processors.tokenization_utils import (
    process_string,
)
from codegen_sources.preprocessing.lang_processors.lang_processor import LangProcessor
from codegen_sources.preprocessing.obfuscation.bobskater_obfuscator import (
    obfuscateString,
)
from codegen_sources.preprocessing.obfuscation.utils_deobfuscation import dico_to_string

import tokenize
from io import BytesIO
import re
import pyllvm

uints = frozenset([ pyllvm.lltok.GlobalID, 
                    pyllvm.lltok.LocalVarID, 
                    pyllvm.lltok.AttrGrpID,
                    pyllvm.lltok.SummaryID])

strings = frozenset([pyllvm.lltok.StringConstant,
                pyllvm.lltok.DwarfTag,
                pyllvm.lltok.DwarfAttEncoding,
                pyllvm.lltok.DwarfVirtuality,
                pyllvm.lltok.DwarfLang,
                pyllvm.lltok.DwarfCC,
                pyllvm.lltok.EmissionKind,
                pyllvm.lltok.NameTableKind,
                pyllvm.lltok.DwarfOp,
                pyllvm.lltok.DIFlag,
                pyllvm.lltok.DISPFlag,
                pyllvm.lltok.DwarfMacinfo,
                pyllvm.lltok.ChecksumKind])

class LLVMProcessor(LangProcessor):
    def __init__(self, root_folder=None, simplify=True):
        self.spetoken2char = {
            # "STOKEN00": ";",
            # "STOKEN1": "\\n",
            # "STOKEN2": '"""',
            # "STOKEN3": "'''",
        }
        self.char2spetoken = {
            value: " " + key + " " for key, value in self.spetoken2char.items()
        } 
        self.language = "llvm"  
        self.simplify = simplify

    def process_string(self, tok, char2tok, tok2char, is_comment):
        if is_comment:
            tok = re.sub(' +', ' ', tok)
            tok = re.sub(r"(.)\1\1\1\1+", r"\1\1\1\1\1", tok)
            if len(re.sub(r'\W', '', tok)) < 2:
                return ''
        tok = tok.replace(' ', ' ▁ ')
        tok = tok.replace('\n', ' STRNEWLINE ')
        tok = tok.replace('\t', ' TABSYMBOL ')
        tok = re.sub(' +', ' ', tok)
        # tok = tokenize_v14_international(tok) explore more 
        tok = re.sub(' +', ' ', tok)
        for special_token, char in tok2char.items():
            tok = tok.replace(special_token, char)
        tok = tok.replace('\r', '')
        return tok


    
    def get_tokens_and_types(self, s):
        try: 
            assert isinstance(s, str)
            lex = pyllvm.lexer(s)
            isFirst = True; 
            tokens = [] 
            toktypes = []
            while True:
                if isFirst:
                    toktype, tok = lex.getFirstTok()
                    isFirst = False 
                else: 
                    toktype, tok = lex.getTok()
                tok = tok.strip()
                if(tok != ''): 
                    tokens.append(tok)
                
                if len(toktypes) >= 1: 
                    #clean ; comments
                    if(toktypes[-1] == pyllvm.lltok.rbrace):
                        tokens[-1] = "}"
                    elif (toktypes[-1] == pyllvm.lltok.APSInt):
                        tokens[-1] = str(re.findall(r"-*\d+",tokens[-1])[0])
                    elif toktypes[-1] == pyllvm.lltok.LabelID:
                        tokens[-1] = re.findall(r"\d+",tokens[-1])[0] + ":"
                    elif toktypes[-1] in uints:
                        tokens[-1] = str(tokens[-1][0]) + re.findall(r"\d+",tokens[-1])[0] 
                    elif toktypes[-1] in strings:
                        try:
                            tokens[-1] = self.process_string(tokens[-1], self.spetoken2char, self.char2spetoken, False)
                        except UnicodeDecodeError:
                            print(tokens[-1])
                    #remove packed struct
                    elif (len(tokens)>=2 and tokens[-1] == ">"
                        and tokens[-2] == "}"):
                        del tokens[-1]; del toktypes[-1]
                    elif (len(tokens)>=2 and tokens[-1] == "{"
                        and tokens[-2] == "<"):
                        del tokens[-2]; del toktypes[-2]   
                    elif tokens[-1][0] == "#": 
                        del tokens[-1]; del toktypes[-1]
                    elif tokens[-1] == 'internal': 
                        del tokens[-1]; del toktypes[-1]
        
                    if len(tokens) >=2 and tokens[-2] == "align" and re.findall(r"-*\d+",tokens[-1]) != None: 
                        if len(tokens) >=3 and tokens[-3] == ',': 
                            del toktypes[-3:]
                            del tokens[-3:] 
                        else: 
                            del toktypes[-2:]
                            del tokens[-2:] 

                    if toktype == pyllvm.lltok.Eof:
                        return tokens, toktypes
                    elif toktype == pyllvm.lltok.Error: 
                        print("an pyllvm.lltok.Error error in get_llvm_tokens_and_types")
                        return tokens, toktypes
                    toktypes.append(toktype)
        except Exception as e:
            print(f"unknown error in try except {e}")
            return [], [] 

    def get_one_toktype(self, s): 
        assert isinstance(s, str) and s.strip().find(" ") == -1
        lex = pyllvm.lexer(s)
        toktype = lex.getTokType() 
        return toktype 
    
    def infix_to_prefix(self,tokens): 
        try: 
            if isinstance(tokens, str): 
                tokens = tokens.split(' ')
            assert isinstance(tokens, list)
            prefix = [] 
            par = 0
            pars = [0] * 100
            position = dict()
            for i in range(len(tokens)):
                tok = tokens[i] 
                if tok == '[' or tok == '{': 
                    pars[par]+=1
                    par+=1 
                    position[par] = len(prefix)
                    prefix.extend(['placeholder','placeholder'])
                elif tok == '(': 
                    pars[par]+=1
                    par+=1 
                    position[par] = len(prefix)
                    prefix.append(tok)
                elif (tok == ']' or tok == '}') and par > 0: 
                    prefix[position[par]] = f"ARR" if tok == ']' else f"STRUCT"
                    prefix[position[par]+1] = str(pars[par])
                    pars[par] = 0
                    par-=1 
                elif tok == ')': 
                    pars[par] = 0
                    par-=1 
                    prefix.append(tok)
                elif tok == ",": 
                    if par == 0 or prefix[position[par]] == '(':  
                        prefix.append(tok)       
                elif tok == '*': 
                    pos = 0 
                    if self.get_one_toktype(tokens[i-1]) in set([pyllvm.lltok.LocalVar,pyllvm.lltok.Type]): 
                        pos = -1
                    elif tokens[i-1] == ']' or tokens[i-1] == '}' or tokens[i-1] == ')': 
                        pos = position[par+1]
                    elif tokens[i-1] == '*': 
                        index = i-1
                        while tokens[index-1] == '*': 
                            index-=1
                        if self.get_one_toktype(tokens[index-1]) in set([pyllvm.lltok.LocalVar,pyllvm.lltok.Type]): 
                            pos = -1
                        elif tokens[index-1] == ']' or tokens[index-1] == '}':
                            pos = position[par+1]
                    prefix.insert(pos, tok)
                else: 
                    prefix.append(tok)
                    pars[par]+=1
                
            if par == 0:
                return prefix
            else: 
                print(f"par != 0 in infix to prefix at {str(tokens)}", flush=True)
                return tokens  
        except: 
            print(f"error in infix to prefix at {str(tokens)}", flush=True)
            return tokens  

    def get_type(self, tokens, i, add_comma=0):
        #add_comma: 1 means only types; 2 means with value
        try: 
            ty = []
            word_types = set(['half', 'bfloat', 'float', 'double', 
                        'fp128', 'x86_fp80', 'ppc_fp128', 'x86_amx', 'x86_mmx','void'])
            if tokens[i] in word_types:
                ty.append(tokens[i])
                i+=1
            elif re.fullmatch("i\d+", tokens[i]) != None and (int(tokens[i][1:])==1 or int(tokens[i][1:]) %8 == 0): 
                ty.append(tokens[i])
                i+=1
            elif tokens[i][0] == '%' and re.fullmatch("%\d+", tokens[i]) == None: 
                ty.append(tokens[i])
                i+=1
            elif tokens[i] == '[' or tokens[i] == '{': 
                par = 0
                pars = dict()
                while i < len(tokens): 
                    if tokens[i] == '[' or tokens[i] == '{': 
                        if len(ty) >= 1 and ty[-1] not in set(['[','{','x','(',',', 'to']): 
                            if add_comma == 1: 
                                ty.append(',')
                            elif add_comma == 2 and pars[par] %2 == 0: 
                                ty.append(',')
                        if par != 0: pars[par] +=1
                        par+=1 
                        pars[par] = 0
                    elif tokens[i] == ']' or tokens[i] == '}': 
                        par-=1
                    toktype = self.get_one_toktype(tokens[i])
                    if par != 0 and (tokens[i] in set(['c','zeroinitializer','undef,null']) or tokens[i][0] =='@'): 
                        pars[par] +=1
                    if add_comma > 0 and par != 0 and toktype == pyllvm.lltok.Type and ty[-1] not in set(['[','{','x','(','to', ',']): 
                        ty.append(',')
                    ty.append(tokens[i])

                    if add_comma ==2 and tokens[i] == 'getelementptr': 
                        i+=1
                        if tokens[i] == 'inbounds': i+=1 ; ty.append("inbounds")
                        if tokens[i] == '(': i+=1 ; ty.append("(")
                        ty2, i = self.get_type(tokens, i, add_comma=1)
                        ty.extend(ty2)
                        ty2 = [','] + ty2 + ['*']
                        ty.extend(ty2)
                        i-=1

                    i+=1
                    if par==0: 
                        # one token after ] or }s
                        break
            elif tokens[i] == '<': 
                par = 0
                while i < len(tokens): 
                    if tokens[i] == '<': 
                        par +=1 
                    elif tokens[i] == '>': 
                        par -=1 
                    ty.append(tokens[i])
                    i+=1 
                    if par == 0: 
                        break

            while i < len(tokens) and tokens[i] == '*':
                ty.append(tokens[i])
                i+=1

            if i < len(tokens) and tokens[i] == '(': 
                par = 0
                while i < len(tokens): 
                    if tokens[i] == '(': 
                        par +=1 
                    elif tokens[i] == ')': 
                        par -=1 
                    ty.append(tokens[i])
                    i+=1 
                    if par == 0: 
                        break

            while i < len(tokens) and tokens[i] == '*':
                ty.append(tokens[i])
                i+=1

            return ty, i 
        except:
            print("an error in get_llvm_type" + str(tokens) + "\n" + str(ty) )
            return ty, i

    def get_value(self,tokens, i, detok=False): 
        try: 
            ty = []
            if re.fullmatch("\d+",tokens[i]) != None or re.fullmatch("-\d+",tokens[i]) != None: 
                ty.append(tokens[i])
                i+=1 
            elif tokens[i][0] == '@' or tokens[i][0] == '%': 
                ty.append(tokens[i])
                i+=1
            elif tokens[i] in set(['null','undef','zeroinitializer']): 
                ty.append(tokens[i])
                i+=1
            elif tokens[i] == 'bitcast': 
                ty.append(tokens[i])
                i+=1 
                assert(tokens[i] == '('), f"bitcast ("
                par = 0
                while i < len(tokens): 
                    if tokens[i] == '(': 
                        par+=1 
                    elif tokens[i] == ')': 
                        par-=1
                    elif tokens[i] == 'getelementptr': 
                        ty2, i = self.get_value(tokens,i, detok=detok)
                        ty.extend(ty2)
                        continue
                    ty.append(tokens[i]) 
                    i+=1
                    if par == 0: 
                        break
            elif tokens[i] == 'getelementptr': 
                ty.append(tokens[i]); i+=1
                if tokens[i] == "inbounds":  ty.append(tokens[i]); i+=1
                assert tokens[i] == '(', f"getelementptr ("
                ty.append(tokens[i])
                i+=1
                ty2, i = self.get_type(tokens, i)  
                ty.extend(ty2)
                if detok: 
                    ty.extend([","] + ty2 + ["*"])
                else: 
                    _, i = self.get_type(tokens, i+1) 
                par = 1
                ty2, i = self.get_value(tokens, i, detok=detok)
                ty.extend(ty2)
                while tokens[i] != ')': 
                    ty.append(tokens[i]) 
                    i+=1
                ty.append(tokens[i]); i+=1
            return ty, i 
        except:
            print("an error in get_value" + str(tokens) + f"i = {i}" + "\n" + str(ty) )
            return ty, i
            
    def simplify_printer(self, tokens): 
        if len(tokens)>0 and tokens[0] == 'define': 
            tokens = self.infix_to_prefix(tokens[:-1])
            tokens.append('{')
            return tokens
        if len(tokens)>0 and tokens[0] == 'switch' and tokens[-1] == '[': 
            tokens = self.infix_to_prefix(tokens[:-1])
            tokens.append('[')
            return tokens
        if len(tokens) == 1 and tokens[0] == '}':
            #no infix to prefix
            return tokens

        i = 0 
        par = 0
        while i < len(tokens): 
            if tokens[i] in set(['[', '(', '{']): par +=1 
            elif tokens[i] in set([']', ')', '}']): par -=1

            
            if tokens[i] == 'load': 
                i+=1
                if tokens[i] == 'volatile': i+=1
                __, i = self.get_type(tokens, i) 
            # assert tokens[i] == ',', f"no comma after type {tokens[i]} in {str(tokens)}"
                ty, j = self.get_type(tokens, i+1) 
                del tokens[i:j]
                
            if tokens[i] == 'getelementptr':
                i+=1
                if tokens[i] == 'inbounds': i+=1
                if tokens[i] == '(': 
                    i+=1 
                    par+=1 
                _, i = self.get_type(tokens, i) 
            # assert tokens[i] == ',', f"no comma after type {tokens[i]} in {str(tokens)}"
                ty, j = self.get_type(tokens, i+1) 
                del tokens[i:j]
                i-=1
                
            if tokens[i] == ',' and par == 0 and tokens[0] == 'store': 
                ty, j = self.get_type(tokens, i+1)
                del tokens[i:j]
                i-=1

            if tokens[i] == 'constant' or tokens[i] == 'global': 
                ty, j = self.get_type(tokens, i+1)
                if j < len(tokens):
                    ty2, x = self.get_value(tokens, j)
                    tokens[j:x] = ty2
                    i = x 
                else: 
                    i = j
                
            i+=1
        
        tokens = self.infix_to_prefix(tokens)
        return tokens       




    def tokenize_code(self, code, keep_comments=False, process_strings=True): 
        assert isinstance(code, str)
        code = code.replace(r'\r', '')
        if code.find('attributes #0 = {') != -1: 
            code = code[:code.index('attributes #0 = {')]
        code = re.sub("(.*\n){4}\n","",code, 1)
        arr = code.split('\n')
        tokens = [] 
        total_len = 0 
        for line in arr: 
            line, toktypes_line = self.get_tokens_and_types(line)
            if self.simplify == True:
                line = self.simplify_printer(line)
            tokens.extend(line)
            if len(tokens)>0 and tokens[-1] != "NEW_LINE": 
                tokens.append("NEW_LINE")
        # if self.simplify == True:
        #     tokens = remove_globals(tokens)
       
           


   



#!/bin/bash
set -e
cd /home/carl/CodeGen/data/$1
pwd
#rm *.bpe*
# find -iname "*tok" -delete
find -iname "*dictionary*" -delete
find -iname "*obfuscated*" -delete
# # find -iname "*sa*" -delete
# find -iname "*bpe*" -delete
# find -iname "*monolingual*" -delete
# find -iname "*train*" -delete
# find -iname "*valid*" -delete
# find -iname "*test*" -delete
rm -rf XLM-syml
rm -rf log
# find -iname "*functions_standalone*" -delete
# rm -rf cpp-llvm-
# rm -rf cpp-llvm-.XLM-syml
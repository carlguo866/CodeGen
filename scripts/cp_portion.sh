#!/bin/bash
cd /home/carl/datasets
for i in `ls cpp.*.json.gz`; do 
    NUMBER=$((10#$(echo $i | sed 's/[^0-9]*//g')))
    if [ $(($NUMBER)) -ge 40 ] && [ $(($NUMBER)) -lt 50 ] ; then
        echo $i
        cp $i /home/carl/CodeGen/data/github3
    fi
 done
#!/bin/bash
cd /home/carl/CodeGen/data/github
for i in `ls *.json.tgz`; do mv "$i" "`echo $i | rev | cut -c 4- | rev`gz"; done

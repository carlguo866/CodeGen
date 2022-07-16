cd /home/carl/CodeGen/data/github
for i in `ls *.json.gz`; do mv "$i" "cpp.`echo $i | cut -c 14-`"; done
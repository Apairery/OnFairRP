#!/usr/bin/env bash



#!/usr/bin/env bash



t[0]=0
t[1]=0.008
t[2]=0.04
t[3]=0.2
#a[0]=0.95

for i in `seq ${#t[@]}`
do
    echo "run python main.py --scheme OnFair --runDays 16 17 18 19 20 --a ${t[i-1]}"
    python main.py --scheme OnFair --runDays 16 17 18 19 20 --threshold ${t[i-1]}
done
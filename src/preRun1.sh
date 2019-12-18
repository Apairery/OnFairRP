#!/usr/bin/env bash

a[0]=0.95
a[1]=0.98
a[2]=0.91
a[3]=0.87
a[4]=0.99


for i in `seq ${#a[@]}`
do
    echo "run python main.py --runDays 9 10 11 12 13 --a ${a[i-1]}"
    python main.py --preRun True --runDays 9 10 11 12 13 --a ${a[i-1]}
    echo "run python main.py --runDays 16 17 18 19 20 --a ${a[i-1]}"
    python main.py --preRun True --runDays 16 17 18 19 20 --a ${a[i-1]}
    echo "run python main_normalization.py --a ${a[i-1]}"
    python main_normalization.py --a ${a[i-1]}
done

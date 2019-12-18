#!/usr/bin/env bash


o[0]=0.46
o[1]=0.48
o[2]=0.52
o[3]=0.54
#o[4]=0.5 # default


for j in `seq ${#o[@]}`
do
    echo "run python main.py --runDays 9 10 11 12 13 --omega ${o[j-1]}"
    python main.py --preRun True --runDays 9 10 11 12 13 --omega ${o[j-1]}
    echo "run python main.py --runDays 16 17 18 19 20 --omega ${o[j-1]}"
    python main.py --preRun True --runDays 16 17 18 19 20 --omega ${o[j-1]}
    echo "run python main_normalization.py --omega ${o[j-1]}"
    python main_normalization.py --omega ${o[j-1]}
done
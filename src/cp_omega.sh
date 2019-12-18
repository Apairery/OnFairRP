#!/usr/bin/env bash


o[0]=0.46
o[1]=0.48
o[2]=0.52
o[3]=0.54

for i in `seq ${#o[@]}`
do
    echo "run python main.py --scheme OnFair --runDays 16 17 18 19 20 --omega ${o[i-1]}"
    python main.py --scheme OnFair --runDays 16 17 18 19 20 --omega ${o[i-1]}
    echo "run python main.py --scheme ProfitOnly --runDays 16 17 18 19 20 --a ${o[i-1]}"
    python main.py --scheme ProfitOnly --runDays 16 17 18 19 20 --omega ${o[i-1]}
    echo "run python main.py --scheme FIXED --runDays 16 17 18 19 20 --a ${o[i-1]}"
    python main.py --scheme FIXED --runDays 16 17 18 19 20 --omega ${o[i-1]}

    echo "run python main.py --scheme OnFair_all --runDays 16 17 18 19 20 --a ${o[i-1]}"
    python main.py --scheme OnFair_all --runDays 16 17 18 19 20 --omega ${o[i-1]}

    echo "run python main.py --scheme PAA --runDays 16 17 18 19 20 --a ${o[i-1]}"
    python main.py --scheme PAA --runDays 16 17 18 19 20 --omega ${o[i-1]}
done
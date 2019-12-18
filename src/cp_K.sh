#!/usr/bin/env bash

K[0]=0.02
K[1]=0.07
K[2]=0.33
K[3]=2.71

for i in `seq ${#K[@]}`
do
    echo "run python main.py --scheme OnFair --runDays 16 17 18 19 20 --K ${K[i-1]}"
    python main.py --scheme OnFair --runDays 16 17 18 19 20 --K ${K[i-1]}
    echo "run python main.py --scheme ProfitOnly --runDays 16 17 18 19 20 --K ${K[i-1]}"
    python main.py --scheme ProfitOnly --runDays 16 17 18 19 20 --K ${K[i-1]}
    echo "run python main.py --scheme FIXED --runDays 16 17 18 19 20 --K ${K[i-1]}"
    python main.py --scheme FIXED --runDays 16 17 18 19 20 --K ${K[i-1]}

    echo "run python main.py --scheme OnFair_all --runDays 16 17 18 19 20 --K ${K[i-1]}"
    python main.py --scheme OnFair_all --runDays 16 17 18 19 20 --K ${K[i-1]}

    echo "run python main.py --scheme PAA --runDays 16 17 18 19 20 --K ${K[i-1]}"
    python main.py --scheme PAA --runDays 16 17 18 19 20 --K ${K[i-1]}
done
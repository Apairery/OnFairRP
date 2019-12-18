#!/usr/bin/env bash



a[0]=0.98
a[1]=0.91
a[2]=0.87
a[3]=0.95
a[4]=0.99
#a[0]=0.95


for i in `seq ${#a[@]}`
do
    echo "run python main.py --scheme OnFair --runDays 16 17 18 19 20 --a ${a[i-1]}"
    python main.py --scheme OnFair --runDays 16 17 18 19 20 --a ${a[i-1]}
    echo "run python main.py --scheme ProfitOnly --runDays 16 17 18 19 20 --a ${a[i-1]}"
    python main.py --scheme ProfitOnly --runDays 16 17 18 19 20 --a ${a[i-1]}
    echo "run python main.py --scheme FIXED --runDays 16 17 18 19 20 --a ${a[i-1]}"
    python main.py --scheme FIXED --runDays 16 17 18 19 20 --a ${a[i-1]}

    echo "run python main.py --scheme OnFair_all --runDays 16 17 18 19 20 --a ${a[i-1]}"
    python main.py --scheme OnFair_all --runDays 16 17 18 19 20 --a ${a[i-1]}

    echo "run python main.py --scheme PAA --runDays 16 17 18 19 20 --a ${a[i-1]}"
    python main.py --scheme PAA --runDays 16 17 18 19 20 --a ${a[i-1]}
done
#!/usr/bin/env bash

a[0]=0.99
a[1]=0.98
a[2]=0.91
a[3]=0.87
a[4]=0.95

for i in `seq ${#a[@]}`
do
    echo "run python main_fairness.py --pricingDays 16 17 18 19 20 --a ${a[i-1]}"
    python main_fairness.py --pricingDays 16 17 18 19 20 --a ${a[i-1]}
done


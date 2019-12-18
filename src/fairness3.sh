#!/usr/bin/env bash

K[0]=0.02
K[1]=0.07
K[2]=0.33
K[3]=2.71

for i in `seq ${#K[@]}`
do
    echo "run python main_fairness.py --pricingDays 16 17 18 19 20 --K ${K[i-1]}"
    python main_fairness.py --pricingDays 16 17 18 19 20 --K ${K[i-1]}
done


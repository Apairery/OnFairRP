#!/usr/bin/env bash

#t[0]=0
t[0]=0.008
t[1]=0.04
t[2]=0.2


for i in `seq ${#t[@]}`
do
    echo "run python main_pricing.py --pricingDays 16 17 18 19 20 --threshold ${t[i-1]}"
    python main_pricing.py --pricingDays 16 17 18 19 20 --threshold ${t[i-1]}
done
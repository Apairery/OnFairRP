#!/usr/bin/env bash


o[0]=0.46
o[1]=0.48
o[2]=0.52
o[3]=0.54
#o[4]=0.5 # default

for i in `seq ${#o[@]}`
do
    echo "run python main_pricing.py --pricingDays 16 17 18 19 20 --omega ${o[i-1]}"
    python main_pricing.py --pricingDays 16 17 18 19 20 --omega ${o[i-1]}
#    python main_pricing.py --pricingDays 16 17 18 19 20 --omega ${o[i-1]}
done
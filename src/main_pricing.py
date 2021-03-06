#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from setproctitle import setproctitle as ptitle
from util.arg_parser import init_parser
from pricing.onlineFairRSPricing import onlineFairRSPricing, fairness_metrics
from util.utils import read_others
import numpy as np
from datetime import datetime
import pandas as pd

if __name__ == '__main__':
    print('################ START TIME: {} ################'.format(datetime.now().strftime("%m/%d/%Y, %H:%M:%S")))

    parser = init_parser()
    args = parser.parse_args()
    ptitle('Pri_a{}_K{}_o{}'.format(args.a, args.K, args.omega))

    if not args.OMEGA: OMEGA = np.array([0.4, 0.42, 0.44, 0.46, 0.48, 0.5, 0.52, 0.54, 0.56, 0.58])
    else: OMEGA = [float(i) for i in args.OMEGA]

    if not args.pricingDays: pricingDays = [16, 17, 18, 19, 20] #[0.49, 0.5, 0.51, 0.52]
    else: pricingDays = [int(i) for i in args.pricingDays]

    # li = []
    # for day in pricingDays:
    #     df = pd.read_csv('../data/haikou_10_{}_3km.csv'.format(day))
    #     df = df.sort_values(by=['time_step'], ascending=[True])
    #     li.append(df)
    # all_riders = pd.concat(li, axis=0, ignore_index=True)

    pricing_args = {
        'OMEGA':OMEGA,
        'omega': args.omega,
        'a':args.a,
        'K':args.K,
        'eta_peak':args.eta_peak,
        'eta_off':args.eta_off,
        'sigma': args.sigma, #args.sigma
        'days': pricingDays,
        'threshold': args.threshold
    }


    onlineFairRSPricing(**pricing_args)

    # if len(pricingDays) > 1:
    #     order_file = '../data/haikou_10_{}to{}_3km_default.csv'.format(pricingDays[0], pricingDays[1])
    # else:
    #     order_file = '../data/haikou_10_{}_3km_default.csv'.format(pricingDays[0])
    #
    # fairness_metrics('ProfitOnly',K=args.K, order_file=order_file)

    print('################ END TIME: {} ################'.format(datetime.now().strftime("%m/%d/%Y, %H:%M:%S")))
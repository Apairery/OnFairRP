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
    ptitle('F_a{}_K{}_o{}'.format(args.a, args.K, args.omega))

    if not args.OMEGA: OMEGA = np.array([0.4, 0.42, 0.44, 0.46, 0.48, 0.5, 0.52, 0.54, 0.56, 0.58])
    else: OMEGA = [float(i) for i in args.OMEGA]

    if not args.pricingDays: pricingDays = [16] #[0.49, 0.5, 0.51, 0.52]
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


    order_file = '../data/hk_d16to20_a{}_K{}_o{}.csv'.format(args.a, args.K, args.omega)

    fairness_metrics('ProfitOnly',K=args.K, order_file=order_file)
    fairness_metrics('PAA', K=args.K, order_file=order_file)

    print('################ END TIME: {} ################'.format(datetime.now().strftime("%m/%d/%Y, %H:%M:%S")))
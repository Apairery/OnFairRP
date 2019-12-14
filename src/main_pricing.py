#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from setproctitle import setproctitle as ptitle
from util.arg_parser import init_parser
from pricing.onlineFairRSPricing import onlineFairRSPricing, fairness_metrics
from util.utils import read_others
import numpy as np

if __name__ == '__main__':
    ptitle('OnlineFairRidesharingPricing')
    parser = init_parser()
    args = parser.parse_args()

    if not args.OMEGA: OMEGA = np.array([0.46, 0.48, 0.5, 0.52, 0.54]) #[0.49, 0.5, 0.51, 0.52]
    else: OMEGA = [float(i) for i in args.OMEGA]
    omega =0.5
    pricing_args = {
        'OMEGA':OMEGA,
        'omega': omega,
        'a':args.a,
        'K':args.K,
        'eta_peak':args.eta_peak,
        'eta_off':args.eta_off,
        'sigma': args.sigma, #args.sigma
        'threshold':1,
    }

    # onlineFairRSPricing(OMEGA, omega, a, K, eta_peak, eta_off, sigma, threshold=1, Transition=600)
    onlineFairRSPricing(**pricing_args)
    # fairness_metrics('ProfitOnly',K=0.01,order_file='../data/haikou_10_16_3km_default.csv')
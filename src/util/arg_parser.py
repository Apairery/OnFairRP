#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse

def init_parser():
    parser = argparse.ArgumentParser(description='OnlineFairRSPricing')

    parser.add_argument('-O', '--OMEGA', nargs='*', help='set of values of omegas, (defalut=[0.4, 0.42, 0.44, 0.46, 0.48, 0.5, 0.52, 0.54, 0.56, 0.58])', required=False)
    parser.add_argument('--eta_peak', type=float, default=0.8, help='eta of peak hour (default=0.8)')
    parser.add_argument('--eta_off', type=float, default=0.6, help='eta of off hour (default=0.6)')
    parser.add_argument('--omega', type=float, default=0.5, help='omega (default=0.5)')
    # parser.add_argument('--dolp', type=float, default=0.95, help='discount of learning phase (default=0.95)')
    parser.add_argument('--running_times', type=int, default=1, help='running times of data every day (default=1)')
    parser.add_argument('--K', type=float, default=0.16, help='constant K (default=0.16)')
    parser.add_argument('--sigma', type=float, default=0.08, help='sigma (default=0.08)')
    parser.add_argument('--a', type=float, default=0.99, help='constant discount a (default=0.99)')
    parser.add_argument('--preRun', type=bool, default=False, help='preRun or not (default=False)')
    parser.add_argument('-D', '--runDays', nargs='*', help='set of values of the dates (Oct.) to simulate, (default=[16, 17, 18, 19, 20])', required=False)
    parser.add_argument('--pricingDays', nargs='*', help='set of values of the dates (Oct.) to price, (default=[16, 17, 18, 19, 20])', required=False)
    parser.add_argument('--scheme', type=str, default='OnFair', help='scheme name (default=\'OnFair\'), [OnFair, ProfitOnly, FIXED, CalPayment, OnFairRP-Exploit]')
    parser.add_argument('--threshold', type=float, default=1.0, help='threshold of learning (default=1.0)')
    return parser

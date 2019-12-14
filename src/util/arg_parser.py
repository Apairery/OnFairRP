#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse

def init_parser():
    parser = argparse.ArgumentParser(description='OnlineFairRSPricing')

    parser.add_argument('-O', '--OMEGA', nargs='*', help='<Required> Set flag', required=False)
    parser.add_argument('--eta_peak', type=float, default=0.8, help='eta of peak hour (default=0.8)')
    parser.add_argument('--eta_off', type=float, default=0.6, help='eta of off hour (default=0.6)')
    parser.add_argument('--omega', type=float, default=0.5, help='omega (default=0.5)')
    parser.add_argument('--dolp', type=float, default=0.95, help='discount of learning phase (default=0.95)')
    parser.add_argument('--running_times', type=int, default=1, help='running times of data of every day (default=1)')
    parser.add_argument('--K', type=float, default=0.008, help='K of \'K-Lipschitz\' (default=0.008)')
    parser.add_argument('--sigma', type=float, default=0.08, help='sigma (default=0.08)')
    parser.add_argument('--a', type=float, default=0.95, help='constant discount a (default=0.95)')
    parser.add_argument('--preRun', type=bool, default=False, help='preRun or not (default=False)')
    parser.add_argument('-D', '--preRunDays', nargs='*', help='<Required> Set flag', required=True)
    parser.add_argument('--experiment', type=str, default='OnFair', help='experiment name (default=\'Onfair\')')
    return parser

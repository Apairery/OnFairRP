#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from setproctitle import setproctitle as ptitle
from util.arg_parser import init_parser
from carpool.carpool_simulation import carpool_running
from datetime import datetime

if __name__ == '__main__':
    print('################ START TIME: {} ################'.format(datetime.now().strftime("%m/%d/%Y, %H:%M:%S")))

    parser = init_parser()
    args = parser.parse_args()
    if args.preRun:
        ptitle('C_p_a{}_o{}'.format(args.a, args.omega))
    else:
        ptitle('{}_a{}_K{}_o{}'.format(args.experiment,args.a, args.K, args.omega))

    if args.preRun:
        if args.runDays:
            days = [int(day) for day in args.runDays]
        else:
            days = [9, 10, 11, 12, 13]
    else:
        if args.runDays:
            days = [int(day) for day in args.runDays]
        else:
            days = [16, 17, 18, 19, 20]

    if args.scheme == 'CalPayment': scheme = 'PAA'
    else: scheme = args.scheme

    args_ = {
        'preRun': args.preRun,
        'days': days,
        'eta_peak': args.eta_peak,
        'eta_off': args.eta_off,
        'omega': args.omega,
        'running_times': args.running_times,
        'scheme': scheme,
        'K': args.K,
        'dolp': args.a,
        'threshold':args.threshold
    }


    carpool_running(**args_)

    print('################ END TIME: {} ################'.format(datetime.now().strftime("%m/%d/%Y, %H:%M:%S")))
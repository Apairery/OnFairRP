#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from setproctitle import setproctitle as ptitle
from util.arg_parser import init_parser
from carpool.carpool_simulation import carpool_running

if __name__ == '__main__':
    ptitle('Carpooling')
    parser = init_parser()
    args = parser.parse_args()


    args_ = {
        'preRun': args.preRun,
        'days': [int(day) for day in args.preRunDays],
        'eta_peak': args.eta_peak,
        'eta_off': args.eta_off,
        'omega': args.omega,
        'running_times': args.running_times,
        'experiment': args.experiment,
        'K': args.K,
        'dolp': args.dolp
    }

    carpool_running(**args_)
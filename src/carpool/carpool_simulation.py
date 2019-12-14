#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import osmnx as ox
from pre_run import pre_run
from util.utils import read_all_riders,read_others, get_shortest_path
import numpy as np
from driver_rider import Driver, Rider
from km_match import km_matching
import pickle
import pandas as pd

def carpool_running(eta_peak=0.8, eta_off=0.6, omega=0.5, K=0.008, dolp=0.95, days=None, running_times=1, interval=2, preRun=False, experiment='OnFair'):
    days = [9] if not days else days
    G = ox.graph_from_address('Haikou, Hainan, China', network_type='drive')
    fee_per_unit = 0.03
    cost_per_unit = 0.03 * 0.25
    speed = 8 # m/s

    if preRun:
        running_times = 5
        pre_run(G, fee_per_unit, cost_per_unit, speed, eta_peak, eta_off, omega, dolp, days, running_times, interval)
    else:

        route_cache = {}
        dis_cache = {}
        others = read_others(filename='../data/others_10_16to20_3km.csv', eta_peak=eta_peak, eta_off=eta_off)
        for i in range(len(others.index)):
            o = others.loc[i, 'o']
            d = others.loc[i, 'd']
            distance = others.loc[i, 'distance']
            if (o, d) not in route_cache.keys():
                route_cache[(o, d)] = get_shortest_path(G, route_cache, o, d)[0]
                dis_cache[(o, d)] = distance

        total_profits = {}
        share_rates = {}
        nums_all_riders = {}
        nums_S_riders = {}
        cumulative_profit = pd.DataFrame()
        if experiment == 'PAA': nums_violate_budgets_list = []

        for day in days:
            all_riders = read_all_riders(filename='../data/haikou_10_{}_3km.csv'.format(day))
            nums_riders = len(all_riders.index)
            nums_all_riders[day] = nums_riders
            nums_S_riders[day] = []
            total_profits[day] = []
            share_rates[day] = []

            for _ in range(running_times):
                all_Riders = []
                time_step_dict = {}
                nums_shared = 0
                total_profit = 0
                r_id = 0
                round_dict = {}
                if experiment == 'PAA': nums_violate_budgets = 0

                for i in range(nums_riders):
                    # gamma = np.random.normal(eta_off, 0.08, 1)[0] if all_riders.loc[i, 'tau'] == 3 else np.random.normal(eta_peak, 0.08, 1)[0]
                    o = all_riders.loc[i, 'o']
                    d = all_riders.loc[i, 'd']
                    tau = all_riders.loc[i, 'tau']
                    discount = all_riders.loc[i, experiment] if experiment != 'PAA' else 1 # else for pAA
                    p_price = dis_cache[(o, d)] * fee_per_unit
                    time_step = all_riders.loc[i, 'time_step']
                    gamma = all_riders.loc[i, 'gamma']
                    rider = Rider(r_id, time_step, discount, gamma, o, d, tau, p_price, dis_cache[(o, d)], omega)
                    rider.isSRide = bool(all_riders.loc[i, experiment + '_status'])
                    if rider.isSRide:
                        nums_S_riders += 1
                        if rider.time_step not in time_step_dict.keys():
                            time_step_dict[rider.time_step] = [r_id]
                        else:
                            time_step_dict[rider.time_step].append(r_id)
                        all_Riders.append(rider)
                        r_id += 1

                active_Drivers = []
                full_Drivers = []
                for t in range(int(1440 * 60 / interval)):
                    cur_Riders = []
                    c_t = int(t * interval)
                    for t_ in range(t * interval, t * interval + interval):
                        if t_ in time_step_dict.keys():
                            for r_id in time_step_dict[t_]:
                                cur_Riders.append(all_Riders[r_id])
                    round_dict[t] = cur_Riders

                    if not active_Drivers:
                        for rider in cur_Riders:
                            r_id = rider.r_id
                            o = rider.o
                            d = rider.d
                            active_Drivers.append(Driver(r_id, c_t, o, route_cache[(o, d)][1:], speed))
                            rider.responded()
                            rider.cost = rider.dis * cost_per_unit
                            rider.profit = rider.dis * fee_per_unit - rider.cost
                    else:
                        for driver in active_Drivers:
                            driver.update(c_t, all_Riders, G, route_cache, dis_cache)
                        for driver in full_Drivers:
                            driver.update(c_t, all_Riders, G, route_cache, dis_cache)

                        to_remove = []
                        for driver in active_Drivers:
                            if driver.isFull():
                                to_remove.append(driver)
                                full_Drivers.append(driver)
                            elif driver.isEmpty():
                                to_remove.append(driver)
                        for driver in to_remove:
                            active_Drivers.remove(driver)

                        to_remove = []
                        for driver in full_Drivers:
                            if (not driver.isFull()) and (not driver.isEmpty()):
                                pass
                                # active_Drivers.append(driver)
                            elif driver.isEmpty():
                                to_remove.append(driver)
                        for driver in to_remove:
                            full_Drivers.remove(driver)

                        if experiment == 'PAA':
                            (route_cache, dis_cache), nvb = \
                                km_matching(cur_Riders, active_Drivers, all_Riders, G,
                                            c_t, route_cache, dis_cache, cost_per_unit, experiment)
                            nums_violate_budgets += nvb
                        else:
                            route_cache, dis_cache = km_matching(cur_Riders, active_Drivers, all_Riders, G,
                                                             c_t, route_cache, dis_cache, cost_per_unit, experiment)

                        left_riders = []
                        for rider in cur_Riders:
                            if not rider.isResponded():
                                left_riders.append(rider)
                        for rider in left_riders:
                            r_id = rider.r_id
                            o = all_Riders[r_id].o
                            d = all_Riders[r_id].d
                            active_Drivers.append(Driver(r_id, c_t, o, route_cache[(o, d)][1:], speed))
                            rider.responded()
                            rider.cost = rider.dis * cost_per_unit
                            rider.profit = rider.dis * fee_per_unit - rider.cost

                '''save results'''

                nums_violate_budgets_list.append(nums_violate_budgets)
                round_profit_list = []
                # for t in range(int(1440 * 60 / interval)):
                #     riders_list = round_dict[t]
                #     for rider in riders_list:
                #         total_profit += rider.profit
                #         nums_shared = nums_shared + 1 if rider.isShared else nums_shared
                #     round_profit_list.append(total_profit)

                for rider in all_Riders:
                    total_profit += rider.profit
                    nums_shared = nums_shared + 1 if rider.isShared else nums_shared
                    round_profit_list.append(total_profit)

                cumulative_profit['{}_{}'.format(day, _)] = round_profit_list

                share_rate = nums_shared / len(all_Riders)
                total_profits[day].append(total_profit)
                share_rates[day].append(share_rate)

        eta_peak_ = str(eta_peak).replace('.', '-')
        eta_off_ = str(eta_off).replace('.', '-')
        omega_ = str(omega).replace('.', '-')
        K_ = str(K).replace('.', '-')
        dolp_ = str(dolp).replace('.', '-')
        cumulative_profit.to_csv('../result/cp_{}_{}t{}_{}_{}_{}_{}_{}.csv'.format(experiment, days[0], days[-1], eta_peak_, eta_off_, omega_, K_, dolp_),
                                 index=False, sep=',', header=True)

        if experiment == 'PAA': print(nums_violate_budgets_list)

        # all_dict = {'total_profits':total_profits,
        #             'share_rates':share_rates,
        #             'nums_all_riders':nums_all_riders,
        #             'nums_S_riders':nums_S_riders}
        #
        # f = open('../result/om_{}_{}to{}_{}_{}_{}.pkl'.format(experiment, days[0], days[-1], eta_peak_, eta_off_, omega_), "wb")
        # pickle.dump(all_dict, f)
        # f.close()
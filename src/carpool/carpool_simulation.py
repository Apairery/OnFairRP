#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import osmnx as ox
from pre_run import pre_run
from util.utils import get_shortest_path, read_all_riders_default, read_others_default, read_others
import numpy as np
from driver_rider import Driver, Rider
from km_match import km_matching
import pickle
import pandas as pd

def carpool_running(eta_peak, eta_off, omega, K, dolp, days=None, running_times=1, interval=2, preRun=False, experiment='OnFair', threshold=1.0):
    ox.config(log_console=False, use_cache=True)
    # G = ox.graph_from_address('Haikou, Hainan, China', network_type='drive')
    # G = ox.graph_from_place('Haikou, Hainan, China', network_type='drive')
    G = ox.graph_from_address('Haikou, Hainan, China', distance=100000, network_type='drive') # n
    fee_per_unit = 0.003
    cost_per_unit = 0.003 * 0.25
    speed = 13 # m/s

    if preRun:
        running_times = 5
        pre_run(G, fee_per_unit, cost_per_unit, speed, eta_peak, eta_off, omega, dolp, days, running_times, interval)
    else:

        route_cache = {}
        dis_cache = {}
        # others = read_others(filename='../data/others_10_16to20_3km.csv', eta_peak=eta_peak, eta_off=eta_off)
        others = read_others(filename='../data/others_d16to20_a0.99_o0.5.csv', eta_peak=eta_peak, eta_off=eta_off)
        # others = read_others_default(filename='../data/others_10_9to13_3km_default.csv', eta_peak=eta_peak, eta_off=eta_off)
        for i in range(len(others.index)):
            o = others.loc[i, 'o']
            d = others.loc[i, 'd']
            distance = others.loc[i, 'distance']
            if (o, d) not in route_cache.keys():
                route_cache[(o, d)] = get_shortest_path(G, route_cache, o, d)[0]
                dis_cache[(o, d)] = distance

        total_profits = []
        total_costs = []
        share_rates = []
        nums_S_riders = []
        cumulative_profit = pd.DataFrame()
        if experiment == 'PAA': nums_violate_budgets_ratio_list = []

        filename = '../data/hk_d{}to{}_a{}_K{}_o{}_t{}.csv'.format(days[0], days[-1], dolp, K, omega, threshold)
        all_riders = read_all_riders_default(filename=filename)
        nums_riders = len(all_riders.index)
        nums_all_riders = nums_riders
        # nums_S_riders[day] = []
        # total_profits[day] = []
        # total_costs[day] = []
        # share_rates[day] = []

        for _ in range(running_times):
            nums_S_riders.append(0)
            all_Riders = []
            time_step_dict = {}
            nums_shared = 0
            total_profit = 0
            total_cost = 0
            r_id = 0
            if experiment == 'PAA':
                nums_violate_budgets, total_check = 0, 0
                all_riders['PAA'] = 0.0

            for i in range(nums_riders):
                # gamma = np.random.normal(eta_off, 0.08, 1)[0] if all_riders.loc[i, 'tau'] == 3 else np.random.normal(eta_peak, 0.08, 1)[0]
                o = all_riders.loc[i, 'o']
                d = all_riders.loc[i, 'd']
                tau = all_riders.loc[i, 'tau']
                if experiment == 'PAA':
                    discount = 1
                else:
                    discount = all_riders.loc[i, experiment]
                p_price = dis_cache[(o, d)] * fee_per_unit
                time_step = all_riders.loc[i, 'time_step']
                gamma = all_riders.loc[i, 'gamma']
                o_lat = all_riders.loc[i, 'o_lat']
                o_lng = all_riders.loc[i, 'o_lng']
                d_lat = all_riders.loc[i, 'd_lat']
                d_lng = all_riders.loc[i, 'd_lng']
                day = all_riders.loc[i, 'day']
                rider = Rider(r_id, time_step, discount, gamma, o, d, tau, p_price, dis_cache[(o, d)], omega, o_lat, o_lng, d_lat, d_lng)
                rider.isSRide = bool(all_riders.loc[i, experiment + '_status']) if experiment != 'PAA' else bool(all_riders.loc[i, 'OnFair_status']) #todo:!!!
                # rider.isSRide = bool(
                #     all_riders.loc[i, experiment + '_{}_status'.format(_)]) if experiment != 'PAA' else bool(
                #     all_riders.loc[i, 'OnFair_all_{}_status'.format(_)])

                if rider.isSRide:
                    nums_S_riders[_] += 1
                    if rider.time_step not in time_step_dict.keys():
                        time_step_dict[(day, rider.time_step)] = [r_id]
                    else:
                        time_step_dict[(day, rider.time_step)].append(r_id)
                    all_Riders.append(rider)
                    r_id += 1

            active_Drivers = []
            full_Drivers = []
            day_rounds = int(1440 * 60 / interval)
            T_range = [int(t) for t in range(day_rounds)] * len(days)
            day = days[0] - 1
            for t in T_range:
                if t % day_rounds == 0:
                    day += 1
                    active_Drivers.clear()
                cur_Riders = []
                c_t = int(t * interval)
                for t_ in range(t * interval, t * interval + interval):
                    if (day, t_) in time_step_dict.keys():
                        for r_id in time_step_dict[(day, t_)]:
                            cur_Riders.append(all_Riders[r_id])

                if not active_Drivers:
                    for rider in cur_Riders:
                        r_id = rider.r_id
                        o = rider.o
                        d = rider.d
                        active_Drivers.append(Driver(r_id, c_t, o, route_cache[(o, d)][1:], speed))
                        rider.responded()
                        rider.cost = rider.dis * cost_per_unit
                        rider.profit = rider.s_price - rider.cost
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
                        (route_cache, dis_cache), (nvb, t) = \
                            km_matching(cur_Riders, active_Drivers, all_Riders, G,
                                        c_t, route_cache, dis_cache, cost_per_unit, experiment)
                        nums_violate_budgets += nvb
                        total_check += t
                    else:
                        # print(len(cur_Riders), len(active_Drivers))
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
                        rider.profit = rider.s_price - rider.cost

            '''save results'''

            if experiment=='PAA':
                # print('PAA_here1')
                nums_violate_budgets_ratio_list.append(nums_violate_budgets/total_check)
                j = 0
                for i in range(len(all_riders.index)):
                    if all_riders.loc[i, 'OnFair_status'] == 1:
                    # if all_riders.loc[i, 'OnFair_all_{}_status'.format(_)] == 1:
                        all_riders.at[i, 'PAA'] = all_Riders[j].s_price / all_Riders[j].p_price
                        # print(all_riders.loc[i, 'PAA'], all_Riders[j].s_price, all_Riders[j].p_price)
                        j += 1
                assert j == len(all_Riders), '{}_{}'.format(j, len(all_Riders))


            round_profit_list = []
            j = 0
            for i in range(len(all_riders.index)):
                isS = bool(all_riders.loc[i, experiment + '_status']) if experiment != 'PAA' else bool(all_riders.loc[i, 'OnFair_status'])
                # isS = bool(
                #     all_riders.loc[i, experiment + '_{}_status'.format(_)]) if experiment != 'PAA' else bool(
                #     all_riders.loc[i, 'OnFair_all_{}_status'.format(_)])
                if isS:
                    total_profit += all_Riders[j].profit
                    total_cost += all_Riders[j].cost
                    nums_shared = nums_shared + 1 if all_Riders[j].isShared else nums_shared
                    j += 1
                else:
                    total_profit += 0
                    total_cost += 0
                round_profit_list.append(total_profit)

            assert j == len(all_Riders), '{}_{}'.format(j, len(all_Riders))
            # for rider in all_Riders:
            #     total_profit += rider.profit
            #     nums_shared = nums_shared + 1 if rider.isShared else nums_shared
            #     round_profit_list.append(total_profit)

            cumulative_profit['T{}'.format(_)] = round_profit_list

            share_rate = nums_shared / len(all_Riders)
            total_profits.append(total_profit)
            total_costs.append(total_cost)
            share_rates.append(share_rate)

        # if experiment == 'PAA':
        #     all_riders.to_csv(filename, sep=',', index=False, header=True)


        if experiment == 'PAA':
            print('nums_violate_budgets_ratio_list:', nums_violate_budgets_ratio_list)

        print('total_profits:', total_profits)
        print('total_costs:', total_costs)
        print('share_rates:', share_rates)
        print('nums_all_riders:', nums_all_riders)
        print('nums_S_riders:', nums_S_riders)
        # all_dict = {'total_profits':total_profits,
        #             'share_rates':share_rates,
        #             'nums_all_riders':nums_all_riders,
        #             'nums_S_riders':nums_S_riders}
        #
        # f = open('../result/om_{}_{}to{}_{}_{}_{}.pkl'.format(experiment, days[0], days[-1], eta_peak_, eta_off_, omega_), "wb")
        # pickle.dump(all_dict, f)
        # f.close()
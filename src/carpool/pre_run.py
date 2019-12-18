#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import numpy as np
from util.utils import read_all_riders, read_partial_others, get_shortest_path
from driver_rider import Driver, Rider
import pandas as pd
from km_match import km_matching

def pre_run(G, fee_per_unit, cost_per_unit, speed, eta_peak, eta_off, omega, dolp, days, running_times, interval):

    partial_others_dict = {}
    distribution_dict = {}
    route_cache = {}
    dis_cache = {}
    partial_others = read_partial_others(filename='../data/partial_others_10_{}to{}_3km.csv'.format(days[0], days[-1]))
    for i in range(len(partial_others.index)):
        o = partial_others.loc[i, 'o']
        d = partial_others.loc[i, 'd']
        tau = partial_others.loc[i, 'tau']
        distance = partial_others.loc[i, 'distance']
        nums = 0
        cost = 0
        distribution_dict[(o, d, tau)] = 0
        partial_others_dict[(o, d, tau)] = [distance * fee_per_unit, nums, cost, distance]
        if (o, d) not in route_cache.keys():
            route_cache[(o, d)] = get_shortest_path(G, route_cache, o, d)[0]
            dis_cache[(o, d)] = distance

    nums_S_riders = 0
    nums_all_riders = 0
    share_rates = []
    total_profits = []

    assert fee_per_unit / cost_per_unit == 4, 'here'

    for day in days:

        all_riders = read_all_riders(filename='../data/haikou_10_{}_3km.csv'.format(day))
        nums_riders = len(all_riders.index)

        for _ in range(running_times):
            all_Riders = []
            time_step_dict = {}
            nums_shared = 0
            total_profit = 0
            r_id = 0

            for i in range(nums_riders):
                gamma = np.random.normal(eta_off, 0.08, 1)[0] if all_riders.loc[i, 'tau'] == 3 else \
                np.random.normal(eta_peak, 0.08, 1)[0]
                o = all_riders.loc[i, 'o']
                d = all_riders.loc[i, 'd']
                tau = all_riders.loc[i, 'tau']
                p_price = dis_cache[(o, d)] * fee_per_unit
                time_step = all_riders.loc[i, 'time_step']
                o_lat = all_riders.loc[i, 'o_lat']
                o_lng = all_riders.loc[i, 'o_lng']
                d_lat = all_riders.loc[i, 'd_lat']
                d_lng = all_riders.loc[i, 'd_lng']
                rider = Rider(r_id, time_step, dolp, gamma, o, d, tau, p_price, dis_cache[(o, d)], omega, o_lat, o_lng, d_lat, d_lng)
                distribution_dict[(o, d, tau)] += 1
                nums_all_riders += 1
                if rider.isSRide:
                    partial_others_dict[(o, d, tau)][1] += 1
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

                if not active_Drivers:
                    for rider in cur_Riders:
                        r_id = rider.r_id
                        o = rider.o
                        d = rider.d
                        active_Drivers.append(Driver(r_id, c_t, o, route_cache[(o, d)][1:], speed))
                        rider.responded()
                        rider.cost = rider.dis * cost_per_unit
                        # rider.profit = rider.dis * fee_per_unit - rider.cost
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

                    route_cache, dis_cache = km_matching(cur_Riders, active_Drivers, all_Riders, G, c_t, route_cache,
                                                         dis_cache, cost_per_unit, False)

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

            # total_profit = 0
            # nums_shared = 0
            for rider in all_Riders:
                o = rider.o
                d = rider.d
                tau = rider.tau
                total_profit += rider.profit
                nums_shared = nums_shared + 1 if rider.isShared else nums_shared
                partial_others_dict[(o, d, tau)][2] += rider.cost

            share_rate = nums_shared / len(all_Riders)
            total_profits.append(total_profit)
            share_rates.append(share_rate)
    li = []
    for key in partial_others_dict.keys():
        if partial_others_dict[key][1] > 0:
            partial_others_dict[key][2] /= partial_others_dict[key][1]
            partial_others_dict[key][1] = distribution_dict[key] / nums_all_riders
            # partial_others_dict[key][1] /= nums_S_riders
        li.append([key[0], key[1], key[2]] + partial_others_dict[key])
    df = pd.DataFrame(li, columns=['o', 'd', 'tau', 'price', 'distribution', 'cost', 'distance'])
    df['o_lat'] = partial_others['o_lat']
    df['o_lng'] = partial_others['o_lng']
    df['d_lat'] = partial_others['d_lat']
    df['d_lng'] = partial_others['d_lng']
    # df = df[df.distribution > 0]
    df.to_csv('../data/others_d{}to{}_a{}_o{}.csv'.format(days[0], days[-1], dolp, omega), sep=',', index=False, header=True)

    print(share_rates)
    print(total_profits)
    print(nums_S_riders/nums_all_riders)
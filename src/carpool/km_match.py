#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from munkres import Munkres, make_cost_matrix, DISALLOWED
from sys import maxsize
import numpy as np
from util.utils import get_shortest_path_length
from calPaymentOfPAA import calPayment
from scipy.spatial.distance import cosine

def km_matching(cur_Riders, active_Drivers, all_Riders, G, c_t, route_cache, dis_cache, cost_per_unit=0.003 * 0.25, experiment='OnFair'):
    if len(cur_Riders) == 0 or len(active_Drivers) == 0:
        if experiment == 'PAA': return (route_cache, dis_cache), (0, 0)
        return route_cache, dis_cache
    profit_matrix = [[-1] * len(active_Drivers) for i in range(len(cur_Riders))]
    cost_matrix = np.zeros(shape=[len(cur_Riders), len(active_Drivers)])
    mode_matrix = np.zeros(shape=[len(cur_Riders), len(active_Drivers)])
    total_dis_matrix = np.zeros(shape=[len(cur_Riders), len(active_Drivers)])
    if experiment == 'PAA':
        pAA_payment_dict = {}
        nums_violate_budgets = 0
        total_check = 0
    for i in range(len(cur_Riders)):
        rider2 = cur_Riders[i]
        for j in range(len(active_Drivers)):
            driver = active_Drivers[j]
            cur_onboard = driver.riders
            assert len(cur_onboard) > 0, 'here1'
            assert cur_onboard[0] < len(all_Riders), '{},{}'.format(cur_onboard[0], len(all_Riders))
            rider1 = all_Riders[cur_onboard[0]]
            o1 = rider1.o
            d1 = rider1.d
            o2 = rider2.o
            d2 = rider2.d
            dis1, exists = get_shortest_path_length(G, dis_cache, o2, d1)
            if not exists: dis_cache[(o2, d1)] = dis1
            dis2, exists = get_shortest_path_length(G, dis_cache, o2, d2)
            if not exists: dis_cache[(o2, d2)] = dis2
            # dis3, exists = get_shortest_path_length(G, dis_cache, o1, o2)
            # if not exists: dis_cache[(o1, o2)] = dis3
            dis4, exists = get_shortest_path_length(G, dis_cache, d1, d2)
            if not exists: dis_cache[(d1, d2)] = dis4
            dis5, exists = get_shortest_path_length(G, dis_cache, d2, d1)
            if not exists: dis_cache[(d2, d1)] = dis4
            dis6, exists = get_shortest_path_length(G, dis_cache, o1, driver.c_loc)
            if not exists: dis_cache[(o1, driver.c_loc)] = dis6
            dis7, exists = get_shortest_path_length(G, dis_cache, driver.c_loc, o2)
            if not exists: dis_cache[(driver.c_loc, o2)] = dis7
            if -1 in [dis1, dis2, dis4, dis5, dis6, dis7]: profit_matrix[i][j] = -1
            else:
                '''rules out'''
                od1 = [rider1.d_lat - rider1.o_lat, rider1.d_lng - rider1.d_lat]
                od2 = [rider2.d_lat - rider2.o_lat, rider2.d_lng - rider2.d_lat]
                if 1 - cosine(od1, od2) <= 0: continue
                dis_list = []
                if dis1 > dis2:
                    total_dis = (dis6 + dis7 + dis2 + dis5)
                    if total_dis / rider1.dis >= 1.55: continue
                    if total_dis > rider1.dis + rider2.dis: continue
                    dis_list += [dis6, dis7, dis2, dis5]
                else:
                    total_dis = (dis6 + dis7 + dis1 + dis4)
                    if (dis6 + dis7 + dis1) / rider1.dis >= 1.55: continue
                    if (dis1 + dis4) / rider2.dis >= 1.55: continue
                    if total_dis > rider1.dis + rider2.dis: continue
                    dis_list += [dis6, dis7, dis1, dis4]
                    mode_matrix[i][j] = 1
                cost = total_dis * cost_per_unit
                cost_matrix[i][j] = cost
                total_dis_matrix[i][j] = total_dis
                if experiment == 'PAA':
                    total_check += 1
                    payment1, payment2 = calPayment(rider1, rider2, mode_matrix[i][j], dis_list)
                    if payment1 > 0 and payment2 > 0:
                        pass
                        # profit = payment1 + payment2 - cost
                        # # if profit < rider1.profit + rider2.profit: continue
                        # if profit < 0:
                        #     payment1 = payment2 = 1.2 * cost
                        #     profit = cost
                        # profit_matrix[i][j] = profit
                    else:
                        nums_violate_budgets += 1
                    payment1 = 1.8 * cost if payment1 < 0 else payment1
                    payment2 = 1.8 * cost if payment2 < 0 else payment2
                    # profit = payment1 + payment2 - cost
                    # if profit < 0:
                    if payment1 + payment2 - cost < 0:
                        payment1 = payment2 = 1.8 * cost
                    payment1 = min(payment1, rider1.p_price)
                    payment2 = min(payment2, rider2.p_price)
                    profit = payment1 + payment2 - cost
                    profit_matrix[i][j] = profit
                    pAA_payment_dict[(i, j)] = [payment1, payment2]
                else:
                    profit = rider1.s_price + rider2.s_price - cost
                    if profit < rider1.profit + rider2.profit: continue
                    profit_matrix[i][j] = profit

    # km_weights = make_cost_matrix(profit_matrix, lambda item: (maxsize - item) if item != 0 else DISALLOWED)
    km_weights = make_cost_matrix(profit_matrix)
    m = Munkres()
    indexes = m.compute(km_weights)
    for row, column in indexes:
        value = profit_matrix[row][column]
        if value > 0:
            rider2 = cur_Riders[row]
            driver = active_Drivers[column]
            cur_onboard = driver.riders
            rider1 = all_Riders[cur_onboard[0]]
            if True: #value >= (rider1.profit + rider2.profit):  # is it too hard ?

                driver.append_rider(rider2.r_id, c_t, all_Riders, G=G, mode=int(mode_matrix[row][column]), route_cache=route_cache, dis_cache=dis_cache)
                rider2.responded()

                rider2.cost = cost_matrix[row][column] * rider2.dis / (rider2.dis + rider1.dis)
                rider1.cost = cost_matrix[row][column] * rider1.dis / (rider2.dis + rider1.dis)
                rider1.profit = value * rider1.dis / (rider2.dis + rider1.dis)
                rider2.profit = value * rider2.dis / (rider2.dis + rider1.dis)
                rider1.isShared = rider2.isShared = True
                rider1.share_id = rider2.r_id
                rider2.share_id = rider1.r_id

                if experiment == 'PAA':
                    rider1.s_price = pAA_payment_dict[(row, column)][0]
                    rider2.s_price = pAA_payment_dict[(row, column)][1]

    if experiment == 'PAA':
        return (route_cache, dis_cache), (nums_violate_budgets, total_check)
    else:
        return route_cache, dis_cache




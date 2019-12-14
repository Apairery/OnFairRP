#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from util.utils import get_shortest_path_length

def calPayment(rider1, rider2, mode, dis_list):

    dis_rider1 = rider1.dis
    dis_rider2 = rider2.dis
    total_dis = dis_rider1 + dis_rider2
    ratio1 = dis_rider1 / total_dis
    ratio2 = dis_rider2 / total_dis

    ratio = {rider1: ratio1, rider2:ratio2}
    budget = {rider1:rider1.p_price, rider2:rider2.p_price} # todo: ???
    payment = {rider1:0, rider2:0}

    active_r = {}
    active_r[0] = [rider1]
    active_r[1] = [rider1, rider2]
    active_r[2] = [rider1, rider2]
    if mode == 0: active_r[3] = [rider1]
    else: active_r[3] = [rider2]

    for i in range(4):
        for rider in active_r[i]:
            payment[rider] += budget[rider] * ratio[rider] * dis_list[i] / 1000
            if payment[rider] > budget[rider]:
                return -1, -1
            budget[rider] -= payment[rider]

    return payment[rider1], payment[rider2]
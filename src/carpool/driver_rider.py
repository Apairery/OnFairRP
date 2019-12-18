#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import osmnx as ox
import networkx as nx
import numpy as np
from random import uniform
from util.utils import get_shortest_path, get_shortest_path_length

class Driver(object):
    def __init__(self, r_id, c_t, c_loc, route, speed):
        self.riders = [r_id]
        self.c_t = c_t
        self.c_loc = c_loc
        if len(route) == 0:
            raise RuntimeError('self.route = []')
        self.route = route
        self.speed = speed

    def isFull(self):
        return True if len(self.riders) >= 2 else False

    def isEmpty(self):
        return True if len(self.riders) == 0 else False

    def append_rider(self, r_id, t, all_Riders, G, mode, route_cache, dis_cache):
        self.riders.append(r_id)
        self.update_route(t, all_Riders, mode=mode, G=G, newRider=True, route_cache=route_cache, dis_cache=dis_cache)
        # self.update_riders(all_Riders)

    def update(self, t, all_Riders, G, route_cache, dis_cache):
        self.update_route(t, all_Riders, G=G, route_cache=route_cache, dis_cache=dis_cache)
        # self.update_riders(all_Riders)

    def update_route(self, t, all_Riders, mode=0, newRider=False, G=None, route_cache=None, dis_cache=None):

        if newRider:
            rider2 = all_Riders[self.riders[1]]
            rider1 = all_Riders[self.riders[0]]
            d1 = rider1.d
            o2 = rider2.o
            d2 = rider2.d

            route1, _ = get_shortest_path(G, route_cache, self.c_loc, o2) # nx.shortest_path(G, self.c_loc, o2, weight='length')
            if mode == 0:
                route2, _ = get_shortest_path(G, route_cache, o2, d2)
                route3, _ = get_shortest_path(G, route_cache, d2, d1)
            else:
                route2, _ = get_shortest_path(G, route_cache, o2, d1)
                route3, _ = get_shortest_path(G, route_cache, d1, d2)

            self.route = route1[1:-1] + route2[:-1] + route3

        if len(self.route) == 0: return # this is because some update will be conducted in km phase
        time = get_shortest_path_length(G, dis_cache, self.c_loc, self.route[0])[0]/ self.speed

        if t >= self.c_t + time:
            self.c_loc = self.route.pop(0)
            self.c_t = t
            self.update_riders(all_Riders)


    def update_riders(self, all_Riders):
        to_remove = []
        for r_id in self.riders:
            if self.c_loc == all_Riders[r_id].d:
                to_remove.append(r_id)
        for r_id in to_remove:
            self.riders.remove(r_id)

class Rider(object):
    def __init__(self, r_id, time_step, discount, gamma, o, d, tau, p_price, distance, omega, o_lat, o_lng, d_lat, d_lng):
        self.r_id = r_id
        self.time_step = time_step
        self.respond_status = False
        self.discount = discount
        self.p_price = p_price
        self.dis = distance
        self.gamma = gamma
        self.o = o
        self.d = d
        self.o_lat = o_lat
        self.o_lng = o_lng
        self.d_lat = d_lat
        self.d_lng = d_lng
        self.tau = tau
        self.prob_SRide = -omega * self.discount + self.gamma
        self.isSRide = self.isSRide_()
        self.cost = 0
        self.profit = 0
        self.share_id = None
        self.isShared = False
        self.s_price = self.p_price * self.discount

    def isResponded(self):
        return self.respond_status

    def responded(self):
        self.respond_status = True

    def isSRide_(self):
        return uniform(0, 1) <= self.prob_SRide

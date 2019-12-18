#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pandas as pd
import numpy as np
import networkx as nx

# def priceOf_P_ride(rider):
#     pass
#
# def get_cost(rider):
#     pass
#
# def get_profit(rider):
#     pass
#
# def get_gamma(rider, eta_peak, eta_off):
#     pass
#
# def prob_of_S_Ride(discount, omega, rider, eta_peak, eta_off):
#     pass

def read_all_riders_default(filename='../data/haikou_10_9_3km_default.csv'):
    # usecols = ['time_step', 'o', 'd', 'month', 'day', 'tau', 'dis', 'o_lat', 'o_lng', 'd_lat', 'd_lng',
    #            'ProfitOnly', 'FIXED', 'OnFair', 'OnFair_status', 'ProfitOnly_status', 'FIXED_status', 'gamma'],
    li = []
    for i in [1]:
        df_ = pd.read_csv(filename, sep=',', header='infer',
                          dtype={'time_step': np.int, 'o': np.int, 'd': np.int, 'tau': np.int, 'month': np.int, 'day': np.int,
                                 'OnFair_status':np.int, 'ProfitOnly_status':np.int, 'FIXED_status':np.int})
        li.append(df_)
    df = pd.concat(li, axis=0, ignore_index=True)
    df = df[df.o != df.d]
    return df

def read_all_riders(filename='../data/haikou_10_9_3km.csv'):
    li = []
    for i in [1]:
        df_ = pd.read_csv(filename, sep=',', header='infer',
                          usecols=['time_step', 'o', 'd', 'month', 'day', 'tau', 'dis', 'o_lat', 'o_lng', 'd_lat', 'd_lng'],
                          dtype={'time_step': np.int, 'o': np.int, 'd': np.int, 'tau': np.int, 'month': np.int, 'day': np.int})
        li.append(df_)
    df = pd.concat(li, axis=0, ignore_index=True)
    df = df[df.o != df.d]
    return df

def read_partial_others(filename='../data/partial_others_10_9_3km.csv'):
    df = pd.read_csv(filename, sep=',', header='infer',
                     usecols=['o', 'd', 'tau', 'distance', 'o_lat', 'o_lng', 'd_lat', 'd_lng'],
                     dtype={'o':np.int, 'd':np.int, 'tau':np.int})
    return df

def read_others(filename='../data/others_10_9to13_3km.csv', eta_peak=0.8, eta_off=0.6):
    df = pd.read_csv(filename, sep=',', header='infer',
                     usecols=['o', 'd', 'tau', 'distribution', 'price', 'cost', 'distance'],
                     dtype={'o':np.int, 'd':np.int, 'tau':np.int})
    total, nums_off = len(df.index), len(list(df.groupby(['tau']))[3][1].index)
    peak = np.random.normal(eta_peak, 0.08, total - nums_off).tolist()
    off = np.random.normal(eta_off, 0.08, nums_off).tolist()
    df['gamma'] = df.apply(lambda x: off.pop() if x['tau'] == 3 else peak.pop(), axis=1)
    return df

def read_others_default(filename='../data/others_10_9to13_3km_default.csv', eta_peak=0.8, eta_off=0.6):
    df = pd.read_csv(filename, sep=',', header='infer',
                     usecols=['o', 'd', 'tau', 'distribution', 'price', 'cost', 'distance', 'odt', 'OnFair'],
                     dtype={'o':np.int, 'd':np.int, 'tau':np.int, 'odt':np.int})
    total, nums_off = len(df.index), len(list(df.groupby(['tau']))[3][1].index)
    peak = np.random.normal(eta_peak, 0.08, total - nums_off).tolist()
    off = np.random.normal(eta_off, 0.08, nums_off).tolist()
    df['gamma'] = df.apply(lambda x: off.pop() if x['tau'] == 3 else peak.pop(), axis=1)
    return df

def get_shortest_path(G, route_cache, o, d):
    exists = False
    if (o, d) in route_cache.keys():
        route = route_cache[(o, d)]
        exists = True
    else:
        try:
            route = nx.shortest_path(G, o, d, weight='length')
        except:
            try:
                route = nx.shortest_path(G, d, o, weight='length')
                route.reverse()
            except:
                route = -1
    return route, exists


def get_shortest_path_length(G, dis_cache, o, d):
    exists = False
    if (o, d) in dis_cache.keys():
        dis = dis_cache[(o, d)]
        exists = True
    else:
        try:
            dis = nx.shortest_path_length(G, o, d, weight='length')
        except:
            try:
                dis = nx.shortest_path_length(G, d, o, weight='length')
            except:
                dis = -1
    return dis, exists
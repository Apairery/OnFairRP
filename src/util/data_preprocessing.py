#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pandas as pd
import glob
import osmnx as ox
import networkx as nx
import numpy as np
from utils import read_all_riders
from setproctitle import setproctitle as ptitle

ox.config(log_console=True, use_cache=True)
# G = ox.graph_from_address('Haikou, Hainan, China', network_type='drive')
# G = ox.graph_from_place('Haikou, Hainan, China', network_type='drive')
G = ox.graph_from_address('Haikou, Hainan, China', distance=100000, network_type='drive') # n

def map_to_tau(x):
    x = x['hour']
    if x <= 9 and x >= 7: return 0
    elif x <= 14 and x >= 10: return 1
    elif x <= 20 and x >= 17: return 2
    else: return 3

def map_to_o(x):
    return ox.get_nearest_node(G, (round(x['starting_lat'], 2), round(x['starting_lng'], 2)))

def map_to_o_(x):
    # lat = round(x['starting_lat'], 3)
    # lng = round(x['starting_lng'], 3)
    return ox.get_nearest_node(G, (x['o_lat'], x['o_lng']))

def map_to_d(x):
    return ox.get_nearest_node(G, (round(x['dest_lat'], 2), round(x['dest_lng'], 2)))

def map_to_d_(x):
    # lat = round(x['dest_lat'], 3)
    # lng = round(x['dest_lng'], 3)
    return ox.get_nearest_node(G, (x['d_lat'], x['d_lng']))

def map_to_od(x):
    return ox.get_nearest_node(G, (round(x['starting_lat'], 2), round(x['starting_lng'], 2))), \
           ox.get_nearest_node(G, (round(x['dest_lat'], 2), round(x['dest_lng'], 2)))


def map_to_dis(x):
    try:
        length = nx.shortest_path_length(G, int(x['o']), int(x['d']), weight='length')
    except:
        length = -1
    return length

def read_all():
    print(type(G))
    dateParser = lambda x: pd.datetime.strptime(x, '%Y-%m-%d %H:%M:%S')

    li = []
    for i in range(8, 9):
        df_ = pd.read_csv('../../originalData/haikou_{}.csv'.format(i), sep=',', header='infer',
                          usecols=['departure_time','pre_total_fee','dest_lng', 'dest_lat','starting_lng','starting_lat','month', 'day'],
                          dtype={'pre_total_fee':np.float, 'dest_lat':np.float, 'dest_lng':np.float, 'starting_lng':np.float, 'starting_lat':np.float, 'month':np.int, 'day':np.int},
                          parse_dates=['departure_time'], date_parser= dateParser)
        li.append(df_)
    df = pd.concat(li, axis=0, ignore_index=True)

    df['day'] = df.apply(lambda x: int(x['departure_time'].day), axis=1)
    df['month'] = df.apply(lambda x: int(x['departure_time'].month), axis=1)
    df = df[(df.month == 10) & ( ((df.day <= 20) & (df.day >= 16)) | ((df.day <= 13) & (df.day >= 9)) )]
    df = df.dropna()
    print('here')

    df['hour'] = df.apply(lambda x: int(x['departure_time'].hour), axis=1)
    print('here')
    df['tau'] = df.apply(lambda x: int(map_to_tau(x)), axis=1)
    print('here')
    df['time_step'] = df.apply(lambda x: int(x['departure_time'].hour * 3600 +
                                             x['departure_time'].minute * 60 +
                                             x['departure_time'].second), axis=1)
    print('here')
    df['o_lat'] = df.apply(lambda x: round(round(x['starting_lat'] / 0.03) * 0.03, 2), axis=1)
    df['o_lng'] = df.apply(lambda x: round(round(x['starting_lng'] / 0.03) * 0.03, 2), axis=1)
    df['o'] = df.apply(lambda x: int(map_to_o_(x)), axis=1)  # 3.4h
    print('here')
    df['d_lat'] = df.apply(lambda x: round(round(x['dest_lat'] / 0.03) * 0.03, 2), axis=1)
    df['d_lng'] = df.apply(lambda x: round(round(x['dest_lng'] / 0.03) * 0.03, 2), axis=1)
    df['d'] = df.apply(lambda x: int(map_to_d_(x)), axis=1) # 3.4h

    df = df.drop(['starting_lat', 'starting_lng', 'dest_lat', 'dest_lng', 'departure_time', 'hour'], axis=1)
    print('here')
    # df['od'] = df.apply(lambda x: int(map_to_od(x)), axis=1)
    # print('here')
    df['dis'] = df.apply(lambda x: map_to_dis(x), axis=1)
    print('here')
    df = df[df.dis > 0]
    print('here')

    grouped = df.groupby(['month','day'])
    group = [g[1] for g in list(grouped)]
    # day = [9,10,11,12,13,16,17,18,19,20]
    for i in range(len(group)):
        df_ = group[i].sort_values(by = 'time_step')
        df_.to_csv('../../data/haikou_10_{}_3km.csv'.format(16+i), index=False, header=True, sep=',', float_format='%.2f')
        print('here1')


def cal_partial_others(days):
    li = []
    for day in days:
        li.append(read_all_riders(filename='../../data/haikou_10_{}_3km.csv'.format(day)))
    all_riders = pd.concat(li, axis=0, ignore_index=True)

    grouped = all_riders.groupby(['o', 'd', 'tau'])
    li = []
    for key, group in grouped:
        group_len = len(group.index)
        li.append([key[0], key[1], key[2], group.loc[group.index.tolist()[0], 'dis'],
                   group.loc[group.index.tolist()[0], 'o_lat'], group.loc[group.index.tolist()[0], 'o_lng'],
                   group.loc[group.index.tolist()[0], 'd_lat'], group.loc[group.index.tolist()[0], 'd_lng']])
    df = pd.DataFrame(li, columns = ['o', 'd', 'tau', 'distance', 'o_lat', 'o_lng', 'd_lat', 'd_lng'])
    df.to_csv('../../data/partial_others_10_{}to{}_3km.csv'.format(days[0], days[-1]), sep=',', index=False, header=True, float_format='%.2f')

if __name__ == '__main__':
    ptitle('DataPre')
    # read_all()
    cal_partial_others(days=[9, 10, 11, 12, 13])
    cal_partial_others(days=[16, 17, 18, 19, 20])
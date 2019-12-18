#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from util.utils import read_all_riders, read_others
import numpy as np
import pandas as pd
from scipy.optimize import minimize


def EuclideanDistances(A, B):
    BT = B.transpose()
    vecProd = np.dot(A, BT)
    SqA = A ** 2
    sumSqA = np.matrix(np.sum(SqA, axis=1))
    sumSqAEx = np.tile(sumSqA.transpose(), (1, vecProd.shape[1]))
    SqB = B ** 2
    sumSqB = np.sum(SqB, axis=1)
    sumSqBEx = np.tile(sumSqB, (vecProd.shape[0], 1))
    SqED = sumSqBEx + sumSqAEx - 2 * vecProd
    SqED[SqED < 0] = 0.0
    ED = (SqED.getA()) ** 0.5
    return np.matrix(ED)


def calculate_similarity(df):
    # usecols=['o_lat', 'o_lng', 'd_lat', 'd_lng', 'tau']
    m = len(df)  # number of odtau

    # for tau: 0 if tau_1 == tau_2 else 1
    tau = df.tau.values
    tau_diff = np.tile(tau, m).reshape(m, m).T - np.tile(tau, m).reshape(m, m)
    tau_diff[tau_diff != 0] = 1

    # for lat & lng: ed + min-max
    odfeatures = df.values[:, 1:]
    oded = EuclideanDistances(odfeatures, odfeatures)
    # edmin = oded.min() # is 0
    edmax = oded.max()
    oded = oded / edmax

    similarity = oded + tau_diff
    np.savetxt("../data/similarity_d9to13_3km.csv", similarity, delimiter=",")
    # return similarity


def ProfitOBJ(d, Distribution, gamma, omega, price, cost):
    return -1 * Distribution.T.dot(((gamma - d * omega) * (d * price - cost)))


def fair(Distribution, gamma, omega, price, cost, similarity, K, a):
    m = len(gamma)
    d0 = np.ones(m) * a

    constraints = []
    constraints.append({'type': 'ineq', 'fun': lambda d: d})  # lower bound = 0
    constraints.append({'type': 'ineq', 'fun': lambda d: a - d})  # upper bound = a
    constraints.append({'type': 'ineq', 'fun': lambda d: (K * similarity - (
                np.tile(d, m).reshape(m, m).T - np.tile(d, m).reshape(m, m))).flatten()})  # fairness constraints

    # s = time.time()
    res = minimize(fun=ProfitOBJ, x0=d0, args=(Distribution, gamma, omega, price, cost), method='SLSQP',
                   constraints=constraints, options={'maxiter': 100})
    # print('Time: ',time.time()-s)
    # print('Opt value: ',res.fun)
    # print('Success: ', res.success)
    # print('Iteration: ',res.nit)
    # print(res.message)
    # print(res.x)
    return res.x


def FIXED(Distribution, gamma, omega, price, cost, a):
    d0 = a

    constraints = []
    constraints.append({'type': 'ineq', 'fun': lambda d: d})  # lower bound = 0
    constraints.append({'type': 'ineq', 'fun': lambda d: a - d})  # upper bound = a

    res = minimize(fun=ProfitOBJ, x0=d0, args=(Distribution, gamma, omega, price, cost), method='SLSQP',
                   constraints=constraints, options={'maxiter': 100})
    # print('Opt value: ',res.fun)
    # print('Success: ', res.success)
    # print('Iteration: ',res.nit)
    # print(res.message)
    # print(res.x)
    return res.x


def ProfitOnly(Distribution, gamma, omega, price, cost, a):
    m = len(gamma)
    d0 = np.ones(m)

    constraints = []
    constraints.append({'type': 'ineq', 'fun': lambda d: d})  # lower bound = 0
    constraints.append({'type': 'ineq', 'fun': lambda d: a - d})  # upper bound = a

    # s = time.time()
    res = minimize(fun=ProfitOBJ, x0=d0, args=(Distribution, gamma, omega, price, cost), method='SLSQP',
                   constraints=constraints, options={'maxiter': 200})
    # print('Time: ',time.time()-s)
    # print('Opt value: ',res.fun)
    # print('Success: ', res.success)
    # print('Iteration: ',res.nit)
    # print(res.message)
    # print(type(res.x))
    return res.x

# order,gamma,Omega,omega,a,threshold
# def learning(order, gamma, Omega, omega, a):
def learning(order, gamma, Omega, omega, a, threshold):
    # Xi = np.ones(len(Omega))
    Xi = np.zeros(len(Omega))
    T = len(order)
    t = 0
    omega_choose = np.random.choice(Omega)
    check_status = np.identity(len(Omega))
    order_status = []

    while t < T:
        ind = np.argwhere(np.min(check_status, axis=1) == 1)
        if len(ind) != 0:
            omega_choose = Omega[np.random.choice(ind[:, 0])]  # break tie arbitrarily
            # print(temp)
            return omega_choose, t, order_status, check_status
            # break
        o = order.loc[t, 'o']
        d = order.loc[t, 'd']
        tau = order.loc[t, 'tau']
        gamma_ = gamma.loc[(o, d, tau), :].values[0]
        rnd = order.loc[t, 'rnd']

        status = 1 if rnd < gamma_ - a * omega else 0  # rider's decision; 1 = order
        order_status.append(status)
        probability = gamma_ - a * Omega  # prob of making an request given fixed discount a

        probability[probability <= 0] = 2.2250738585072014e-308
        probability[probability >= 1] = 1 - 2.2250738585072014e-308

        # Xi = Xi * probability if status == 1 else Xi * (1 - probability)
        Xi = Xi + np.log(probability) if status == 1 else Xi + np.log(1 - probability)
        temp = np.tile(Xi, len(Omega)).reshape(len(Omega), len(Omega)).T - np.tile(Xi, len(Omega)).reshape(len(Omega),
                                                                                                           len(Omega))
        # check_status[temp > np.log(T)] = 1
        check_status[temp > threshold * np.log(T)] = 1
        t += 1

    check_ = np.sum(check_status, axis=1)
    omega_choose = Omega[np.random.choice(np.argwhere(check_ == np.max(check_))[:, 0])]
    return omega_choose, t, order_status, check_status


''' Run this main_pricing.py '''


# def onlineFairRSPricing(OMEGA, omega, a, K, eta_peak, eta_off, sigma, days, Transition=600):
def onlineFairRSPricing(OMEGA, omega, a, K, eta_peak, eta_off, sigma, days, threshold=1, Transition=600):
    '''
    :param OMEGA: Hypothesis \Omega
    :param a: Constants discount a \in [0, 1]
    :param K: K of 'K-Lipschitz'
    :param eta_peak
    :param eta_off
    :return:
        after determine discounts for every riders,
        add a new column 'discounts' to dataframe all_riders for their corresponding discounts.
        Write a csv file with all_riders, including their corresponding discount
    '''

    ''' 
        all_riders: Dataframe,
        refer to all_riders.loc[t] for the rider of time step t,
        refer to all_riders.loc[t, 'o'] for the origin of rider at time step t,
        refer to len(all_riders.index) for total rounds T 
        other attributes including 'd': destination, 'tau': time zone id,
    '''
    # all_riders = read_all_riders()
    # all_riders = pd.read_csv('../data/haikou_10_16_3km.csv')
    # all_riders = all_riders.sort_values(by=['time_step'], ascending=[True])
    li = []
    for day in days:
        df = pd.read_csv('../data/haikou_10_{}_3km.csv'.format(day))
        # df = df.sort_values(by=['time_step'], ascending=[True])
        li.append(df)
    all_riders = pd.concat(li, axis=0, ignore_index=True)
    T = len(all_riders)
    all_riders['rnd'] = [np.random.random() for i in range(T)]
    '''
        others: Dataframe,
        others['distribution'].tolist()
        others['gamma'].tolist()
        others['price'].tolist()
        others['cost'].tolist()
        o: others['o_lat'], others['o_lng']
        d: others['d_lat'], others['d_lng']
        tau: others['tau']
    '''
    # others = read_others()
    others = pd.read_csv("../data/others_d9to13_a{}_o{}.csv".format(a, omega))
    others['gamma'] = others.apply(
        lambda x: sigma * np.random.randn() + eta_off if x['tau'] == 3 else sigma * np.random.randn() + eta_peak,
        axis=1)
    others['odt'] = [i for i in range(len(others))]
    Distribution = others.distribution.values
    gamma = others.gamma.values
    price = others.price.values
    cost = others.cost.values

    # df = others[['o_lat', 'o_lng', 'd_lat', 'd_lng', 'tau']] # todo: no need any more
    # calculate_similarity(df)  # to "../data/similarity_10_9to13_3km_default.csv"
    # del df

    print('Total: ', T)
    gamma_list = others[['o', 'd', 'tau', 'gamma']].set_index(['o', 'd', 'tau'])
    omega_choose, t, order_status, check_status = learning(all_riders, gamma_list, OMEGA, omega, a, threshold)
    # omega_choose, t, order_status, check_status = learning(all_riders, gamma_list, OMEGA, omega, a)
    print('omega_choose: ', omega_choose)
    print('Learning t: ', t)  # = len(order_status)

    # solving optimization
    similarity = pd.read_csv("../data/similarity_d9to13_3km.csv", header=None).values
    others['OnFair'] = fair(Distribution, gamma, omega_choose, price, cost, similarity, K, a)

    # Benchmark discount
    others['ProfitOnly'] = ProfitOnly(Distribution, gamma, omega, price, cost, 1)
    others['FIXED'] = [FIXED(Distribution, gamma, omega, price, cost, 1)[0]] * len(others)
    others.to_csv('../data/others_d9to13_a{}_K{}_o{}.csv'.format(a, K, omega), index=False)

    discount = others[['o', 'd', 'tau', 'odt', 'gamma', 'ProfitOnly', 'FIXED', 'OnFair']]
    all_riders = pd.merge(all_riders, discount, on=['o', 'd', 'tau'], how='left')

    all_riders = all_riders.sort_values(by=['day', 'time_step'], ascending=[True, True]).reset_index()

    all_riders['OnFair_all'] = all_riders['OnFair']

    all_riders.loc[:t + Transition - 1, 'OnFair'] = [a] * (t + Transition)
    all_riders['OnFair_status'] = all_riders.apply(lambda x: 1 if x['rnd'] < x['gamma'] - x['OnFair'] * omega else 0,
                                                   axis=1)
    all_riders.loc[:t - 1, 'OnFair_status'] = order_status
    all_riders['OnFair_all_status'] = all_riders.apply(
        lambda x: 1 if x['rnd'] < x['gamma'] - x['OnFair_all'] * omega else 0, axis=1)
    all_riders['ProfitOnly_status'] = all_riders.apply(
        lambda x: 1 if x['rnd'] < x['gamma'] - x['ProfitOnly'] * omega else 0, axis=1)
    all_riders['FIXED_status'] = all_riders.apply(lambda x: 1 if x['rnd'] < x['gamma'] - x['FIXED'] * omega else 0,
                                                  axis=1)

    if len(days) > 1:
        all_riders.to_csv('../data/hk_d{}to{}_a{}_K{}_o{}_t{}.csv'.format(days[0], days[-1], a, K, omega, threshold), index=False)
    else:
        all_riders.to_csv('../data/hk_{}_a{}_K{}_o{}_t{}.csv'.format(days[0], a, K, omega, threshold), index=False)


def diff_discount(df, algo):
    discounts = df[algo].values
    m = len(discounts)
    disc_diff = np.tile(discounts, m).reshape(m, m).T - np.tile(discounts, m).reshape(m, m)
    return disc_diff


def cal_ratio1(K_pair, m):
    K_pair = K_pair[:m + 1][:m + 1]
    try:
        count1 = sum(sum(K_pair))  # violation pairs
        # count1 = sum(sum(K_pair>0))
    except:
        count1 = K_pair
    m += 1  # number of rounds
    ratio1 = count1 / (m * (m + 1) / 2)
    return ratio1


def fairness_metrics(algo, K, order_file):
    '''
    Calculate violation ratio1 and violation ratio2
    algo: 'ProfitOnly'
    [Finished in 904.1s]
    '''
    riders = pd.read_csv(order_file)
    riders['rider_index'] = riders.index

    # df = pd.DataFrame()

    del riders['level_0']
    riders = riders[riders.day == 16]
    riders = riders.sort_values(by=['time_step'], ascending=[True])

    s = algo if algo != 'PAA' else 'OnFair'
    all_riders = riders[riders['{}_status'.format(s)] == 1].reset_index()
    m = len(all_riders)

    # print('similarity')
    similarity = pd.read_csv("../data/similarity_d9to13_3km.csv", header=None).values
    odt_list = all_riders.odt.values
    similarity_riders = np.zeros((m, m))
    for j in range(m):
        for i in range(j, m):
            similarity_riders[i][j] = similarity[odt_list[i]][odt_list[j]]

    # print('disc_diff')
    disc_diff = diff_discount(all_riders, algo)  # (df,discount_type)

    K_pair = np.tril(disc_diff - K * similarity_riders, 0)
    K_pair[K_pair <= 0] = 0
    K_pair[K_pair > 0] = 1  # violation

    all_riders[algo + '_ratio1'] = [cal_ratio1(K_pair, i) for i in range(m)]
    # df[algo + '_ratio1'] = [cal_ratio1(K_pair, i) for i in range(m)]

    violation2 = K_pair.max(axis=1)
    # ratio2 = violation2.mean()
    # print(ratio2)

    all_riders[algo + '_vio2_status'] = violation2
    # df[algo + '_vio2_status'] = violation2

    all_riders = all_riders[['rider_index', algo + '_vio2_status', algo + '_ratio1']]
    # print(all_riders.head())
    all_riders = pd.merge(riders, all_riders, on='rider_index', how='left')
    all_riders[algo + '_ratio1'] = all_riders[algo + '_ratio1'].fillna(method='pad')
    all_riders = all_riders.fillna(0)
    # all_riders.to_csv(order_file, index=False)
    all_riders[algo + '_ratio2'] = all_riders.apply(
        lambda x: all_riders[all_riders.index <= x['rider_index']][algo + '_vio2_status'].sum() /
                  all_riders[all_riders.index <= x['rider_index']][s + '_status'].sum(), axis=1)

    del all_riders['rider_index']
    all_riders.to_csv(algo + '_F.csv', index=False)


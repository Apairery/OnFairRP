#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pandas as pd
from util.arg_parser import init_parser
from setproctitle import setproctitle as ptitle
import numpy as np

if __name__ == '__main__':

    parser = init_parser()
    args = parser.parse_args()
    ptitle('Nor_a{}_o{}'.format(args.a, args.omega))

    df1 = pd.read_csv('../data/others_d9to13_a{}_o{}.csv'.format(args.a, args.omega), sep=',', header='infer') # 41720 + 44375 + 35902 + 36972 + 45863 --> 40966.4
    df2 = pd.read_csv('../data/others_d16to20_a{}_o{}.csv'.format(args.a, args.omega), sep=',', header='infer')

    list1 = [tuple(i) for i in np.array(df1[['o', 'd', 'tau']], dtype=np.int).tolist()]
    index1 = len(df1.index)
    list2 = [tuple(i) for i in np.array(df2[['o', 'd', 'tau']], dtype=np.int).tolist()]
    index2 = len(df1.index)
    set1 = set(list1)
    set2 = set(list2)
    print(len(set1), len(set2))
    dto2 = set1 - set2
    dto1 = set2 - set1
    print(len(dto2), len(dto1))
    j = 0
    for item in dto2:
        i = list1.index(item)
        df2.loc[index2 + j] = df1.loc[i]
        df2.loc[index2 + j, 'distribution'] = 0
        j += 1
    df2.to_csv('../data/others_d16to20_a{}_o{}.csv'.format(args.a, args.omega), sep=',', header=True, index=False)
    j = 0
    for item in dto1:
        i = list2.index(item)
        df1.loc[index1 + j] = df2.loc[i]
        df1.loc[index1 + j, 'distribution'] = 0
        j += 1
    df1.to_csv('../data/others_d9to13_a{}_o{}.csv'.format(args.a, args.omega), sep=',', header=True, index=False)
    list1 = [tuple(i) for i in np.array(df1[['o', 'd', 'tau']], dtype=np.int).tolist()]
    index1 = len(df1.index)
    list2 = [tuple(i) for i in np.array(df2[['o', 'd', 'tau']], dtype=np.int).tolist()]
    index2 = len(df1.index)
    set1 = set(list1)
    set2 = set(list2)
    print(len(set1), len(set2))
    dto2 = set1 - set2
    dto1 = set2 - set1
    print(len(dto2), len(dto1))
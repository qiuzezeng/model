#! /usr/bin/env python3
# coding=utf-8
# ================================================================
# Copyright (C), 2019, TP-LINK Technologies Co., Ltd.
# package       :
# description   :
# date          :   2021/1/19
# author        :   qiuzezeng
# ================================================================
import time
import pandas as pd
from tqdm import tqdm

for i in tqdm(range(1, 10)):
    tm = pd.read_csv('F:/tm统计/tmAll/tm4/' + str(i) + '.csv')


    def delete_str(x):
        x = x.split(':')[-1].replace('第', '')
        x = x.replace('次测试', '')
        return x


    res = tm[['用例id', '测试结果', '子项目名称', '总项目名称', '预期开始时间', '预期结束时间', '上传结果时间']]
    res['测试轮次'] = tm['测试轮次名称'].apply(delete_str)
    res['预期开始时间'] = res['预期开始时间'].apply(lambda x: time.strftime('%Y/%m/%d %H:%M:%S', time.localtime(x)))
    res['预期结束时间'] = res['预期结束时间'].apply(lambda x: time.strftime('%Y/%m/%d %H:%M:%S', time.localtime(x)))
    res['上传结果时间'] = res['上传结果时间'].apply(lambda x: time.strftime('%Y/%m/%d %H:%M:%S', time.localtime(x)))
    if i == 1:
        res_total = res
    else:
        res_total = pd.concat([res_total,res])

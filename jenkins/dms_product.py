#! /usr/bin/env python3
# coding=utf-8
# ================================================================
# Copyright (C), 2019, TP-LINK Technologies Co., Ltd.
# package       :
# description   :
# date          :   2021/1/27
# author        :   qiuzezeng
# ================================================================
import pandas as pd

a = pd.read_table(r'F:\jenkins\out\jenkins产物文件名.txt',header=None)
a['file_name'] = a[0].apply(lambda x: x.split('!')[0])
a['file_str'] = a[0].apply(lambda x: x.split('!')[1])
def eval_list(x):
    try:
        return eval(x)
    except:
        return ''
a['file_list'] = a['file_str'].apply(eval_list)




















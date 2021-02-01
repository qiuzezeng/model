#! /usr/bin/env python3
# coding=utf-8
# ================================================================
# Copyright (C), 2019, TP-LINK Technologies Co., Ltd.
# package       :
# description   :
# date          :   2021/1/19
# author        :   qiuzezeng
# ================================================================
import pandas as pd

team = pd.read_csv(r'E:\compare\middle\temp\teams.csv')
change_base = pd.read_csv(r'E:\compare\middle\temp\change基础表.csv')
change_base = pd.merge(change_base, team, left_on='change上传人', right_on='员工姓名', how='left')
temp = change_base[change_base['created_on'] > '2020-01-01 11:13:43']
res = temp.groupby(['change上传人','组织']).apply(lambda x: list(x[['代码语言']].value_counts().items())).reset_index()














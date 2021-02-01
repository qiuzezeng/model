#! /usr/bin/env python3
# coding=utf-8
# ================================================================
# Copyright (C), 2019, TP-LINK Technologies Co., Ltd.
# package       :
# description   :
# date          :   2021/1/12
# author        :   qiuzezeng
# ================================================================
import pandas as pd

path = r'\\file.tp-link.net\测试部\测试部自动化与实验室管理组\IT组\@统计数据\餐补\out_ess_0111_001.csv'
ess = pd.read_csv(path, header=None)
path1 = r'\\file.tp-link.net\测试部\测试部自动化与实验室管理组\IT组\@统计数据\餐补\out_ess_0114_001.csv'
ess1 = pd.read_csv(path1, header=None)
ess = pd.concat([ess, ess1])
ess = ess.iloc[:, [3, 4, 9, 21, 22, 23]]
ess.columns = ['工号', '员工姓名', '性别', 'datetime', 'date', '餐补次数']
ess = ess.sort_values(by='datetime')
ess = ess.drop_duplicates(subset=['工号', '员工姓名', 'date'], keep='last')
season_list = []
for year in range(2017, 2021):
    season_list_example = [
        {
            'year': year,
            'season': 1,
            'start_time': str(year) + '-01-01 00:00:00',
            'end_time': str(year) + '-03-31 23:59:59'
        },
        {
            'year': year,
            'season': 2,
            'start_time': str(year) + '-04-01 00:00:00',
            'end_time': str(year) + '-06-30 23:59:59'
        },
        {
            'year': year,
            'season': 3,
            'start_time': str(year) + '-07-01 00:00:00',
            'end_time': str(year) + '-09-30 23:59:59'
        },
        {
            'year': year,
            'season': 4,
            'start_time': str(year) + '-10-01 00:00:00',
            'end_time': str(year) + '-12-31 23:59:59'
        }
    ]
    season_list += season_list_example

i = -1
for season in season_list:
    i += 1

    cur_ess = ess[(ess['date'] >= season['start_time']) & (ess['date'] <= season['end_time'])]
    res = cur_ess.groupby(['工号', '员工姓名'])['餐补次数'].agg({'sum'}).reset_index()
    res = res.rename(columns={'sum': '餐补次数'})
    res['year'] = season['year']
    res['season'] = season['season']
    if i == 0:
        res_total = res
    else:
        res_total = pd.concat([res_total, res])

temp = res_total.drop_duplicates(subset=['员工姓名', 'year', 'season'])

res = pd.read_excel(r'E:\compare\middle\result\按季度统计2021-01-11_161559.xlsx')
temp = temp.drop(columns=['工号'])
res = pd.merge(res, temp, on=['员工姓名', 'year', 'season'], how='left')
grade = pd.read_csv(r'F:\Gerrit\人员信息\person_performance.csv', encoding='gbk')
grade = grade.drop(columns=['employeeNumber'])
grade = grade.rename(columns={'userName': '员工姓名', 'result': 'grade'})
grade['grade'] = grade['grade'].map({'A': 95, 'B': 85, 'B-': 75, 'C': 65, 'D': 55})
res = pd.merge(res, grade, on=['员工姓名', 'year', 'season'], how='left')
last_grade = grade.copy()


def last(line):
    if line['season'] == 4:
        return [line['year'] + 1, 1]
    else:
        return [line['year'], line['season'] + 1]


last_grade['last'] = last_grade.apply(last, axis=1)
last_grade['year'] = last_grade['last'].apply(lambda x: x[0])
last_grade['season'] = last_grade['last'].apply(lambda x: x[1])
last_grade = last_grade.drop(columns=['last'])
last_grade = last_grade.rename(columns={'grade': 'pre_grade'})
res = pd.merge(res, last_grade, on=['员工姓名', 'year', 'season'], how='left')

last_grade = grade.copy()


def last(line):
    if line['season'] == 4:
        return [line['year'] + 1, 2]
    elif line['season'] == 3:
        return [line['year'] + 1, 1]
    else:
        return [line['year'], line['season'] + 2]


last_grade['last'] = last_grade.apply(last, axis=1)
last_grade['year'] = last_grade['last'].apply(lambda x: x[0])
last_grade['season'] = last_grade['last'].apply(lambda x: x[1])
last_grade = last_grade.drop(columns=['last'])
last_grade = last_grade.rename(columns={'grade': 'pre_two_grade'})
res = pd.merge(res, last_grade, on=['员工姓名', 'year', 'season'], how='left')
res.to_excel(r'E:\compare\middle\result\按季度统计_train.xlsx', index=0)

path = r'E:\compare\middle\result\按季度统计_train.xlsx'
data_df = pd.read_excel(path)
data_df = data_df.dropna(subset=['grade'])
# 查看grade分布
temp = data_df.grade.value_counts(dropna=False)
temp = pd.DataFrame(temp)
temp['s'] = temp.grade.sum()
temp['rate'] = temp['grade'] / temp['s']

# 数据处理
data_df['pre_grade'] = data_df['pre_grade'].fillna(70)
data_df['pre_two_grade'] = data_df['pre_two_grade'].fillna(70)
drop_col = []
cols = data_df.columns
for col in cols:
    if str(data_df[col].dtype) == 'object':
        drop_col.append(col)
drop_cols = drop_col.copy()
drop_cols.append('grade')
cols = list(set(data_df.columns).difference(set(drop_cols)))
train1 = data_df[(data_df['year'] == 2020) & (data_df['season'] == 1) | (data_df['year'] < 2020)]
train2 = data_df[(data_df['year'] == 2020) & (data_df['season'] == 2)]
test_with_lable = data_df[(data_df['year'] == 2020) & (data_df['season'] == 3)]
test = test_with_lable[cols]
train = pd.concat([train1, train2])
train_x = train[cols]
train_y = train[['grade']]

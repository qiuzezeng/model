#! /usr/bin/env python3
# coding=utf-8
# ================================================================
# Copyright (C), 2019, TP-LINK Technologies Co., Ltd.
# package       :
# description   :
# date          :   2021/1/8
# author        :   qiuzezeng
# ================================================================
import lightgbm as lgb
import pandas as pd
import numpy as np
from sklearn.model_selection import KFold

path = r'E:\compare\middle\result\按季度统计_train.xlsx'
data_df = pd.read_excel(path)
data_df = data_df.dropna(subset=['grade'])
# 查看grade分布
temp = data_df.grade.value_counts(dropna=False)
temp = pd.DataFrame(temp)
temp['s'] = temp.grade.sum()
temp['rate'] = temp['grade']/temp['s']

# 数据处理
data_df['pre_grade'] = data_df['pre_grade'].fillna(70)
data_df['pre_two_grade'] = data_df['pre_two_grade'].fillna(70)
drop_col = []
cols = data_df.columns
for col in cols:
    if str(data_df[col].dtype) == 'object':
        drop_col.append(col)

data_df = data_df.dropna(subset=['change上传人','审核人'])
data_df = data_df.fillna(0)
data_df = data_df[data_df['总change数_提交']>=5]
data_df = data_df[data_df['workday(天)']>=0]
data_df = data_df.drop_duplicates(subset=['员工姓名','year','season'])

grade = pd.read_csv(r'F:\Gerrit\人员信息\person_performance.csv',encoding='gbk')
grade= grade.drop(columns=['employeeNumber'])
grade= grade.rename(columns={'userName':'员工姓名','result':'grade'})
grade['grade'] = grade['grade'].map({'A':95, 'B':85, 'B-':75, 'C':65, 'D':55})
last_grade = grade.copy()
def last(line):
    if line['season'] == 4:
        return [line['year']+1,3]
    elif line['season'] == 3:
        return [line['year']+1,2]
    elif line['season'] == 2:
        return [line['year']+1,1]
    else:
        return [line['year'],line['season']+3]
last_grade['last'] = last_grade.apply(last, axis=1)
last_grade['year'] = last_grade['last'].apply(lambda x: x[0])
last_grade['season'] = last_grade['last'].apply(lambda x: x[1])
last_grade = last_grade.drop(columns=['last'])
last_grade = last_grade.rename(columns={'grade':'pre_three_grade'})
data_df = pd.merge(data_df,last_grade,on=['员工姓名','year','season'],how='left')
data_df['pre_three_grade'] = data_df['pre_three_grade'].fillna(68)

# 拆分训练集
drop_cols = drop_col.copy()
drop_cols += ['grade','餐补次数']
cols = list(set(data_df.columns).difference(set(drop_cols)))
train1 = data_df[(data_df['year']==2020)&(data_df['season']==1)| (data_df['year']<2020)]
train2 = data_df[(data_df['year']==2020)&(data_df['season']==2)]
test_with_lable = data_df[(data_df['year']==2020)&(data_df['season']==3)]
test = test_with_lable[cols]
train = pd.concat([train1,train2])
train_x = train[cols]
train_y = train[['grade']]

# 训练
num_round = 200
params = {'boosting_type': 'gbdt',
          'num_leaves': 31,
          'min_data_in_leaf': 50,
          'objective': 'regression',
          'max_depth': -1,
          'learning_rate': 0.02,
          "min_sum_hessian_in_leaf": 6,
          "boosting": "gbdt",
          "feature_fraction": 0.9,
          "bagging_freq": 1,
          "bagging_fraction": 0.7,
          "bagging_seed": 11,
          "lambda_l1": 0.1,
          "verbosity": -1,
          "nthread": 4,
          'metric': 'mae',
          "random_state": 2019,
          # 'device': 'gpu'
          }

folds = KFold(n_splits=5, shuffle=True, random_state=2019)
oof = np.zeros(train_x.shape[0])
predictions = np.zeros(test.shape[0])
feature_importance_df = pd.DataFrame()

for fold_, (trn_idx, val_idx) in enumerate(folds.split(train_x)):
    print("fold {}".format(fold_ + 1))
    trn_data = lgb.Dataset(train_x.iloc[trn_idx], label=train_y.iloc[trn_idx])
    val_data = lgb.Dataset(train_x.iloc[val_idx], label=train_y.iloc[val_idx])

    clf = lgb.train(params,
                    trn_data,
                    num_round,
                    valid_sets=[trn_data, val_data],
                    verbose_eval=200,
                    early_stopping_rounds=200)
    oof[val_idx] = clf.predict(train_x.iloc[val_idx], num_iteration=clf.best_iteration)

    fold_importance_df = pd.DataFrame()
    fold_importance_df["Feature"] = cols
    fold_importance_df["importance"] = clf.feature_importance()
    fold_importance_df["fold"] = fold_ + 1
    feature_importance_df = pd.concat([feature_importance_df, fold_importance_df], axis=0)
    predictions += clf.predict(test, num_iteration=clf.best_iteration) / folds.n_splits

result = test_with_lable[['员工姓名','grade']]
result['prediction_score'] = predictions
temp = result.sort_values(by='prediction_score').reset_index(drop=True)
d_score = temp.loc[int(temp.shape[0] * 0.025)].prediction_score
c_score = temp.loc[int(temp.shape[0] * 0.485)].prediction_score
b_score = temp.loc[int(temp.shape[0] * 0.785)].prediction_score
b2_score = temp.loc[int(temp.shape[0] * 0.94)].prediction_score
def score_to_grade(line):
    if line['prediction_score']<=d_score:
        return 55
    elif line['prediction_score']<=c_score:
        return 65
    elif line['prediction_score']<=b_score:
        return 75
    elif line['prediction_score']<=b2_score:
        return 85
    else:
        return 95
result['prediction_grade'] = result.apply(score_to_grade,axis=1)
def count_acc(line):
    if line['grade'] == line['prediction_grade']:
        return 1
    else:
        return 0
result['acc'] = result.apply(count_acc,axis=1)
acc = result['acc'].sum()/result['acc'].count()
def two(line):
    if (line['grade']>70 and line['prediction_grade']>70) or (line['grade']<70 and line['prediction_grade']<70):
        return 1
    else:
        return 0
result['two_acc'] = result.apply(two,axis=1)
two_acc = result['two_acc'].sum()/result['two_acc'].count()




# 特征重要性
fold_importance_df = fold_importance_df.sort_values(by='importance',ascending=False).head(20)
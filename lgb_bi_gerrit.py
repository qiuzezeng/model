#! /usr/bin/env python3
# coding=utf-8
# ================================================================
# Copyright (C), 2019, TP-LINK Technologies Co., Ltd.
# package       :
# description   :
# date          :   2021/1/11
# author        :   qiuzezeng
# ================================================================
import lightgbm as lgb
import pandas as pd
import numpy as np
from sklearn.model_selection import KFold

path = r'\\file.tp-link.net\测试部\测试部自动化与实验室管理组\IT组\@统计数据\gerrit\提交者.csv'
submit = pd.read_csv(path)
submit['pre_score'] = submit['pre_score'].apply(lambda x: 65 if x == 0 else x)
submit['score'] = submit['score'].apply(lambda x: 1 if x > 85 else 0)
submit = submit[submit.userName != submit['负责人姓名']]

num_round = 100
params = {'num_leaves': 31,  # 结果对最终效果影响较大，越大值越好，太大会出现过拟合
          'min_data_in_leaf': 30,
          'objective': 'binary',  # 定义的目标函数
          'max_depth': -1,
          'learning_rate': 0.03,
          "min_sum_hessian_in_leaf": 6,
          "boosting": "gbdt",
          "feature_fraction": 0.9,  # 提取的特征比率
          "bagging_freq": 1,
          "bagging_fraction": 0.8,
          "bagging_seed": 11,
          "lambda_l1": 0.1,  # l1正则
          # 'lambda_l2': 0.001,		#l2正则
          "verbosity": -1,
          "nthread": -1,  # 线程数量，-1表示全部线程，线程越多，运行的速度越快
          'metric': {'auc'},  ##评价函数选择
          "random_state": 2019,  # 随机数种子，可以防止每次运行的结果不一致
          # 'device': 'gpu' ##如果安装的事gpu版本的lightgbm,可以加快运算
          'Is_unbalace': True
          }

cols = ['总change数', '总merge数', 'abandon数',
        'abandon占总change比例', '自己abandon数', '自己abandon占总change比例', '被abandon数',
        '被abandon占总change比例', '单个change最大评论数', '单个change平均评论数',
        '单个change评论的中位数', '被打分总数', '被打-1数量', '被打-1比例', '被打-2数量', '被打-2比例',
        '被打1数量', '被打1比例', '被打2数量', '被打2比例', '被打0数量', '被打0比例', 'change最大通过时间（天）',
        'change平均通过时间（天）', 'change通过时间中位数（天）', '最大响应时间（天）', '平均响应时间（天）',
        '响应时间中位数（天）', '被直接merge的change数', '被直接merge比例', '总操作代码行数',
        '平均操作代码行数', '操作代码行数的中位数', 'change类型为代码的数量', 'change类型为配置的数量',
        'change类型为文本的数量', 'change类型为非代码的数量', 'change功能为append的数量',
        'change功能为authority的数量', 'change功能为debug的数量', 'change功能为delete的数量',
        'change功能为fix的数量', 'change功能为modify的数量', 'change功能为new的数量',
        'change功能为optimize的数量', 'change功能为remove的数量', 'change功能为update的数量',
        '有效代码的change数', '无效代码的change数', '重要性最大得分', '重要性平均得分', '重要性得分中位数',
        '打分者平均数', '评论者平均数', '参与提交的仓库数',
        '有效代码的change数-比例', '无效代码的change数-比例',
        'change功能为append的数量-比例', 'change功能为authority的数量-比例',
        'change功能为debug的数量-比例', 'change功能为delete的数量-比例', 'change功能为fix的数量-比例',
        'change功能为modify的数量-比例', 'change功能为new的数量-比例',
        'change功能为optimize的数量-比例', 'change功能为remove的数量-比例',
        'change功能为update的数量-比例', 'change类型为代码的数量-比例', 'change类型为配置的数量-比例',
        'change类型为文本的数量-比例', 'change类型为非代码的数量-比例', 'quarter', 'pre_score',
        'workdays']
train1 = submit[(submit['currentYear'] == 2020) & (submit['quarter'] == 1)]
train2 = submit[(submit['currentYear'] == 2020) & (submit['quarter'] == 2)]
test_with_lable = submit[(submit['currentYear'] == 2020) & (submit['quarter'] == 3)]
test = test_with_lable[cols]
train = pd.concat([train1, train2])
train_x = train[cols]
train_y = train[['score']]
folds = KFold(n_splits=5, shuffle=True, random_state=2019)
prob_oof = np.zeros((train_x.shape[0],))
test_pred_prob = np.zeros((test.shape[0],))

## train and predict
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
                    early_stopping_rounds=60,
                    )
    prob_oof[val_idx] = clf.predict(train_x.iloc[val_idx], num_iteration=clf.best_iteration)

    fold_importance_df = pd.DataFrame()
    fold_importance_df["Feature"] = cols
    fold_importance_df["importance"] = clf.feature_importance()
    fold_importance_df["fold"] = fold_ + 1
    feature_importance_df = pd.concat([feature_importance_df, fold_importance_df], axis=0)

    test_pred_prob += clf.predict(test[cols], num_iteration=clf.best_iteration) / folds.n_splits

result = test_with_lable[['userName', 'score']]
result['prediction_p'] = test_pred_prob
temp = result.sort_values(by='prediction_p').reset_index(drop=True)
d_score = temp.loc[int(temp.shape[0] * 0.03)].prediction_p
c_score = temp.loc[int(temp.shape[0] * 0.5)].prediction_p
b_score = temp.loc[int(temp.shape[0] * 0.8)].prediction_p
b2_score = temp.loc[int(temp.shape[0] * 0.95)].prediction_p
result['prediction_score'] = result['prediction_p'].apply(lambda x: 1 if x >= b2_score else 0)


def count_acc(line):
    if line['score'] == line['prediction_score']:
        return 1
    else:
        return 0


result['acc'] = result.apply(count_acc, axis=1)
acc = result['acc'].sum() / result['acc'].count()
p = ((result['score'] == 1) & (result['prediction_score'] == 1)).sum()/(result['score'] == 1).sum()
r = ((result['score'] == 1) & (result['prediction_score'] == 1)).sum()/(result['prediction_score'] == 1).sum()

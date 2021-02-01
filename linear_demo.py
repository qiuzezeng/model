#! /usr/bin/env python3
# coding=utf-8
# ================================================================
# Copyright (C), 2019, TP-LINK Technologies Co., Ltd.
# package       :
# description   :
# date          :   2021/1/13
# author        :   qiuzezeng
# ================================================================
import pandas as pd
import numpy as np
from sklearn import preprocessing

from sklearn.model_selection import train_test_split  # 这里是引用了交叉验证
from sklearn.linear_model import LinearRegression  # 线性回归


def Normalization():
    # 对数据进行归一化处理 并存储到eth2.csv
    pd_data = pd.read_csv('eth.csv')
    sam = []
    a = ['priceUSD', 'activeAddresses', 'adjustedVolume', 'paymentCount', 'exchangeVolume', 'priceBTC']
    for i in a:
        y = pd_data.loc[:, i]
        ys = list(preprocessing.scale(y))  # 归一化
        sam.append(ys)

    print
    len(sam)
    with open('eth2.csv', 'w') as file:
        writer = csv.writer(file)
        for i in range(len(sam[0])):
            writer.writerow([sam[0][i], sam[1][i], sam[2][i], sam[3][i], sam[4][i], sam[5][i]])
    print('完毕')


def build_lr():
    X = pd_data.loc[:, ('activeAddresses', 'adjustedVolume', 'paymentCount', 'exchangeVolume', 'priceBTC')]
    y = pd_data.loc[:, 'priceUSD']
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=532)  # 选择20%为测试集
    print('训练集测试及参数:')
    print('X_train.shape={}\n y_train.shape ={}\n X_test.shape={}\n,  y_test.shape={}'.format(X_train.shape,
                                                                                              y_train.shape,
                                                                                              X_test.shape,
                                                                                              y_test.shape))
    linreg = LinearRegression()
    # 训练
    model = linreg.fit(X_train, y_train)
    print('模型参数:')
    print(model)
    # 训练后模型截距
    print('模型截距:')
    print
    linreg.intercept_
    # 训练后模型权重（特征个数无变化）
    print('参数权重:')
    print(linreg.coef_)

    y_pred = linreg.predict(X_test)
    sum_mean = 0
    for i in range(len(y_pred)):
        sum_mean += (y_pred[i] - y_test.values[i]) ** 2
    sum_erro = np.sqrt(sum_mean / len(y_pred))  # 测试级的数量
    # calculate RMSE
    print("RMSE by hand:", sum_erro)
    # 做ROC曲线
    plt.figure()
    plt.plot(range(len(y_pred)), y_pred, 'b', label="predict")
    plt.plot(range(len(y_pred)), y_test, 'r', label="test")
    plt.legend(loc="upper right")  # 显示图中的标签
    plt.xlabel("the number of sales")
    plt.ylabel('value of sales')
    plt.show()
#! /usr/bin/env python3
# coding=utf-8
# ================================================================
# Copyright (C), 2019, TP-LINK Technologies Co., Ltd.
# package       :
# description   :
# date          :   2021/1/21
# author        :   qiuzezeng
# ================================================================
import pandas as pd
import os
from tqdm import tqdm
import time

try:
    import xml.etree.cElementTree as ET
except ImportError:
    import xml.etree.ElementTree as ET

path = 'F:/jenkins/result_sohoci_20210112/result_1/'
arrs = os.listdir(path)
res = pd.DataFrame(columns=('file_name', 'product_name', 'manifest', 'displayName', 'time'))
for cnt in tqdm(range(len(arrs))):
    try:
        tree = ET.parse(path + arrs[cnt])
        root = tree.getroot()
        info_dic = {}
        info_dic['file_name'] = arrs[cnt]
        if root.find('actions') and root.find('actions').find('hudson.model.ParametersAction'):
            for i in root.find('actions').find('hudson.model.ParametersAction').find('parameters').findall(
                    'hudson.model.StringParameterValue'):
                if i.find('name').text in ['BRANCH_XML', 'ManifestFile']:
                    info_dic['manifest'] = i.find('value').text
                if i.find('name').text in ['MODEL', 'product_name']:
                    info_dic['product_name'] = i.find('value').text
        if root.find('displayName') != None:
            info_dic['displayName'] = root.find('displayName').text
        info_dic['time'] = root.find('timestamp').text
        cur = pd.DataFrame(info_dic, index=[0])
        res = res.append(cur, ignore_index=True)
    except Exception:
        pass
res.to_csv('F:/jenkins/out/机型_mamnifest关联2.csv', index=0, encoding='utf-8-sig')

# 解析项目
import pandas as pd
import os

try:
    import xml.etree.cElementTree as ET
except ImportError:
    import xml.etree.ElementTree as ET

path = 'F:/jenkins/result_sohoci_20210112/result/'
# 去重
path1 = 'F:/jenkins/out/机型_mamnifest关联1.csv'
df1 = pd.read_csv(path1)
path2 = 'F:/jenkins/out/机型_mamnifest关联2.csv'
df2 = pd.read_csv(path2)
df3 = pd.concat([df1, df2])
df3['pre'] = df3['file_name'].apply(lambda x: x.split('+')[0])
df3 = df3.dropna(subset=['product_name']).drop_duplicates(subset=['pre','product_name','manifest'])
arrs = list(df3['file_name'])
res = pd.DataFrame(columns=('file_name', 'product_name', 'manifest', 'displayName', 'time', 'project', 'revision'))
for cnt in tqdm(range(len(arrs))):
    try:
        tree = ET.parse(path + arrs[cnt])
        root = tree.getroot()
        info_dic = {}
        info_dic['file_name'] = arrs[cnt]
        if root.find('actions') and root.find('actions').find('hudson.model.ParametersAction'):
            for i in root.find('actions').find('hudson.model.ParametersAction').find('parameters').findall(
                    'hudson.model.StringParameterValue'):
                if i.find('name').text in ['BRANCH_XML', 'ManifestFile']:
                    info_dic['manifest'] = i.find('value').text
                if i.find('name').text in ['MODEL', 'product_name']:
                    info_dic['product_name'] = i.find('value').text
        if root.find('displayName') != None:
            info_dic['displayName'] = root.find('displayName').text
        info_dic['time'] = root.find('timestamp').text
        if root.find('actions') and root.find('actions').find('hudson.plugins.repo.RevisionState'):
            m = root.find('actions').find('hudson.plugins.repo.RevisionState').find('manifest').text
            if m:
                m = [i for i in m.split('\n') if i.startswith('  <project name=')]
                for project in m:
                    info_dic['project'] = project.split('"')[1]
                    info_dic['revision'] = project.split('"')[-2]
                    cur = pd.DataFrame(info_dic, index=[0])
                    res = res.append(cur, ignore_index=True)
    except Exception:
        pass
res.to_csv('F:/jenkins/out/机型_项目关联1.csv', index=0, encoding='utf-8-sig')

# 机型-项目对应
res['time'] = res['time'].apply(lambda x : time.strftime('%Y/%m/%d %H:%M:%S',time.localtime(int(x)/1000)))
res = res.drop_duplicates(subset=['product_name','project'])
project = pd.DataFrame(res.groupby('product_name').apply(lambda x: list(x.project))).reset_index()
project.columns = ['product_name','project_list']
same = pd.DataFrame()
dic = {}
for i in tqdm(range(len(project)-1)):
    for j in range(i+1,len(project)):
        dic['productA'] = project.loc[i].product_name
        dic['productB'] = project.loc[j].product_name
        dic['procuctA_len'] = len(project.loc[i].project_list)
        dic['procuctB_len'] = len(project.loc[j].project_list)
        s = len(set(project.loc[i].project_list+project.loc[j].project_list))
        dic['相似度'] = (dic['procuctA_len']+dic['procuctB_len']-s)/s
        same = same.append(pd.DataFrame(dic,index=[0]),ignore_index=True)



# 字符串相似度,只做大写处理，取相似性最大
res = pd.read_csv('F:/jenkins/out/机型_项目关联v2.csv')
res['time'] = res['time'].apply(lambda x : time.strftime('%Y/%m/%d %H:%M:%S',time.localtime(int(x)/1000)))
res = res.drop_duplicates(subset=['product_name','project'])
product = res[['product_name']].drop_duplicates().sort_values(by=['product_name']).reset_index()
product['product_name_大写'] = product['product_name'].str.upper()

tm_df = pd.read_csv(r'\\file.tp-link.net\测试部\测试部自动化与实验室管理组\IT组\@统计数据\tm\tm_0120\tm_0120_002.csv',header=None)
tm_df = tm_df[[4]]
tm_df.columns=['机型型号']
tm_df = tm_df.drop_duplicates().reset_index()
tm_df['机型型号_大写'] = tm_df['机型型号'].str.upper()

import difflib
def string_similar(s1, s2):
    return difflib.SequenceMatcher(None, s1, s2).quick_ratio()

for i in tqdm(range(len(product))):
    max_ = 0
    j = 0
    for j in range(len(tm_df)):
        similar = string_similar(str(product['product_name_大写'][i]), str(tm_df['机型型号_大写'][j]))
        if max_ < similar:
            max_ = similar
            index = j
    product.loc[1,'对应tm机型'] = tm_df['机型型号'][index]

# 字符串相似度, 完全匹配
res = pd.read_csv('F:/jenkins/out/机型_项目关联v2.csv')
res['time'] = res['time'].apply(lambda x : time.strftime('%Y/%m/%d %H:%M:%S',time.localtime(int(x)/1000)))
res = res.drop_duplicates(subset=['product_name','project'])
product = res[['product_name']].drop_duplicates().sort_values(by=['product_name']).reset_index()
tm_df = product.copy()
tm_df['机型型号'] = tm_df['product_name'].copy()
tm_df['机型型号'] = tm_df['机型型号'].str.replace('-cn', '')
tm_df['机型型号'] = tm_df['机型型号'].str.replace('\\s+', '_')
tm_df['机型型号'] = tm_df['机型型号'].str.replace('-', '_', regex=False)
tm_df['机型型号'] = tm_df['机型型号'].str.replace('-', '_', regex=False)
tm_df['机型型号'] = tm_df['机型型号'].str.replace('—', '_', regex=False)
tm_df['机型型号'] = tm_df['机型型号'].str.replace('_', '', regex=False)
tm_df['机型型号'] = tm_df['机型型号'].str.replace('：', '', regex=False)
tm_df['机型型号'] = tm_df['机型型号'].str.replace('【', '[', regex=False)
tm_df['机型型号'] = tm_df['机型型号'].str.replace('】', ']', regex=False)
tm_df['机型型号'] = tm_df['机型型号'].str.replace('（', '(', regex=False)
tm_df['机型型号'] = tm_df['机型型号'].str.replace('）', ')', regex=False)
tm_df['机型型号'] = tm_df['机型型号'].str.replace('(P)', 'P', regex=False)
tm_df['机型型号'] = tm_df['机型型号'].str.replace('\\(.*?\\)$', '')
tm_df['机型型号'] = tm_df['机型型号'].str.replace('\\[.*?\\]$', '')
tm_df['机型型号'] = tm_df['机型型号'].str.replace('^\\[.*?\\]', '')
tm_df['机型型号'] = tm_df['机型型号'].str.replace('^\\(.*?\\)', '')
tm_df['机型型号'] = tm_df['机型型号'].str.upper()
tm_df['机型型号'] = tm_df['机型型号'].str.replace('=', '')
tm_df['机型型号'] = tm_df['机型型号'].str.replace('V', '')
product = tm_df.copy()

tm_df = pd.read_csv(r'\\file.tp-link.net\测试部\测试部自动化与实验室管理组\IT组\@统计数据\tm\tm_0120\tm_0120_002.csv',header=None)
tm_df = tm_df[[4]]
tm_df.columns=['机型型号']
tm_df = tm_df.drop_duplicates().reset_index()
tm_df.columns=['机型型号']
tm_df['机型型号_原始'] = tm_df['机型型号'].copy()
tm_df['机型型号'] = tm_df['机型型号'].str.replace('\\s+', '_')
tm_df['机型型号'] = tm_df['机型型号'].str.replace('-', '_', regex=False)
tm_df['机型型号'] = tm_df['机型型号'].str.replace('-', '_', regex=False)
tm_df['机型型号'] = tm_df['机型型号'].str.replace('—', '_', regex=False)
tm_df['机型型号'] = tm_df['机型型号'].str.replace('_', '', regex=False)
tm_df['机型型号'] = tm_df['机型型号'].str.replace('：', '', regex=False)
tm_df['机型型号'] = tm_df['机型型号'].str.replace('【', '[', regex=False)
tm_df['机型型号'] = tm_df['机型型号'].str.replace('】', ']', regex=False)
tm_df['机型型号'] = tm_df['机型型号'].str.replace('（', '(', regex=False)
tm_df['机型型号'] = tm_df['机型型号'].str.replace('）', ')', regex=False)
tm_df['机型型号'] = tm_df['机型型号'].str.replace('(P)', 'P', regex=False)
tm_df['机型型号'] = tm_df['机型型号'].str.replace('\\(.*?\\)$', '')
tm_df['机型型号'] = tm_df['机型型号'].str.replace('\\[.*?\\]$', '')
tm_df['机型型号'] = tm_df['机型型号'].str.replace('^\\[.*?\\]', '')
tm_df['机型型号'] = tm_df['机型型号'].str.replace('^\\(.*?\\)', '')
tm_df['机型型号'] = tm_df['机型型号'].str.upper()

def compare(line):
    for s in tm_df.机型型号:
        if str(line['机型型号']) in str(s):
            return s
product['tm机型'] = product.apply(compare, axis=1)

















## 机型相似度
res['time'] = res['time'].apply(lambda x : time.strftime('%Y/%m/%d %H:%M:%S',time.localtime(int(x)/1000)))
res = res.drop_duplicates(subset=['product_name','project'])
project = pd.DataFrame(res.groupby('product_name').apply(lambda x: list(x.project))).reset_index()
project.columns = ['product_name','project_list']
project['length'] = project.project_list.apply(lambda x: len(x))
same = pd.DataFrame()
dic = {}
for i in tqdm(range(len(project)-1)):
    for j in range(i+1,len(project)):
        dic['productA'] = project.loc[i].product_name
        dic['productB'] = project.loc[j].product_name
        dic['procuctA_len'] = len(project.loc[i].project_list)
        dic['procuctB_len'] = len(project.loc[j].project_list)
        s = len(set(project.loc[i].project_list+project.loc[j].project_list))
        dic['相似度'] = (dic['procuctA_len']+dic['procuctB_len']-s)/s
        same = same.append(pd.DataFrame(dic,index=[0]),ignore_index=True)

## 机型聚类
temp = same[same['相似度'] > 0.9]
compare = same[same['相似度'] > 0.8]
arrs = list(set(list(temp.productA) + list(temp.productB)))
cnt = 0
res = [[]]
al = []
for i in tqdm(range(len(arrs)-1)):
    if arrs[i] in al:
        continue
    else:
        res[cnt].append(arrs[i])
        al.append(arrs[i])
        for j in range(i+1,len(arrs)):
            if arrs[j] not in al:
                # 判断与res[cnt]里机型的相似性
#                 flag = 0
#                 for cur in res[cnt]:
#                     compare1 = compare[(compare['productA']==cur) & (compare['productB']==arrs[j])]
#                     compare2 = compare[(compare['productB']==cur) & (compare['productA']==arrs[j])]
#                     if len(compare1) == 1 or len(compare2)==1:
#                         pass
#                     else:
#                         flag = 1
#                         break

                compare1 = temp[(temp['productA']==arrs[i]) & (temp['productB']==arrs[j])]
                compare2 = temp[(temp['productB']==arrs[i]) & (temp['productA']==arrs[j])]
                if len(compare1) == 1 or len(compare2)==1:
                    res[cnt].append(arrs[j])
                    al.append(arrs[j])
        cnt += 1
        res.append([])





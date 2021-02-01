#! /usr/bin/env python3
# coding=utf-8
# ================================================================
# Copyright (C), 2019, TP-LINK Technologies Co., Ltd.
# package       :
# description   :
# date          :   2021/2/1
# author        :   qiuzezeng
# ================================================================
import pandas as pd
import numpy as np
import time
from tqdm import tqdm

a1 = pd.read_table(r'F:\jenkins\out\jenkins产物文件名.txt', header=None)
a2 = pd.read_table(r'F:\jenkins\out\jenkins产物文件名2.txt', header=None)
a = pd.concat([a1, a2])
a['file_name'] = a[0].apply(lambda x: x.split('!')[0])
a['file_str'] = a[0].apply(lambda x: x.split('!')[1])
jenkins = a[['file_name', 'file_str']]
dms = pd.read_csv(r'\\file.tp-link.net\测试部\测试部自动化与实验室管理组\IT组\@统计数据\DMS\DMS测试申请单.csv')
dms = dms[dms['approveStatus'] != '中止']
dms = dms[(dms['requesterProductLineName'] == '研发杭州分部') | (dms['requesterProductLineName'] == '视频产品线') | (
            dms['requesterProductLineName'] == 'SMB产品线')
          | (dms['requesterProductLineName'] == '运营商研发') | (dms['requesterProductLineName'] == '无线产品线')]
dms = dms[(dms['creationDate'] >= '2020-07-01') & (dms['creationDate'] < '2020-10-01')]

# 无url
tqdm.pandas(desc="my bar!")
dms_test = dms.copy()

def link(files):
    files = eval(files)
    files = list(map(lambda x: x[:x.rfind('.')], files))
    for file in files:
        for xml in list(jenkins['file_str']):
            if file in xml:
                return jenkins.loc[jenkins[jenkins['file_str'] == xml].index[0]]['file_name']
dms_test['link_xml'] = dms_test['attachFiles'].progress_apply(link)


# 有url
dms = pd.read_csv(r'\\file.tp-link.net\测试部\测试部自动化与实验室管理组\IT组\@统计数据\DMS\DMS测试申请单.csv')
dms = dms[dms['approveStatus'] != '中止']
dms = dms[(dms['requesterProductLineName'] == '研发杭州分部')|(dms['requesterProductLineName'] == '视频产品线')|(dms['requesterProductLineName'] == 'SMB产品线')
         |(dms['requesterProductLineName'] == '运营商研发')|(dms['requesterProductLineName'] == '无线产品线')]
dms = dms[(dms['creationDate'] >= '2020-07-01') & (dms['creationDate'] < '2020-10-01')]
dms = dms.dropna(subset=['jenkinsUrl'])
dms['link_xml'] = dms['jenkinsUrl'].apply(lambda x: x.split('\/')[-3] + '+'+x.split('\/')[-2]+'_bulid.xml' )
arrs = list(dms['link_xml'])
try:
    import xml.etree.cElementTree as ET
except ImportError:
    import xml.etree.ElementTree as ET

def find_project(path):
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
    return res
path1 = 'F:/jenkins/result_sohoci_20210112/result/'
path2 = 'F:/jenkins/result_sohoci_20210112/result_1/'
res = pd.concat([find_project(path1),find_project(path2)])

pro = pd.merge(dms,res, left_on='link_xml',right_on='file_name',how='left')

# 连接change
dms_change = dms[['fileId','attachFiles','itemModel','testType','creationDate','testNum','link_xml','requester','requesterProductLineName']]
dms_change['creationDate'] = dms_change['creationDate'].apply(lambda x:x.replace('T', ' '))
dms_change['last_fileId'] = dms_change['fileId'].shift(1)
dms_change['last_itemModel'] = dms_change['itemModel'].shift(1)
dms_change['last_testType'] = dms_change['testType'].shift(1)
dms_change['last_creationDate'] = dms_change['creationDate'].shift(1)
dms_change['last_testNum'] = dms_change['testNum'].shift(1)
dms_change = dms_change[(dms_change['itemModel'] == dms_change['last_itemModel']) & (dms_change['testType'] == dms_change['last_testType']) &
          (dms_change['testNum'] == dms_change['last_testNum']+1)]
dms_change['距离上一轮测试时间(天)'] = (pd.to_datetime(dms_change['creationDate']) - pd.to_datetime(dms_change['last_creationDate'])).map(
            lambda x: x / np.timedelta64(1, 'D'))
pro = pro[['fileId','product_name','manifest','displayName','time','project','revision']]
res = pd.merge(dms_change,pro,on='fileId',how='left')
res['time'] = res['time'].fillna(0)
res['这次编译时间'] = res['time'].apply(lambda x : time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(int(x)/1000)))
res = res.drop(columns=['time'])

change = pd.read_csv(r'\\file.tp-link.net\测试部\测试部自动化与实验室管理组\IT组\@统计数据\gerrit\all_years\changes.csv')
change = change[change['status']=='M']
def find_change(line):
    res = change[change['dest_project_name'] == line['project']]
    res = res[(res['last_updated_on']>=line['last_creationDate']) & (res['last_updated_on']<=line['creationDate'])]
    return list(res['change_id'])
res['关联change'] = res.progress_apply(find_change, axis=1)
def merge_change(df):
    arrs = []
    for arr in list(df['关联change']):
        arrs += arr
    return arrs
pro_change = res.groupby('fileId').apply(merge_change).reset_index()
pro_change.columns=['fileId','关联change']
pro_change = pd.merge(pro_change, dms_change, on='fileId', how='left').sort_values(by=['itemModel','testType','creationDate'])

# change具体信息
df = pro_change.copy()
res = pd.DataFrame()

for i in list(df['fileId']):
    dic = {}
    print(df[df['fileId']==i]['关联change'])
    for j in eval(df.loc[df[df['fileId']==i].index[0]]['关联change']):
        dic['fileId'] = i
        dic['change_id'] = j
        res = res.append(pd.DataFrame(dic,index=[0]))
res = pd.merge(res, df, on='fileId', how='left')
res = res.drop(columns=['关联change','attachFiles'])
change = pd.read_excel(r'E:\compare\middle\result\change基础表2021-01-28_191733.xlsx')
res = pd.merge(res, change, on='change_id', how='left')
team = pd.read_csv(r'\\file.tp-link.net\测试部\测试部自动化与实验室管理组\IT组\@统计数据\人员团队\20Q4绩效系统团队名单-名单导入-处理后(所有团队).csv')
res = pd.merge(res, team, left_on='change上传人', right_on='员工姓名', how='left')
res = pd.merge(res,team,left_on='requester', right_on='员工姓名', how='left')
res.to_csv('F:/jenkins/out/机型测试关联change具体信息.csv',index=0,encoding='utf-8-sig')







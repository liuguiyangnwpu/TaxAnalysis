# -*- coding: utf-8 -*-
import xlrd
import re
import jieba
import jieba.posseg
import jieba.analyse
import pandas as pd
import matplotlib.pyplot as plt
import sys
import codecs
import pickle as pkl
from .convert_chinese2arabic import convertChineseDigitsToArabic

def open_excel(file='file.xls'):
    try:
        data = xlrd.open_workbook(file)
        return data
    except Exception as e:
        print(str(e))

#根据名称获取Excel表格中的数据   参数:file：Excel文件路径     colnameindex：表头列名所在行的所以  ，by_name：Sheet1名称
def excel_table_byname(file='file.xls', colnameindex=0, by_name=u'Sheet1'):
    data = open_excel(file)
    table = data.sheet_by_name(by_name)
    nrows = table.nrows
    colnames =  table.row_values(colnameindex) #某一行数据
    list =[]
    for rownum in range(1,nrows):
         row = table.row_values(rownum)
         if row:
             app = {}
             for i in range(len(colnames)):
                app[colnames[i]] = row[i]
             list.append(app)
    return list

def processLabels():
   tables = excel_table_byname(file=u'../data/案例报告.xlsx')
   labels = []
   for row in tables:
       line = re.split(',|，|。|：', row["法规意见"].strip())
       ReLawname01 = re.compile(r'《[^》《]*\》[\u4e00-\u9fa5]{3,5}')
       ReLawname02 = re.compile(r'国家税务总局关于纳税人善意取得虚开增值税专用发票处理问题的通知[\u4e00-\u9fa5]{3,5}')
       ReLawname03 = re.compile(r'([《]\S+?[》])(?:（\S+?）)([\u4e00-\u9fa50-9]{3,7})')
       ReLawname04 = re.compile(r'([《]\S+?[》])(?:\[\S+?\])([\u4e00-\u9fa50-9]{3,7})')
       labels.append([])
       for item in line:
           res01 = ReLawname01.findall(item)
           if len(res01) == 0:
               res02 = ReLawname02.findall(item)
               if len(res02) == 0:
                   res03 = ReLawname03.findall(item)
                   if len(res03) == 0:
                       res04 = ReLawname04.findall(item)
                       if len(res04) != 0:
                           labels[-1].extend(res04)
                       else:
                           pass
                   else:
                       labels[-1].extend(res03)
               else:
                   labels[-1].extend(res02)
           else:
               labels[-1].extend(res01)
   return fetchSampleLabel(labels)

def fetchSampleLabel(labels):
    pass

def processSamples():
    def dealItem(infolist):
        reslist = []
        downalpha = [chr(c + ord('a')) for c in range(0, 26)]
        upalpha = [chr(c + ord('A')) for c in range(0, 26)]
        downalpha.extend(upalpha)
        downalpha.extend(['\t', '(', ')', '》', '《', ' ', '“', '”', '÷', '＋', '+', '-', '*', '/', '=', '%', '"', '"', ':', ';', '；', '／', '×', '％', '＝', '（', '一', '）', '二', '三'])
        for item in infolist:
            item = item.strip()
            if len(item) == 0:
                continue
            item = "".join(list(filter(lambda x:x not in '0123456789.,、', item)))
            item = "".join(list(filter(lambda x:x not in downalpha, item)))
            if len(item) > 1:
                reslist.append(item)
        return reslist

    tables = excel_table_byname(file=u'../data/案例报告.xlsx')
    samples = []
    for row in tables:
        line = re.split('\r\n', row["违法事实"].strip())
        rowsInfo,washInfo = [], []
        for item in line:
            rowsInfo.append([])
            rowsInfo[-1].extend(re.split(',|，|。|：', item.strip()))
            tmp = dealItem(rowsInfo[-1])
            if len(tmp) > 0:
                washInfo.append(tmp[-1])
        samples.append(washInfo)
    return samples

def statisticsEvent(samples):
    jieba.load_userdict("../data/laxdict.txt")
    print("Samples Nums is ", len(samples))
    topK = 50
    mostHighFrequent = {}
    for item in samples:
        singleEvent = ",".join(item) + "."
        seg_list = list(jieba.analyse.extract_tags(singleEvent, topK=topK))
        for word in seg_list:
            if word not in mostHighFrequent.keys():
                mostHighFrequent[word] = 1
            else:
                mostHighFrequent[word] += 1
    mostHighFrequent = sorted(mostHighFrequent.items(), key=lambda x:x[1], reverse=True)
    for item in mostHighFrequent:
        print(item[0], item[1])
    # pd_data = pd.DataFrame.from_dict(mostHighFrequent, orient='index')
    # pd_data.columns = ["cnt"]
    # pd_data['cnt'].plot()
    # plt.show()
    # print(pd_data)

def build_law_label():
    filepath = "../data/law.info"
    ind = 1
    law_dict = {}
    with codecs.open(filepath, 'r', 'utf-8') as handle:
        for line in handle:
            line = line.strip()
            law_dict[line] = ind
    with codecs.open("../data/law.pkl", 'wb') as handle:
        pkl.dump(law_dict, handle)

if __name__=="__main__":
    # samples = processSamples()
    # statisticsEvent(samples)
    build_law_label()
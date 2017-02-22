import sys
from sklearn.naive_bayes import GaussianNB
import numpy
import jieba
import jieba.posseg
import jieba.analyse
import xlrd
import pickle as pkl
import codecs


#读取excel
def open_excel(file=u'file.xls'):
    try:
        data = xlrd.open_workbook(file)
        return data
    except Exception as e:
        print(str(e))

#根据名称获取Excel表格中的数据   参数:file：Excel文件路径     colnameindex：表头列名所在行的所以  ，by_name：Sheet1名称
def excel_table_byname(file=u'file.xls', colnameindex=0, by_name=u'Sheet1'):
    data = open_excel(file)
    table = data.sheet_by_name(by_name)
    nrows = table.nrows
    colnames =  table.row_values(colnameindex) #某一行数据
    print("text col is："+str(nrows))
    l =[]
    for rownum in range(1,nrows):
         row = table.row_values(rownum)
         if row:
             app = {}
             for i in range(len(colnames)):
                app[colnames[i]] = row[i]
             l.append(app)
    return l

#读取标签
def read_label(labelfile=u'label.txt',lawinf=u'law.dict'):
    #labelfile  标签文件
    #lawinf     法律法规对应编号
    labels = []

    laws = read_lawinf(lawinf=lawinf,keycol=1,valuecol=0)
    lawclass = len(laws)
    print(labelfile)
    with codecs.open(labelfile, 'r', 'utf-8') as f:
        for line in f.readlines():
            label = line.strip().split(' ')[1:]
            index = numpy.zeros(lawclass,dtype=int) #根据标签包含的种类进行编号[0,0,1,...,0],以此作为样本标签
            if len(label) != 0:
                for i in range(0,len(label)):
                    lawindex = label[i].split('-')[0]
                    index[int(lawindex)-1] = 1
            labels.append(''.join(list(map(str,list(index)))))
    return numpy.array(labels)

#提取法律法规
def read_lawinf(lawinf=u'lawinf.dict',keycol=1,valuecol=0):
    #keywordsfile  法律法规对应编号
    #keywordindex  key所在的列
    #countindex    value所在的列
    law = {}
    print(lawinf)
    if lawinf.endswith('pkl'):
        if valuecol == 1:
            with open(lawinf, 'rb') as f:
                return pkl.load(f)
        if valuecol == 0:
            with open(lawinf, 'rb') as f:
                data = pkl.load(f)
                t = {}
                for key, val in data.items():
                    t[val] = key
                return t

#读取关键词
def read_keywords(keywordsfile=u'keywords.txt',keywordindex=0,countindex=1):
    #keywordsfile  结巴分词字典路径
    #keywordindex  关键词所在的列
    #countindex    词频所在的列
    keywords = {}
    with codecs.open(keywordsfile, 'r', 'utf-8') as f:
        index = 0
        for item in f.readlines():
            tmp = item.strip().split(' ')
            keywords[tmp[keywordindex]]=index #编号
            index += 1
    return keywords
    
#提取特征
def ext_feature(textfile=u'file.xls',dicfile=u'dic.txt', keywordsfile=u'keywords.txt'):
    #textfile      训练样本文件
    #dicfile       结巴分词字典路径
    #keywordsfile  关键词路径

    jieba.load_userdict(dicfile)
    
    tables = excel_table_byname(file=textfile)
    samplecount = len(tables) #样本个数
    keywords = read_keywords(keywordsfile=keywordsfile)
    featlen = len(keywords) #特征维数

    print(samplecount,featlen)
    features = numpy.zeros((samplecount,featlen),dtype=int)
    index = 0
    for row in tables:
        line = row[u'违法事实'].strip()
        tags = jieba.analyse.extract_tags(line)
        for item in tags:
            if item in keywords.keys():
                features[index][keywords[item]] = 1
        index += 1
 
    return features

def train(textfile=u'file.xlsx',dicfile=u'result_cut_for_search-2.txt',keywordsfile=u'keywords.txt',labelfile=u'labels.txt',lawinf=u'lawinf.dict'):
    #textfile     训练样本文件
    #dicfile      结巴分词字典路径
    #keywordsfile 关键词路径
    #labelfile    训练样本标签文件
    #lawinf       法律法规对应编号

    print ('training.')
    
    features = ext_feature(textfile=textfile,dicfile=dicfile,keywordsfile=keywordsfile)
    labels   = read_label(labelfile=labelfile,lawinf=lawinf)
    
    if features.shape[0] <= 0 or labels.shape[0] <= 0 or features.shape[0] != labels.shape[0]:
        raise ValueError("samples or labels error.")
    
    clf = GaussianNB()
    clf.fit(features, labels)
    return clf

def predict(textfile=u'file.xls',dicfile=u'dic.txt', keywordsfile=u'keywords.txt',lawinf=u'lawinf.dict',clf = GaussianNB()):
    jieba.load_userdict(dicfile)
    
    tables = excel_table_byname(file=textfile)
    samplecount = len(tables) #样本个数
    keywords = read_keywords(keywordsfile=keywordsfile)
    featlen = len(keywords) #特征维数

    laws = read_lawinf(lawinf=lawinf)
  
    results = []
    for row in tables:
        line = row[u'违法事实'].strip()
        tags = jieba.analyse.extract_tags(line)
        feature = numpy.zeros(featlen, dtype=int)
        for item in tags:
            if item in keywords.keys():
                feature[keywords.get(item)] = 1
        res = ''.join(clf.predict(feature.reshape(1, -1)))
        tmp = []
        for i in range(0, len(res)):
            if res[i] == '1':
                if i+1 in laws.keys():
                    tmp.append(laws[i+1])
                else:
                    print(str(i+1))
                    raise ValueError("laws error.")
        results.append(tmp)
 
    return results
    
def match(labelfile=u'labels.txt',resultfile=u'result.txt',lawinf=u'law.dict'):
    labels   = read_label(labelfile=labelfile,lawinf=lawinf)
    laws = read_lawinf(lawinf=lawinf,keycol=0,valuecol=1)
    lawclass = len(laws)
    result=[]
    with codecs.open(resultfile, 'r', 'utf-8') as f:
        for line in f.readlines():
            if len(line.strip()) == 0:
                result.append("0" * lawclass)
                continue
            tmp = line.strip().split(' ')
            index = numpy.zeros(lawclass, dtype=int)
            for i in range(0, len(tmp)):
                if tmp[i] in laws.keys():
                    lawindex = laws[tmp[i]]
                    index[int(lawindex)-1] = 1
                else:
                    print(tmp, len(tmp[i]))
                    raise ValueError("match error.")
            result.append(''.join(list(map(str, list(index)))))
    
    result = numpy.array(result)
    count = result.shape[0]

    def evaluation01(standard, sample):
        a, b = set(), set()
        for i in range(0, len(standard)):
            if standard[i] == '1':
                a.add(i)
            if sample[i] == '1':
                b.add(i)
        if len(a) == 0 and len(b): return False
        if len(a) == 0 and len(b) == 0: return True
        if len(b - a) / len(a) <= 0.5: return True
        return False

    def evaluation02(standard, sample):
        a, b = set(), set()
        for i in range(0, len(standard)):
            if standard[i] == '1':
                a.add(i)
            if sample[i] == '1':
                b.add(i)
        if len(a) == 0 and len(b): return False
        if len(a) == 0 and len(b) == 0: return True
        if len(a & b): return True
        return False

    def evaluation03(standard, sample):
        a, b = set(), set()
        for i in range(0, len(standard)):
            if standard[i] == '1':
                a.add(i)
            if sample[i] == '1':
                b.add(i)
        if len(a) == 0 and len(b): return 0.0
        if len(a) == 0 and len(b) == 0: return 1.0
        if len(a & b): return len(a&b) / len(a) * 1.0
        return 0.0

    rate = 0.0
    for i in range(0, len(labels)):
        val = evaluation03(labels[i], result[i])
        rate += val

    return rate/count

def main():
    textfile = '../data/train/案例报告.xlsx'
    dicfile = '../data/train/lawdict.txt'
    keywordsfile = '../data/train/keywords.txt'
    labelfile = '../data/train/samples.label'
    lawinf = '../data/train/law.pkl'

    if False:
        clf = train(textfile, dicfile, keywordsfile, labelfile, lawinf)
        result = predict(textfile, dicfile, keywordsfile, lawinf, clf)
        with codecs.open("result.txt", 'w', 'utf-8') as handle:
            for item in result:
                print(*item, file=handle)
    else:
        print(match(labelfile, 'result.txt', lawinf))


if __name__=="__main__":
    main()
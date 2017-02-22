from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
import sys
import os
import jieba
import jieba.posseg
import jieba.analyse
import pprint
import numpy as np
import codecs
from sklearn.naive_bayes import GaussianNB
from sklearn.externals import joblib

from source.UI.TaxUI import Ui_Form
from source.datawash import excel_table_byname
from source.datawash import processLabels
from source.datawash import processSamples
from source.datawash import build_law_label
from source.datawash import ext_feature
from source.prediction import read_keywords
from source.prediction import read_lawinf


class MyMainWidget(QWidget, Ui_Form):
    signal_ShowProgress = pyqtSignal(int)

    def __init__(self):
        super(MyMainWidget, self).__init__()
        self.setupUi(self)

        self.tableWidget_trainSamples.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tableWidget_trainFeature.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tableWidget_testBoard.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        # connect the signal to slots
        self.pushButton_loadSample.clicked.connect(self.load_TrainSamples)
        self.pushButton_loadTestCase.clicked.connect(self.load_TestSamples)
        self.pushButton_startTrain.clicked.connect(self.startTrain)
        self.pushButton_startTest.clicked.connect(self.startTest)
        self.pushButton_extractFeature.clicked.connect(self.extractFeature)

        # self make QObject
        self.basicTimer = QBasicTimer()
        self.basicTimer.stop()
        self.m_step = 0

        # global environments
        self.m_projDir = '/'.join(sys.path[0].split('/')[:-1]) + "/"
        self.m_dataDir = self.m_projDir + 'data/'
        self.m_trainDir = self.m_dataDir + "train/"
        self.m_testDir = self.m_dataDir + "test/"
        self.m_modelDir = self.m_dataDir + "model/"
        self.m_modelPath = self.m_modelDir + "lawGaussian.model"
        self.m_keywordsfile = self.m_trainDir + 'keywords.txt'
        self.m_dicfile = self.m_trainDir + 'lawdict.txt'

        # global data
        self.m_caseTable = None
        self.m_labelTable = None
        self.m_labelTableID = None
        self.m_keywords = None
        self.m_clf = None
        self.checkPrepare()

    def showQMessageBox(self, info, mode='info'):
        button = None
        if mode == 'info':
            button = QMessageBox.information(self, "通知", info,
                                             QMessageBox.Ok, QMessageBox.Ok)
        if mode == 'warn':
            button = QMessageBox.warning(self, "警告", info,
                                         QMessageBox.Ok|QMessageBox.Cancel, QMessageBox.Cancel)
        if mode == 'error':
            button = QMessageBox.critical(self, "严重问题", info,
                                          QMessageBox.Ok, QMessageBox.Ok)
        return button

    def checkPrepare(self):
        if not (os.path.isdir(self.m_dataDir) and os.path.isdir(self.m_trainDir) and os.path.isdir(self.m_testDir) and os.path.isdir(self.m_modelDir)):
            self.showQMessageBox("工程目录结构不对！！！", "error")
            raise Exception("目录结构不对，请检查工程的目录！")
        if not (os.path.isfile(self.m_dicfile) and os.path.isfile(self.m_keywordsfile)):
            self.showQMessageBox("重要文件缺失！！！", "error")
            raise Exception("语料库文件或者关键词文件可能不存在！")

    def timerEvent(self, event):
        if self.m_step >= 100:
            self.basicTimer.stop()
            self.m_step = 0
            return
        self.m_step += 1
        self.progressBar.setValue(self.m_step)

    def doAction(self):
        if self.basicTimer.isActive():
            self.basicTimer.stop()
        else:
            self.basicTimer.start(10, self)

    def load_TrainSamples(self):
        if self.tableWidget_trainSamples.rowCount():
            button = self.showQMessageBox("确定导入新的数据?", "warn")
            if button == QMessageBox.Cancel:
                return
            else:
                self.tableWidget_trainSamples.clearContents()
                self.tableWidget_trainSamples.clear()
                self.tableWidget_trainSamples.setHorizontalHeaderLabels(['案件描述', '法规意见'])
        filepath = self.m_trainDir + "案例报告.xlsx"
        tables = excel_table_byname(filepath)
        self.m_caseTable = processSamples(tables)
        lawpath = self.m_trainDir + "law.info"
        build_law_label(lawpath)
        self.m_labelTable, self.m_labelTableID = processLabels(filepath, tables)
        self.tableWidget_trainSamples.setRowCount(len(tables))
        ind = 0
        for i in range(0, len(self.m_caseTable)):
            a, b = ','.join(self.m_caseTable[i]) + ".", tables[i]['法规意见']
            self.tableWidget_trainSamples.setItem(ind, 0, QTableWidgetItem(a))
            self.tableWidget_trainSamples.setItem(ind, 1, QTableWidgetItem(b))
            ind += 1

    def extractFeature(self):
        if self.tableWidget_trainFeature.rowCount():
            button = self.showQMessageBox("确定导入新的数据?", "warn")
            if button == QMessageBox.Cancel:
                return
            else:
                self.tableWidget_trainFeature.clearContents()
                self.tableWidget_trainFeature.clear()
                self.tableWidget_trainFeature.setHorizontalHeaderLabels(['案件描述', '法规意见'])
        features = ext_feature(self.m_caseTable, self.m_trainDir)
        self.tableWidget_trainFeature.setRowCount(len(features))
        ind = 0
        for i in range(0, len(features)):
            a = ','.join(features[i])
            b = ','.join(self.m_labelTable[i])
            self.tableWidget_trainFeature.setItem(ind, 0, QTableWidgetItem(a))
            self.tableWidget_trainFeature.setItem(ind, 1, QTableWidgetItem(b))
            ind += 1
        self.lineEdit_caseNum.setText(str(len(features)) + " 件")
        if self.m_keywords == None:
            self.m_keywords = read_keywords(self.m_keywordsfile)
        self.lineEdit_featureDim.setText(str(len(self.m_keywords)) + " 维")
        self.lineEdit_lawNum.setText(str(len(self.m_keywords)) + " 部")
        with codecs.open(self.m_dicfile, 'r', 'utf-8') as handle:
            corpusSize = len(handle.readlines())
            self.lineEdit_corpusSize.setText(str(corpusSize) + " 条")

    def startTrain(self):
        lawinf = '../data/train/law.pkl'
        if self.m_caseTable == None or self.m_labelTableID == None:
            self.showQMessageBox("请先加载原始数据，并进行特征提取", 'warn')
            return
        def case2features():
            jieba.load_userdict(self.m_dicfile)
            if self.m_keywords == None:
                self.m_keywords = read_keywords(self.m_keywordsfile)
            featlen = len(self.m_keywords)  # 特征维数
            samplecount = len(self.m_caseTable)
            t_features = np.zeros((samplecount, featlen), dtype=int)
            index = 0
            for row in self.m_caseTable:
                line = ','.join(row) + "."
                tags = jieba.analyse.extract_tags(line)
                for item in tags:
                    if item in self.m_keywords.keys():
                        t_features[index][self.m_keywords[item]] = 1
                index += 1
            return t_features

        def label2features():
            t_labels = []
            laws = read_lawinf(lawinf=lawinf, keycol=1, valuecol=0)
            lawclass = len(laws)
            for line in self.m_labelTableID:
                index = np.zeros(lawclass, dtype=int)  # 根据标签包含的种类进行编号[0,0,1,...,0],以此作为样本标签
                if len(line) != 0:
                    for i in range(0, len(line)):
                        lawindex = line[i].split('-')[0]
                        index[int(lawindex) - 1] = 1
                t_labels.append(''.join(list(map(str, list(index)))))
            return np.array(t_labels)

        features = case2features()
        labels = label2features()

        if features.shape[0] <= 0 or labels.shape[0] <= 0 or features.shape[0] != labels.shape[0]:
            raise ValueError("samples or labels error.")

        self.m_clf = GaussianNB()
        self.m_clf.fit(features, labels)
        joblib.dump(self.m_clf, self.m_modelPath)
        self.showQMessageBox("朴素贝叶斯模型训练完成!")

    def load_TestSamples(self):
        pass

    def startTest(self):
        pass

if __name__ == "__main__":
    app = QApplication(sys.argv)
    mainWidget = MyMainWidget()
    mainWidget.show()
    sys.exit(app.exec_())
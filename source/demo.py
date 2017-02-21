from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
import sys
import os
import time
from source.UI.TaxUI import Ui_Form
from source.datawash import excel_table_byname
from source.datawash import processLabels
from source.datawash import processSamples
from source.datawash import build_law_label
from source.datawash import ext_feature
import pprint

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

        # self make QObject
        self.progressBar = QProgressDialog()
        self.progressBar.setWindowModality(Qt.WindowModal)
        # self.progressBar.setMinimumDuration(5)
        self.progressBar.setWindowTitle("数据处理中")
        self.progressBar.setLabelText("处理中...")
        self.progressBar.setRange(0, 100)

        self.basicTimer = QBasicTimer()
        self.basicTimer.stop()
        self.m_step = 0

        # global environments
        self.m_projDir = '/'.join(sys.path[0].split('/')[:-1]) + "/"
        self.m_dataDir = self.m_projDir + 'data/'
        self.m_trainDir = self.m_dataDir + "train/"
        self.m_testDir = self.m_dataDir + "test/"
        self.m_modelDir = self.m_dataDir + "model/"

        # global data
        self.m_caseTable = None
        self.m_labelTable = None
        self.checkPrepare()

    def checkPrepare(self):
        if not (os.path.isdir(self.m_dataDir) and os.path.isdir(self.m_trainDir) and os.path.isdir(self.m_testDir) and os.path.isdir(self.m_modelDir)):
            raise Exception("目录结构不对，请检查工程的目录！")

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
            self.progressBar.show()
            self.basicTimer.start(10, self)

    def load_TrainSamples(self):
        # self.doAction()
        filepath = self.m_trainDir + "案例报告.xlsx"
        tables = excel_table_byname(filepath)
        self.m_caseTable = processSamples(tables)
        lawpath = self.m_trainDir + "law.info"
        build_law_label(lawpath)
        self.m_labelTable, _ = processLabels(filepath, tables)
        self.tableWidget_trainSamples.setRowCount(len(tables))
        ind = 0
        for i in range(0, len(self.m_caseTable)):
            a, b = ','.join(self.m_caseTable[i]) + ".", tables[i]['法规意见']
            self.tableWidget_trainSamples.setItem(ind, 0, QTableWidgetItem(a))
            self.tableWidget_trainSamples.setItem(ind, 1, QTableWidgetItem(b))
            ind += 1

        features = ext_feature(self.m_caseTable, self.m_trainDir)
        self.tableWidget_trainFeature.setRowCount(len(features))
        ind = 0
        for i in range(0, len(features)):
            a = ','.join(features[i])
            b = ','.join(self.m_labelTable[i])
            self.tableWidget_trainFeature.setItem(ind, 0, QTableWidgetItem(a))
            self.tableWidget_trainFeature.setItem(ind, 1, QTableWidgetItem(b))
            ind += 1
        # pprint.pprint(self.m_caseTable)
        # pprint.pprint(self.m_labelTable)

    def load_TestSamples(self):
        pass

    def startTrain(self):
        pass

    def startTest(self):
        pass

if __name__ == "__main__":
    app = QApplication(sys.argv)
    mainWidget = MyMainWidget()
    mainWidget.show()
    sys.exit(app.exec_())
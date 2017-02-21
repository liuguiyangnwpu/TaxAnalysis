from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
import PyQt5.QtCore as QtCore
import sys
import os
from source.UI.TaxUI import Ui_Form

class MyMainWidget(QWidget, Ui_Form):
    def __init__(self):
        super(MyMainWidget, self).__init__()
        self.setupUi(self)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    mainWidget = MyMainWidget()
    mainWidget.show()
    sys.exit(app.exec_())
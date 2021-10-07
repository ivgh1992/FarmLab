#Created by: Ivan Guerrero
#Last change: 10.09.2021

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QFileDialog, QWidget, QGridLayout, QMessageBox
from myMethods import importCSV2
import pandas as pd

csvList = []
printersdf = pd.read_excel(r'printerConfig.xlsx') 
i = 0
for i in range (len(printersdf)):    
    ip = printersdf.iloc[i,1]
    csvList.append(ip)

print (csvList)

#Attention! It was necessary to change Ui_newWindow(object) to Ui_downloadWindow(QWidget)
class Ui_downloadWindow(QWidget):
    def setupUi(self, downloadWindow):
        downloadWindow.setObjectName("downloadWindow")
        downloadWindow.resize(1175, 162)
        self.centralwidget = QtWidgets.QWidget(downloadWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.title = QtWidgets.QLabel(self.centralwidget)
        self.title.setGeometry(QtCore.QRect(310, 10, 471, 51))
        font = QtGui.QFont()
        font.setFamily("Century Gothic")
        font.setPointSize(16)
        font.setBold(True)
        font.setWeight(75)
        self.title.setFont(font)
        self.title.setObjectName("title")
        self.labelFilePath = QtWidgets.QLabel(self.centralwidget)
        self.labelFilePath.setGeometry(QtCore.QRect(10, 60, 111, 51))
        font = QtGui.QFont()
        font.setFamily("Century Gothic")
        font.setPointSize(16)
        font.setBold(True)
        font.setWeight(75)
        self.labelFilePath.setFont(font)
        self.labelFilePath.setObjectName("labelFilePath")
        self.lineEdit = QtWidgets.QLineEdit(self.centralwidget)
        self.lineEdit.setGeometry(QtCore.QRect(120, 69, 801, 31))
        self.lineEdit.setObjectName("lineEdit")
        #Browse Button
        self.browseButton = QtWidgets.QPushButton(self.centralwidget)
        self.browseButton.setGeometry(QtCore.QRect(940, 70, 101, 31))
        font = QtGui.QFont()
        font.setFamily("Century Gothic")
        font.setPointSize(10)
        self.browseButton.setFont(font)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap("Photos/Browse.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.browseButton.setIcon(icon)
        self.browseButton.setObjectName("browseButton")
        self.browseButton.clicked.connect(self.selectDirectory)
        #Save button
        self.saveButton = QtWidgets.QPushButton(self.centralwidget)
        self.saveButton.setGeometry(QtCore.QRect(1060, 70, 101, 31))
        font = QtGui.QFont()
        font.setFamily("Century Gothic")
        font.setPointSize(10)
        self.saveButton.setFont(font)
        icon1 = QtGui.QIcon()
        icon1.addPixmap(QtGui.QPixmap("Photos/Upload.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.saveButton.setIcon(icon1)
        self.saveButton.setObjectName("saveButton")
        self.saveButton.clicked.connect(lambda: importCSV2(csvList, self.lineEdit.text()))
        downloadWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(downloadWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 1175, 21))
        self.menubar.setObjectName("menubar")
        downloadWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(downloadWindow)
        self.statusbar.setObjectName("statusbar")
        downloadWindow.setStatusBar(self.statusbar)

        self.retranslateUi(downloadWindow)
        QtCore.QMetaObject.connectSlotsByName(downloadWindow)
    
    def selectDirectory(self):
        directoryName = QFileDialog.getExistingDirectory(self, "Select path")
        self.lineEdit.setText(directoryName)
    
    def retranslateUi(self, downloadWindow):
        _translate = QtCore.QCoreApplication.translate
        downloadWindow.setWindowTitle(_translate("downloadWindow", "downloadWindow"))
        self.title.setText(_translate("downloadWindow", "Select where you want to save the CSV-files"))
        self.labelFilePath.setText(_translate("downloadWindow", "File Path:"))
        self.browseButton.setText(_translate("downloadWindow", "Browse"))
        self.saveButton.setText(_translate("downloadWindow", "Save"))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    downloadWindow = QtWidgets.QMainWindow()
    ui = Ui_downloadWindow()
    ui.setupUi(downloadWindow)
    downloadWindow.show()
    sys.exit(app.exec_())


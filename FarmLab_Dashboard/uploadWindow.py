#Created by: Ivan Guerrero
#Last change: 10.09.2021

from PyQt5 import QtCore, QtGui, QtWidgets
import sys
from PyQt5.QtCore import QThread, pyqtSignal, QObject
from PyQt5.QtWidgets import QFileDialog, QWidget, QGridLayout, QMessageBox
from PyQt5.uic import loadUi
from octorest import OctoRest
import os
from myMethods import updateJobsList
import time

class External(QThread):
    def __init__(self, printer, path, combobox):
        super().__init__()
        self.printer = printer
        self.path = path
        self.combobox = combobox
    uploadStateChanged = pyqtSignal(str)
    def run(self):
        filePath = self.path.text()
        if filePath != "": 
            try:    
                uploadState = self.printer.upload(filePath)
                if uploadState["done"] == True:
                        name = str(uploadState["files"]["local"]["name"])
                        self.uploadStateChanged.emit(name + " was successfully uploaded")
                        
            except RuntimeError as ex:
                self.uploadStateChanged.emit(str(ex))
            except TypeError as ex:
                self.uploadStateChanged.emit(str(ex))
        if filePath == "":
            self.uploadStateChanged.emit("No file was selected")
        

#Attention! It was necessary to change Ui_newWindow(object) to Ui_uploadWindow(QWidget)
class Ui_uploadWindow(QWidget):
    def __init__(self, printer, combobox): 
        super().__init__()      
        self.printer = printer
        self.combobox = combobox

    def setupUi(self, uploadWindow):
        uploadWindow.setObjectName("uploadWindow")
        uploadWindow.resize(941, 200)
        self.centralwidget = QtWidgets.QWidget(uploadWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.scrollArea = QtWidgets.QScrollArea(self.centralwidget)
        self.scrollArea.setGeometry(QtCore.QRect(0, 0, 1, 1))
        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.setObjectName("scrollArea")
        self.scrollAreaWidgetContents = QtWidgets.QWidget()
        self.scrollAreaWidgetContents.setGeometry(QtCore.QRect(0, 0, 16, 16))
        self.scrollAreaWidgetContents.setObjectName("scrollAreaWidgetContents")
        self.scrollArea.setWidget(self.scrollAreaWidgetContents)
        #pathLabel
        self.pathLabel = QtWidgets.QLabel(self.centralwidget)
        self.pathLabel.setGeometry(QtCore.QRect(10, 90, 90, 31))
        self.pathLabel.setObjectName("pathLabel")
        font = QtGui.QFont()
        font.setPointSize(12)
        font.setBold(True)
        self.pathLabel.setFont(font)
        #Path
        self.path = QtWidgets.QLineEdit(self.centralwidget)
        self.path.setGeometry(QtCore.QRect(120, 90, 630, 31))
        self.path.setObjectName("path")
        #Browse Button
        self.browseButton = QtWidgets.QPushButton(self.centralwidget)
        self.browseButton.setGeometry(QtCore.QRect(730, 90, 88, 31))
        self.browseButton.setObjectName("browseButton")
        self.browseButton.clicked.connect(self.browseFiles)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap("Photos/Browse.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.browseButton.setIcon(icon)
        #Upload Button
        self.uploadButton = QtWidgets.QPushButton(self.centralwidget)
        self.uploadButton.setGeometry(QtCore.QRect(830, 90, 91, 31))
        self.uploadButton.setObjectName("uploadButton")
        self.uploadButton.clicked.connect(lambda: self.runUplaod(self.printer, self.path, self.combobox))
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap("Photos/Upload.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.uploadButton.setIcon(icon)
        #Title
        self.title = QtWidgets.QLabel(self.centralwidget)
        self.title.setGeometry(QtCore.QRect(220, 10, 141, 41))
        font = QtGui.QFont()
        font.setPointSize(16)
        font.setBold(True)
        self.title.setFont(font)
        self.title.setAlignment(QtCore.Qt.AlignCenter)
        self.title.setObjectName("title")
        uploadWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(uploadWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 941, 21))
        self.menubar.setObjectName("menubar")
        uploadWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(uploadWindow)
        self.statusbar.setObjectName("statusbar")
        uploadWindow.setStatusBar(self.statusbar)
        #StatusLight
        self.statusLight = QtWidgets.QLabel(self.centralwidget)
        self.statusLight.setGeometry(QtCore.QRect(10, 150, 30, 30))
        self.statusLight.setObjectName("statusLight")
        self.statusLight.setStyleSheet("background-color: #00838F; border-radius: 15px;")
        font = QtGui.QFont()
        font.setPointSize(10)
        self.statusLight.setFont(font)
        #StatusLabel
        self.statusLabel = QtWidgets.QLabel(self.centralwidget)
        self.statusLabel.setGeometry(QtCore.QRect(50, 150, 300, 30))
        self.statusLabel.setObjectName("statusLabel")
        #self.statusLabel.setStyleSheet("background-color: #00838F;")
        font = QtGui.QFont()
        font.setPointSize(10)
        self.statusLabel.setFont(font)
        
        self.retranslateUi(uploadWindow)
        QtCore.QMetaObject.connectSlotsByName(uploadWindow)
    
           
    def browseFiles(self):
        fileName = QFileDialog.getOpenFileName(self, "Open File")
        self.path.setText(fileName[0])


    def runUplaod(self, printer, path, combobox):
        self.upload = External(printer, path, combobox)
        self.upload.uploadStateChanged.connect(self.onUploadStateChanged)
        self.upload.start()
        self.statusLight.setStyleSheet("background-color: #FA897B; border-radius: 15px;")
        self.statusLabel.setText("Status: Uploading. Please wait a moment...")
        
    def onUploadStateChanged(self, text):
        updateJobsList(self.printer, self.combobox)
        self.statusLight.setStyleSheet("background-color: #00838F; border-radius: 15px;")
        self.statusLabel.setText("Status: Waiting for a file to upload")
        self.msg = QMessageBox()       
        self.msg.setText(str(text))
        self.msg.setIcon(QMessageBox.Information)
        self.msg.exec()

    def retranslateUi(self, uploadWindow):
        _translate = QtCore.QCoreApplication.translate
        uploadWindow.setWindowTitle(_translate("uploadWindow", "MainWindow"))
        self.pathLabel.setText(_translate("uploadWindow", "File Path:"))
        self.statusLabel.setText(_translate("uploadWindow", "Status: Waiting for a file to upload"))
        self.browseButton.setText(_translate("uploadWindow", "Browse"))
        self.uploadButton.setText(_translate("uploadWindow", "Upload"))
        self.title.setText(_translate("uploadWindow", "SELECT THE G-CODE YOU WANT TO UPLOAD"))
        self.title.adjustSize()


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    uploadWindow = QtWidgets.QMainWindow()
    ui = Ui_uploadWindow()
    ui.setupUi(uploadWindow)
    uploadWindow.show()
    sys.exit(app.exec_())

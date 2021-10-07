#Created by: Ivan Guerrero
#Last change: 10.09.2021

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QWidget, QMessageBox
from myMethods import *
import psycopg2

#Attention! It was necessary to change Ui_newWindow(object) to Ui_changeSpoolWindow(QWidget)
class Ui_changeSpoolWindow(QWidget):

    def __init__(self, myHost, myDatabase, myUser, myPass, myPrinterid, printer): 
        super().__init__()      
        self.myHost = myHost
        self.myDatabase = myDatabase
        self.myUser = myUser
        self.myPass = myPass
        self.myPrinterid = myPrinterid 
        self.printer = printer
        
    def setupUi(self, changeSpoolWindow):
        changeSpoolWindow.setObjectName("changeSpoolWindow")
        changeSpoolWindow.resize(597, 140)
        #get number of tools
        self.toolInfo = self.printer.tool()
        self.toolQuantity = len(self.toolInfo)
        #get an updated list of the spools being used
        self.spoolsList = get_spoolsList(self.myHost,self.myDatabase,self.myUser,self.myPass,self.myPrinterid)
        self.spoolsList.append("--Remove Spool--")
        #Create the layout for the window
        self.centralwidget = QtWidgets.QWidget(changeSpoolWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.scrollArea = QtWidgets.QScrollArea(self.centralwidget)
        self.scrollArea.setGeometry(QtCore.QRect(160, 10, 1, 1))
        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.setObjectName("scrollArea")
        self.scrollAreaWidgetContents = QtWidgets.QWidget()
        self.scrollAreaWidgetContents.setGeometry(QtCore.QRect(0, 0, 16, 16))
        self.scrollAreaWidgetContents.setObjectName("scrollAreaWidgetContents")
        self.scrollArea.setWidget(self.scrollAreaWidgetContents)
        self.title = QtWidgets.QLabel(self.centralwidget)
        self.title.setGeometry(QtCore.QRect(1, 20, 600, 31))
        font = QtGui.QFont()
        font.setPointSize(16)
        self.title.setFont(font)
        self.title.setAlignment(QtCore.Qt.AlignCenter)
        self.title.setObjectName("title")
        #tool box
        self.toolBox = QtWidgets.QComboBox(self.centralwidget)
        self.toolBox.setGeometry(QtCore.QRect(80, 70, 50, 31))
        self.toolBox.setObjectName("toolBox")
        for tool in range(0,self.toolQuantity):    
                self.toolBox.addItem(str(tool))
        #combo box
        self.comboBox = QtWidgets.QComboBox(self.centralwidget)
        self.comboBox.setGeometry(QtCore.QRect(150, 70, 300, 31))
        self.comboBox.setObjectName("comboBox")
        for spool in self.spoolsList:    
                self.comboBox.addItem(spool)
        #selectButton
        self.selectButton = QtWidgets.QPushButton(self.centralwidget)
        self.selectButton.setGeometry(QtCore.QRect(470, 70, 75, 31))
        self.selectButton.setObjectName("selectButton")
        self.selectButton.clicked.connect(lambda: self.changeSpool(self.myPrinterid))
        
        changeSpoolWindow.setCentralWidget(self.centralwidget)
        self.statusbar = QtWidgets.QStatusBar(changeSpoolWindow)
        self.statusbar.setObjectName("statusbar")
        changeSpoolWindow.setStatusBar(self.statusbar)

        self.retranslateUi(changeSpoolWindow)
        QtCore.QMetaObject.connectSlotsByName(changeSpoolWindow)
        
    
    def changeSpool(self, myPrinterid):
        try:
            #Read the name of the spool to change and the selected tool
            newSpool = self.comboBox.currentText()
            selectedTool = self.toolBox.currentText()
            if newSpool == "--Remove Spool--":
                #sql_remove = "DELETE FROM selections WHERE client_id = '%s' and tool = %s;"
                sql_remove = "UPDATE selections set spool_id = NULL WHERE client_id = '%s' and tool = %s;"
                conn = psycopg2.connect(dbname = self.myDatabase, user = self.myUser, password = self.myPass, host = self.myHost)
                #get the id of the spool being selected
                cursor = conn.cursor()
                cursor.execute(sql_remove%(myPrinterid,selectedTool))
                conn.commit()
                cursor.close()
                conn.close()
                msg = QMessageBox()
                msg.setText("Spool was succcessfully removed")
                msg.setStandardButtons(QMessageBox.Ok)
                msg.setIcon(QMessageBox.Information)
                msg.exec()
            elif newSpool != "--Remove Spool--":
                #get the id of the selected spool
                sql_id = "SELECT id FROM spools WHERE name='%s';"
                #change the spool 
                sql_update = "UPDATE selections SET spool_id= %s WHERE client_id='%s' and tool=%s;"
                conn = psycopg2.connect(dbname = self.myDatabase, user = self.myUser, password = self.myPass, host = self.myHost)
                #get the id of the spool being selected
                cursor = conn.cursor()
                cursor.execute(sql_id%(newSpool))
                spoolid = cursor.fetchall()
                #update to the new spool
                cursor.execute(sql_update%(spoolid[0][0],myPrinterid,selectedTool))#spoolid has the form [(1,)], therefore we have to extract the integer of the list by using spoolid[0][0]
                conn.commit()
                cursor.close()
                conn.close()
                msg = QMessageBox()
                msg.setText("Spool was succcessfully changed")
                msg.setStandardButtons(QMessageBox.Ok)
                msg.setIcon(QMessageBox.Information)
                msg.exec()
        
        except:  
            msg = QMessageBox()
            msg.setText("Spool couldn't be changed")
            msg.setIcon(QMessageBox.Warning)
            msg.setStandardButtons(QMessageBox.Ok)
            msg.setInformativeText("Check your connection to the PostgreSQL server")
            msg.exec()
    
    def retranslateUi(self, changeSpoolWindow):
        _translate = QtCore.QCoreApplication.translate
        changeSpoolWindow.setWindowTitle(_translate("changeSpoolWindow", "MainWindow"))
        self.title.setText(_translate("changeSpoolWindow", "Select a tool and assign a spool to it"))
        self.selectButton.setText(_translate("changeSpoolWindow", "SELECT"))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    changeSpoolWindow = QtWidgets.QMainWindow()
    ui = Ui_changeSpoolWindow()
    ui.setupUi(changeSpoolWindow)
    changeSpoolWindow.show()
    sys.exit(app.exec_())


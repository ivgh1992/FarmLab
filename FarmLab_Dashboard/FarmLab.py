#Created by: Ivan Guerrero
#Last change: 10.09.2021

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import QUrl, QThread, pyqtSignal, QSize
from PyQt5.QtWidgets import QWidget, QGridLayout, QMessageBox, QVBoxLayout, QGraphicsOpacityEffect
from PyQt5 import QtWebEngineWidgets
from PyQt5.QtGui import QMovie
from uploadWindow import Ui_uploadWindow
from changeSpoolWindow import Ui_changeSpoolWindow
from CSVdownloadWindow import Ui_downloadWindow
import pandas as pd
from myMethods import *
import re

#Create list to store the clients, used for the list of user status
clientList = []
#Read Postgres Credentials
postgresdf = pd.read_excel(r'postgresConfig.xlsx') 
#save postgres credentials
myHost = postgresdf.iloc[0,0]
myDatabase = postgresdf.iloc[0,1]
myUser = postgresdf.iloc[0,2]
myPass = postgresdf.iloc[0,3]
#create printers list for CSV-import by reading printerconfig file
csvList = []
printersdf = pd.read_excel(r'printerConfig.xlsx') 
i = 0
for i in range (len(printersdf)):    
    ip = printersdf.iloc[i,1]
    csvList.append(ip)
#Read url of TSD server
tsd_df = pd.read_excel(r'TSDConfig.xlsx')
tsd_url = tsd_df.iloc[0,0] 

#Create a class inheriting from QThread to create a background procees for each printer
class External(QThread):
    def __init__(self, printer, postgresID): #Add __init__ in order to pass
        super().__init__()      #the printer property
        self.printer = printer  #and make the code rehusable for each printer
        self.postgresID = postgresID
        
    progressChanged = pyqtSignal(int)    
    jobNameChanged = pyqtSignal(str)
    statusChanged = pyqtSignal(str)
    timeLeftChanged = pyqtSignal(str)
    toolTempChanged = pyqtSignal(str)
    bedTempChanged = pyqtSignal(str)
    spoolChanged = pyqtSignal(list)
    
    def run(self):
        while True:
            jobName = get_jobName(self.printer)
            status = get_status(self.printer)
            timeLeft = get_timeLeft(self.printer)
            progress = get_printProgress(self.printer)
            toolTemp = get_toolTemp(self.printer)
            bedTemp = get_bedTemp(self.printer)
            spoolsList = get_spoolInUse(myHost, myDatabase, myUser, myPass, self.postgresID)
            self.progressChanged.emit(progress)
            self.jobNameChanged.emit(jobName)
            self.statusChanged.emit(status)
            self.timeLeftChanged.emit(timeLeft)
            self.toolTempChanged.emit(toolTemp)
            self.bedTempChanged.emit(bedTemp)
            self.spoolChanged.emit(spoolsList)
            time.sleep(3)
            
#Create a class inheriting from QThread to create a background procees to extract a list of the status of the printers
class External_2(QThread):
    def __init__(self, printerList): 
        super().__init__()              
        self.printerList = printerList  
        
    statusListChanged = pyqtSignal(list)
    def run(self):
        while True: 
            statusList = get_statusList(self.printerList)
            self.statusListChanged.emit(statusList)
            time.sleep(3)

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(985, 822)
        #camera counter fro changing between cameras
        self.cameraCount=1
        #Layout Counters: used to assign a space for the widgets in the gridLayout
        self.i=4
        self.j=0
        self.k=2
        #start background process for the status list of the printers
        self.calc = External_2(clientList)
        self.calc.statusListChanged.connect(self.onStatusListChanged)
        self.calc.start()
        #widget List
        self.widgetListCameras = []
        self.widgetListCP = []
        self.widgetListPJH = []
        #Central Widget
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.gridLayout_12 = QtWidgets.QGridLayout(self.centralwidget)
        self.gridLayout_12.setObjectName("gridLayout_12")
        self.tabWidget = QtWidgets.QTabWidget(self.centralwidget)
        font = QtGui.QFont()
        font.setPointSize(16)
        self.tabWidget.setFont(font)
        self.tabWidget.setObjectName("tabWidget")
        self.tabCameras = QtWidgets.QWidget()
        self.tabCameras.setObjectName("tabCameras")
        self.tabCameras.setStyleSheet("border-radius :10px;")
        self.gridLayout_3 = QtWidgets.QGridLayout(self.tabCameras)
        self.gridLayout_3.setObjectName("gridLayout_3")
        self.scrollArea_2 = QtWidgets.QScrollArea(self.tabCameras)
        self.scrollArea_2.setWidgetResizable(True)
        self.scrollArea_2.setObjectName("scrollArea_2")
        self.scrollAreaCameras = QtWidgets.QWidget()
        self.scrollAreaCameras.setGeometry(QtCore.QRect(0, 0, 941, 705))
        self.scrollAreaCameras.setObjectName("scrollAreaCameras")   
        self.gridLayout_5 = QtWidgets.QGridLayout(self.scrollAreaCameras)
        self.gridLayout_5.setObjectName("gridLayout_5")
        self.gridLayoutCameras = QtWidgets.QGridLayout()
        self.gridLayoutCameras.setObjectName("gridLayoutCameras")
        self.scrollAreaCameras.setStyleSheet("background-color: #fff;")
        self.gridLayout_5.addLayout(self.gridLayoutCameras, 0, 0, 1, 1) 
        ###Start of: Status counters###
        #closed
        self.closedPrinters = QtWidgets.QLabel(self.scrollAreaCameras)
        self.closedPrinters.setObjectName("closedPrinters")
        self.closedPrinters.setMaximumSize(QtCore.QSize(500, 20))
        self.closedPrinters.setText("Disconnected")
        font = QtGui.QFont()
        font.setFamily("Arial")
        font.setPointSize(8)
        self.closedPrinters.setFont(font)
        self.closedPrinters.setAlignment(QtCore.Qt.AlignRight)
        self.gridLayoutCameras.addWidget(self.closedPrinters,0,3,1,1)
        #Operational
        self.operationalPrinters = QtWidgets.QLabel(self.scrollAreaCameras)
        self.operationalPrinters.setObjectName("operationalPrinters")
        self.operationalPrinters.setMaximumSize(QtCore.QSize(500, 20))
        self.operationalPrinters.setText("Operational")
        font = QtGui.QFont()
        font.setFamily("Arial")
        font.setPointSize(8)
        self.operationalPrinters.setFont(font)
        self.operationalPrinters.setAlignment(QtCore.Qt.AlignRight)
        self.gridLayoutCameras.addWidget(self.operationalPrinters,1,3,1,1)
        #printing
        self.printingPrinters = QtWidgets.QLabel(self.scrollAreaCameras)
        self.printingPrinters.setObjectName("printingPrinters")
        self.printingPrinters.setMaximumSize(QtCore.QSize(500, 20))
        self.printingPrinters.setText("Printing")
        font = QtGui.QFont()
        font.setPointSize(8)
        font.setFamily("Arial")
        self.printingPrinters.setFont(font)
        self.printingPrinters.setAlignment(QtCore.Qt.AlignRight)
        self.gridLayoutCameras.addWidget(self.printingPrinters,2,3,1,1)
        #paused
        self.pausedPrinters = QtWidgets.QLabel(self.scrollAreaCameras)
        self.pausedPrinters.setObjectName("pausedPrinters")
        self.pausedPrinters.setMaximumSize(QtCore.QSize(500, 20))
        self.pausedPrinters.setText("Paused")
        font = QtGui.QFont()
        font.setPointSize(8)
        font.setFamily("Arial")
        self.pausedPrinters.setFont(font)
        self.pausedPrinters.setAlignment(QtCore.Qt.AlignRight)
        self.gridLayoutCameras.addWidget(self.pausedPrinters,3,3,1,1)
        ###End of: Status Counters###
        #Logo FarmLab
        self.FarmLabIcon = QtWidgets.QLabel(self.scrollAreaCameras)
        self.FarmLabIcon.setObjectName("FarmLabIcon")
        self.FarmLabIcon.setMinimumSize(QtCore.QSize(300, 100))
        self.FarmLabIcon.setMaximumSize(QtCore.QSize(300, 100))
        self.FarmLabIcon.setPixmap(QtGui.QPixmap("Photos/Logo.png"))
        self.FarmLabIcon.setScaledContents(True)
        self.FarmLabIcon.setStyleSheet("background-color: rgba(0,0,0,0)")
        self.gridLayoutCameras.addWidget(self.FarmLabIcon,0,0,4,1, alignment=QtCore.Qt.AlignLeft)   
        self.scrollArea_2.setWidget(self.scrollAreaCameras)
        self.gridLayout_3.addWidget(self.scrollArea_2, 1, 0, 1, 1)
        self.tabWidget.addTab(self.tabCameras, "")
        self.tabControl = QtWidgets.QWidget()
        self.tabControl.setObjectName("tabControl")
        self.tabControl.setStyleSheet("border-radius :10px;")
        self.gridLayout_2 = QtWidgets.QGridLayout(self.tabControl)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.scrollAreaControl = QtWidgets.QScrollArea(self.tabControl)
        self.scrollAreaControl.setStyleSheet("")
        self.scrollAreaControl.setWidgetResizable(True)
        self.scrollAreaControl.setObjectName("scrollAreaControl")
        self.scrollAreaControl.setStyleSheet("background-color: #fff;")
        self.scrollAreaWidgetContents = QtWidgets.QWidget()
        self.scrollAreaWidgetContents.setGeometry(QtCore.QRect(0, 0, 941, 705))
        self.scrollAreaWidgetContents.setObjectName("scrollAreaWidgetContents")
        self.verticalLayout_11 = QtWidgets.QVBoxLayout(self.scrollAreaWidgetContents)
        self.verticalLayout_11.setObjectName("verticalLayout_11")
        self.verticalLayoutCP = QtWidgets.QVBoxLayout()
        self.verticalLayoutCP.setObjectName("verticalLayoutCP")
        self.verticalLayout_11.addLayout(self.verticalLayoutCP)
        self.scrollAreaControl.setWidget(self.scrollAreaWidgetContents)
        self.gridLayout_2.addWidget(self.scrollAreaControl, 0, 0, 1, 1)
        self.tabWidget.addTab(self.tabControl, "")
        self.tabJobHistory = QtWidgets.QWidget()
        self.tabJobHistory.setObjectName("tabJobHistory")
        self.verticalLayout_3 = QtWidgets.QVBoxLayout(self.tabJobHistory)
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.labelPrintJobHistory = QtWidgets.QLabel(self.tabJobHistory)
        self.labelPrintJobHistory.setMinimumSize(QtCore.QSize(0, 75))
        self.labelPrintJobHistory.setMaximumSize(QtCore.QSize(16777215, 75))
        font = QtGui.QFont()
        font.setPointSize(24)
        self.labelPrintJobHistory.setFont(font)
        self.labelPrintJobHistory.setFrameShape(QtWidgets.QFrame.Box)
        self.labelPrintJobHistory.setFrameShadow(QtWidgets.QFrame.Plain)
        self.labelPrintJobHistory.setAlignment(QtCore.Qt.AlignCenter)
        self.labelPrintJobHistory.setObjectName("labelPrintJobHistory")
        self.verticalLayout_3.addWidget(self.labelPrintJobHistory)
        self.scrollArea = QtWidgets.QScrollArea(self.tabJobHistory)
        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.setObjectName("scrollArea")
        self.scrollAreaWidgetContents_3 = QtWidgets.QWidget()
        self.scrollAreaWidgetContents_3.setGeometry(QtCore.QRect(0, 0, 941, 593))
        self.scrollAreaWidgetContents_3.setObjectName("scrollAreaWidgetContents_3")
        self.gridLayout_6 = QtWidgets.QGridLayout(self.scrollAreaWidgetContents_3)
        self.gridLayout_6.setObjectName("gridLayout_6")
        self.gridLayoutJobHistory = QtWidgets.QGridLayout()
        self.gridLayoutJobHistory.setObjectName("gridLayoutJobHistory")
        self.gridLayout_6.addLayout(self.gridLayoutJobHistory, 0, 0, 1, 1)
        self.scrollArea.setWidget(self.scrollAreaWidgetContents_3)
        #Style for the PJH Tab
        self.scrollArea.setStyleSheet("background-color: #fff;")
        self.verticalLayout_3.addWidget(self.scrollArea)
        self.label_2 = QtWidgets.QLabel(self.tabJobHistory)
        self.label_2.setText("")
        self.label_2.setObjectName("label_2")
        self.verticalLayout_3.addWidget(self.label_2)
        self.tabWidget.addTab(self.tabJobHistory, "")
        self.tabTSD = QtWidgets.QWidget()
        self.tabTSD.setObjectName("tabTSD")
        self.gridLayout_4 = QtWidgets.QGridLayout(self.tabTSD)
        self.gridLayout_4.setObjectName("gridLayout_4")
        self.scrollAreaTSD = QtWidgets.QScrollArea(self.tabTSD)
        self.scrollAreaTSD.setWidgetResizable(True)
        self.scrollAreaTSD.setObjectName("scrollAreaTSD")
        self.scrollAreaWidgetContents_2 = QtWidgets.QWidget()
        self.scrollAreaWidgetContents_2.setGeometry(QtCore.QRect(0, 0, 941, 705))
        self.scrollAreaWidgetContents_2.setObjectName("scrollAreaWidgetContents_2")
        self.gridLayout_7 = QtWidgets.QGridLayout(self.scrollAreaWidgetContents_2)
        self.gridLayout_7.setObjectName("gridLayout_7")
        #TSD Browser
        self.browserTSD = QtWebEngineWidgets.QWebEngineView(self.scrollAreaWidgetContents_2)
        self.browserTSD.setUrl(QtCore.QUrl("about:blank"))
        self.browserTSD.setObjectName("browserTSD")
        self.browserTSD.load(QUrl(tsd_url))
        self.gridLayout_7.addWidget(self.browserTSD, 0, 0, 1, 1)
        self.scrollAreaTSD.setWidget(self.scrollAreaWidgetContents_2)
        self.gridLayout_4.addWidget(self.scrollAreaTSD, 0, 0, 1, 1)
        self.tabWidget.addTab(self.tabTSD, "")
        self.gridLayout_12.addWidget(self.tabWidget, 0, 0, 1, 1)
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 985, 21))
        self.menubar.setObjectName("menubar")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)
        ###Widgets for Print Job History###
        #Widget for CSV import
        self.widget = QWidget()
        self.widget.setMinimumSize(500,110)
        self.widget.setMaximumSize(500,110)
        self.JPHLayout = QVBoxLayout(self.widget)
        self.widget.setLayout(self.JPHLayout) 
        #TitlePJH
        self.title = QtWidgets.QLabel(self.widget)
        self.title.setObjectName("title")
        self.title.setMaximumSize(QtCore.QSize(500, 60))
        self.title.setText("All Printers")
        font = QtGui.QFont()
        font.setPointSize(16)
        font.setFamily("Arial")
        self.title.setFont(font)
        self.title.setStyleSheet("QLabel{border-radius: 5px; background-color: #F2F2F2;}")
        self.title.setAlignment(QtCore.Qt.AlignCenter)
        self.JPHLayout.addWidget(self.title)
        #csvButton
        self.csvButton = QtWidgets.QPushButton(self.widget)
        self.csvButton.setObjectName("csvButton")
        self.csvButton.setMaximumSize(QtCore.QSize(500, 60))
        self.csvButton.setStyleSheet("QPushButton{background-color: #00838F;} QPushButton::pressed{background-color: #c5caca;}")
        font = QtGui.QFont()
        font.setPointSize(12)
        font.setFamily("Arial")
        self.csvButton.setFont(font)
        self.csvButton.setText("Import CSV")
        self.csvButton.clicked.connect(self.openCSVdownloadWindow)
        self.JPHLayout.addWidget(self.csvButton)
        self.gridLayoutJobHistory.addWidget(self.widget, 0,1,1,2 )
        ###End Widgets for Print Job History###
        
        self.retranslateUi(MainWindow)
        self.tabWidget.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)
        
        try:
            self.createPrinters()
        except RuntimeError as exe:
            print(exe)
            msg = QMessageBox()
            msg.setText("Couldn't create the printers")
            msg.setIcon(QMessageBox.Warning)
            msg.setInformativeText("Check your connection and the credentials in the printerConfig file")
            msg.exec()
            
    #Create an instance of a printer in each Tab of the Dashboard.
    def addPrinter(self,name,ip,key,postgresID):
        #Methods to change values of labels of Bravo  
        def onProgressChanged(value):
            if value == 100:
                progressBar.setValue(value)
                progressBar.setStyleSheet("QProgressBar{background-color: #fff; border: solid grey; border-radius: 10px;}"
                                                "QProgressBar::chunk{background-color: #A5CF51;border-radius :10px;}")
                progressBarCP.setValue(value)
                progressBarCP.setStyleSheet("QProgressBar{background-color: #fff; border: solid grey; border-radius: 20px;}"
                                                "QProgressBar::chunk{background-color: #A5CF51;border-radius :20px;}")
            else:
                progressBar.setValue(value)
                progressBar.setStyleSheet("QProgressBar{background-color: #fff; border: solid grey; border-radius: 10px;}"
                                                "QProgressBar::chunk{background-color: #3fa6d6; border-radius :10px;}")
                progressBarCP.setValue(value)
                progressBarCP.setStyleSheet("QProgressBar{background-color: #fff; border: solid grey; border-radius: 20px;}"
                                                "QProgressBar::chunk{background-color: #3fa6d6;border-radius :20px;}")
        def onNameChanged(text):
            jobName.setText("Job Name: "+ text)
            jobNameCP.setText("Job Name: "+ text)
        def onStatusChanged(text):
            opacity_effect = QGraphicsOpacityEffect()
            status.setText("Status: " + text)
            statusCP.setText("Status: " + text)
            if text == "Printing" or "Printing from SD":
                status.setStyleSheet("background-color: #428CD4; border-radius: 5px; border: 1px solid;border-color: #fff;")
                statusCP.setStyleSheet("background-color: #428CD4; border-radius: 5px; border: 1px solid;border-color: #fff;")
                connectButton.setEnabled(False)
                opacity_effect.setOpacity(0.2)
                connectButton.setGraphicsEffect(opacity_effect)
            if text == "Operational":
                status.setStyleSheet("background-color: #A5CF51; border-radius: 5px; border: 1px solid;border-color: #fff;")
                statusCP.setStyleSheet("background-color: #A5CF51; border-radius: 5px; border: 1px solid;border-color: #fff;")
                connectButton.setEnabled(False)
                opacity_effect.setOpacity(0.2)
                connectButton.setGraphicsEffect(opacity_effect)
            if text == "Paused":
                status.setStyleSheet("background-color: #FFC543; border-radius: 5px; border: 1px solid;border-color: #fff;")
                statusCP.setStyleSheet("background-color: #FFC543; border-radius: 5px; border: 1px solid;border-color: #fff;")
                connectButton.setEnabled(False)
                opacity_effect.setOpacity(0.2)
                connectButton.setGraphicsEffect(opacity_effect)
            if text == "Closed":
                status.setStyleSheet("background-color: #FA897B; border-radius: 5px; border: 1px solid;border-color: #fff;")
                status.setText("Status: Disconnected")
                statusCP.setStyleSheet("background-color: #FA897B; border-radius: 5px; border: 1px solid;border-color: #fff;")
                statusCP.setText("Status: Disconnected")
                connectButton.setDisabled(False)
                opacity_effect.setOpacity(1)
                connectButton.setGraphicsEffect(opacity_effect)
                
        def onTimeLeftChanged(text):
            timeLeft.setText("Time Left: " + text)
            timeLeftCP.setText(text)
        def onBedTempChanged(text):
            bedTemp.setText("Bed " + text)
            temperatures = []
            for temp in re.split("/|°| ", text):
                if temp.isdigit():
                    temperatures.append(int(temp))
            actualTemp = temperatures[0]
            targetTemp = temperatures[1]
            animatedGif = QMovie("Photos/TemperatureGif.gif")
            if actualTemp < targetTemp-1 and targetTemp>0:
                bedTempIcon.setMovie(animatedGif)
                animatedGif.start()
            else:
                bedTempIcon.setMovie(animatedGif)
                animatedGif.stop()
                bedTempIcon.setPixmap(QtGui.QPixmap("Photos/Temperature.png"))
        def onToolTempChanged(text):
            toolTemp.setText("Tool " + text)
            temperatures = []
            for temp in re.split("/|°| ", text):
                if temp.isdigit():
                    temperatures.append(int(temp))
            actualTemp = temperatures[0]
            targetTemp = temperatures[1]
            animatedGif = QMovie("Photos/TemperatureGif.gif")
            if actualTemp < targetTemp-1 and targetTemp>0:
                toolTempIcon.setMovie(animatedGif)
                animatedGif.start()
            else:
                toolTempIcon.setMovie(animatedGif)
                animatedGif.stop()
                toolTempIcon.setPixmap(QtGui.QPixmap("Photos/Temperature.png"))
        def onSpoolChanged(spoolsList):
            spoolBox.clear()
            for spool in spoolsList:    
                spoolBox.addItem(spool)   
        
        widget = QWidget()
        widget.setMaximumSize(500,600)
        gridLayout = QGridLayout(widget)
        widget.setLayout(gridLayout)
        widget.setStyleSheet("background-color: #F2F2F2;")        
        videoURL = ip + "/webcam/?action=stream"
        ####Cameras####
        #create client
        printer = make_client(url=ip,apikey=key)
        clientList.append(printer)
        #Start background processes
        calc = External(printer, postgresID)
        calc.progressChanged.connect(onProgressChanged)
        calc.jobNameChanged.connect(onNameChanged)
        calc.timeLeftChanged.connect(onTimeLeftChanged)
        calc.statusChanged.connect(onStatusChanged)
        calc.toolTempChanged.connect(onToolTempChanged)
        calc.bedTempChanged.connect(onBedTempChanged)
        calc.spoolChanged.connect(onSpoolChanged)
        calc.start()
        #Title
        title = QtWidgets.QLabel(widget)
        title.setObjectName("title")
        title.setMaximumSize(QtCore.QSize(500, 60))
        title.setText(name)
        font = QtGui.QFont()
        font.setPointSize(16)
        font.setBold(True)
        font.setFamily("Arial")
        title.setFont(font)
        title.setAlignment(QtCore.Qt.AlignCenter)
        title.setStyleSheet("QLabel{border-radius: 5px; border-color: #3a3d3d; background-color: #fff}")
        gridLayout.addWidget(title,0,0,1,2)
        #video
        video = QtWebEngineWidgets.QWebEngineView(widget)
        video.setMinimumSize(QtCore.QSize(300, 250))
        video.setMaximumSize(QtCore.QSize(500, 400))
        video.setUrl(QtCore.QUrl("about:blank"))
        video.setObjectName("video")
        video.load(QUrl(videoURL))
        video.show()
        gridLayout.addWidget(video,1,0,1,2)
        #Progress Bar
        progressBar = QtWidgets.QProgressBar(widget)
        progressBar.setMinimumSize(QtCore.QSize(250, 20))
        progressBar.setMaximumSize(QtCore.QSize(500, 20))
        progressBar.setStyleSheet("QProgressBar{border: solid grey; border-radius:10px 10px 10px 10px;} QProgressBar::chunk{background-color: #3fa6d6; border-radius:10px 10px 10px 10px;}")
        progressBar.setProperty("value", 0)
        progressBar.setAlignment(QtCore.Qt.AlignCenter)
        progressBar.setObjectName("progressBar")
        gridLayout.addWidget(progressBar, 2, 0, 1, 2)
        #StopButton
        stopButton = QtWidgets.QPushButton(widget)
        stopButton.setObjectName("stopButton" + name)
        stopButton.setMinimumSize(QtCore.QSize(125, 30))
        stopButton.setMaximumSize(QtCore.QSize(125, 30))
        stopButton.setStyleSheet("QPushButton{background-color: #00838F; text-align: left; padding: 5px;} QPushButton::pressed{background-color: #c5caca;}")
        font = QtGui.QFont()
        font.setPointSize(12)
        font.setFamily("Arial")
        stopButton.setFont(font)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap("Photos/Pause.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        stopButton.setIcon(icon)
        stopButton.setIconSize(QSize(20,20))
        gridLayout.addWidget(stopButton,3,1,1,1)
        stopButton.setText("Pause")
        stopButton.clicked.connect(lambda: pausePrinter(printer))
        #resumeButton
        resumeButton = QtWidgets.QPushButton(widget)
        resumeButton.setObjectName("resumeButton" + name)
        resumeButton.setMinimumSize(QtCore.QSize(125, 30))
        resumeButton.setMaximumSize(QtCore.QSize(125, 30))
        resumeButton.setStyleSheet("QPushButton{background-color: #00838F; text-align: left; padding: 5px;} QPushButton::pressed{background-color: #c5caca;}")
        font = QtGui.QFont()
        font.setPointSize(12)
        font.setFamily("Arial")
        resumeButton.setFont(font)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap("Photos/Resume.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        resumeButton.setIcon(icon)
        resumeButton.setIconSize(QSize(20,20))
        gridLayout.addWidget(resumeButton,4,1,1,1)
        resumeButton.setText("Resume")
        resumeButton.clicked.connect(lambda: resumePrinter(printer))
        #Status Label
        status = QtWidgets.QLabel(widget)
        status.setObjectName("status")
        status.setMinimumSize(QtCore.QSize(200, 30))
        status.setMaximumSize(QtCore.QSize(400, 30))
        status.setText("Status: ")
        font = QtGui.QFont()
        font.setFamily("Arial")
        font.setPointSize(12)
        status.setFont(font)
        status.setAlignment(QtCore.Qt.AlignLeft)
        gridLayout.addWidget(status,3,0,1,1)
        #Time Left Label
        timeLeft = QtWidgets.QLabel(widget)
        timeLeft.setObjectName("timeLeft")
        timeLeft.setMinimumSize(QtCore.QSize(200, 30))
        timeLeft.setMaximumSize(QtCore.QSize(400, 30))
        timeLeft.setText("Time Left: ")
        font = QtGui.QFont()
        font.setFamily("Arial")
        font.setPointSize(12)
        timeLeft.setFont(font)
        timeLeft.setAlignment(QtCore.Qt.AlignLeft)
        gridLayout.addWidget(timeLeft,4,0,1,1)
        #Job name label
        jobName = QtWidgets.QLabel(widget)
        jobName.setObjectName("jobName")
        jobName.setMinimumSize(QtCore.QSize(200, 30))
        jobName.setMaximumSize(QtCore.QSize(500, 30))
        jobName.setText("Job Name: ")
        font = QtGui.QFont()
        font.setFamily("Arial")
        font.setPointSize(12)
        jobName.setFont(font)
        jobName.setAlignment(QtCore.Qt.AlignLeft)
        gridLayout.addWidget(jobName,5,0,1,1)
        
        self.gridLayoutCameras.addWidget(widget, self.i, self.j)
        self.widgetListCameras.append(widget)
            
        ####Control Panel####
        widgetCP = QWidget()
        widgetCP.setMaximumSize(2500,200)
        gridLayoutCP = QGridLayout(widgetCP)
        widgetCP.setLayout(gridLayoutCP)
        #set background colors
        if(self.k % 2) ==0:
            widgetCP.setStyleSheet("background-color: #D0D5DD;")
        else:
            widgetCP.setStyleSheet("background-color: #F2F2F2;")
        self.k+=1
        #video
        videoCP = QtWebEngineWidgets.QWebEngineView(widgetCP)
        videoCP.setMinimumSize(QtCore.QSize(200, 100))
        videoCP.setMaximumSize(QtCore.QSize(200, 200))
        videoCP.setUrl(QtCore.QUrl("about:blank"))
        videoCP.setObjectName("videoCP")
        videoCP.load(QUrl(videoURL))
        videoCP.show()
        gridLayoutCP.addWidget(videoCP,0,0,3,1)
        #titleCP
        titleCP = QtWidgets.QLabel(widgetCP)
        titleCP.setObjectName("titleCP")
        titleCP.setMaximumSize(QtCore.QSize(150, 40))
        titleCP.setText(name)
        font = QtGui.QFont()
        font.setPointSize(12)
        font.setBold(True)
        font.setFamily("Arial")
        titleCP.setFont(font)
        titleCP.setAlignment(QtCore.Qt.AlignCenter)
        titleCP.setStyleSheet("QLabel{border-radius: 5px; border: 1px solid;border-color: #fff;}")
        gridLayoutCP.addWidget(titleCP,0,1,1,1)
        #octoButton
        octoButton = QtWidgets.QPushButton(widget)
        octoButton.setObjectName("octoButton")
        octoButton.setMinimumSize(QtCore.QSize(150, 40))
        octoButton.setMaximumSize(QtCore.QSize(150, 40))
        if(self.k % 2) ==0:
            octoButton.setStyleSheet("QPushButton{background-color: #00838F;} QPushButton::pressed{background-color: #c5caca;}")
        else:
            octoButton.setStyleSheet("QPushButton{background-color: #144466;} QPushButton::pressed{background-color: #c5caca;}")
        font = QtGui.QFont()
        font.setPointSize(10)
        font.setFamily("Arial")
        octoButton.setFont(font)
        gridLayoutCP.addWidget(octoButton,0,2,1,1)
        octoButton.setText("Open OctoPrint")
        octoButton.clicked.connect(lambda: open_webbrowser(ip))
        #bedTemp
        bedTemp = QtWidgets.QLabel(widgetCP)
        bedTemp.setObjectName("bedTemp")
        bedTemp.setMinimumSize(QtCore.QSize(150, 40))
        bedTemp.setMaximumSize(QtCore.QSize(150, 40))
        bedTemp.setText("Bed ")
        font = QtGui.QFont()
        font.setPointSize(10)
        font.setFamily("Arial")
        bedTemp.setFont(font)
        bedTemp.setAlignment(QtCore.Qt.AlignCenter)
        bedTemp.setStyleSheet("QLabel{border-radius: 5px; border: 1px solid;border-color: #fff;}")
        gridLayoutCP.addWidget(bedTemp,0,3,1,1)
        #bedTempIcon
        bedTempIcon = QtWidgets.QLabel(widgetCP)
        bedTempIcon.setObjectName("bedTempIcon")
        bedTempIcon.setMinimumSize(QtCore.QSize(20, 35))
        bedTempIcon.setMaximumSize(QtCore.QSize(20, 35))
        bedTempIcon.setPixmap(QtGui.QPixmap("Photos/Temperature.png"))
        bedTempIcon.setScaledContents(True)
        bedTempIcon.setStyleSheet("background-color: rgba(0,0,0,0)")
        gridLayoutCP.addWidget(bedTempIcon,0,3,1,1)
        #toolTemp
        toolTemp = QtWidgets.QLabel(widgetCP)
        toolTemp.setObjectName("toolTemp")
        toolTemp.setMinimumSize(QtCore.QSize(150, 40))
        toolTemp.setMaximumSize(QtCore.QSize(150, 40))
        toolTemp.setText("Tool ")
        font = QtGui.QFont()
        font.setPointSize(10)
        font.setFamily("Arial")
        toolTemp.setFont(font)
        toolTemp.setAlignment(QtCore.Qt.AlignCenter)
        toolTemp.setStyleSheet("QLabel{border-radius: 5px; border: 1px solid;border-color: #fff;}")
        gridLayoutCP.addWidget(toolTemp,0,4,1,1)
        #toolTempIcon
        toolTempIcon = QtWidgets.QLabel(widgetCP)
        toolTempIcon.setObjectName("toolTempIcon")
        toolTempIcon.setMinimumSize(QtCore.QSize(20, 35))
        toolTempIcon.setMaximumSize(QtCore.QSize(20, 35))
        toolTempIcon.setPixmap(QtGui.QPixmap("Photos/Temperature.png"))
        toolTempIcon.setScaledContents(True)
        toolTempIcon.setStyleSheet("background-color: rgba(0,0,0,0)")
        gridLayoutCP.addWidget(toolTempIcon,0,4,1,1)
        #spool
        spoolBox = QtWidgets.QComboBox(widgetCP)
        spoolBox.setMinimumSize(QtCore.QSize(300, 40))
        spoolBox.setMaximumSize(QtCore.QSize(1000, 40))
        spoolBox.setStyleSheet("QComboBox{background-color: rgb(255, 255, 255); border-radius: 5px;}"
                               "QComboBox::drop-down{background-color: #fff; border-radius: 5px; padding-right: 15px;}"
                               "QComboBox::down-arrow{image:url(Photos/DropDown.png); width: 30px; height: 30px;}")
        spoolBox.setObjectName("spoolBox")
        font = spoolBox.font()
        font.setPointSize(10)
        spoolBox.setFont(font)
        gridLayoutCP.addWidget(spoolBox, 0, 5, 1, 4)
        #changeSpoolButton
        changeSpoolButton = QtWidgets.QPushButton(widgetCP)
        changeSpoolButton.setObjectName("changeSpoolButton")
        changeSpoolButton.setMinimumSize(QtCore.QSize(40, 40))
        changeSpoolButton.setMaximumSize(QtCore.QSize(40, 40))
        if(self.k % 2) ==0:
            changeSpoolButton.setStyleSheet("QPushButton{background-color: #00838F;} QPushButton::pressed{background-color: #c5caca;}")
        else:
            changeSpoolButton.setStyleSheet("QPushButton{background-color: #144466;} QPushButton::pressed{background-color: #c5caca;}")
        font = QtGui.QFont()
        font.setPointSize(10)
        font.setFamily("Arial")
        changeSpoolButton.setFont(font)
        gridLayoutCP.addWidget(changeSpoolButton,0,9,1,1)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap("Photos/Spool.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        changeSpoolButton.setIcon(icon)
        changeSpoolButton.setIconSize(QSize(25,25))
        changeSpoolButton.clicked.connect(lambda: self.openChangeSpoolWindow(myHost, myDatabase, myUser, myPass, postgresID, printer))
        #upButton
        upButton = QtWidgets.QPushButton(widgetCP)
        upButton.setObjectName("upButton")
        upButton.setMinimumSize(QtCore.QSize(50, 40))
        upButton.setMaximumSize(QtCore.QSize(50, 40))
        if(self.k % 2) ==0:
            upButton.setStyleSheet("QPushButton{background-color: #00838F;} QPushButton::pressed{background-color: #c5caca;}")
        else:
            upButton.setStyleSheet("QPushButton{background-color: #144466;} QPushButton::pressed{background-color: #c5caca;}")
        font = QtGui.QFont()
        font.setPointSize(10)
        font.setFamily("Arial")
        upButton.setFont(font)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap("Photos/Up.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        upButton.setIcon(icon)
        upButton.setIconSize(QSize(25,25))
        gridLayoutCP.addWidget(upButton,0,11,1,1)
        upButton.clicked.connect(lambda: zUp(printer))
        #ZAxis
        zAxis = QtWidgets.QLabel(widgetCP)
        zAxis.setObjectName("zAxis")
        zAxis.setMaximumSize(QtCore.QSize(50, 40))
        zAxis.setStyleSheet("background-color: #fff;")
        zAxis.setText("Z")
        font = QtGui.QFont()
        font.setPointSize(10)
        font.setFamily("Arial")
        font.setBold(True)
        zAxis.setFont(font)
        zAxis.setAlignment(QtCore.Qt.AlignCenter)
        zAxis.setStyleSheet("QLabel{border-radius: 5px; border: 1px solid;border-color: #fff;}")
        gridLayoutCP.addWidget(zAxis,0,12,1,1)
        #downButton
        downButton = QtWidgets.QPushButton(widgetCP)
        downButton.setObjectName("downButton")
        downButton.setMinimumSize(QtCore.QSize(50, 40))
        downButton.setMaximumSize(QtCore.QSize(50, 40))
        if(self.k % 2) ==0:
            downButton.setStyleSheet("QPushButton{background-color: #00838F;} QPushButton::pressed{background-color: #c5caca;}")
        else:
            downButton.setStyleSheet("QPushButton{background-color: #144466;} QPushButton::pressed{background-color: #c5caca;}")
        font = QtGui.QFont()
        font.setPointSize(10)
        font.setFamily("Arial")
        downButton.setFont(font)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap("Photos/Down.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        downButton.setIcon(icon)
        downButton.setIconSize(QSize(25,25))
        gridLayoutCP.addWidget(downButton,0,13,1,1)
        downButton.clicked.connect(lambda: zDown(printer))
        #Status
        statusCP = QtWidgets.QLabel(widgetCP)
        statusCP.setObjectName("statusCP")
        statusCP.setMaximumSize(QtCore.QSize(150, 40))
        statusCP.setText("Status: ")
        font = QtGui.QFont()
        font.setPointSize(10)
        font.setFamily("Arial")
        statusCP.setFont(font)
        statusCP.setAlignment(QtCore.Qt.AlignCenter)
        statusCP.setFrameShape(QtWidgets.QFrame.Box)
        statusCP.setFrameShadow(QtWidgets.QFrame.Plain)
        gridLayoutCP.addWidget(statusCP,1,1,1,1)
        #timeLeftCP
        timeLeftCP = QtWidgets.QLabel(widgetCP)
        timeLeftCP.setObjectName("timeLeftCP")
        timeLeftCP.setMaximumSize(QtCore.QSize(150, 40))
        font = QtGui.QFont()
        font.setPointSize(10)
        font.setFamily("Arial")
        timeLeftCP.setFont(font)
        timeLeftCP.setAlignment(QtCore.Qt.AlignCenter)
        timeLeftCP.setStyleSheet("QLabel{border-radius: 5px; border: 1px solid;border-color: #fff;}")
        gridLayoutCP.addWidget(timeLeftCP,1,2,1,3)
        #timeTempIcon
        timeTempIcon = QtWidgets.QLabel(widgetCP)
        timeTempIcon.setObjectName("timeTempIcon")
        timeTempIcon.setMinimumSize(QtCore.QSize(35, 30))
        timeTempIcon.setMaximumSize(QtCore.QSize(35, 30))
        timeTempIcon.setPixmap(QtGui.QPixmap("Photos/Time.png"))
        timeTempIcon.setScaledContents(True)
        timeTempIcon.setStyleSheet("background-color: rgba(0,0,0,0); padding-left: 5px;")
        gridLayoutCP.addWidget(timeTempIcon,1,2,1,1)
        #jobNameCP
        jobNameCP = QtWidgets.QLabel(widgetCP)
        jobNameCP.setObjectName("jobNameCP")
        jobNameCP.setMaximumSize(QtCore.QSize(1000, 40))
        jobNameCP.setText("Job Name: ")
        font = QtGui.QFont()
        font.setPointSize(10)
        font.setFamily("Arial")
        jobNameCP.setFont(font)
        jobNameCP.setAlignment(QtCore.Qt.AlignCenter)
        jobNameCP.setStyleSheet("QLabel{border-radius: 5px; border: 1px solid;border-color: #fff;}")
        gridLayoutCP.addWidget(jobNameCP,1,3,1,7)
        #progressBarCP
        progressBarCP = QtWidgets.QProgressBar(widgetCP)
        progressBarCP.setMinimumSize(QtCore.QSize(300, 40))
        progressBarCP.setMaximumSize(QtCore.QSize(1000, 40))
        progressBarCP.setStyleSheet("QProgressBar{border: solid grey; border-radius:10px 10px 10px 10px;} QProgressBar::chunk{background-color: #3fa6d6; border-radius:10px 10px 10px 10px;}")
        progressBarCP.setProperty("value", 0)
        progressBarCP.setAlignment(QtCore.Qt.AlignCenter)
        progressBarCP.setObjectName("progressBarCP")
        gridLayoutCP.addWidget(progressBarCP, 1, 10, 1, 6)
        #connectButton
        connectButton = QtWidgets.QPushButton(widgetCP)
        connectButton.setObjectName("connectButton")
        connectButton.setMinimumSize(QtCore.QSize(150, 40))
        connectButton.setMaximumSize(QtCore.QSize(150, 40))
        if(self.k % 2) ==0:
            connectButton.setStyleSheet("QPushButton{background-color: #00838F;} QPushButton::pressed{background-color: #c5caca;}")
        else:
            connectButton.setStyleSheet("QPushButton{background-color: #144466;} QPushButton::pressed{background-color: #c5caca;}")
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap("Photos/connect.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        connectButton.setIcon(icon)
        connectButton.setIconSize(QSize(25,25))
        font = QtGui.QFont()
        font.setPointSize(10)
        font.setFamily("Arial")
        connectButton.setFont(font)
        gridLayoutCP.addWidget(connectButton,2,1,1,1)
        connectButton.setText("Connect")
        connectButton.clicked.connect(lambda: connectPrinter(printer))
        #pauseButton
        pauseButton = QtWidgets.QPushButton(widgetCP)
        pauseButton.setObjectName("pauseButton")
        pauseButton.setMinimumSize(QtCore.QSize(150, 40))
        pauseButton.setMaximumSize(QtCore.QSize(150, 40))
        if(self.k % 2) ==0:
            pauseButton.setStyleSheet("QPushButton{background-color: #00838F;} QPushButton::pressed{background-color: #c5caca;}")
        else:
            pauseButton.setStyleSheet("QPushButton{background-color: #144466;} QPushButton::pressed{background-color: #c5caca;}")
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap("Photos/Pause.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        pauseButton.setIcon(icon)
        pauseButton.setIconSize(QSize(25,25))
        font = QtGui.QFont()
        font.setPointSize(10)
        font.setFamily("Arial")
        pauseButton.setFont(font)
        gridLayoutCP.addWidget(pauseButton,2,2,1,1)
        pauseButton.setText("Pause")
        pauseButton.clicked.connect(lambda: pausePrinter(printer))
        #resumeButton
        resumeButton = QtWidgets.QPushButton(widgetCP)
        resumeButton.setObjectName("resumeButton")
        resumeButton.setMinimumSize(QtCore.QSize(150, 40))
        resumeButton.setMaximumSize(QtCore.QSize(150, 40))
        if(self.k % 2) ==0:
            resumeButton.setStyleSheet("QPushButton{background-color: #00838F;} QPushButton::pressed{background-color: #c5caca;}")
        else:
            resumeButton.setStyleSheet("QPushButton{background-color: #144466;} QPushButton::pressed{background-color: #c5caca;}")
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap("Photos/Resume.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        resumeButton.setIcon(icon)
        resumeButton.setIconSize(QSize(25,25))
        font = QtGui.QFont()
        font.setPointSize(10)
        font.setFamily("Arial")
        resumeButton.setFont(font)
        gridLayoutCP.addWidget(resumeButton,2,3,1,1)
        resumeButton.setText("Resume")
        resumeButton.clicked.connect(lambda: resumePrinter(printer))
        #cancelButton
        cancelButton = QtWidgets.QPushButton(widgetCP)
        cancelButton.setObjectName("cancelButton")
        cancelButton.setMinimumSize(QtCore.QSize(150, 40))
        cancelButton.setMaximumSize(QtCore.QSize(150, 40))
        if(self.k % 2) ==0:
            cancelButton.setStyleSheet("QPushButton{background-color: #00838F;} QPushButton::pressed{background-color: #c5caca;}")
        else:
           cancelButton.setStyleSheet("QPushButton{background-color: #144466;} QPushButton::pressed{background-color: #c5caca;}")
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap("Photos/cancel.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        cancelButton.setIcon(icon)
        cancelButton.setIconSize(QSize(25,25))
        font = QtGui.QFont()
        font.setPointSize(10)
        font.setFamily("Arial")
        cancelButton.setFont(font)
        gridLayoutCP.addWidget(cancelButton,2,4,1,1)
        cancelButton.setText("Cancel")
        cancelButton.clicked.connect(lambda: cancelPrinter(printer))
        #printButton
        printButton = QtWidgets.QPushButton(widgetCP)
        printButton.setObjectName("printButton")
        printButton.setMinimumSize(QtCore.QSize(100, 40))
        printButton.setMaximumSize(QtCore.QSize(100, 40))
        if(self.k % 2) ==0:
            printButton.setStyleSheet("QPushButton{background-color: #00838F;} QPushButton::pressed{background-color: #c5caca;}")
        else:
            printButton.setStyleSheet("QPushButton{background-color: #144466;} QPushButton::pressed{background-color: #c5caca;}")
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap("Photos/Print.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        printButton.setIcon(icon)
        printButton.setIconSize(QSize(28,28))
        font = QtGui.QFont()
        font.setPointSize(10)
        font.setFamily("Arial")
        printButton.setFont(font)
        gridLayoutCP.addWidget(printButton,2,7,1,1)
        printButton.setText("Print")
        printButton.clicked.connect(lambda: printJob(printer, comboBox))
        #deleteButton
        deleteButton = QtWidgets.QPushButton(widgetCP)
        deleteButton.setObjectName("deleteButton")
        deleteButton.setMinimumSize(QtCore.QSize(40, 40))
        deleteButton.setMaximumSize(QtCore.QSize(40, 40))
        if(self.k % 2) ==0:
            deleteButton.setStyleSheet("QPushButton{background-color: #00838F;} QPushButton::pressed{background-color: #c5caca;}")
        else:
            deleteButton.setStyleSheet("QPushButton{background-color: #144466;} QPushButton::pressed{background-color: #c5caca;}")
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap("Photos/Bin.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        deleteButton.setIcon(icon)
        deleteButton.setIconSize(QSize(25,25))
        font = QtGui.QFont()
        font.setPointSize(10)
        font.setFamily("Arial")
        deleteButton.setFont(font)
        gridLayoutCP.addWidget(deleteButton,2,8,1,1)
        deleteButton.clicked.connect(lambda: deleteJob(printer, comboBox))
        #addFileButton
        addFileButton = QtWidgets.QPushButton(widgetCP)
        addFileButton.setObjectName("addFileButton")
        addFileButton.setMinimumSize(QtCore.QSize(40, 40))
        addFileButton.setMaximumSize(QtCore.QSize(40, 40))
        if(self.k % 2) ==0:
            addFileButton.setStyleSheet("QPushButton{background-color: #00838F;} QPushButton::pressed{background-color: #c5caca;}")
        else:
            addFileButton.setStyleSheet("QPushButton{background-color: #144466;} QPushButton::pressed{background-color: #c5caca;}")
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap("Photos/addFile.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        addFileButton.setIcon(icon)
        addFileButton.setIconSize(QSize(25,25))
        font = QtGui.QFont()
        font.setPointSize(10)
        font.setFamily("Arial")
        addFileButton.setFont(font)
        gridLayoutCP.addWidget(addFileButton,2,9,1,1)
        addFileButton.clicked.connect(lambda: self.openAddFileWindow(printer,comboBox))
        #comboBox
        comboBox = QtWidgets.QComboBox(widgetCP)
        comboBox.setMinimumSize(QtCore.QSize(300, 40))
        comboBox.setMaximumSize(QtCore.QSize(1000, 40))
        comboBox.setStyleSheet("QComboBox{background-color: #fff; border-radius: 5px;}"
                               "QComboBox::drop-down{background-color: #fff; border-radius: 5px; padding-right: 15px;}")
        comboBox.setObjectName("comboBox")
        font = comboBox.font()
        font.setPointSize(10)
        comboBox.setFont(font)
        gridLayoutCP.addWidget(comboBox, 2, 10, 1, 6)
        updateJobsList(printer, comboBox)
        #updateButton
        updateButton = QtWidgets.QPushButton(widgetCP)
        updateButton.setObjectName("updateButton")
        updateButton.setMinimumSize(QtCore.QSize(40, 40))
        updateButton.setMaximumSize(QtCore.QSize(40, 40))
        if(self.k % 2) ==0:
            updateButton.setStyleSheet("QPushButton{background-color: #00838F;} QPushButton::pressed{background-color: #c5caca;}")
        else:
            updateButton.setStyleSheet("QPushButton{background-color: #144466;} QPushButton::pressed{background-color: #c5caca;}")
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap("Photos/Refresh.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        updateButton.setIcon(icon)
        updateButton.setIconSize(QSize(25,25))
        font = QtGui.QFont()
        font.setPointSize(10)
        font.setFamily("Arial")
        updateButton.setFont(font)
        gridLayoutCP.addWidget(updateButton,2,15,1,1)
        updateButton.clicked.connect(lambda: updateJobsList(printer, comboBox))
       
        self.verticalLayoutCP.addWidget(widgetCP)
        self.widgetListCP.append(widgetCP)
       
        ####Print Job History####
        widgetPJH = QWidget()
        widgetPJH.setMaximumSize(200,150)
        layoutPJH = QVBoxLayout(widgetPJH)
        widgetPJH.setLayout(layoutPJH)
        widgetPJH.setStyleSheet("background-color: #F2F2F2; border-radius: 10px;")
        #TitleJPH
        title = QtWidgets.QLabel(widgetPJH)
        title.setObjectName("title")
        title.setMaximumSize(QtCore.QSize(500, 60))
        title.setText(name)
        font = QtGui.QFont()
        font.setPointSize(16)
        font.setFamily("Arial")
        title.setFont(font)
        title.setAlignment(QtCore.Qt.AlignCenter)
        layoutPJH.addWidget(title)
        #csvButton
        csvButton = QtWidgets.QPushButton(self.widget)
        csvButton.setObjectName("csvButton")
        csvButton.setMaximumSize(QtCore.QSize(500, 60))
        csvButton.setStyleSheet("QPushButton{background-color: #00838F;} QPushButton::pressed{background-color: #c5caca;}")
        font = QtGui.QFont()
        font.setPointSize(12)
        font.setFamily("Arial")
        csvButton.setFont(font)
        csvButton.setText("Import CSV")
        layoutPJH.addWidget(csvButton)
        csv_url = ip + "/plugin/PrintJobHistory/exportPrintJobHistory/CSV"
        csvButton.clicked.connect(lambda: open_webbrowser(csv_url))
        self.gridLayoutJobHistory.addWidget(widgetPJH, self.i+1, self.j)
        self.widgetListPJH.append(widgetCP)
        
        #Arrange widgets in columns of 4
        self.j +=1
        if self.j>3:
            self.j=0    
            self.i+=1
            
    #Iterate the addPrinter method for each printer in an excel table  
    def createPrinters(self):
        #read excel table
        printersdf = pd.read_excel(r'printerConfig.xlsx') 
        #create printers by running addPrinter Method for every printer in the DF
        i = 0
        for i in range (len(printersdf)):    
            name = printersdf.iloc[i,0]
            ip = printersdf.iloc[i,1]
            key = printersdf.iloc[i,2]
            postgresID = printersdf.iloc[i,3]
            self.addPrinter(name,ip,key,postgresID)
            
    #Method to set Text of the labels in the Cameras Tab        
    def onStatusListChanged(self, text):
        self.closedPrinters.setText("Disconnected: " + str(text[0]))
        self.operationalPrinters.setText("Operational: " + str(text[1]))
        self.printingPrinters.setText("Printing: " + str(text[2]))
        self.pausedPrinters.setText("Paused: " + str(text[3]))
        
    #Method to open a window to add files
    def openAddFileWindow(self, printer, combobox):
        self.newWindow = QtWidgets.QMainWindow()
        self.ui = Ui_uploadWindow(printer, combobox)
        self.ui.setupUi(self.newWindow)
        self.newWindow.show()
    
    #Method to open a window to change spools
    def openChangeSpoolWindow(self, Host, Database, User, Pass, Printerid, Printer):
        try:
            self.newWindow = QtWidgets.QMainWindow()
            self.ui = Ui_changeSpoolWindow(Host, Database, User, Pass, Printerid, Printer)
            self.ui.setupUi(self.newWindow)
            self.newWindow.show()
        except RuntimeError as ex:
            msg = QMessageBox()
            msg.setText(str(ex))
            msg.setIcon(QMessageBox.Critical)
            msg.setStandardButtons(QMessageBox.Ok)
            msg.exec() 
        except:
            msg = QMessageBox()
            msg.setText("No connection to PostgreSQL")
            msg.setIcon(QMessageBox.Critical)
            msg.setStandardButtons(QMessageBox.Ok)
            msg.exec()
    #Method to open a window to download CSV-Files
    def openCSVdownloadWindow(self, printer):
        self.newWindow = QtWidgets.QMainWindow()
        self.ui = Ui_downloadWindow()
        self.ui.setupUi(self.newWindow)
        self.newWindow.show()

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "FarmLab"))
        MainWindow.setWindowIcon(QtGui.QIcon("Photos/Logo1.png"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tabCameras), _translate("MainWindow", "CAMERAS"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tabControl), _translate("MainWindow", "CONTROL PANEL"))
        self.labelPrintJobHistory.setText(_translate("MainWindow", "PRINT JOB HISTORY"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tabJobHistory), _translate("MainWindow", "JOB HISTORY"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tabTSD), _translate("MainWindow", "TSD SERVER"))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    styleSheet= '''
            QMessageBox{
                background-color: #c5caca;
                }    
            QPushButton{
                background-color: #00838F;
                color: #fff;
                border-radius: 5px 5px 5px 5px;
                width: 100 px;
                height: 30 px;
                }
            QPushButton::pressed{
                background-color: #c5caca;
                }
            QPushButton::hover{
                background-color: #05748F;
                }
            QProgressBar{
                border: solid grey;
                border-radius: 20px;               
                }
            QProgressBar::chunk{
                background-color: #3fa6d6;
                border-radius :20px;
                }
            QComboBox {
                border-radius: 20px;
                }     
    '''
    app.setStyleSheet(styleSheet)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())


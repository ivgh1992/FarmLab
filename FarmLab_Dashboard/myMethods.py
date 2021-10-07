#Created by: Ivan Guerrero
#Last change: 10.09.2021

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import QUrl, QThread, pyqtSignal, Qt
from PyQt5 import QtWebEngineWidgets
from PyQt5.QtWidgets import QMessageBox
import psycopg2
import psycopg2.extras
import pandas as pd
import webbrowser
from octorest import OctoRest
import time
from datetime import datetime
import pyautogui
import os

def make_client(url, apikey):
        #Creates and returns an instance of the OctoRest client.
        try:
            client = OctoRest(url=url, apikey=apikey)
            return client
        except:
            msg = QMessageBox()
            msg.setText("Couldn`t connect to printer: ")
            msg.setIcon(QMessageBox.Critical)
            msg.setStandardButtons(QMessageBox.Ok)
            msg.setInformativeText(url)
            msg.exec()
            return("offline")
            
#Method to retrieve the progress of a printer
def get_printProgress(printer):
    try:
        printProgress = printer.job_info()["progress"]["completion"]        
        return int(printProgress)
    except TypeError:
        return(0)
    except:
        return(0)

#Method to retrieve job Name
def get_jobName(printer):
    try:    
        jobName = printer.job_info()["job"]["file"]["name"]        
        return jobName
    except TypeError:
        return("-")
    except:
        return("No connection")

#Method to retrieve Print Time
def get_status(printer):
    try:
        status = printer.connection_info()["current"]["state"]
        return status
    except TypeError:
        return("-")
    except:
        return("No connection")
#Method to retrieve the number of printers closed,operational, printing and paused
def get_statusList(printersList):
    disconnectedPrinters = []
    operationalPrinters = []
    printingPrinters = []
    pausedPrinters = []
    #Retrieve the status of each client and append it to the corresponding list
    for i in range(len(printersList)):
        status = get_status(printersList[i])
        if status == "Closed":
            disconnectedPrinters.append(status)
        if status == "Operational":
            operationalPrinters.append(status)
        if status == "Paused":
            pausedPrinters.append(status)
        if status == "Printing":
            printingPrinters.append(status)
        
    #status list
    statusList = []
    statusList.append(len(disconnectedPrinters))
    statusList.append(len(operationalPrinters))
    statusList.append(len(printingPrinters))
    statusList.append(len(pausedPrinters))
    return(statusList)

#Method to retrieve time left
def get_timeLeft(printer):
    try:
        timeLeft = printer.job_info()["progress"]["printTimeLeft"]
        minutesLeft = timeLeft/60
        hoursLeft , minutesLeft =divmod(minutesLeft, 60)
        timeLeft = str("%02dh %02dm"%(hoursLeft,minutesLeft))
        return timeLeft
    except TypeError:
        return("-")
    except:
        return("")
    
#Method to retrieve a list of job files
def get_jobsList(printer):
    try:    
        jobsList = []
        files = printer.files(location = "local")["files"]
        files.sort(key = lambda x : x['date'], reverse=True)
        for file in files:    
            d = file["path"]
            jobsList.append(d)
        return jobsList
    except:
        return("No connection")
    
#Method to retrieve bed temperatures - actual/target
def get_bedTemp(printer):
    try:    
        bedTemp = printer.bed()
        bedTempActual = bedTemp["bed"]["actual"]
        bedTempTarget = bedTemp["bed"]["target"]
        return(str(int(bedTempActual))+"°C / "+str(int(bedTempTarget))+"°C")
    except:
        return(" 0°C / 0°C")

#Method to retrieve tool temperatures - actual/target
def get_toolTemp(printer):
    try:    
        toolTemp = printer.tool()
        toolTempActual = toolTemp["tool0"]["actual"]
        toolTempTarget = toolTemp["tool0"]["target"]
        return(str(int(toolTempActual))+"°C / "+str(int(toolTempTarget))+"°C")
    except:
        return(" 0°C / 0°C")
#Method to retrieve the spool in use
def get_spoolsList(myHost,myDatabase,myUser,myPass,myPrinterid):
    try:
        spoolsList = []
        #create a connection with the data base
        conn = psycopg2.connect(dbname = myDatabase, user = myUser, password = myPass, host = myHost)
        #get spools file
        cursor = conn.cursor()
        cursor.execute("SELECT id,name FROM spools ORDER BY id ASC;")
        spools = cursor.fetchall()
        cursor.close()
        conn.close()
        #convert spools dictionary to dataFrame
        spools=pd.DataFrame.from_dict(spools)
        spools.sort_values(0,ascending=True, inplace=True)
        spools.reset_index(drop=True, inplace=True)
        spools.rename(columns={0:"id", 1:"name"}, inplace=True)
        spoolsList=spools.name.tolist()
        return(spoolsList)
    except:
        return("No connection to PostgreSQL server")

#Method to retrieve the spool in use
def get_spoolInUse(myHost,myDatabase,myUser,myPass,myPrinterid):
    spoolsInUseList = []
    try:
        #sql code to extract elements of interest
        sql_spools ="SELECT selections.tool, selections.client_id, spools.name, profiles.material,spools.weight,spools.used FROM profiles JOIN spools ON profile_id=profiles.id JOIN selections ON spool_id=spools.id WHERE client_id= '%s';"
        #create a connection with the data base
        conn = psycopg2.connect(dbname = myDatabase, user = myUser, password = myPass, host = myHost)
        #get spools file
        cursor = conn.cursor()
        cursor.execute(sql_spools%(myPrinterid))
        spools = cursor.fetchall()
        cursor.close()
        conn.close()
        #convert spools dictionary to dataFrame
        spools=pd.DataFrame.from_dict(spools)
        spools.sort_values(0,ascending=True, inplace=True)
        spools.reset_index(drop=True, inplace=True)
        spools.rename(columns={0:"tool", 1:"client_id", 2:"name", 3:"material", 4:"weight",5:"used"}, inplace=True)
        #extract the data from each column of the DF for a given printerID
        for i in range (0, len(spools)):
            tool = spools.loc[spools.client_id == myPrinterid,"tool"].values[i]
            spoolName = spools.loc[spools.client_id == myPrinterid,"name"].values[i]
            material = spools.loc[spools.client_id == myPrinterid,"material"].values[i]
            weight = spools.loc[spools.client_id == myPrinterid,"weight"].values[i]
            used = spools.loc[spools.client_id == myPrinterid,"used"].values[i]
            remainingMaterial = weight - used
            spoolInUse = "tool"+str(tool)+" - "+spoolName+" - "+material+" - "+str(int(remainingMaterial))+" [g]"
            spoolsInUseList.append(spoolInUse)
        return(spoolsInUseList)
    except KeyError:
        spoolsInUseList.append("No spools selected")
        return(spoolsInUseList)
    except:
        spoolsInUseList.append("No connection to PostgreSQL server")
        return(spoolsInUseList)
 
#Methods for the push buttons
def cancelPrinter(printer):
        msg = QMessageBox()
        try:
            msg.setText("Are you sure you want to cancel the print Job?")
            msg.setIcon(QMessageBox.Information)
            msg.setStandardButtons(QMessageBox.Yes|QMessageBox.No)
            msg.setDefaultButton(QMessageBox.No)
            returnValue = msg.exec()
            if returnValue == QMessageBox.Yes:
                printer.cancel()  
        except RuntimeError as ex:
            msg = QMessageBox()
            msg.setText("Something went wrong!")
            msg.setIcon(QMessageBox.Warning)
            msg.setDetailedText(str(ex))
            msg.setStandardButtons(QMessageBox.Ok)
            msg.setInformativeText("Click 'Show Details' for more")
            msg.exec()
        except:
            msg = QMessageBox()
            msg.setText("No connection detected")
            msg.setIcon(QMessageBox.Critical)
            msg.setStandardButtons(QMessageBox.Ok)
            msg.exec()

def pausePrinter(printer):
        try:
            printer.pause()
        except RuntimeError as ex:
            msg = QMessageBox()
            msg.setText("Something went wrong!")
            msg.setIcon(QMessageBox.Warning)
            msg.setDetailedText(str(ex))
            msg.setStandardButtons(QMessageBox.Ok)
            msg.setInformativeText("Click 'Show Details' for more")
            msg.exec()
        except:
            msg = QMessageBox()
            msg.setText("No connection detected")
            msg.setIcon(QMessageBox.Critical)
            msg.setStandardButtons(QMessageBox.Ok)
            msg.exec()

def resumePrinter(printer):
    try:
        printer.resume()
    except RuntimeError as ex:
        msg = QMessageBox()
        msg.setText("Something went wrong!")
        msg.setIcon(QMessageBox.Warning)
        msg.setDetailedText(str(ex))
        msg.setStandardButtons(QMessageBox.Ok)
        msg.setInformativeText("Click 'Show Details' for more")
        msg.exec()
    except:
        msg = QMessageBox()
        msg.setText("No connection detected")
        msg.setIcon(QMessageBox.Critical)
        msg.setStandardButtons(QMessageBox.Ok)
        msg.exec()
        
def connectPrinter(printer):
        try:
            printer.connect()
        except RuntimeError as ex:
            msg = QMessageBox()
            msg.setText("Couldn't connect to Octoprint")
            msg.setIcon(QMessageBox.Critical)
            msg.setDetailedText(str(ex))
            msg.setStandardButtons(QMessageBox.Ok)
            msg.setInformativeText("Click 'Show Details' for more")
            msg.exec()
        except:
            msg = QMessageBox()
            msg.setText("No connection detected")
            msg.setIcon(QMessageBox.Critical)
            msg.exec()
            
def zUp(printer):
        try:
            status = printer.connection_info()["current"]["state"]
            if status == "Operational":
                printer.jog(z=50)
            if status == "Printing":
                msg = QMessageBox()
                msg.setText("Unable to move the Tool. Printer is printing")
                msg.setIcon(QMessageBox.Critical)
                msg.exec()
            if status == "Paused":
                msg = QMessageBox()
                msg.setText("Unable to move the Tool. Printer is printing")
                msg.setIcon(QMessageBox.Critical)
                msg.exec()
            if status == "Closed":
                msg = QMessageBox()
                msg.setText("Unable to move the Tool. Check the connection.")
                msg.setIcon(QMessageBox.Critical)
                msg.exec()
        except:
            msg = QMessageBox()
            msg.setText("No connection detected")
            msg.setIcon(QMessageBox.Critical)
            msg.exec()

def zDown(printer):
        try:
            status = printer.connection_info()["current"]["state"]
            if status == "Operational":
                printer.jog(z=-50)
            if status == "Printing":
                msg = QMessageBox()
                msg.setText("Unable to move the Tool. Printer is printing")
                msg.setIcon(QMessageBox.Critical)
                msg.exec()
            if status == "Paused":
                msg = QMessageBox()
                msg.setText("Unable to move the Tool. Printer is printing")
                msg.setIcon(QMessageBox.Critical)
                msg.exec()
            if status == "Closed":
                msg = QMessageBox()
                msg.setText("Unable to move the Tool. Check the connection.")
                msg.setIcon(QMessageBox.Critical)
                msg.exec()
        except:
            msg = QMessageBox()
            msg.setText("No connection detected")
            msg.setIcon(QMessageBox.Critical)
            msg.exec()

            
def updateJobsList(printer, comboBox):
        try:
            jobsList = get_jobsList(printer)
            comboBox.clear()
            for job in jobsList:    
                comboBox.addItem(job)
        except:
            msg = QMessageBox()
            msg.setText("No connection detected")
            msg.setIcon(QMessageBox.Critical)
            msg.exec()
    
def printJob(printer, comboBox):
        msg = QMessageBox()
        try:
            msg.setText("Are you using the right spool?")
            msg.setIcon(QMessageBox.Information)
            msg.setStandardButtons(QMessageBox.No|QMessageBox.Yes)
            msg.setDefaultButton(QMessageBox.No)
            returnValue = msg.exec()
            if returnValue == QMessageBox.Yes:
                job = str(comboBox.currentText())
                printer.select(job)
                printer.start()                           
        except RuntimeError as ex:
            msg.setText("Something went wrong")
            msg.setIcon(QMessageBox.Warning)
            msg.setDetailedText(str(ex))
            msg.setStandardButtons(QMessageBox.Ok)
            msg.setInformativeText("Click 'Show Details' for more")
            returnValue = msg.exec()
        except:
            msg = QMessageBox()
            msg.setText("No connection detected")
            msg.setIcon(QMessageBox.Critical)
            msg.setStandardButtons(QMessageBox.Ok)
            msg.exec()
            
def deleteJob(printer, comboBox):
        msg = QMessageBox()
        try:
            msg.setText("Are you sure want to remove the selected file?")
            msg.setIcon(QMessageBox.Information)
            msg.setStandardButtons(QMessageBox.Yes|QMessageBox.No)
            msg.setDefaultButton(QMessageBox.No)
            returnValue = msg.exec()
            if returnValue == QMessageBox.Yes:
                job = str(comboBox.currentText())
                printer.delete(job)
                updateJobsList(printer, comboBox)
                msg.setText("File succesfully deleted")
                msg.setIcon(QMessageBox.Information)
                msg.setStandardButtons(QMessageBox.Ok)
                returnValue = msg.exec()
        except RuntimeError as ex:
            msg.setText("You didn't select a job or the job you selected doesn't exist")
            msg.setIcon(QMessageBox.Warning)
            msg.setDetailedText(str(ex))
            msg.setStandardButtons(QMessageBox.Ok)
            msg.setInformativeText("Click 'Show Details' for more")
            msg.exec()
        except:
            msg = QMessageBox()
            msg.setText("No connection detected")
            msg.setStandardButtons(QMessageBox.Ok)
            msg.setIcon(QMessageBox.Critical)
            msg.exec()
                      
def open_webbrowser(url):
        webbrowser.open(url)
     
def importCSV(printerPathList):
        #Make a directory in the desktop if it doesn't exist
        pathDesktopDir = os.path.join("C:\\","Users","Ivan","Desktop","Octoprint_Job_History")
        if not os.path.exists(pathDesktopDir):
            os.mkdir(pathDesktopDir)
        #get date and time at the moment    
        now = datetime.now() 
        dateTime = now.strftime("%Y%m%d_%H%M%S")	
        #make a new directory with the date and time 
        path = os.path.join("C:\\","Users","Ivan","Desktop","Octoprint_Job_History", "Job_History_"+dateTime)
        os.mkdir(path)
        linkPath = "plugin/PrintJobHistory/exportPrintJobHistory/CSV"
        #import Bravo
        i=1
        for printer in printerPathList:
            pathPrinter = printer + linkPath
            webbrowser.open(pathPrinter)
            time.sleep(4) # Wait for the Save As dialog to load.
            fileName = "JobHistory_" + str(i) + "_"+ dateTime 
            FILE_NAME = path+"\\"+ fileName + ".csv" 
            pyautogui.typewrite(FILE_NAME)
            pyautogui.hotkey('enter')
            i = i+1
        #open a pop up with finished message
        msg = QMessageBox()
        msg.setText("Import finished")
        msg.setIcon(QMessageBox.Information)
        msg.setStandardButtons(QMessageBox.Ok)
        msg.setInformativeText("The files where saved in a folder in your desktop")
        msg.exec()
        
def importCSV2(printerPathList, directoryPath):
        if directoryPath != "": 
            try:
                msg = QMessageBox()
                msg.setText("Please don't touch any key or click anything during the download. The programm will do everything for you.")
                msg.setIcon(QMessageBox.Information)
                msg.setStandardButtons(QMessageBox.Ok)
                msg.setInformativeText("Click 'OK' to start download")
                msg.exec()
                #Make a directory in the desktop if it doesn't exist
                directory = directoryPath.replace("/", "\\")
                directoryPathJH = os.path.join(directory, "Octoprint_Job_History")
                if not os.path.exists(directoryPathJH):
                    os.mkdir(directoryPathJH)
                #get date and time at the moment    
                now = datetime.now() 
                dateTime = now.strftime("%Y%m%d_%H%M%S")	
                #make a new directory with the date and time 
                path = os.path.join(directoryPathJH, "Job_History_"+dateTime)
                os.mkdir(path)
                linkPath = "/plugin/PrintJobHistory/exportPrintJobHistory/CSV"
                #import Bravo
                i=1
                for printer in printerPathList:
                    pathPrinter = printer + linkPath
                    webbrowser.open(pathPrinter)
                    time.sleep(2) # Wait for the Save As dialog to load.
                    fileName = "JobHistory_" + str(i) + "_"+ dateTime 
                    FILE_NAME = path+"\\"+ fileName + ".csv" 
                    pyautogui.typewrite(FILE_NAME)
                    pyautogui.hotkey('enter')
                    i = i+1
                #open a pop up with finished message
                msg = QMessageBox()
                msg.setText("Import finished")
                msg.setIcon(QMessageBox.Information)
                msg.setStandardButtons(QMessageBox.Ok)
                msg.setInformativeText("The files where saved in the folder you selected")
                msg.exec()
            except FileNotFoundError as ex:
                #open a pop up with error message
                msg = QMessageBox()
                msg.setText("Something went wrong")
                msg.setIcon(QMessageBox.Warning)
                msg.setDetailedText(str(ex))
                msg.setStandardButtons(QMessageBox.Ok)
                msg.setInformativeText("Click 'Show Details' for more")
                msg.exec()
        
        elif directoryPath == "":
            msg = QMessageBox()
            msg.setText("No folder was selected")
            msg.setIcon(QMessageBox.Warning)
            msg.setInformativeText("Use the browse button to search for a directory")
            msg.exec()


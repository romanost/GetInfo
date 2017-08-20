'''
Created on Mar 23, 2016

@author: user

http://stackoverflow.com/questions/6783194/background-thread-with-qthread-in-pyqt
https://nikolak.com/pyqt-threading-tutorial/


'''


import sys
import os
#from PyQt4 import QtCore, QtGui, QtNetwork4

from PyQt4 import QtCore, QtGui, QtNetwork

from PyQt4.QtCore import QThread, SIGNAL
import datetime
from socket import *

from mainform import Ui_MainWindow
from prefs import Ui_Dialog
from about import Ui_aboutDialog
import subprocess
from PyQt4.Qt import QTime

from PyQt4.QtGui import *
import config
from whois import NICClient
import cmd
#from signal import signal
import signal

class pingthread(QThread):
    def __init__(self,parent=None):
        QThread.__init__(self,parent)
        self.addr=str(parent.ui.pingIn.text())
        self.shrink=parent.ui.shrinkPing.isChecked()

    def __del__(self):
        self.wait()
    
    def run(self):
        self.stinfo=subprocess.STARTUPINFO()
        self.stinfo.dwFlags|=subprocess.STARTF_USESHOWWINDOW
        self.pr = subprocess.Popen(['ping', '-t',self.addr], startupinfo=self.stinfo, stdout=subprocess.PIPE,stderr=subprocess.STDOUT, shell=False)
                
        self.runs=True
        prevs=""
        prevc=0
        while self.runs:
            inchar = self.pr.stdout.readline()
            if inchar: #neither empty string nor None
                s=str(inchar.decode('utf-8')).rstrip()
                ctime=datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                if not self.shrink:
                    self.emit(SIGNAL('sping(QString)'),s)
                else:
                    if (("Reply from" in s) and ("Reply from" in prevs)) or (s in prevs):
                        prevc+=1   
                        #print(prevc,prevs)                                                                                         
                    else:
                        if prevc>0:
                            self.emit(SIGNAL('sping(QString)'),"Previous line repeats "+str(prevc)+" times")
                        #print("Repeated:",prevs)
                        prevc=0
                        self.emit(SIGNAL('sping(QString)'),ctime+":"+s)
                    prevs=s
        self.pr.kill()
        if self.shrink:
            self.emit(SIGNAL('sping(QString)'),"Previous line repeats "+str(prevc)+" times")
            self.emit(SIGNAL('sping(QString)'),ctime+":"+s)
        return 
    
    def stop(self):
        #print "stop ping "+str(self.pr.pid)
        #self.pr.communicate("^c")
        #os.kill(self.pr.pid,signal.CTRL_C_EVENT)
        #self.pr.send_signal(signal.CTRL_C_EVENT)
        #self.pr.kill()
        self.pr.terminate()
        self.runs=False

class whoisthread(QThread):
    def __init__(self,parent=None):
        QThread.__init__(self,parent)
        self.addr=str(parent.ui.whoisIn.text())

    def __del__(self):
        self.wait()
    
    def run(self):
        nic_client = NICClient()
        output=nic_client.whois_lookup(None,self.addr, 0)
        self.emit(SIGNAL('swhois(QString)'),output)

class dnsthread(QThread):
    def __init__(self,parent=None):
        QThread.__init__(self,parent)
        self.addr=str(parent.ui.dnsIn.text())
        self.dnsArr=[]
        self.dnsCmd=["nslookup"]
        self.srv=str(parent.ui.dnsSrv.text()) if parent.ui.dnsSrv.text() else ""
        if parent.ui.dnsRec.model().item(10).checkState()==QtCore.Qt.Checked:
            self.dnsCmd.append("-d2")
        if parent.ui.dnsRec.model().item(1).checkState()==QtCore.Qt.Checked:
            self.dnsCmd.append("-q=all")            
            self.dnsCmd.append(self.addr)            
            if self.srv:
                self.dnsCmd.append(self.srv)            
            self.dnsArr.append(self.dnsCmd)
        else:
            tdns=self.dnsCmd
            for i in range(2,10):
                if parent.ui.dnsRec.model().item(i).checkState()==QtCore.Qt.Checked:
                    tdns=[]
                    tdns=self.dnsCmd[:]
                    tdns.append("-q="+str(parent.ui.dnsRec.model().item(i).text()))
                    tdns.append(self.addr)
                    if self.srv:
                        tdns.append(self.srv)
                    self.dnsArr.append(tdns)

    def __del__(self):
        self.wait()
    
    def run(self):
        for cmd in self.dnsArr:
            s=""
            self.dnspr = subprocess.Popen(cmd, stdout=subprocess.PIPE,stderr=subprocess.STDOUT, shell=True)
            self.emit(SIGNAL('sdns(QString)'),"Running: "+" ".join(cmd))
            self.emit(SIGNAL('sdns(QString)'),"-------------------------------------------------------------")
            inlines,err=self.dnspr.communicate()
            s=str(inlines.decode('utf-8'))
            self.emit(SIGNAL('sdns(QString)'),s)

class portthread(QThread):
    def __init__(self,parent=None):
        QThread.__init__(self,parent)
        self.addr=str(parent.ui.portIn.text())
        self.port=int(parent.ui.portBox.text())

    def __del__(self):
        self.wait()
    
        
    def run(self):
        #try:
        s=socket(AF_INET,SOCK_STREAM)
        s.settimeout(3)
        try:
            s.connect(("google.com",self.port))
            res="Port open"
        except:
            res="Time out"
        #print(res)
        #except Exception:
        #    print ("Error")
        #    pass
        self.emit(SIGNAL('sport(QString)'),res)

class tracethread(QThread):
    def __init__(self,parent=None):
        QThread.__init__(self,parent)
        self.addr=str(parent.ui.traceIn.text())
        self.traceCmd=["tracert"]
        if parent.ui.resolveTrace.checkState()!=QtCore.Qt.Checked:
            self.traceCmd.append("-d")
        self.traceCmd.append(self.addr)

    def __del__(self):
        self.wait()
    
    def run(self):
#         self.pr = subprocess.Popen(['tracert', self.addr], stdout=subprocess.PIPE,stderr=subprocess.STDOUT, shell=True)
#         self.runs=True
        self.stinfo=subprocess.STARTUPINFO()
        self.stinfo.dwFlags|=subprocess.STARTF_USESHOWWINDOW
        self.tracepr = subprocess.Popen(self.traceCmd, startupinfo=self.stinfo,stdout=subprocess.PIPE,stderr=subprocess.STDOUT, shell=False)
        #inlines,err=self.tracepr.communicate()
        #s=str(inlines.decode('utf-8'))
        #self.emit(SIGNAL('strace(QString)'),s)
        self.traceruns=True
        
        while self.traceruns:
            if self.tracepr.poll()==0:
                self.traceruns=False
                self.emit(SIGNAL('finished()'))                
            inchar = self.tracepr.stdout.readline()
            if inchar: #neither empty string nor None
                s=str(inchar.decode('utf-8')).rstrip()
                self.emit(SIGNAL('strace(QString)'),s)
        #self.pr.kill()
        
#         output=nic_client.whois_lookup(None,self.addr, 0)
#         self.emit(SIGNAL('swhois(QString)'),output)
        self.tracepr.kill()
        #print "done"

    def stop(self):
        #print "stop ping"
        #os.kill(self.pr.pid,signal.CTRL_C_EVENT)
        #self.pr.kill()
        self.tracepr.terminate()
        self.traceruns=False

    
class StartQT4(QtGui.QMainWindow):
    # Pings
    runs=False
    
    #Whois
    whoisruns=False
    whoisoutput=""
    
    #dns
    dnsruns=False
    
    #port check
    portruns=False
    
    #ptr
    ptrruns=False
    
    #trace
    traceruns=False
    
    #all
    allruns=False
    
    def closeEvent(self, *args, **kwargs):
        if self.runs:
            self.mythread.stop()
        if self.traceruns:
            self.tracet.stop()
        return QtGui.QMainWindow.closeEvent(self, *args, **kwargs)
    
    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self, parent)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
         
        self.ui.pingButton.clicked.connect(self.doping)
        self.ui.pingIn.returnPressed.connect(self.doping)
        self.ui.whoisButton.clicked.connect(self.dowhois)
        self.ui.whoisIn.returnPressed.connect(self.dowhois)
        self.ui.dnsButton.clicked.connect(self.dodns)
        self.ui.dnsIn.returnPressed.connect(self.dodns)
        self.ui.dnsSrv.returnPressed.connect(self.dodns)
        self.ui.portButton.clicked.connect(self.doport)
        self.ui.portIn.returnPressed.connect(self.doport)
        self.ui.portBox.returnPressed.connect(self.doport)
        self.ui.traceButton.clicked.connect(self.dotrace)
        self.ui.traceIn.returnPressed.connect(self.dotrace)
        self.ui.allButton.clicked.connect(self.doall)
        self.ui.allIn.returnPressed.connect(self.doall)
        
        self.ui.action_Prefrences.triggered.connect(self.openPrefs)
        self.ui.action_About.triggered.connect(self.openAbout)
        self.ui.action_Exit.triggered.connect(self.openExit)
        
        self.ui.pingOut.customContextMenuRequested.connect(self.openConMenu)
        self.ui.whoisOut.customContextMenuRequested.connect(self.openConMenu)
        self.ui.dnsOut.customContextMenuRequested.connect(self.openConMenu)
        self.ui.portOut.customContextMenuRequested.connect(self.openConMenu)
        self.ui.allOut.customContextMenuRequested.connect(self.openConMenu)
        self.ui.dnsRec.view().pressed.connect(self.dnsHandleRec)
        
        dnsArr=["ALL","A","AAAA","CNAME","MX","PTR","NS","TXT","SOA","DEBUG"]
        model = QtGui.QStandardItemModel(len(dnsArr), 1)        
        
        it=QtGui.QStandardItem("Select")
        it.setBackground(QtGui.QBrush(QtGui.QColor(200, 200, 200)))
        it.setSelectable(False)
        model.setItem(0, 0, it)

        for i,dtxt in enumerate(dnsArr):          
            it=QtGui.QStandardItem(dtxt)
            it.setFlags(QtCore.Qt.ItemIsUserCheckable|QtCore.Qt.ItemIsEnabled)
            it.setData(QtCore.Qt.Checked,QtCore.Qt.CheckStateRole)
            model.setItem(i+1,0,it)
        self.ui.dnsRec.setModel(model)

    def dnsHandleRec(self,index):
        if index.row()==0:
            return
        item = self.ui.dnsRec.model().itemFromIndex(index)
        if item.checkState() == QtCore.Qt.Checked:
            item.setCheckState(QtCore.Qt.Unchecked)
        else:
            item.setCheckState(QtCore.Qt.Checked)

    def openConMenu(self,position):
        self.seltext=self.sender().textCursor()
        
        conMenu=QMenu()
        conMenu=self.sender().createStandardContextMenu()
        conMenu.addSeparator()
        act1=QAction("&1 - Ping",self)
        act1.triggered.connect(self.cmPing)
        conMenu.addAction(act1)
        act2=QAction("&2 - whoIs",self)
        act2.triggered.connect(self.cmWhoIs)
        conMenu.addAction(act2)
        act3=QAction("&3 - DNS",self)
        act3.triggered.connect(self.cmDns)
        conMenu.addAction(act3)
        act4=QAction("&4 - Port check",self)
        act4.triggered.connect(self.cmPort)
        conMenu.addAction(act4)
        act4=QAction("&5 - Trace",self)
        act4.triggered.connect(self.cmTrace)
        conMenu.addAction(act4)
        act5=QAction("&6 - All",self)
        act5.triggered.connect(self.cmAll)
        conMenu.addAction(act5)
        #QtGui.QMessageBox.information(str)   
        conMenu.exec_(self.sender().viewport().mapToGlobal(position))     
        return
    
    def cmPing(self):
        self.ui.tabWidget.setCurrentIndex(0)
        self.ui.pingIn.setText(self.seltext.selectedText())
        self.doping()
    def cmWhoIs(self):
        self.ui.tabWidget.setCurrentIndex(1)
        self.ui.whoisIn.setText(self.seltext.selectedText())
        self.dowhois()
    def cmDns(self):
        self.ui.tabWidget.setCurrentIndex(2)
        #self.ui.dnsRec.setCurrentIndex(0)
        self.ui.dnsIn.setText(self.seltext.selectedText())
        self.dodns()
    def cmPort(self):
        self.ui.tabWidget.setCurrentIndex(3)
        self.ui.portIn.setText(self.seltext.selectedText())
        self.doport()
    def cmTrace(self):
        self.ui.tabWidget.setCurrentIndex(4)
        self.ui.traceIn.setText(self.seltext.selectedText())
        self.dotrace()
    def cmAll(self):
        self.ui.tabWidget.setCurrentIndex(5)
        self.ui.allIn.setText(self.seltext.selectedText())
        self.doall()
    
    def openPrefs(self):
        dialog=QDialog()
        dialog.ui=Ui_Dialog()
        dialog.ui.setupUi(dialog)
        res=dialog.exec_()
        self.ui.allOut.append(str(res))
        z=str(dialog.ui.lineEdit.text())
        self.ui.allOut.append(z)
        
    def openAbout(self):
        dialog=QDialog()
        dialog.ui=Ui_aboutDialog()
        dialog.ui.setupUi(dialog)
        dialog.exec_()
    
    def openExit(self):
        #print "open"
        if self.runs:
            self.mythread.stop()
        if self.traceruns:
            self.tracet.stop()
        sys.exit()
        
    def doping(self):
        #addr=str(self.ui.pingIn.text())
        if (self.runs):
            self.runs=False
            self.ui.pingButton.setText("Ping")
            self.mythread.stop()
            #self.ui.pingOut.append("end")
            #self.ui.pingOut.append(str(self.mythread.isRunning()))
        else:
            addr=str(self.ui.pingIn.text())
            self.ui.pingOut.setPlainText("Pinging: "+addr)
            self.ui.pingButton.setText("Stop")
            self.mythread=pingthread(self)
            self.connect(self.mythread, SIGNAL("sping(QString)"),self.sping)
            self.connect(self.mythread, SIGNAL("finished()"), self.doneping)
            #self.ui.pingOut.append(str(self.mythread.isRunning()))
            self.mythread.start()
            self.runs=True
        
    def sping(self,stxt):
        self.ui.pingOut.append(stxt)
        if (config.autoscroll):
            self.ui.pingOut.moveCursor(QtGui.QTextCursor.End)
        
    def doneping(self):
        self.ui.pingOut.append("Done.")
        self.checkall()
    
    def dowhois(self):
        if (self.whoisruns):
            QtGui.QMessageBox.information(self, "Message", "Please wait previous whois request to finish")
            return
        self.whoisruns=True
        self.whoist=whoisthread(self)
        url=str(self.ui.whoisIn.text())
        self.ui.whoisOut.setPlainText("Whois: "+url)
        self.connect(self.whoist, SIGNAL("swhois(QString)"),self.swhois)
        self.connect(self.whoist, SIGNAL("finished()"), self.donewhois)
        self.whoist.start()
        
    def swhois(self,stxt):
        self.ui.whoisOut.append(stxt)

    def donewhois(self):
        self.whoisruns=False
        self.ui.whoisOut.append("Done.")
        self.checkall()
        
    def dodns(self):
        if (self.dnsruns):
            QtGui.QMessageBox.information(self, "Message", "Please wait previous DNS request to finish")
            return
        self.dnsruns=True
        self.dnst=dnsthread(self)        
        addr=str(self.ui.dnsIn.text())
        self.ui.dnsOut.setPlainText("DNS query for: "+addr)
        self.connect(self.dnst, SIGNAL("sdns(QString)"),self.sdns)
        self.connect(self.dnst, SIGNAL("finished()"), self.donedns)
        self.dnst.start()
#         self.dnspr = subprocess.Popen(['nslookup', '-q=all',addr,'8.8.8.8'], stdout=subprocess.PIPE,stderr=subprocess.STDOUT, shell=True)

    def sdns(self,stxt):
        self.ui.dnsOut.append(stxt)
    def donedns(self):
        self.dnsruns=False
        self.ui.dnsOut.append("Done.")
        self.checkall()
        
    def doport(self):
        if (self.portruns):
            QtGui.QMessageBox.information(self, "Message", "Please wait previous port check request to finish")
            return
        if not self.ui.portBox.text():
            QtGui.QMessageBox.information(self, "Message", "Invalid port")
            return
        addr=str(self.ui.portIn.text())
        port=str(self.ui.portBox.text())
        self.portruns=True
        self.portt=portthread(self)
        self.ui.portOut.setPlainText("Checking port "+port+" on: "+addr)
        self.connect(self.portt, SIGNAL("sport(QString)"),self.sport)
        self.connect(self.portt, SIGNAL("finished()"), self.doneport)
        self.portt.start()
        
    def sport(self,stxt):
        self.ui.portOut.append(stxt)
    def doneport(self):
        self.portruns=False
        self.ui.portOut.append("Done.")
        self.checkall()

    def dotrace(self):
        if (self.traceruns):
            self.traceruns=True
            self.ui.traceButton.setText("Trace")
            self.tracet.stop()
            #QtGui.QMessageBox.information(self, "Message", "Please wait previous trace request to finish")
            return
        else:
            addr=str(self.ui.traceIn.text())
            self.traceruns=True
            self.tracet=tracethread(self)
            self.ui.traceOut.setPlainText("Tracing "+addr)
            self.ui.traceButton.setText("Stop")
            self.connect(self.tracet, SIGNAL("strace(QString)"),self.strace)
            self.connect(self.tracet, SIGNAL("finished()"), self.donetrace)
            self.tracet.start()

    def strace(self,stxt):
        self.ui.traceOut.append(stxt)
    def donetrace(self):
        self.traceruns=False
        self.ui.traceOut.append("Done.")
        self.ui.traceButton.setText("Trace")
        self.checkall()
        
    def doall(self):
        if (self.allruns):
            QtGui.QMessageBox.information(self, "Message", "Please wait previous requests to finish")
            return
        if (self.runs):
            QtGui.QMessageBox.information(self, "Message", "Please stop ping")
            return
        if (self.whoisruns):
            QtGui.QMessageBox.information(self, "Message", "Please wait previous whois request to finish")
            return
        if (self.dnsruns):
            QtGui.QMessageBox.information(self, "Message", "Please wait previous DNS request to finish")
            return
        addr=str(self.ui.allIn.text())
        self.ui.allOut.setPlainText("Getting info for:"+addr)
        self.ui.pingIn.setText(addr)
        self.ui.whoisIn.setText(addr)
        self.ui.dnsRec.setCurrentIndex(0)
        self.ui.dnsIn.setText(addr)
        self.doping()
        self.dowhois()
        self.dodns()
        self.allruns=True

    def checkall(self):
        if not self.allruns:
            return
        if self.whoisruns or self.dnsruns:
            return
        if self.runs:
            self.doping()
        
        self.ui.allOut.append("--------------------------WhoIs------------------------------")
        self.ui.allOut.append(self.ui.whoisOut.toPlainText())
        self.ui.allOut.append("---------------------------DNS-------------------------------")
        self.ui.allOut.append(self.ui.dnsOut.toPlainText())
        self.ui.allOut.append("---------------------------Ping------------------------------")
        self.ui.allOut.append(self.ui.pingOut.toPlainText())
        self.allruns=False
        
        
    

if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    myapp = StartQT4()
    myapp.show()
    sys.exit(app.exec_())

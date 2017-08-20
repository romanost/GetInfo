# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'about.ui'
#
# Created by: PyQt4 UI code generator 4.11.4
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

try:
    _encoding = QtGui.QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)

class Ui_aboutDialog(object):
    def setupUi(self, aboutDialog):
        aboutDialog.setObjectName(_fromUtf8("aboutDialog"))
        aboutDialog.resize(400, 300)
        self.aboutTitle = QtGui.QLabel(aboutDialog)
        self.aboutTitle.setGeometry(QtCore.QRect(10, 20, 151, 51))
        font = QtGui.QFont()
        font.setFamily(_fromUtf8("Gabriola"))
        font.setPointSize(42)
        font.setItalic(True)
        self.aboutTitle.setFont(font)
        self.aboutTitle.setObjectName(_fromUtf8("aboutTitle"))
        self.label = QtGui.QLabel(aboutDialog)
        self.label.setGeometry(QtCore.QRect(30, 90, 111, 16))
        self.label.setObjectName(_fromUtf8("label"))
        self.label_2 = QtGui.QLabel(aboutDialog)
        self.label_2.setGeometry(QtCore.QRect(30, 110, 111, 16))
        self.label_2.setObjectName(_fromUtf8("label_2"))

        self.retranslateUi(aboutDialog)
        QtCore.QMetaObject.connectSlotsByName(aboutDialog)

    def retranslateUi(self, aboutDialog):
        aboutDialog.setWindowTitle(_translate("aboutDialog", "Dialog", None))
        self.aboutTitle.setText(_translate("aboutDialog", "Get Info", None))
        self.label.setText(_translate("aboutDialog", "Get info by Roman Ost.", None))
        self.label_2.setText(_translate("aboutDialog", "Version 0.4", None))


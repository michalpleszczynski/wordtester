# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'RecordDialog.ui'
#
# Created: Tue Apr 12 11:57:53 2011
#      by: PyQt4 UI code generator 4.7.4
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

class Ui_RecordDialog(object):
    def setupUi(self, RecordDialog):
        RecordDialog.setObjectName("RecordDialog")
        RecordDialog.resize(400, 109)
        self.recordNStopButton = QtGui.QPushButton(RecordDialog)
        self.recordNStopButton.setGeometry(QtCore.QRect(20, 20, 131, 27))
        self.recordNStopButton.setCheckable(True)
        self.recordNStopButton.setObjectName("recordNStopButton")
        self.playButton = QtGui.QPushButton(RecordDialog)
        self.playButton.setGeometry(QtCore.QRect(20, 70, 98, 27))
        self.playButton.setCheckable(True)
        self.playButton.setObjectName("playButton")
        self.timeLabel = QtGui.QLabel(RecordDialog)
        self.timeLabel.setGeometry(QtCore.QRect(160, 70, 91, 17))
        self.timeLabel.setObjectName("timeLabel")
        self.fileNameLineEdit = QtGui.QLineEdit(RecordDialog)
        self.fileNameLineEdit.setGeometry(QtCore.QRect(160, 20, 113, 27))
        self.fileNameLineEdit.setObjectName("fileNameLineEdit")

        self.retranslateUi(RecordDialog)
        QtCore.QMetaObject.connectSlotsByName(RecordDialog)

    def retranslateUi(self, RecordDialog):
        RecordDialog.setWindowTitle(QtGui.QApplication.translate("RecordDialog", "Record", None, QtGui.QApplication.UnicodeUTF8))
        self.recordNStopButton.setText(QtGui.QApplication.translate("RecordDialog", "Stop recording...", None, QtGui.QApplication.UnicodeUTF8))
        self.playButton.setText(QtGui.QApplication.translate("RecordDialog", "Play", None, QtGui.QApplication.UnicodeUTF8))
        self.timeLabel.setText(QtGui.QApplication.translate("RecordDialog", "Time: 99:99", None, QtGui.QApplication.UnicodeUTF8))


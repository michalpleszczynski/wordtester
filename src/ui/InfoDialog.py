#-*- coding: utf-8 -*-

from __future__ import division

from PyQt4.QtCore import SIGNAL, QString
from PyQt4.QtGui import QDialog, QApplication

import ui_InfoDialog

class InfoDialog(QDialog, ui_InfoDialog.Ui_InfoDialog):
    def __init__(self, word, parent = None):
        super(InfoDialog, self).__init__(parent)
        self.setupUi(self)

        self.wordLineEdit.setText(word.getWord())
        self.meaningsLineEdit.setText(word.meaningsToText())
        self.contextLineEdit.setText(word.getContext() if word.getContext() is not None else QString())
        self.difficultyComboBox.setCurrentIndex(self.difficultyComboBox.findText(word.getDifficulty()))

        self.askedLabel.setText("..asked: " + str(word.getAsked()) + " times.")
        if word.getAsked() != 0:
            self.answeredLabel.setText("..answered: " + str(word.getAnswered()) + " times. " + "%.2f" % (word.getAnswered() / word.getAsked() * 100) + "% right.")
        else:
            self.answeredLabel.setText("..answered: " + str(word.getAnswered()) + " times. ")
        
        self.wordChanged = False
        self.meaningsChanged = False
        self.contextChanged = False
        self.difficultyChanged = False

        self.connect(self.wordLineEdit, SIGNAL("textChanged(QString)"),
                    lambda: self.changed("word"))
        self.connect(self.meaningsLineEdit, SIGNAL("textChanged(QString)"),
                    lambda: self.changed("meanings"))
        self.connect(self.contextLineEdit, SIGNAL("textChanged(QString)"),
                    lambda: self.changed("context"))
        self.connect(self.difficultyComboBox, SIGNAL("currentIndexChanged(const QString&)"),
                    lambda: self.changed("difficulty"))
        self.connect(self.closeButton, SIGNAL("clicked()"),
                    self.accept)

    def changed(self,who):
        if who == 'word':
            self.wordChanged = True
        elif who == 'meanings':
            self.meaningsChanged = True
        elif who == 'context':
            self.contextChanged = True
        elif who == 'difficulty':
            self.difficultyChanged = True

    def result(self):
        whatChanged = [None,None,None,None]
        if self.wordChanged:
            whatChanged[0] = str(self.wordLineEdit.text())
        if self.meaningsChanged:
            whatChanged[1] = unicode(self.meaningsLineEdit.text())
        if self.contextChanged:
            whatChanged[2] = str(self.contextLineEdit.text())
        if self.difficultyChanged:
            whatChanged[3] = str(self.difficultyComboBox.currentText())
        return whatChanged
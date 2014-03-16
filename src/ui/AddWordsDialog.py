#-*- coding: utf-8 -*-

from PyQt4.QtCore import SIGNAL
from PyQt4.QtGui import QDialog, QSpinBox, QHBoxLayout, QDialogButtonBox, QLabel, \
    QVBoxLayout

class AddWordsDialog(QDialog):
    """
    Dialog that allows the user to insert the number of words he wants to add.
    """
    def __init__(self, parent = None):
        super(AddWordsDialog, self).__init__(parent)

        label = QLabel("How many words do you want to add?")
        self.spinBox = QSpinBox()
        self.spinBox.setMinimum(1)
        self.spinBox.setMaximum(50)
        label.setBuddy(self.spinBox)
        buttonBox = QDialogButtonBox(QDialogButtonBox.Ok|QDialogButtonBox.Cancel)
        HLayout = QHBoxLayout()
        HLayout.addWidget(label)
        HLayout.addWidget(self.spinBox)
        HLayout2 = QHBoxLayout()
        HLayout2.addWidget(buttonBox)
        VLayout = QVBoxLayout()
        VLayout.addLayout(HLayout)
        VLayout.addLayout(HLayout2)

        self.setLayout(VLayout)
        self.spinBox.setFocus()
        self.setWindowTitle("Add Words")

        self.connect(buttonBox, SIGNAL("accepted()"),
                    self.accept)
        self.connect(buttonBox, SIGNAL("rejected()"),
                    self.reject)

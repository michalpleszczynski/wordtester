#-*- coding: utf-8 -*-
import sys
from PyQt4.QtCore import *
from PyQt4.QtGui import *

import StartDialog

app = QApplication(sys.argv)
app.setApplicationName("Word Tester")

if not QFile.exist("users.dat"):
    pass

dialog = StartDialog.StartDialog()
if dialog.exec_():
    pass

app.exec_()


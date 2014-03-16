#-*- coding: utf-8 -*-

from PyQt4.QtCore import *
from PyQt4.QtGui import *
import ui_StartDialog

class StartDialog(QDialog, ui_StartDialog.Ui_StartDialog):
    def __init__(self, parent = None):
        super(StartDialog, self).__init__(parent)
        self.setupUi(self)

        self.userComboBox.addItem("Test User")
        self.passwordLineEdit.setEchoMode(QLineEdit.Password)

        settings = QSettings()

        if settings.contains("UserList"):
            userList = settings.value("UserList").toList()
            for item in userList:
                self.userComboBox.addItem(item.toString())

        if settings.contains("Lastuser"):
            lastUser = settings.value("LastUser").toString()
            self.userComboBox.setCurrentIndex(self.userComboBox.findText(lastUser))


if __name__ == '__main__':
    import sys
    app = QApplication(sys.argv)
    form = StartDialog()
    form.show()
    app.exec_()
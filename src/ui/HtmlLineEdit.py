#-*- coding: utf-8 -*-

import platform

from PyQt4.QtCore import Qt
from PyQt4.QtGui import QTextEdit, QFontMetrics, QKeySequence


class HtmlLineEdit(QTextEdit):
    """
    Subclass of QTextEdit, it behaves just line QLineEdit, but accepts html.
    """
    def __init__(self, parent=None):
        super(HtmlLineEdit, self).__init__(parent)
        
        self.setLineWrapMode(QTextEdit.NoWrap)
        self.setTabChangesFocus(True)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        fm = QFontMetrics(self.font())
        h = int(fm.height() * (1.4 if platform.system() == "Windows" \
                                   else 1.2))
        self.setMinimumHeight(int(h*1.3))
        self.setMaximumHeight(int(h * 1.6))

       
    def keyPressEvent(self, event):
        if event == QKeySequence.InsertParagraphSeparator:
            event.ignore()
        else:
            QTextEdit.keyPressEvent(self, event)

    def text(self):
        return self.toPlainText()

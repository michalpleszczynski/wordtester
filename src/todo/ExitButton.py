#-*- coding: utf-8 -*-

from PyQt4.QtGui import *
from PyQt4.QtCore import *

class ExitButton(QAbstractButton):
    def __init__(self, pixmap, parent=None):
        super(PicButton, self).__init__(parent)
        self.pixmap = pixmap

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.drawPixmap(event.rect(), self.pixmap)kjsad

    def sizeHint(self):
        return self.pixmap.size()

    def mouseReleaseEvent(self, event):
        self.emit(SIGNAL("clicked()"))


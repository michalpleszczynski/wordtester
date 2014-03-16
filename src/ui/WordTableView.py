#-*- coding: utf-8 -*-

from PyQt4.QtCore import Qt, QEvent
from PyQt4.QtGui import QTableView, QKeyEvent

WORD, MEANINGS, CONTEXT, DIFFICULTY = range(4)

class WordTableView(QTableView):
    """
    Subclass of QTableView.
    """
    def __init__(self, parent = None):
        super(WordTableView, self).__init__(parent)

    # when pressing Tab, user switches only between WORDS, MEANINGS, and CONTEXT
    # columns. This makes editing easier.
    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Tab:
            index = self.currentIndex()
            model = index.model()
            if index.column() == WORD:
                self.setCurrentIndex(index.sibling(index.row(),MEANINGS))
            elif index.column() == MEANINGS:
                self.setCurrentIndex(index.sibling(index.row(),CONTEXT))
            elif index.column() == CONTEXT and index.row() != model.rowCount()-1:
                self.setCurrentIndex(index.sibling(index.row()+1,WORD))
        else:
            QTableView.keyPressEvent(self, event)

    # while done editing a cell (Enter/Return) focus jumps to the next column
    def closeEditor(self, editor, hint):
        QTableView.closeEditor(self, editor, hint)
        self.keyPressEvent(QKeyEvent(QEvent.KeyPress,Qt.Key_Tab,Qt.NoModifier))
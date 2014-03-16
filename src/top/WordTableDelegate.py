# -*- coding: utf-8 -*-

from PyQt4.QtCore import *
from PyQt4.QtGui import *

WORD, MEANINGS, CONTEXT, DIFFICULTY = range(4)

class WordTableDelegate(QItemDelegate):

    """
    Subclass of QItemDelegate responsible for the apperance of the wordsTable widget.
    Right now all it does is creating and handling the editor for the difficulty field.
    """

    def __init__(self, parent = None):
        super(WordTableDelegate, self).__init__(parent)

    def createEditor(self, parent, option, index):
        if index.column() == DIFFICULTY:
            comboBox = QComboBox(parent)
            list = QStringList()
            for item in ('EASY','MEDIUM','HARD'):
                list.append(item)
            comboBox.addItems(list)
            return comboBox
        else:
            return QItemDelegate.createEditor(self, parent, option,
                                              index)

    def setEditorData(self, editor, index):
        text = index.model().data(index, Qt.DisplayRole).toString()
        if index.column() == DIFFICULTY:
            i = editor.findText(text)
            if i == -1:
                i = 0
            editor.setCurrentIndex(i)
        else:
            QItemDelegate.setEditorData(self, editor, index)


    def setModelData(self, editor, model, index):
        if index.column() == DIFFICULTY:
            model.setData(index, QVariant(editor.currentText()))
        else:
            QItemDelegate.setModelData(self, editor, model, index)
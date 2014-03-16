#!/usr/bin/python
#-*- coding: utf-8 -*-

import os
import pickle
import platform

try:
    from PyQt4.QtCore import Qt, SIGNAL, QSettings, QString, QVariant, \
            QFile, QFileInfo, QTimer, QPoint
    from PyQt4.QtGui import QMainWindow, QAbstractItemView, QFileDialog, \
            QKeySequence, QApplication, QAction, QStatusBar, QMessageBox, QMenu, \
                QClipboard
except:
    print "Failed to locate PyQt4. Please install needed packages."
    print "In order to do that, type in your console window:"
    print "sudo apt-get install python-qt4"

import top.WordContainerClass as WordContainerClass
import top.WordTableModel as WordTableModel
import top.WordTableDelegate as WordTableDelegate
import top.WordTesterExceptions as wtexception

import ui.ui_WordTesterWindow
import ui.TestDialog as TestDialog
import ui.AddWordsDialog as AddWordsDialog
import ui.InfoDialog as InfoDialog

WORD, MEANINGS, CONTEXT, DIFFICULTY = range(4)

class WordTester(QMainWindow, ui.ui_WordTesterWindow.Ui_WordTesterWindow):
    """
    Main class of the program. Subclass of QMainWindow.
    """
    def __init__(self, clipboard, parent=None):
        super(WordTester, self).__init__(parent)
        self.setupUi(self)

        ########################################
        # WORDS TABLE STUFF (most of it)
        ########################################

        self.model = WordTableModel.WordTableModel()
        self.wordsTable.setModel(self.model)
        self.wordsTable.setItemDelegate(WordTableDelegate.WordTableDelegate(self))

        self.wordsTable.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.wordsTable.setContextMenuPolicy(Qt.CustomContextMenu)
        self.wordsTable.customContextMenuRequested.connect(self.contextMenu)
        self.wordsTable.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.wordsTable.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        showSearchBarAction = self.createAction("Find",self.showSearchBar, QKeySequence.Find)
        closeSearchBarAction = self.createAction("Close search bar", self.closeSearchBar, Qt.Key_Escape)
        searchForNextWordAction = self.createAction("Find next", self.searchForNextOccurance, QKeySequence.FindNext)
        wordsTableActions = (showSearchBarAction, closeSearchBarAction, searchForNextWordAction)
        self.wordsTable.addActions(wordsTableActions)

        header = self.wordsTable.horizontalHeader()
        self.connect(header, SIGNAL("sectionClicked(int)"),
                    self.sortTable)
        self.connect(self.model, SIGNAL("dataChanged(QModelIndex,QModelIndex)"),
                    self.fnameChanged)

        ##############################################
        # OTHER WIDGETS
        ##############################################

        self.clipboard = clipboard

        self.statusBar = QStatusBar(self)
        self.setStatusBar(self.statusBar)

        self.allCheckBox.setChecked(True)

        self.searchBarFrame.setVisible(False)
        self.searchCheckBox.setChecked(True)

        ###############################################
        # ACTIONS
        ###############################################

        # file menu actions
        newFileAction = self.createAction("&New", self.newFile, QKeySequence.New,
                                tip = "Create list of words")
        openFileAction = self.createAction("&Open", self.load, QKeySequence.Open,
                                tip = "Open Word Tester file")
        saveFileAction = self.createAction("&Save", self.save, QKeySequence.Save,
                                tip = "Save Word Tester file")
        saveAsFileAction = self.createAction("Save &As", self.saveAs,
                                tip = "Save Word Tester file using a new name")
        importFileAction = self.createAction("&Import", self.importWords,
                                tip = "Import words from .txt file")
        exportFileAction = self.createAction("&Export", self.exportWords,
                                tip = "Export words to .txt file")
        closeAction = self.createAction("&Quit", self.close)

        self.fileMenu = self.menuBar().addMenu("&File")
        self.fileMenuActions = (newFileAction, openFileAction, saveFileAction,
                                saveAsFileAction, importFileAction, exportFileAction,
                                closeAction)

        # edit menu actions
        addWordsAction = self.createAction("Add", self.addWords, "CTRL++", tip = "Add new words")
        deleteWordsAction = self.createAction("Delete", self.deleteWords,
                                    QKeySequence.Delete, tip = "Delete words")
        showInfoAction = self.createAction("Properties", self.showInfo)

        easyAction = self.createAction("To easy", lambda difficulty = "EASY": self.changeDifficulty(difficulty))
        mediumAction = self.createAction("To medium", lambda difficulty = "MEDIUM": self.changeDifficulty(difficulty))
        hardAction = self.createAction("To hard", lambda difficulty = "HARD": self.changeDifficulty(difficulty))

        addWordsFromFileAction = self.createAction("Add from file..", self.addWordsFromFile, \
                                                    tip = "Add words from existing file, duplicates won't be appended")

        showAllAction = self.createAction("Show all", self.showAll, "CTRL+A", tip = "Show all words")
        hideAction = self.createAction("Hide", self.hideWords, "CTRL+H", tip = "Hide selected words")

        self.editMenu = self.menuBar().addMenu("&Edit")
        self.editMenuActions = (addWordsAction, hideAction, deleteWordsAction, showSearchBarAction, showAllAction)
        self.editMenu.addActions(self.editMenuActions)
        # submenu change difficulty
        difficultyMenu = self.editMenu.addMenu("Change difficulty")
        self.difficultyActions = (easyAction, mediumAction, hardAction)
        difficultyMenu.addActions(self.difficultyActions)
        self.editMenu.addSeparator()
        self.editMenu.addAction(addWordsFromFileAction)

        # words table context menu actions
        self.contextMenuActions = (deleteWordsAction, hideAction, showAllAction, showInfoAction)

        ###############################################
        # CONNECTIONS
        ###############################################

        self.connect(self, SIGNAL("resizeColumns"), self.resizeColumns)
        self.connect(self, SIGNAL("fnameChanged"), self.fnameChanged)
        self.connect(self.searchLineEdit, SIGNAL("returnPressed()"),
                    self.searchForWord)
        self.connect(self.searchCheckBox, SIGNAL("stateChanged(int)"),
                    self.searchLineEdit.setFocus)
        self.connect(self.fileMenu, SIGNAL("aboutToShow()"),
                                self.updateFileMenu)

        for checkBox in (self.allCheckBox, self.easyCheckBox, \
                        self.mediumCheckBox, self.hardCheckBox):
            self.connect(checkBox, SIGNAL("clicked()"),
                        lambda text = checkBox.text().toLower(): self.showGroup(text))

        self.connect(self.beginTestButton, SIGNAL("clicked()"),
                        self.beginTest)
        self.connect(self.wordsOnlyCheckBox, SIGNAL("stateChanged(int)"),
                        self.showWordsOnly)
        self.connect(self.clipboard, SIGNAL("dataChanged()"),
                        self.scanKeyboard)

        ####################################################
        # SETTINGS
        ####################################################

        settings = QSettings(QSettings.IniFormat, QSettings.UserScope,
                            "Word Tester", "michauStuff")
        self.recentFiles = settings.value("RecentFiles").toStringList()
        self.restoreGeometry(settings.value("Geometry").toByteArray())

        #####################################################
        # VARIABLES AND STARTUP FUNCTIONS
        #####################################################

        self.setWindowTitle('Word Tester - Unknown File')
        self.recentlySearchedWord = ""

        self.updateFileMenu()
        # QTimer.singleShot just in case the file is large and will take a while to load
        if settings.value("LastFile") == QVariant() or settings.value("LastFile").toString().isEmpty():
            QTimer.singleShot(0, lambda num = 5: self.initialWords(num)) # if there is no Last File
        else:
            QTimer.singleShot(0, self.loadInitialFile)

    ######################################################
    # reimplemented QMainWindow methods
    ######################################################

    def resizeEvent(self, event):
        self.emit(SIGNAL("resizeColumns"))
        QMainWindow.resizeEvent(self, event)

    def closeEvent(self, event):
        if self.okToContinue():
            self.addRecentFiles(self.model.fname)
            settings = QSettings(QSettings.IniFormat, QSettings.UserScope, "Word Tester", "michauStuff")
            filename = QVariant(QString(self.model.fname)) \
                    if self.model.fname is not None else QVariant()
            settings.setValue("LastFile", filename)
            settings.setValue("Geometry", self.saveGeometry())
            recentFiles = QVariant(self.recentFiles) if self.recentFiles \
                else QVariant()
            settings.setValue("RecentFiles", recentFiles)
        else:
            event.ignore()

    # this is not really a QMainWindow method, but fits in here
    def contextMenu(self, pos):
        menu = QMenu()
        menu.addActions(self.contextMenuActions)
        difficultyMenu = menu.addMenu("Change difficulty")
        difficultyMenu.addActions(self.difficultyActions)
        # change position a little to have a corner of the menu where the mouse is
	if platform.system() != "Windows":
            menu.exec_(self.wordsTable.mapToGlobal(QPoint(pos.x()+18,pos.y()	+24)))
        else:
            menu.exec_(self.wordsTable.mapToGlobal(QPoint(pos.x()+16,pos.y()	+24)))

    ######################################################
    # SIGNALS
    ######################################################

    def resizeColumns(self):
        """
        Resizes WORD and DIFFICULTY columns to match their content. MEANIGS and
        CONTEXT columns share the left space - 50 pixels of margin.
        """
        size = self.wordsTable.size()
        tableWidth = size.width()
        # this used to be resizeColumns() method
        for column in (WORD,DIFFICULTY):
            self.wordsTable.resizeColumnToContents(column)
        wordColumnWidth = self.wordsTable.columnWidth(WORD)
        difficultyColumnWidth = self.wordsTable.columnWidth(DIFFICULTY)
        self.wordsTable.setColumnWidth(MEANINGS, \
            (tableWidth - wordColumnWidth - difficultyColumnWidth)/2 - 25)
        self.wordsTable.setColumnWidth(CONTEXT, \
            (tableWidth - wordColumnWidth - difficultyColumnWidth)/2 - 25)

    def fnameChanged(self):
        """
        Sets main window's title.
        """
        if self.model.fname.isEmpty():
            if self.model.dirty:
                title = 'Word Tester - Unknown File*'
            else:
                title = 'Word Tester - Unknown File'
        else:
            if self.model.dirty:
                title = 'Word Tester - %s*' % \
                    os.path.basename(unicode(self.model.fname))
            else:
                title = 'Word Tester - %s' % \
                    os.path.basename(unicode(self.model.fname))
        self.setWindowTitle(title)


    def scanKeyboard(self, mode = QClipboard.Clipboard):
        """
        If the scan option is on, retrieves text from system keyboard and places
        it in a new word.
        """
        if not self.scanCheckBox.isChecked():
            return None
        text = self.clipboard.text(mode)
        text = text.split("\n")
        # if there is more than one word
        for word in text:
            row = self.model.rowCount()
            self.model.insertRows(row+1,1)
            index = self.model.index(self.model.rowCount()-1,WORD)
            self.wordsTable.setCurrentIndex(index)
            self.model.setData(index,QVariant(word))


    ############################################################
    # HELPER METHODS
    ############################################################

    def createAction(self, text, slot=None, shortcut=None, icon=None,
                     tip=None, checkable=False, signal="triggered()"):
        action = QAction(text, self)
        if icon is not None:
            action.setIcon(QIcon(":/%s.png" % icon))
        if shortcut is not None:
            action.setShortcut(shortcut)
        if tip is not None:
            action.setToolTip(tip)
            action.setStatusTip(tip)
        if slot is not None:
            self.connect(action, SIGNAL(signal), slot)
        if checkable:
            action.setCheckable(True)
        return action

    def getVisibleWords(self):
        """
        Returns words that are visible at the moment.
        
        :rtype WordContainer
            WordContainer with a list of all visible words.
        """
        visibleWords = WordContainerClass.WordContainer()
        # iterate over main WordContainer. If the word is hidden, create
        # index in visibleWords (*) and then tie that index to the word in self.model.words.
        # visibleWords.append(self.model.words[row]) would create a shallow copy, so
        # changes made to it wouldn't be reflected in self.model.words
        for row in range(len(self.model.words)):
            if not self.wordsTable.isRowHidden(row):
                visibleWords.append('x') #(*)
                visibleWords[-1] = self.model.words[row]
        return visibleWords
    
    
    def okToContinue(self):
        if self.model.dirty:
            ans = QMessageBox.question(self, "Word Tester - Unsaved changes",
                    "Save unsaved changes?",
                    QMessageBox.Yes|QMessageBox.No|QMessageBox.Cancel)
            if ans == QMessageBox.Yes:
                self.save()
            elif ans == QMessageBox.Cancel:
                return False
        return True
    
    def addRecentFiles(self, fname):
        if fname is None:
            return
        if not self.recentFiles.contains(fname):
            self.recentFiles.prepend(QString(fname))
            while self.recentFiles.count() > 9:
                self.recentFiles.takeLast()

    def loadRecentFile(self, fname):
        if self.okToContinue():
            try:
                self.addRecentFiles(self.model.fname)
                self.model.fname = fname
                self.model.load()
            except (pickle.UnpicklingError, IOError, AttributeError, wtexception.FileHandlingExceptions) as e:
                self.statusBar.showMessage(str(e),5000)
            self.emit(SIGNAL("resizeColumns"))
            self.emit(SIGNAL("fnameChanged"))
    
    ######################################################
    # GUI FUNCTIONALITY
    ######################################################

    def showSearchBar(self):
        if self.searchBarFrame.isVisible():
            self.searchBarFrame.setVisible(False)
            self.wordsTable.setFocus()
        else:
            self.searchBarFrame.setVisible(True)
            self.searchLineEdit.selectAll()
            self.searchLineEdit.setFocus()


    def updateFileMenu(self):
        """
        Creates new file menu everytime the user invokes it. File menu can't be created
        only once, because of recent files section which has to be refreshed.
        """
        self.fileMenu.clear()
        # add all fixed actions, but close
        self.fileMenu.addActions(self.fileMenuActions[:-1])
        current = QString(self.model.fname) \
                if self.model.fname is not None else None
        recentFiles = []
        for fname in self.recentFiles:
            if fname != current and QFile.exists(fname):
                recentFiles.append(fname)
        if recentFiles:
            self.fileMenu.addSeparator()
            self.recentFilesMenu = self.fileMenu.addMenu("Recent Files")
            for i, fname in enumerate(recentFiles):
                action = QAction("&%d %s" % (
                        i + 1, QFileInfo(fname).fileName()), self)
                action.setData(QVariant(fname))
                self.connect(action, SIGNAL("triggered()"),
                             lambda file = fname: self.loadRecentFile(file))
                self.recentFilesMenu.addAction(action)
        self.fileMenu.addSeparator()
        # add the last action - close
        self.fileMenu.addAction(self.fileMenuActions[-1])


    def closeSearchBar(self):
        if self.searchBarFrame.isVisible():
            self.searchBarFrame.setVisible(False)
            self.wordsTable.setFocus()


    def searchForWord(self):
        self.recentlySearchedWord = unicode(self.searchLineEdit.text())
        backwards = self.searchCheckBox.isChecked()
        try:
            row = self.model.words.searchForWord(unicode(self.searchLineEdit.text()))
        except ValueError:
            return None # not found
        if backwards:
            # of backwards is on, we don't have to worry if searched word is before
            # or after the current one
            index = self.model.index(row, WORD)
        else:
            currentRow = self.wordsTable.currentIndex().row()
            # if the searched word is in the [currentRow:] part of self.model.words
            row = self.model.words.slice(currentRow).searchForWord(unicode(self.searchLineEdit.text()))
            if row != -1:
                index = self.model.index(row + currentRow, WORD)
            else:
                return None
        self.wordsTable.setCurrentIndex(index)
        self.searchLineEdit.selectAll()
        self.wordsTable.setFocus()


    def searchForNextOccurance(self):
        if self.recentlySearchedWord == "":
            return None
        else:
            backwards = self.searchCheckBox.isChecked()
            currentRow = self.wordsTable.currentIndex().row()+1
            row = self.model.words.slice(currentRow).searchForWord(self.recentlySearchedWord)
            if row != -1:
                # row is a position of searched row in [currentRow:] list, so row + currentRow
                # is a position in the whole list
                index = self.model.index(row + currentRow, WORD)
            else:
                if backwards:
                    row = self.model.words.slice(0,currentRow-1).searchForWord(self.recentlySearchedWord)
                    if row != -1:
                        index = self.model.index(row, WORD)
                    else:
                        return None
                else:
                    return None
            self.wordsTable.setCurrentIndex(index)
            self.searchLineEdit.selectAll()

    def showInfo(self):
        indexes = self.wordsTable.selectedIndexes()
        if (len(indexes)/self.model.columnCount() > 1):
            QMessageBox.warning(self,"Error!","Please select only one word.")
            return
        else:
            index = indexes[0]
        dialog = InfoDialog.InfoDialog(self.model.words[index.row()])
        if dialog.exec_():
            whatChanged = dialog.result()
            if whatChanged[0]:
                self.model.words[index.row()].setWord(whatChanged[0])
                self.model.dirty = True
            if whatChanged[1]:
                self.model.words[index.row()].setMeanings(whatChanged[1])
                self.model.dirty = True
            if whatChanged[2]:
                self.model.words[index.row()].setContext(whatChanged[2])
                self.model.dirty = True
            if whatChanged[3]:
                self.model.words[index.row()].setDifficulty(whatChanged[3])
                self.model.dirty = True
            if self.model.dirty:
                self.emit(SIGNAL("fnameChanged"))
                self.emit(SIGNAL("resizeColumns"))
                self.model.reset()


    ###########################################################
    # SAVE, LOAD, EXPORT, IMPORT
    ###########################################################

    def loadInitialFile(self):
        settings = QSettings(QSettings.IniFormat, QSettings.UserScope, "Word Tester", "michauStuff")
        fname = settings.value("LastFile").toString()
        if fname and QFile.exists(fname):
            self.model.fname = fname
            self.model.load()
            self.emit(SIGNAL("resizeColumns"))
        else:
            self.newFile()
        self.emit(SIGNAL("fnameChanged"))


    def addWordsFromFile(self):
        dir = os.path.dirname(unicode(self.model.fname)) \
            if not self.model.fname.isEmpty() else '.'
        fname = QFileDialog.getOpenFileName(self,
                        "Select a file to add words from", dir,
                        "Word Tester file *.pkl *.txt")
        if fname:
            if fname.endsWith(".pkl"):
                try:
                    self.model.load(fname,True)
                except (pickle.UnpicklingError, IOError, AttributeError, wtexception.FileHandlingExceptions) as e:
                    self.statusBar.showMessage(str(e),5000)
            elif fname.endsWith(".txt"):
                try:
                    self.model.importWords(fname,True)
                except (IOError, wtexception.FileHandlingExceptions) as e:
                    self.statusBar.showMessage(unicode(e),15000)

        self.emit(SIGNAL("resizeColumns"))
        self.emit(SIGNAL("fnameChanged"))


    def newFile(self):
        if self.okToContinue():
            self.model.removeRows(0,len(self.model.words))
            self.initialWords(5)
            self.addRecentFiles(self.model.fname)
            self.model.fname = QString()
            self.model.dirty = False
            self.emit(SIGNAL("fnameChanged"))


    def save(self):
        if self.model.fname.isEmpty():
            self.saveAs()
        else:
            self.model.removeDuplicates()
            try:
                self.model.save()
            except (pickle.PicklingError, IOError, wtexception.FileHandlingExceptions) as e:
                self.statusBar.showMessage(str(e),5000)
            else:
                self.emit(SIGNAL("fnameChanged"))

    def saveAs(self):
        dir = self.model.fname if not self.model.fname.isEmpty() else '.'
        fname = QFileDialog.getSaveFileName(self,
                        "Word Tester - Save Words", dir,
                        "Word Tester file *.pkl")
        if fname:
            if not fname.contains('.'):
                fname.append('.pkl')
            self.model.fname = fname
            self.save()

    def load(self):
        """
        Loads one or more files. If there are > 1 files to load, the new filename
        is set to Unknown.

        :throws:
            pickle.UnpicklingError, IOError, AttributeError, wtexception.FileHandlingExceptions (from model.import())
        """
        if not self.okToContinue():
            return
        dir = os.path.dirname(unicode(self.model.fname)) \
            if not self.model.fname.isEmpty() else '.'
        fnames = QFileDialog.getOpenFileNames(self,
                        "Select a file to open", dir,
                        "Word Tester files *.pkl")
        if not fnames.isEmpty():
            try:
                if len(fnames) != 1: # if the user chose more than one file to open
                    self.model.load(fnames[0])
                else:
                    self.addRecentFiles(self.model.fname)
                    self.model.fname = fnames[0]
                    self.model.load()
            except (pickle.UnpicklingError, IOError, AttributeError, wtexception.FileHandlingExceptions) as e:
                self.statusBar.showMessage(str(e),5000)
            # the first file was already loaded
            fnames.removeAt(0)
            for fname in fnames: # if there are any left
                try:
                    self.model.load(fname, True) # true, because we are appending to the fnames[0]
                except (pickle.UnpicklingError, IOError, AttributeError, wtexception.FileHandlingExceptions) as e:
                    self.statusBar.showMessage(str(e),5000)
            # if the user loaded more than one file, we set fname as Unknown
            if len(fnames) != 0:
                self.model.fname = QString()
            self.emit(SIGNAL("fnameChanged"))
        self.emit(SIGNAL("fillTheSize"))

    def importWords(self):
        """
        Imports one or more .txt files. The current filename is not changed.

        :throws:
            IOError, wtexception.FileHandlingExceptions (from model.import())
        """
        if not self.okToContinue():
            return
        dir = os.path.dirname(unicode(self.model.fname)) \
            if not self.model.fname.isEmpty() else '.'
        fnames = QFileDialog.getOpenFileNames(self,
                        "Select a file to import from", dir,
                        "(UTF-8) *.txt")
        # the idea is identical as in self.load()
        if not fnames.isEmpty():
            try:
                self.model.importWords(fnames[0])
            except (IOError, wtexception.FileHandlingExceptions) as e:
                self.statusBar.showMessage(unicode(e),15000)
            fnames.removeAt(0)
            for fname in fnames:
                try:
                    self.model.importWords(fname, True)
                except (IOError, wtexception.FileHandlingExceptions) as e:
                    self.statusBar.showMessage(unicode(e),15000)
            self.emit(SIGNAL("fnameChanged"))
            self.emit(SIGNAL("resizeColumns"))

    def exportWords(self):
        """
        Exports all visibleWords to the .txt file.

        :throws:
            IOError, wtexception.FileHandlingExceptions (from model.export())
        """
        dir = os.path.dirname(unicode(self.model.fname)) \
            if not self.model.fname.isEmpty() else '.'
        fname = QFileDialog.getSaveFileName(self,
                        "Word Tester - Export to txt", dir,
                        "(UTF-8) *.txt")
        if fname:
            if not fname.contains('.'):
                fname.append('.txt')
            try:
                # if all words are visible at the moment
                if len(self.getVisibleWords()) == len(self.model.words):
                    self.model.exportWords(fname)
                else:
                    self.model.exportWords(fname, self.getVisibleWords())
            except (IOError, wtexception.FileHandlingExceptions) as e:
                self.statusBar.showMessage(str(e),5000)

    #########################################################
    # PRESENTING DATA
    #########################################################

    def hideWords(self):
        index = self.wordsTable.selectedIndexes()
        for item in index:
            self.wordsTable.hideRow(item.row())
        self.emit(SIGNAL("resizeColumns"))


    def addWords(self):
        dialog = AddWordsDialog.AddWordsDialog(self)
        if dialog.exec_():
            toAdd = dialog.spinBox.value()
            row = self.model.rowCount()
            self.model.insertRows(row, toAdd)
            self.emit(SIGNAL("fnameChanged"))
            self.emit(SIGNAL("resizeColumns"))


    def deleteWords(self):
        index = self.wordsTable.selectedIndexes()
        while len(index) != 0:
            self.model.removeRows(index[0].row(),1,index[0])
            index = self.wordsTable.selectedIndexes()
        self.emit(SIGNAL("fnameChanged"))
        self.emit(SIGNAL("resizeColumns"))
        
    def changeDifficulty(self, difficulty):
        index = self.wordsTable.selectedIndexes()
        for item in index:
            # index can be in any column, by calling item.sibling we take an index
            # from the same row, but DIFFICULTY column
            self.model.setData(item.sibling(item.row(),DIFFICULTY),QVariant(difficulty))
        self.model.dirty = True
        self.emit(SIGNAL("fnameChanged"))
        self.model.reset()

    def showWordsOnly(self):
        if self.wordsOnlyCheckBox.isChecked():
            for column in (MEANINGS,CONTEXT,DIFFICULTY):
                self.wordsTable.hideColumn(column)
        else:
            for column in (MEANINGS,CONTEXT,DIFFICULTY):
                self.wordsTable.showColumn(column)


    # looks likes it unnecessary, but showAllAction is connected to it
    def showAll(self):
        self.showGroup()


    def showGroup(self,text = None):
        def showRows(self):
            for row in range(len(self.model.words)):
                index = self.model.index(row, DIFFICULTY)
                checked = (self.easyCheckBox.isChecked(),self.mediumCheckBox.isChecked(), \
                                    self.hardCheckBox.isChecked())
                difficulty = index.data().toString()
                if difficulty == 'EASY' and not checked[0]:
                    self.wordsTable.hideRow(row)
                elif difficulty == 'MEDIUM' and not checked[1]:
                    self.wordsTable.hideRow(row)
                elif difficulty == 'HARD' and not checked[2]:
                    self.wordsTable.hideRow(row)
                else:
                    self.wordsTable.showRow(row)

        # checkBoxes send a signal and their text
        if text in ('easy','medium','hard'):
            if self.allCheckBox.isChecked():
                self.allCheckBox.setChecked(False)
            showRows(self)
        else:
            # show all words, and uncheck any checked checkBoxes
            self.allCheckBox.setChecked(True)
            for row in range(len(self.model.words)):
                self.wordsTable.showRow(row)
            for checkBox in (self.easyCheckBox, self.mediumCheckBox, self.hardCheckBox):
                checkBox.setChecked(False)

        # one of the checkBoxes always has to be checked
        if not self.easyCheckBox.isChecked() and not self.mediumCheckBox.isChecked() and not \
                            self.hardCheckBox.isChecked() and not self.allCheckBox.isChecked():
            self.allCheckBox.setChecked(True)
            # hard coded checking as above apparently doesn't send a signal, so
            # we hard code a click
            self.allCheckBox.click()

    def sortTable(self, section):
        if section == WORD:
            self.model.sortByWord()
        elif section == DIFFICULTY:
            self.model.sortByDifficulty()
        # to update visible words
        for checkBox in (self.easyCheckBox, self.mediumCheckBox, self.hardCheckBox):
            if checkBox.isChecked():
                self.showGroup(checkBox.text().toLower())
                break
        self.emit(SIGNAL("resizeColumns"))
        

    def initialWords(self, number = 1):
        """
        Supplies number of empty words, when there is no file to load at the startup.
        """
        row = self.model.rowCount()
        self.model.insertRows(row, number)
        index = self.model.index(row, 0)
        self.model.dirty = False
        self.wordsTable.setFocus()
        self.wordsTable.setCurrentIndex(index)

    #########################################################
    # TEST
    #########################################################

    def beginTest(self):
        """
        Prepares WordContainer of words that the test will be performed on.
        Executes TestDialog.
        """
        visibleWords = self.getVisibleWords()
        # we don't want any empty words in the test
        if not visibleWords.validWords():
            return None
        difficulty = self.testDifficultyComboBox.currentText()
        # some idiot-proof checking
        if not self.repetitionsCheckBox.isChecked():
            if self.numberOfWordsSpinBox.value() > len(visibleWords) \
                and difficulty == 'All':
                    QMessageBox.warning(self,"Error!","Maxiumum number of words (without 'Allow repetition')" + \
                                        " is %d." % len(visibleWords))
                    return
            if difficulty != 'All' and len(visibleWords.getGroupOfWords(difficulty)) < self.numberOfWordsSpinBox.value():
                    QMessageBox.warning(self,"Error!","Maxiumum number of words (without 'Allow repetition')" + \
                                        " is %d." % len(visibleWords.getGroupOfWords(difficulty)))
                    return

        if difficulty == 'All':
            dialog = TestDialog.TestDialog(visibleWords, self)
        # in every difficulty there is some more idiot-proof checking
        # if all goes well create a TestDialog instance, which is later executed
        elif difficulty == 'Easy':
            if len(visibleWords.getGroupOfWords(difficulty)) == 0:
                self.statusBar.showMessage("No words with difficulty: " + difficulty,5000)
                return None
            dialog = TestDialog.TestDialog(visibleWords, self, difficulty)
        elif difficulty == 'Medium':
            if len(visibleWords.getGroupOfWords(difficulty)) == 0:
                self.statusBar.showMessage("No words with difficulty: " + difficulty,5000)
                return None
            dialog = TestDialog.TestDialog(visibleWords, self, difficulty)
        elif difficulty == 'Hard':
            if len(visibleWords.getGroupOfWords(difficulty)) == 0:
                self.statusBar.showMessage("No words with difficulty: " + difficulty,5000)
                return None
            dialog = TestDialog.TestDialog(visibleWords, self, difficulty)
        if dialog.exec_():
            # if the user is working on an Unknown File (not saved), the program
            # won't record results, without saving the file
            if not self.model.fname.isEmpty():
                self.model.dirty = True
                QTimer.singleShot(0, self.save)
            else:
                ans = QMessageBox.question(self, "Word Tester - Unsaved changes",
                                "Do you want to save the file? If not, results of " + \
                                "the test won't be saved.",
                                QMessageBox.Yes|QMessageBox.No)
                if ans == QMessageBox.Yes:
                    self.model.dirty = True
                    QTimer.singleShot(0, self.save)
            # to update visible words
            for checkBox in (self.easyCheckBox, self.mediumCheckBox, self.hardCheckBox):
                if checkBox.isChecked():
                    self.showGroup(checkBox.text().toLower())
                    return


if __name__ == '__main__':
    import sys
    app = QApplication(sys.argv)
    app.setApplicationName("Word Tester")
    form = WordTester(QApplication.clipboard())
    form.show()
    app.exec_()

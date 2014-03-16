#-*- coding: utf-8 -*-

import os
import re
import cPickle as pickle
import copy

from PyQt4.QtCore import Qt, SIGNAL, QAbstractTableModel, QString, QVariant, QModelIndex
from PyQt4.QtGui import QColor

import WordClass
import WordContainerClass
import WordTesterExceptions as wtexception

WORD, MEANINGS, CONTEXT, DIFFICULTY = range(4)

MAGIC_NUMBER = 0x35a5
FILE_VERSION = 1.0

class WordTableModel(QAbstractTableModel):
    """
    Subclass of the QAbstractTableModel responsible for handling wordsTable widget's
    interaction with the user.

    This is the main class that operates on WordContainer.
    Responsible for:
        saving, loading, importing, exporting, removing duplicates, sorting,
        sending and retrieving data from the view, removing and inserting rows
    """

    def __init__(self):
        super(WordTableModel, self).__init__()
        self.fname = QString()
        self.dirty = False
        self.words = WordContainerClass.WordContainer()
        
        self.reversedDiffSort = self.reversedWordSort = False

    # overloaded methods from QAbstractTableModel

    def flags(self, index):
        if not index.isValid():
            return Qt.ItemIsEnabled
        return Qt.ItemFlags(QAbstractTableModel.flags(self, index)|
                            Qt.ItemIsEditable)

    def data(self, index, role=Qt.DisplayRole):
        """
        Retrieves data from the wordsTable widget, also handles editing, alignment,
        and cells backround color (this one really should be in delegate, but..)
        """
        if not index.isValid() or not (0 <= index.row() <= len(self.words)):
            return QVariant()
        word = self.words[index.row()]
        column = index.column()
        if role == Qt.DisplayRole:
            if column == WORD:
                return QVariant(word.getWord())
            if column == MEANINGS:
                return QVariant(word.meaningsToText())
            if column == CONTEXT:
                return QVariant(word.getContext())
            if column == DIFFICULTY:
                return QVariant(word.getDifficulty())
        elif role == Qt.EditRole:
            if column == WORD:
                return QVariant(word.getWord())
            if column == MEANINGS:
                return QVariant(word.meaningsToText())
            if column == CONTEXT:
                return QVariant(word.getContext())
            if column == DIFFICULTY:
                return QVariant(word.getDifficulty())
        elif role == Qt.TextAlignmentRole:
            if column == DIFFICULTY:
                return QVariant(int(Qt.AlignCenter|Qt.AlignCenter))
            return QVariant(int(Qt.AlignLeft|Qt.AlignCenter))
        elif role == Qt.BackgroundColorRole:
            if column == DIFFICULTY:
                if word.getWeight() < 10:
                    return QVariant(QColor(255,0,0))
                if 10 <= word.getWeight() < 20:
                    return QVariant(QColor(255,51,0))
                if 20 <= word.getWeight() < 30:
                    return QVariant(QColor(255,102,0))
                if 30 <= word.getWeight() < 40:
                    return QVariant(QColor(255,153,0))
                if 40 <= word.getWeight() < 50:
                    return QVariant(QColor(255,204,0))
                if 50 <= word.getWeight() < 60:
                    return QVariant(QColor(255,255,0))
                if 60 <= word.getWeight() < 70:
                    return QVariant(QColor(195,255,0))
                if 70 <= word.getWeight() < 80:
                    return QVariant(QColor(135,255,0))
                if 80 <= word.getWeight() < 90:
                    return QVariant(QColor(75,255,0))
                if word.getWeight() >= 90:
                    return QVariant(QColor(0,255,0))
            if column == WORD:
                if word.getDuplicate():
                    return QVariant(QColor(255,0,0))
            return QVariant(QColor(255,255,255))
        return QVariant()

    def headerData(self, section, orientation, role = Qt.DisplayRole):
        """
        Sets headers labels.
        """
        if role == Qt.TextAlignmentRole:
            if orientation == Qt.Horizontal:
                return QVariant(int(Qt.AlignLeft|Qt.AlignVCenter))
            return QVariant(int(Qt.AlignRight|Qt.AlignVCenter))
        if role != Qt.DisplayRole:
            return QVariant()
        if orientation == Qt.Horizontal:
            if section == WORD:
                return QVariant("Word")
            elif section == MEANINGS:
                return QVariant("Meanings")
            elif section == CONTEXT:
                return QVariant("Used in context")
            elif section == DIFFICULTY:
                return QVariant("Difficulty")
        return QVariant(int(section + 1))

    def rowCount(self, index = QModelIndex()):
        return len(self.words)

    def columnCount(self, index = QModelIndex()):
        return 4

    def setData(self, index, value, role = Qt.EditRole):
        """
        Receives data from the user and saves them into the WordContainer object.
        """
        if index.isValid() and (0 <= index.row() <= len(self.words)):
            word = self.words[index.row()]
            column = index.column()
            if column == WORD:
                if unicode((value.toString())) != word.getWord():
                    word.setWord(unicode(value.toString()))
                    self.words.findDuplicates()
                    self.dirty = True
            elif column == MEANINGS:
                if unicode((value.toString())) != word.meaningsToText():
                    word.setMeanings(unicode(value.toString()))
                    self.dirty = True
            elif column == CONTEXT:
                if unicode((value.toString())) != word.getContext():
                    word.setContext(unicode(value.toString()))
                    self.dirty = True
            elif column == DIFFICULTY:
                if str((value.toString())) != word.getDifficulty():
                    word.setDifficulty(str(value.toString()))
                    self.dirty = True

            self.emit(SIGNAL("dataChanged(QModelIndex,QModelIndex)"),
                      index, index)
            return True
        return False

    def insertRows(self, position, rows = 1, index = QModelIndex()):
        self.beginInsertRows(QModelIndex(), position,
                             position + rows - 1)
        for row in range(rows):
            self.words.insert(position + row,WordClass.Word(" ", " "))
        self.endInsertRows()
        self.dirty = True
        self.words.findDuplicates()
        return True


    def removeRows(self, position, rows = 1, index = QModelIndex()):
        self.beginRemoveRows(QModelIndex(), position,
                             position + rows - 1)
        words = copy.deepcopy(self.words)
        self.words.clearWords()
        self.words.addWords(words[:position] + \
                     words[position + rows:])
        self.endRemoveRows()
        self.dirty = True
        self.words.findDuplicates()
        return True

    # sorting methods
    def sortByDifficulty(self):
        self.words.sortByDifficulty(self.reversedDiffSort)
        self.reversedDiffSort = not self.reversedDiffSort
        self.reset()

    def sortByWord(self):
        self.words.sortByWord(self.reversedWordSort)
        self.reversedWordSort = not self.reversedWordSort
        self.reset()

    # saving and loading methods
    def save(self):
        """
        Saves (dumps with pickle) whole WordContainer into the .pkl file.

        :throws:
            IOError, pickle.PicklingError
        """
        if self.dirty == False:
            return
        exception = None
        fh = None
        try:
            # we don't check if the fname exists, main window does it before.
            fh = open(unicode(self.fname),'wb')
            pickle.dump(self.words, fh)
            self.dirty = False
        except (pickle.PicklingError, IOError) as e:
            exception = e
        finally:
            if fh is not None:
                fh.close()
            if exception is not None:
                raise exception


    def load(self, fname = None, append = False):
        """
        Loads from .pkl file into the WordContainer.

        :param fname
            Unicode, it is only explicitly given if the user wants to append to the
            current WordContainer instead of overwriting it.

        :param append
            Bool, append or overwrite.

        :throws:
            pickle.UnpicklingError, IOError, AttributeError, wtexception.FileHandlingExceptions,
            wtexception.SignatureError, wtexception.VersionError
        """
        exception = None
        fh = None
	if fname is None and self.fname is None:
	    return None
        try:
            if fname is None:
                fh = open(unicode(self.fname),'rb')
            else:
                fh = open(unicode(fname),'rb')

            pack = pickle.load(fh)
            # chceck if this is the current version of the Word Tester file
            if not pack.MAGIC_NUMBER == MAGIC_NUMBER:
                raise wtexception.SignatureError("Unable to load from %s. Unrecognized file signature" \
                                            % os.path.basename(unicode(fname)))
            if not pack.FILE_VERSION == FILE_VERSION:
                raise wtexception.VersionError("Unable to load from %s. Unrecognized file type version" \
                                            % os.path.basename(unicode(fname)))
            if not append:
                self.words = pack
                self.dirty = False
            else:
                wordsAppended = False
                # words that were already in WordContainer are not appended
                for item in pack:
                    if item not in self.words:
                        self.words.addWords(item)
                        wordsAppended = True
                if wordsAppended:
                    self.dirty = True
                    self.words.findDuplicates()
            self.reset()
        except (pickle.UnpicklingError, IOError, AttributeError, wtexception.FileHandlingExceptions) as e:
            exception = e
        finally:
            if fh is not None:
                fh.close()
            if exception is not None:
                raise exception


    # importing and exporting methods
    def encloseContextInBrackets(self, words = None):
        """
        Helper method that transofrms context component of the Word object to
        the form it is presented in .txt file.

        :param WordContainer words
            If words are specified, changes only the ones given.

        :rtype WordContainer
        """
        # WordContainer has to be copied, because it is changed only to save in .txt
        # self.words can't be changed during that process
        if words is None:
            enclosedWords = copy.deepcopy(self.words)
        else:
            enclosedWords = copy.deepcopy(words)
        context = ""
        for item in enclosedWords:
            context = item.getContext()
            if context is not None and context != "":
                contextList = context.split(";")
                contextListBrackets = []
                for sentence in contextList:
                    sentence = sentence.strip()
                    sentence = "[" + sentence + "]"
                    contextListBrackets.append(sentence)
                context = ";".join(contextListBrackets)
                item.setContext(context)
        return enclosedWords


    def importCheckAndFormat(self, text):
        """
        Helper method that checks the format of the .txt file before import and
        transforms each line into the Word object.

        :param str text
            Line from the .txt file.

        :rtype
            Word object.

        :throws:
            wtexception.ImportSyntaxError
        """
        line = text

        # if there is a blank line (usually there is at eh EOF)
        if line is None or line.strip() == "":
            return None

        # regular expressions
        squareRe = re.compile('\[.*?\]')
        roundRe = re.compile('\(.*?\)')

        # get everything that is enclosed in square and round brackets
        context = squareRe.findall(text)
        notes = roundRe.findall(text)

        Ucontext = unicode()
        for i in range(len(context)):
            text = text.replace(context[i],'')
            context[i] = context[i].strip(']')
            context[i] = context[i].strip('[')
            Ucontext += unicode(context[i] + ' ; ')

        Ucontext = Ucontext.strip(' ; ')

        # remove everything that is enclosed in round brackets
        for i in range(len(notes)):
            text = text.replace(notes[i],'')

        # so far even if we couldn't find either []'s or ()'s it wasn't a problem
        text = text.split('-')

        if len(text) != 2:
            raise wtexception.ImportSyntaxError("Selected file is not in required format. Error in line: %s" % line)

        word = text[0].strip()
        meanings = text[1].strip()

        return WordClass.Word(word,meanings,Ucontext)

    def exportCheckAndFormat(self, word, meanings, context):
        """
        Helper method that checks the format of the Word object components before
        exporting to .txt file, and transforms each Word object to one str.
        """

        contextList = []
        if context is not None:
            context = context.strip()
            if context != '':
                contextList = context.split(';')
                for i in range(len(contextList)):
                    contextList[i] = contextList[i].strip()
                    if not contextList[i].startswith('[') or not contextList[i].endswith(']'):
                        raise wtexception.ExportSyntaxError("Context has to be enclosed in []. Error occured in word: %s" % word)

        # join meanings with their contexts as long as there are meanings available
        # if no context are present we catch the IndexError and append a comma only
        meaningsNcontext = unicode()
        for i in range(len(meanings)):
            meaningsNcontext += unicode(meanings[i])
            try:
                meaningsNcontext += ' ' + contextList[i] + ', '
            except IndexError:
                meaningsNcontext += ', '
        meaningsNcontext = meaningsNcontext.strip(', ')

        return word + ' - ' + meaningsNcontext + '\r\n'

    def importWords(self, fname, append = False):
        """
        Imports data from the .txt file and transorms it into the WordContainer object.

        :param str fname
            File name to import from. It will never be none because it's checked before.

        :param bool append
            Informs if to append to the current file or open a new one.

        :throws:
            IOError, wtexception.FileHandlingExceptions, wtexception.EncodingError
        """
        pack = WordContainerClass.WordContainer()
        words = []

        fh = None
        exception = None
        try:
            import codecs

            fh = codecs.open(unicode(fname),'r','utf-8')
            try:
                string = fh.readline()
            except UnicodeDecodeError as e:
                raise wtexception.EncodingError("""Unable to import from %s.
Please choose a file with UTF-8 encoding!""" \
                            % os.path.basename(unicode(fname)))

            # strip an utf-8 marker char from the begining of the file
#            if string[0] == unicode(codecs.BOM_UTF8, 'utf-8'):
#                string = string.lstrip(unicode(codecs.BOM_UTF8, 'utf-8'))
#            else:
#                raise wtexception.EncodingError("""Unable to import from %s.
#Please choose a file with UTF-8 encoding!""" \
#                            % os.path.basename(unicode(fname)))

            wordsAppended = False

            # first line has been already read in order to strip BOM_UTF8
            word = self.importCheckAndFormat(string)
            if append:
                if word not in self.words:
                    pack.append(word)
                    wordsAppended = True
            else:
                pack.append(word)

            # iterate over other lines in the file
            for line in fh:
                word = self.importCheckAndFormat(line)
                # if there was a blink line just skip it
                if word is None:
                    continue
                if append:
                    if word not in self.words:
                        pack.append(word)
                        wordsAppended = True
                else:
                    pack.append(word)

            # if append == False, we overwrite self.words with the words retrived
            # from the .txt file
            if not append:
                self.words = copy.deepcopy(pack)
            else:
                if wordsAppended:
                    pack.addWords(words)
                    self.words.addWords(pack)
            if (append and wordsAppended) or not append:
                self.dirty = True
                self.words.findDuplicates()
                self.reset()
            else:
                self.dirty = False

        except (IOError, wtexception.FileHandlingExceptions) as e:
            exception = e
        finally:
            if fh is not None:
                fh.close()
            if exception is not None:
                raise exception


    def exportWords(self, fname, words = None):
        """
        Exports WordContainer into the .txt file.

        :param str fname
            Name of the file to export to. Just like in import it will never be None.

        :words WordContainer
            If
        """
        exception = None
        fh = None
        try:
            import codecs

            fh = codecs.open(unicode(fname),'w')
            fh.write(codecs.BOM_UTF8)
            fh.close()
            fh = codecs.open(unicode(fname),'a','utf-8')
            if words is None:
                enclosedWords = self.encloseContextInBrackets()
            else:
                enclosedWords = self.encloseContextInBrackets(words)
            for item in enclosedWords:
                fh.write(self.exportCheckAndFormat(item.getWord(), item.getMeanings(), item.getContext()))
        except IOError, e:
            exception = e
        finally:
            if fh is not None:
                fh.close()
            if exception is not None:
                raise exception

    def removeDuplicates(self):
        """
        To every word that is repeated through WordContainer this method adds
        approperiate number of '*' at the end to make it unique. ('*''s should, and
        hopefully will be replaced by superscripts)
        """
        while self.hasDuplicates():
            i = len(self.words) - 1
            while i >= 0 and self.hasDuplicates():
                word = self.words[i].getWord()
                if self.words.duplicates.has_key(word):
                    self.words[i].setWord(word + (self.words.duplicates[word]-1)*'*')
                    self.words.duplicates[word] -= 1
                i -= 1
        self.reset()

    def hasDuplicates(self):
        self.words.findDuplicates()
        if len(self.words.duplicates):
            return True
        else:
            return False


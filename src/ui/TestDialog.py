#-*- coding: utf-8 -*-

from __future__ import division

from PyQt4.QtCore import SIGNAL
from PyQt4.QtGui import QDialog, QKeySequence, QMessageBox

import ui_TestDialog

class TestDialog(QDialog, ui_TestDialog.Ui_testDialog):
    """
    Dialog whith which user interacts when performing a test on words.
    """
    def __init__(self, words, parent = None, difficulty = None):
        """
        Initializer of Test Dialog.

        :param WordContainer words
            Set of words that dialog should choose from.

        :param str difficulty
            If the option 'Test difficulty' in main window is set to anything else
            than 'All' dialog gets wanted difficulty through that parameter.
        """
        super(TestDialog, self).__init__(parent)
        self.setupUi(self)
        self.answerLineEdit.setFocus()
        self.contextFrame.setVisible(True)
        self.showContextCheckBox.setChecked(True)

        self.words = words
        self.difficulty = difficulty

        self.usedWords = []
        if self.difficulty:
            self.currentWord = self.words.getRandomWord(self.difficulty)
            # we also have to know how many words with that difficulty is in the set
            # in order to put it in stop condition in checkAnswer
            self.numberOfAvailableWords = self.words.getNumberOfWordsWithDifficulty(self.difficulty)
        else:
            self.currentWord = self.words.getRandomWord()

        self.numRight = 0
        self.numAnswered = 0
        self.prevState = 0

        self.allowRepetition = parent.repetitionsCheckBox.isChecked()
        self.numberOfWords = parent.numberOfWordsSpinBox.value()

        self.connect(self.okButton, SIGNAL("clicked()"),
                    self.checkAnswer)
        self.connect(self.showContextCheckBox, SIGNAL("stateChanged(int)"),
                    self.showContextText)

        self.wordLabel.setText(self.currentWord.getWord())
        self.showPoints()
        self.showContextInTextEdit()
        self.usedWords.append(self.currentWord.getWord())

    def showContextText(self, state):
        """
        Shows/hides the context frame, invoked by showContextCheckBox signal only.

        :param int state
            This variable is sent along with the signal.
        """
        if state == 2:
            self.contextFrame.setVisible(True)
        else:
            self.contextFrame.setVisible(False)

    def showContextInTextEdit(self):
        """
        Show context in context frame, each part of context in separate line.
        """
        self.contextLineEdit.clear()
        if self.currentWord.getContext() is not None:
            context = self.currentWord.getContext().split(";")
            context = [item.strip() for item in context]
            self.contextLineEdit.insertPlainText("\n".join(context))

    def keyPressEvent(self, event):
        if event == QKeySequence.InsertParagraphSeparator:
            self.okButton.click()
        else:
            QDialog.keyPressEvent(self, event)

    def closeEvent(self, event):
        self.accept()

    def nextState(self):
        self.prevState = 0 if self.prevState else 1

    def checkAnswer(self):
        """
        Method that checks if the answer was correct, shows the correct answer,
        updates points, and chooses the next word to the test.
        """
        # if self.prevState == 0 then user just typed in his answer and will hit
        # the Enter/Return button to get the result. Then, the prevState will change to 1.
        # if self.prevState == 1 then user typed in his answer and has already hit
        # the Enter/Return button, so he will hit the Enter/Return button again to get
        # a new word. Then, the prevState will change to 0.
        if not self.prevState:
            answer = self.answerLineEdit.text()
            rightAnswer = self.currentWord.ask(unicode(answer))
            # Word.ask() returns (bool, answer) tuple
            if rightAnswer[0]:
                self.numRight += 1
                self.numAnswered += 1
                for item in self.currentWord.getMeanings():
                    # matching meanings are highlighted in green
                    if item in rightAnswer[1]:
                        answer = answer.replace(item,"<font color='green'>" + item + "</font>")
                    else:
                    # not given by the user, but correct meanings are highlighted in blue
                        answer += ("<font color='blue'>" + ", " + item + "</font>")
                # incorrect meanings given by the user are highlighted in red
                self.answerLineEdit.setText("<font color='red'>" + answer + "</font>")
            else: # if rightAnswer[0] == False
                self.numAnswered += 1
                self.answerLineEdit.setText("<font color='red'>" + rightAnswer[1] + "</font>")
            self.showPoints()
        else: # if self.prevState == 1
            if self.difficulty:
                self.currentWord = self.words.getRandomWord(self.difficulty)
            else:
                self.currentWord = self.words.getRandomWord()
            if not self.allowRepetition:
                while self.currentWord.getWord() in self.usedWords:
                    if self.difficulty:
                        self.currentWord = self.words.getRandomWord(self.difficulty)
                    else:
                        self.currentWord = self.words.getRandomWord()
            self.usedWords.append(self.currentWord.getWord())
            self.wordLabel.setText(self.currentWord.getWord())
            self.answerLineEdit.clear()
            self.showContextInTextEdit()
        self.nextState()
        # if self.allowRepetition is on, we check only if self.numAnswered == self.numberOfWords
        if (self.numAnswered == len(self.words) and not self.allowRepetition) \
            or self.numAnswered == self.numberOfWords:
            self.theEnd()
        # if the difficulty was given we need to check if there are words available
        if self.difficulty is not None:
            if self.numAnswered == self.numberOfAvailableWords:
                self.theEnd()

    def theEnd(self):
        QMessageBox.information(self, "Test finished!", "Congratulations! You've completed the test!\n \
Your score is %.2f" % (self.numRight/self.numAnswered * 100) + "%", "Ok")
        self.accept()

    def showPoints(self):
        self.pointsLabel.setText("<b>Points: " + "<font color='green'>" + \
                    str(self.numRight) + "</font>" + "/" + str(self.numAnswered) + "</b>")


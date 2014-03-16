#-*- coding: utf-8 -*-

from __future__ import division

EASY, MEDIUM, HARD = (75.00,100.00), (50.00,74.99), (0.00,49.99)

class Word:

    """
    This class represents a single Word object.
    """

    def __init__(self, word, meanings, context = None, difficulty = 0.00):

        """
        Initializer of Word object.

        :param unicode word
            Single word (or expression), part of the Word object which is the 'unknown' in the test.

        :param unicode meanings
            List of meanings (separated by commas) of the word variable.
            Held as a list of unicode objects.

        :param unicode context
            List of contexts (separated by semicolon) in which the word could be used.
            Order of contexts is important, each one is assigned to the meaning while
            exporting to the .txt file.

            Optional.

        :param float difficulty
            Difficulty of the word in (0.00,100.00). Essentialy invisible to the user,
            automaticly changes along with __asked and __answered variables.

            Optional, default == 0.00
        """

        self.word = word.strip().lower()
        self.meanings = self.toList(meanings)
        self.difficulty = difficulty
        self.context = context

        self.hasDuplicate = False

        self.__asked = 0
        self.__answered = 0
        self.__weight = difficulty


    # getters, even though simple getters supposedly don't make sense in Python
    # it just feels better to have them around
    def getWord(self):
        return self.word

    def getMeanings(self):
        return self.meanings

    def getContext(self):
        return self.context

    def getDifficulty(self):
        """
        Returns difficulty in the user friendly way.

        :rtype str
            {'EASY','MEDIUM','HARD'}
        """

        if min(EASY) <= self.__weight <= max(EASY):
            return 'EASY'
        elif min(MEDIUM) <= self.__weight <= max(MEDIUM):
            return 'MEDIUM'
        elif min(HARD) <= self.__weight <= max(HARD):
            return 'HARD'

    def getDuplicate(self):
        """
        Informs if the word has a duplicate in the container it is wrapped in.

        :rtype bool
        """
        return self.hasDuplicate

    def getWeight(self):
        if self.__asked < 5:
            return self.__weight
        return self.__answered / self.__asked * 100

    def getAsked(self):
        return self.__asked

    def getAnswered(self):
        return self.__answered

    # setters, same thing here
    def setWord(self, word):
        self.word = word

    def setMeanings(self, meanings):
        """
        :param meanings
            Accepts:
                -a list of meanings (str or unicode)
                -string variable (str or unicode)
        """
        if type(meanings).__name__ == 'list':
            self.meanings = meanings
        elif isinstance(meanings, basestring):
            self.meanings = self.toList(meanings)

    def setContext(self, context):
        self.context = context

    def setDifficulty(self, difficulty):
        self.__asked = 0
        self.__answered = 0
        if difficulty == 'EASY':
            self.__weight = 75.00
        elif difficulty == 'MEDIUM':
            self.__weight = 50.00
        elif difficulty == 'HARD':
            self.__weight = 0.00
        else:
            return None

    def setDuplicate(self, has):
        self.hasDuplicate = has

    #helper methods
    def toList(self, string):
        string = string.split(',')
        return [item.strip().lower() for item in string]

    def meaningsToText(self):
        """
        The same as str.join', '. I don't why it's even here, but need to stay
        for compability.

        :rtype str
            No idea why it works especially if large numbers of meanings have unicode chars.
            Should return unicode.
        """
        string = ''
        for item in self.meanings:
            string = string + item + ', '
        string = string.strip(', ')
        return string

    #methods that actually do something
    def calculateDifficulty(self):
        """
        Changes difficulty of the word, computed from __asked and __answered variables.
        Difficulty changes if the word was 'asked' more than 5 times, to prevent
        changing difficulty levels too rapidly.
        """
        if self.__asked < 5:
            return self.getDifficulty()
        else:
            self.__weight = self.__answered / self.__asked * 100
            if min(EASY) <= self.__weight <= max(EASY):
                return 'EASY'
            elif min(MEDIUM) <= self.__weight <= max(MEDIUM):
                return 'MEDIUM'
            elif min(HARD) <= self.__weight <= max(HARD):
                return 'HARD'
            else:
                return None

    def ask(self, answer):
        """
        Checks if the answer was right or wrong. If the answer contains at least one
        matching word the answer is considered as right.

        :param answer
            unicode, each answer must be separated by comma.

        :rtype tuple(bool,str) # again str, mystery
            Bool is of course the result of the test. Str is the expected (right) answer.
        """
        if answer is None:
            return False, self.meaningsToText()
        answer = self.toList(answer) #multiple answers are fine just like
                                     #multiple meanings
        rightAnswer = [value for value in answer if value in self.meanings]
        if len(rightAnswer) != 0:
        # if intersection of answer and meanings is not empty then
        # at least one right answer was given
            self.__asked += 1
            self.__answered += 1
            self.difficulty = self.calculateDifficulty()
            return True, rightAnswer #given answer is returned for GUI to know
                                     #which part of answer to highlight
        else:
            self.__asked += 1
            self.difficulty = self.calculateDifficulty()
            return False, self.meaningsToText() #meanings are returned to show
                                                #what the answer was suppose to be    

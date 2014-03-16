#-*- coding: utf-8 -*-

import random

import WordClass

class WordContainer:

    """
    Container class for Word objects.

    :static const hex MAGIC_NUMBER
        Constant written to the beging of every file associated with Word Tester,
        in order to identify the file.

    :static const float FILE_VERSION
        Like MAGIC_NUMBER. If any not backwards compatibile changes take place,
        FILE_VERSION will be upgraded, thus old files won't work.
    """

    MAGIC_NUMBER = 0x35a5
    FILE_VERSION = 1.0

    def __init__(self, words = None):

        """
        Initializer of WordContainer object.
        """

        if words is not None:
            self.words = words
        else:
            self.words = []
        self.duplicates = {}

        # counters used in getRandomWorld method
        self.easyCount = self.mediumCount = self.hardCount = 1

    # getters
    def getWords(self):
        """
        :rtype list(str)
        """
        words = []
        for item in self.words:
            words.append(item.getWord())
        return words

    def getMeanings(self):
        """
        Returns list of meanings. One str for one Word object.

        :rtype list(str)
        """
        meanings = []
        for item in self.words:
            meanings.append(item.meaningsToText())
        return meanings

    def getGroupOfWords(self,difficulty):
        """
        Returns all words with given difficulty.

        :param difficulty
            Str in {'EASY','MEDIUM','HARD'} case insensitive.

        :rtype list(Word)
        """
        group = []
        for item in self.words:
            if str(item.getDifficulty()).lower() == str(difficulty).lower():
                group.append(item)
        return group

    def getNumberOfWordsWithDifficulty(self, difficulty):
        i = 0
        for item in self.words:
            if str(item.getDifficulty()).lower() == str(difficulty).lower():
                i += 1
        return i

    # methods for Test
    def validWords(self):
        """
        Returns true if all the words have valid word and meanings components.
        """
        for item in self.words:
            if item.getWord().strip() == "" or item.getWord() is None \
            or item.meaningsToText().strip() == "" or item.meaningsToText() is None:
                return False
        return True

    def resetCounters(self):
        if self.easyCount >= 10000:
            self.easyCount = 0
        if self.mediumCount >= 10000:
            self.mediumCount = 0
        if self.hardCount >= 10000:
            self.hardCount = 0

    def getRandomWord(self, difficulty = None):
        """
        Returns semi-random word from our list.

        Through counters following random choossing is performed:

            we take a list containing of a counter and a tuple
            the counter is being ++'ed and it serves as an index for a tuple
            if tuple[counter % given mod] is not 0, then chosen word is accepted
            otherwise recursively another getRandomWord is called

        easy words have 50% possibility of being chosen
        medium words have 66% possibility of being chosen
        hard words have 80% possibility of being chosen

        :param difficulty optional
            Str in {'EASY','MEDIUM','HARD'} case insensitive. If the difficulty is given
            the first world with that difficulty is returned.
        """
        if len(self.words) == 0:
            return None
        i = random.randint(0,len(self.words)-1)
        word = self.words[i]

        if difficulty is not None:
            while str(word.getDifficulty()).lower() != str(difficulty).lower():
                i = random.randint(0,len(self.words)-1)
                word = self.words[i]
            return word

        #once in a while we reset counters so they don't hold too big values
        self.resetCounters()
        if min(WordClass.EASY) <= word.getWeight() <= max(WordClass.EASY):
            self.easyCount += 1
            if (0,1)[self.easyCount % 2]:
                return word
            else:
                return self.getRandomWord()
        elif min(WordClass.MEDIUM) <= word.getWeight() <= max(WordClass.MEDIUM):
            self.mediumCount += 1
            if (0,1,2)[self.mediumCount % 3]:
                return word
            else:
                return self.getRandomWord()
        elif min(WordClass.HARD) <= word.getWeight() <= max(WordClass.HARD):
            self.hardCount += 1
            if (0,1,2,3,4)[self.hardCount % 5]:
                return word
            else:
                return self.getRandomWord()


    #adding and deleteing words methods
    def addWords(self, words):
        """
        Adds word/words to the container.

        :param words
            Either list(Word), or WordContainer object, or Word object
        """
        if type(words).__name__ == 'list':
            for item in words:
                if not isinstance(item, WordClass.Word):
                    return
            self.words.extend(words)
        elif isinstance(words,WordContainer):
            self.words.extend(words.words)
        else:
            if not isinstance(words, WordClass.Word):
                return
            self.words.append(words)


    def deleteWords(self, words):
        """
        Deletes word/words.

        :param words
            Either str or list(str)
        """
        for item in self.words:
            if item.getWord() in words:
                self.words.remove(item)

    # this method IS needed, we can't use self.words = [] anywhere else, because
    # that would automaticly make self.words a list object instead of WordContainer
    def clearWords(self):
        self.words = []

    def findDuplicates(self):
        """
        Iterates over the container and looks for duplicates. Words are duplicates
        if they have identical word component. Information about duplicates is
        held in a dictionary {'word':n} n - number of occurences in the container
        """
        self.duplicates = {}
        for item in self.words:
            if item.getWord().strip() == "": #we ignore empty words
                continue
            count = self.getWords().count(item.getWord())
            if count >= 2:
                self.duplicates[item.getWord()] = count
                item.setDuplicate(True)
            else:
                item.setDuplicate(False)

    def searchForWord(self, text):
        """
        Searches for the whole word, or at least some that contains text in it.

        :rtype int
            Index of the word, or -1 if not found.
        """
        # using getWords() everywhere is ridiculous, because it just duplicates
        # iterating over the table...
        i = 0
        for item in self.words:
            if text in item.getWord():
                return i
            i = i+1
        return -1

    # overloaded list methods
    def insert(self, position, object):
        self.words.insert(position, object)

    def __iter__(self):
        for word in self.words:
            yield word

    def __len__(self):
        return len(self.words)

    def __getitem__(self, index):
        return self.words[index]

    def __getslice__(self, i = 0,j = None):
        if j is None:
            j = len(self.words)
        return self.words[i:j]

    def slice(self,i = 0,j = None):
        if j is None:
            j = len(self.words)
        return WordContainer(self.words[i:j])

    def __setitem__(self, index, item):
        self.words[index] = item

    def __contains__(self, item):
        """
        While checking if container contains item, we take into account only
        word and meanings components.
        """
        if item.getWord() in self.getWords():
                return True
        return False

    def append(self, x):
        self.words.append(x)

    # sorting methods
    # if reversed == True sorting is descending
    def sortByDifficulty(self, reversed = False):
        if not reversed:
            def compare(a, b):
                return cmp(a.getWeight(), b.getWeight())
        else:
            def compare(a, b):
                return -1 * cmp(a.getWeight(), b.getWeight())
        self.words = sorted(self.words, compare)

    def sortByWord(self, reversed = False):
        if not reversed:
            def compare(a, b):
                return cmp(a.getWord(), b.getWord())
        else:
            def compare(a, b):
                return -1 * cmp(a.getWord(), b.getWord())
        self.words = sorted(self.words, compare)
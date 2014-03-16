#-*- coding: utf-8 -*-

import unittest
from top.WordTableModel import WordTableModel

class  WordTableModelTestsTestCase(unittest.TestCase):
    def setUp(self):
        self.model = WordTableModel()
        self.model.load("dotestow.pkl")

    def testLoading(self):
        assert len(self.model.words) == 5, "incorrect number of loaded words " + \
            "got: " + len(self.model.words) + ", but: 5 was expected"
        list = []
        for word in self.model.words:
            list.append(word.word)
        msg = "failed while loading the words with number: "
        assert list[0] == "sibilant sound", msg + '0'
        assert list[1] == "aberration", msg + '1'
        assert list[2] == "acrid", msg + '2'
        assert list[3] == "adjourn", msg + '3'
        assert list[4] == "ambience", msg + '4'

    def testSorting(self):
        self.model.sortByWord()
        assert self.model.words[0].word == "aberration", "incorrect sorting by word " + \
            "got: " + self.model.words[0].word + ", but: 'aberration' was expected"
        self.model.sortByDifficulty()
        assert self.model.words[0].word == "adjourn", "incorrect sorting by word " + \
            "got: " + self.model.words[0].word + ", but: 'adjourn' was expected"
        self.model.reversedDiffSort = True
        self.model.sortByDifficulty()
        assert self.model.words[0].word == "ambience", "incorrect sorting by word " + \
            "got: " + self.model.words[0].word + ", but: 'ambience' was expected"

    def testExport(self):
        self.model.exportWords("exportTest.txt")
        modelFh = open("dotestow.txt")
        testFh = open("exportTest.txt")
        modelText = modelFh.read()
        testText = testFh.read()
        assert modelText == testText, "incorrect export"
        modelFh.close()
        testFh.close()
        import os
        os.remove("exportTest.txt")

    def testImport(self):
        self.model.words.clearWords()
        self.model.importWords("dotestow.txt")
        self.testLoading()


if __name__ == '__main__':
    unittest.main()


#-*- coding: utf-8 -*-

import unittest
from top.WordContainerClass import WordContainer
from top.WordClass import Word

class  WordContainerClassTestsTestCase(unittest.TestCase):
    def setUp(self):
        self.words = WordContainer()
    
    def testDuplicates(self):
        self.words.clearWords()
        self.word1 = Word("dog","pies, piesek","I walk my dog everyday")
        self.word2 = Word("what's up?","co jest?, co tam?, co słychać?")
        self.word3 = Word("language","język")
        lista = [self.word1, self.word2, self.word3]
        self.words.addWords(lista)
        self.words.findDuplicates()
        assert len(self.words.duplicates) == 0, "incorrect result of looking for duplicates"
        self.words.addWords(Word("dog","pies, piesek","I walk my dog everyday"))
        self.words.findDuplicates()
        assert len(self.words.duplicates) > 0, "incorrect result of looking for dupplicates"

    def testSearching(self):
        self.words.clearWords()
        self.word1 = Word("dog","pies, piesek","I walk my dog everyday")
        self.word2 = Word("what's up?","co jest?, co tam?, co słychać?")
        self.word3 = Word("language","język")
        lista = [self.word1, self.word2, self.word3]
        self.words.addWords(lista)
        result = self.words.searchForWord("lalalaal")
        assert result == -1, "incorrect result while searching"
        result = self.words.searchForWord("dog")
        assert result == 0, "incorrect result while searching"
        self.words.deleteWords("dog")
        result = self.words.searchForWord("dog")
        assert result == -1, "incorrect result after deleteing a word"
        
if __name__ == '__main__':
    unittest.main()


#-*- coding: utf-8 -*-

import unittest
from top.WordClass import Word


class  WordClassTestsTestCase(unittest.TestCase):
    def setUp(self):
        self.word1 = Word("dog","pies, piesek","I walk my dog everyday")
        self.word2 = Word("what's up?","co jest?, co tam?, co słychać?")
        self.word3 = Word("language","język")

    def testAsk(self):
        """Check if the ask method (and most of the others in this class) works fine"""

        evalEr = "wrong evaluation in the ask method: "
        ansEr = "ask returned wrong expected answer: "

        ans1 = self.word1.ask("piesek")
        assert ans1[0] is True, evalEr
        assert ans1[1] == ["piesek"], ansEr + str(ans1[1])

        ans2 = self.word2.ask("lala")
        assert ans2[0] is False, evalEr
        assert ans2[1] == "co jest?, co tam?, co słychać?", ansEr + str(ans2[1])

        ans3 = self.word3.ask("dialekt, język")
        assert ans3[0] is True, evalEr
        assert ans3[1] == ["język"], ansEr + str(ans3[1])

    def testDifficulty(self):
        """Check if the difficulty is calculated right"""
        word = Word("a","b,c")
        for i in range(7):
            word.ask("b")
        for i in range(3):
            word.ask("sdsa")
        assert word.getWeight() == 70.00, "wrong calculation of weight:"
        assert word.calculateDifficulty() == 'MEDIUM', "wrong difficulty returned"

if __name__ == '__main__':
    unittest.main()


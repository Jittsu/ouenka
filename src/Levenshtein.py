# -*- coding: utf-8 -*-
class levenshtein:

    def __init__(self):
        self.leven_table = []

    def culc(self, str1, str2):
        self.leven_table = [[0 for i in range(len(str1) + 1)] for n in range(len(str2) + 1)]
        for i in range(len(str1) + 1):
            self.leven_table[0][i] = i
        for n in range(len(str2)):
            self.leven_table[n+1][0] = n + 1

        for n in range(len(str2)):
            for i in range(len(str1)):
                if(str2[n] == str1[i]):
                    self.leven_table[n + 1][i + 1] = self.leven_table[n][i]
                else:
                    self.leven_table[n + 1][i + 1] = min(self.leven_table[n][i], self.leven_table[n + 1][i], self.leven_table[n][i + 1])
                    self.leven_table[n + 1][i + 1] += 1
    
        return self.leven_table[len(str2)][len(str1)]

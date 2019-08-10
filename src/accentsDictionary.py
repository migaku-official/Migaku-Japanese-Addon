# -*- coding: utf-8 -*-
# 
from os.path import join
import json
import re
from aqt.utils import  showInfo


class AccentsDictionary:
    def  __init__(self, addon_path, counterDict, potentialToKihonkei, adjustedDict, conditionalYomi, readingOnlyDict, exceptionDict, sameYomiDifferentAccent, suffixDict):
        self.hiraganaChart = u"がぎぐげござじずぜぞだぢづでどばびぶべぼぱぴぷぺぽ" \
                u"あいうえおかきくけこさしすせそたちつてと" \
                u"なにぬねのはひふへほまみむめもやゆよらりるれろ" \
                u"わをんぁぃぅぇぉゃゅょっゐゑ"
        self.katakanaChart = u"ガギグゲゴザジズゼゾダヂヅデドバビブベボパピプペポ" \
                u"アイウエオカキクケコサシスセソタチツテト" \
                u"ナニヌネノハヒフヘホマミムメモヤユヨラリルレロ" \
                u"ワヲンァィゥェォャュョッヰヱ"
        self.addon_path = addon_path
        self.counterDict = counterDict
        self.potentialToKihonkei = potentialToKihonkei
        self.adjustedDict = adjustedDict
        self.conditionalYomi = conditionalYomi
        self.readingOnlyDict = readingOnlyDict
        self.exceptionDict = exceptionDict
        self.sameYomiDifferentAccent = sameYomiDifferentAccent
        self.suffixDict = suffixDict
        self.dictionary = self.getDict()

    def getDict(self):
        accentDictionary = []
        dictionary = {}
        for x in range(1, 8):
            accentDictionaryPath = join(self.addon_path, "dict", "compAccDict" + str(x) + "_.json")
            with open(accentDictionaryPath, "r", encoding="utf-8") as accentDictionaryFile:
                accentDictionary += json.loads(accentDictionaryFile.read())

        for entry in accentDictionary:
            if entry[0] in dictionary:
                dictionary[entry[0]].append(entry)
            else:
                dictionary[entry[0]] = [entry]
        return dictionary


    def testPotentialToKihonkei(self, yomi, word):
        if word in self.potentialToKihonkei:
            potential = self.potentialToKihonkei[word]
            return  potential[1], potential[0];
        return yomi, word;

    def testConditionalYomi(self, yomi, word, prevW, nextW):
        if word in self.conditionalYomi:
            return self.getConditionalYomi(word, yomi, prevW, nextW)
        return yomi, False;
    
    def testAdjustedDict(self, word):
        if word in self.adjustedDict:
            return self.adjustedDict[word]
        return word

    def testNumber(self, wordType, word):
        if wordType == u'数' and re.match(u'^[0123456789０１２３４５６７８９]+$', word, re.UNICODE):
            return True
        return False

    def testReadingOnlyDict(self, word):
        if word in self.readingOnlyDict:
                return self.readingOnlyDict[word]
        return False

    def testExceptionDict(self, yomi, word):
        if word in self.exceptionDict:
                yomi = self.exceptionDict[word]
                return yomi, True;
        return yomi, False;

    def testSuffixCounterDict(self, word, prevW):
        if len(prevW) > 2:
            if prevW[2] == u'数' and word in self.counterDict:
                yomi = self.counterDict[word]
                if yomi:
                    return self.counterDict[word], True;
                else: 
                    return False, True;
            if prevW[1] == u'名詞' and prevW[0] != '=--' and word in self.suffixDict:
                return self.suffixDict[word], True;
        return False, False

    def initSearch(self, word, prevW = False, nextW = False, getAudio = False, getGraph = False, wordType = False, specifiedReading = False):
        word = self.convertNumbers(word)
        yomi = specifiedReading
        yomi, word = self.testPotentialToKihonkei(yomi, word)
        yomi, returnNow =  self.testConditionalYomi(yomi, word, prevW, nextW)
        if returnNow:
            return yomi, False, False, False
        if not yomi:
            word = self.testAdjustedDict(word)
            if self.testNumber(wordType, word):
                return False, False, False, False; 
            word = self.convertNumToFullWidth(word)
            if self.singleKana(word):
                return False, False, False, False;
            readingOnly = self.testReadingOnlyDict(word)
            if readingOnly:
                return readingOnly, False, False, False; 
            yomi, exceptionFound = self.testExceptionDict(yomi, word)
            if not yomi and exceptionFound:
                return False, False, False, False; 
            if prevW:
                suffixCounter, suffixCounterFound = self.testSuffixCounterDict(word, prevW)
                if suffixCounter and suffixCounterFound:
                    return suffixCounter, False, False, False;
                elif suffixCounterFound:
                    return False, False, False, False;
        return self.performLookup(word, yomi, getAudio, getGraph)
        
    def performLookup(self, word, yomi, getAudio, getGraph):
        foundCount = 0
        desired = 1
        if word in self.sameYomiDifferentAccent:
            desired = self.sameYomiDifferentAccent[word]
        if word in self.dictionary:
            entries = self.dictionary[word]
            for term in entries:
                foundCount += 1
                if yomi:
                    if yomi == term[1]:
                        return term[1], term[6], term[5], self.getExtraList(getAudio, term[4], getGraph, term[2]);
                    continue
                elif desired == foundCount:
                    return term[1], term[6], term[5], self.getExtraList(getAudio, term[4], getGraph, term[2]);
        return False, False, False, False; 


    def getConditionalYomi(self, word, yomi, prevW, nextW):
        condYomiDict = self.conditionalYomi[word]
        allGo = False
        if 'prev' in condYomiDict:
            if prevW and prevW[0] in condYomiDict['prev']:
                allGo = True
            else:
                allGo = False
        if 'pType' in condYomiDict:
            if prevW and prevW[1] in condYomiDict['pType']:
                allGo = True
            else:
                allGo = False
        if 'next' in condYomiDict:
            if nextW and nextW[0] in condYomiDict['next']:
                allGo = True
            else:
                allGo = False
        if 'nType' in condYomiDict:
            if nextW and nextW[1] in condYomiDict['nType']:
                allGo = True
            else:
                allGo = False
        if allGo:
            return condYomiDict['yomi'], condYomiDict['return'];
        return yomi, False;

    def convertNumbers(self, text):
        halfMonths = [u'11月',u'12月',u'1月',u'2月',u'3月', u'4月',u'5月',u'6月',u'7月',u'8月',u'9月',u'10月']
        fullMonths = [u"１１月", u"１２月", u"１月" , u"２月" , u"３月" , u"４月" , u"５月" , u"６月" , u"７月" , u"８月" , u"９月", u"１０月"]
        kanjiMonths = [u"十一月", u"十二月",u"一月" , u"二月" , u"三月" , u"四月" , u"五月" , u"六月" , u"七月" , u"八月" , u"九月" , u"十月"]
        for idx, val in enumerate(halfMonths):
            if val in text:
                text = text.replace(val, kanjiMonths[idx])

        for idx, val in enumerate(fullMonths):
            if val in text:
                text = text.replace(val, kanjiMonths[idx])
        return text

    def getExtraList(self, audio, aL, graph, gL):
        extraList = []
        if not audio and not gL:
            return False
        if audio and aL:
            extraList.append(aL)
        else:
            extraList.append(False)
        if graph and gL:
            extraList.append(gL)
        else:
            extraList.append(False)
        return extraList

    def convertNumToFullWidth(self, text):
        fullWidth = '０１２３４５６７８９'
        halfWidth = '0123456789'
        halfWidth = [ord(char) for char in halfWidth]
        translate_table = dict(zip(halfWidth, fullWidth))
        return text.translate(translate_table)

    def singleKana(self, word):
        if len(word)  == 1:
            if word in self.hiraganaChart or word in self.katakanaChart:
                return True
        return False

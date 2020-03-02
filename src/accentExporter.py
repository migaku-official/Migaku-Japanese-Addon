# -*- coding: utf-8 -*-
# 
import re
from . import Pyperclip 
import json
from os.path import join, exists
from shutil import copyfile
from aqt.addcards import AddCards
from aqt.utils import  showInfo
from . import reading 
from .constants import *

class AccentDictionaryParser:
    def  __init__(self, exporter, UEManager, adjustVerbs, separateWord, separateVerbPhrase, ignoreVerbs, dontCombineDict, skipList, parseWithMecab, verbToNoun):
        self.exporter = exporter
        self.adjustVerbs = adjustVerbs
        self.separateWord = separateWord
        self.separateVerbPhrase = separateVerbPhrase
        self.mecabAccents = reading.MecabController()
        self.ueMng = UEManager
        self.dictionary = self.exporter.dictionary
        self.mecabReading = reading.MecabController()
        self.verbToNoun = verbToNoun
        self.ignoreVerbs = ignoreVerbs
        self.dontCombineDict = dontCombineDict
        self.skipList = skipList
        self.parseWithMecab = parseWithMecab
        self.verbToNoun = verbToNoun


    def kaner(self, to_translate, hiraganer = False):
        hiragana = u"がぎぐげござじずぜぞだぢづでどばびぶべぼぱぴぷぺぽ" \
                   u"あいうえおかきくけこさしすせそたちつてと" \
                   u"なにぬねのはひふへほまみむめもやゆよらりるれろ" \
                   u"わをんぁぃぅぇぉゃゅょっゐゑ"
        katakana = u"ガギグゲゴザジズゼゾダヂヅデドバビブベボパピプペポ" \
                   u"アイウエオカキクケコサシスセソタチツテト" \
                   u"ナニヌネノハヒフヘホマミムメモヤユヨラリルレロ" \
                   u"ワヲンァィゥェォャュョッヰヱ"
        if hiraganer:
            katakana = [ord(char) for char in katakana]
            translate_table = dict(zip(katakana, hiragana))
            return to_translate.translate(translate_table)
        else:
            hiragana = [ord(char) for char in hiragana]
            translate_table = dict(zip(hiragana, katakana))
            return to_translate.translate(translate_table) 
        
    def generateReadings(self, text):
        text = self.dictionary.convertNumbers(self.exporter.removeBrackets(text))        
        try:     
            if not self.mecabReading:
                self.mecabReading = reading.MecabController()
            text = self.mecabReading.reading(text)        
            return text           
        except Exception as e:
            self.mecabReading = None
            raise
    
    def getParsed(self, text):
        try:
            if not self.mecabAccents:
                self.mecabAccents = reading.MecabController()
            results = self.mecabAccents.accents(text)
            return results
        except Exception as e:
                self.mecabAccents = None
                raise 
     
    def verbCombiner(self, word, results, idx):
        if len(results[idx]) > 1:
            hinshi = results[idx][1]
            while True:
                idx += 1
                if idx == len(results):
                    break
                if len(results[idx]) < 3:
                    return word, idx
                if (hinshi == u'形容詞' and results[idx][0] == u'さ'
                ) or (results[idx][1] == u"助動詞" or results[idx][1] == u"助詞" or (results[idx][1] == u"動詞" and results[idx][0] in [ u'させ',u'られ',u'られる', u'られ', u'れる', u'れ', u'せ', u'せる', u'させる'])) and u"格助詞" != results[idx][2] and results[idx][0] not in  [u'か',u'よ',u'から', u'ので', u'の', u'が', u'だろ']: 
                    word += results[idx][0]
                else:
                    break
        return word, idx;

    def separateVerbPhraseEditor(self, results, idx):
        data = self.separateVerbPhrase[results[idx][7]]
        verbPhrase = results[idx][0]
        for altCount,alternate in enumerate(data):
            verbPhrase = verbPhrase[len(alternate):]
            if altCount == 0:
                results[idx] = self.exporter.wordData(self.getParsed(alternate))[0]
            else:
                results.insert( idx + altCount, self.exporter.wordData(self.getParsed(alternate))[0])
        startIdx = idx + altCount 
        verbPhrase, endIdx  = self.verbCombiner(verbPhrase, results, startIdx)
        verbList = self.exporter.wordData(self.getParsed(verbPhrase))
        for vCount in reversed(range(startIdx+ 1 , endIdx)):
            del results[vCount]
        for v in reversed(verbList):
            results.insert(startIdx + 1, v)
        return results

    def separateWordEditor(self, results, idx):
        data = self.separateWord[results[idx][0]]
        for altCount,alternate in enumerate(data):
            if altCount == 0:
                results[idx] = self.exporter.wordData(self.getParsed(alternate))[0]
            else:
                results.insert( idx + altCount, self.exporter.wordData(self.getParsed(alternate))[0])
        return results

    def checkJyodoushi(self, word, type):
        if word == 'ござい' and type == '助動詞':
            return True
        return False 

    def baseYomi(self, tango, yomi):
        loc = 0
        pitches = ''
        loc = 0
        furigana = yomi
        for c in reversed(yomi):
            if tango[-(loc+1): len(tango) - loc] == c:
                furigana =  furigana[:-1]
                loc += 1
            else:
                break
        if loc == 0:
            return False
        else:  
            return furigana 

    def checkMode(self, mode, text):
        if not mode or text == ';':
            return ''
        return text

    def okuriganer(self, text):
        yomi = re.search( r'\[(.+)\]', text)
        tango = re.search(r'(.+?)\[', text)
        loc = 0
        if yomi and tango:
            yomi = yomi.group(1)
            tango = tango.group(1)
            pitches = ''
            if ';' in yomi:
                yomi, pitches = yomi.split(";")
                pitches = ';' + pitches
            yomi2 = ''
            if ','  in yomi:
                yomi, yomi2 = yomi.split(',')
                yomi2 = ',' + yomi2
            loc = 0
            furigana = yomi
            for c in reversed(yomi):
                if tango[-(loc+1): len(tango) - loc] == c:
                    furigana =  furigana[:-1]
                    loc += 1
                else:
                    break
        if loc == 0:
            return text
        else:  
            return tango[:-loc] + '[' + furigana + yomi2 + pitches + ']' + tango[-loc:] 

    def getPitches(self, array, nums, verbAdj = False):
        pitches = []
        outC = 0
        if not array:
            return ''      
        for val in array:
            inC = 0
            indPitch  = ''
            for pitch in val:
                if pitch == u"頭高":
                    if verbAdj:
                        indPitch += 'k' + str(nums[outC][inC])
                    else:
                        indPitch += 'a'
                elif pitch == u"中高":
                    if verbAdj:
                        indPitch += 'k' + str(nums[outC][inC])
                    else:
                        indPitch += 'n' + str(nums[outC][inC])
                elif pitch == u"尾高":
                        indPitch += 'o'
                elif pitch == u"平板":
                        indPitch += 'h'
                inC +=1
            pitches.append(indPitch)
            outC += 1
        return ','.join(pitches)


    def checkNextWord(self, word, words, index):
        if  len(words) > index:
            if word[2] == u'数' and words[index][0] in [u'時間',u'時半']:
                return True
            if word[0] in self.dontCombineDict:
                allFound = False
                for noComboWord in self.dontCombineDict[word[0]]:
                  if len(words) <= index:
                    return False
                  if noComboWord == words[index][0]:
                    allFound =  True
                  else:
                    allFound = False
                  index += 1  
                return allFound
        return False

    def getExceptionAccents(self, word, words, idx, audioMode, graphMode, wordType):
        prevW = False
        nextW = False
        if idx > 0:
            prevW = words[idx - 1]
        if len(words) > idx + 1:
            nextW = words[idx + 1]
        yomi, pitches, pitchNumAr, self.audioGraph = self.dictionary.initSearch(word[0], prevW, nextW, audioMode, graphMode, wordType)
        if yomi:
            return word[0], [idx, 0, yomi, pitches, pitchNumAr, self.audioGraph];  
        else:
            return False, [idx];

    def checkCompound(self, idx, word, words, audioMode, graphMode, wordType, specifiedReading):
        og = idx
        if word[1] == u'記号' or word[1] == u'助詞' or word[0] in self.skipList: 
            return False, [og];
        if self.checkNextWord(word, words, idx + 1):
            return self.getExceptionAccents(word, words, idx, audioMode, graphMode, wordType)
        combo = ''
        combined = []
        found = False
        removed = 0
        for x in range(3, 0, -1):
            if len(words) > x + idx -1:
                combined.append(words[x+idx-1][0])
                combo = words[x+idx-1][0] + combo
        while not found or len(combo) > 0:
                if combined[0] == '':
                    combined.pop(0)
                    removed = 0
                    if len(combined) == 0:
                       return False, [og];
                prevW = False
                nextW = False
                if og > 0:
                    prevW = words[og -1]
                if idx + len(combined) + 1 < len(words):
                    nextW = words[idx + len(combined)]
                if combo in self.parseWithMecab:
                    return False, [og];
                yomi, pitches, pitchNumAr, self.audioGraph = self.dictionary.initSearch(combo, prevW, nextW, audioMode, graphMode, wordType, self.specifiedReading)
                if yomi:
                    found = True
                    return combo, [idx + len(combined), removed, yomi, pitches, pitchNumAr, self.audioGraph];  
                else:
                    combo = combo[:-1] 
                    combined[0] = combined[0][:-1]
                    removed += 1                 
        return False, [og];

    def cleanWrongYomi(self, word):
        wrongYomiDict = {u'剃[す]り': u'剃[そ]り'}
        for key in wrongYomiDict:
            if key in word:
                word = word.replace(key, wrongYomiDict[key])
        return word

    def getKanaDictPitch(self, individual = True):
        config =  self.exporter.getConfig();
        optList = config["Group:Kana;DictForm;Pitch;Audio;Graphs"].split(';')
        if individual:
            optList = config["Individual:Kana;DictForm;Pitch;Audio;Graphs"].split(';')
        finalList = []
        for opt in optList:
            if opt == 'on':
                finalList.append(True)
            else:
                finalList.append(False)
        return finalList

    def noBracketsNoSpaces(self, text):
        if '[' not in text:
            return text.replace(' ' , '')
        return text


    def checkSeparation(self):
        if self.results[self.idx][0] in self.separateWord:
            self.results = self.separateWordEditor(self.results, self.idx)
        elif len(self.results[self.idx]) > 6 and self.results[self.idx][7] in self.separateVerbPhrase:
            self.results = self.separateVerbPhraseEditor(self.results, self.idx)
        if len(self.results) > self.idx + 1 and self.results[self.idx][0] in self.verbToNoun and self.results[self.idx + 1][0] == self.verbToNoun[self.results[self.idx][0]] :
            self.results[self.idx][1] = '名詞'    


    def getPrevWNextW(self):
        prevW = False
        nextW = False
        if self.idx>0:
            prevW = self.results[self.idx-1]
        if self.idx + 1 < len(self.results):
            nextW = self.results[self.idx+ 1]
        return prevW, nextW;

    def dictBasedParsing(self, results, text, individual = False, configList = False, specifiedReading = False):
        self.results = results
        self.idx = 0
        self.fStr = ''
        self.specifiedReading = specifiedReading
        self.audioGraphList = False
        if configList:
            self.kanaMode, self.dictMode, self.pitchMode, self.audioMode, self.graphMode = configList
        else:
            self.kanaMode, self.dictMode, self.pitchMode, self.audioMode, self.graphMode = self.getKanaDictPitch(individual)
        if (not self.kanaMode and not self.dictMode and not self.pitchMode and not self.audioMode and not self.graphMode ) or len(results) < 1:
            return text, False
        return self.processText(text)


    def checkIgnoreValue(self):
        val = self.val
        if val[0].startswith('input-buffer overflow.'):
            self.idx += 1
            return self.checkProceed()
        if val[0] in 'EOS' or (val[7] == '*' and (val[2] != '数' and val[0] not in [u'此', u'其'])) or val[1] == u'記号' or val[0] in [u'の',u'で',u'た',u'に']:
            if val[0] != 'EOS':
                self.fStr += val[0]
            self.idx += 1
            return self.checkProceed()
        return False

    def checkProceed(self):
        if self.idx == len(self.results):
            return 1
        else:
            return 2

    def checkAdjustedVerbs(self, val):
        vAdjusted = False
        if val[0] in self.adjustVerbs:
            vAdjusted = True
            val[7] = self.adjustVerbs[val[0]]
        if val[0] == u'した':
            baseWord = u''
            val[2] = u"動詞"
        else:    
            baseWord = val[7]
        return val, vAdjusted, baseWord


    def processVerbAdjectives(self):
        val = self.val
        if val[0] == u'した' or (((val[1] == u"動詞" or val[1] == u'形容詞') and val[6] != u"基本形" and val[0] not in self.ignoreVerbs) or self.checkJyodoushi(val[0], val[1])):
            val, vAdjusted, baseWord = self.checkAdjustedVerbs(val)         
            word = val[0]
            word, self.idx = self.verbCombiner(word, self.results, self.idx)
            yomi = False
                
            if not vAdjusted and word[-1:] != u'さ':
                yomi, pitchAr, pitchNumAr, self.audioGraph = self.dictionary.initSearch(word, self.prevW, self.nextW, self.audioMode, self.graphMode, val[2], self.specifiedReading)
            if not yomi:
                yomi, pitchAr, pitchNumAr, self.audioGraph = self.dictionary.initSearch(baseWord, self.prevW, self.nextW, self.audioMode, self.graphMode, val[2], self.specifiedReading)
            if yomi:
                baseReading = self.baseYomi(baseWord, yomi)
                if (self.audioMode or self.graphMode) and self.audioGraph:
                    self.audioGraphList.append(self.audioGraph)
                elif (self.audioMode or self.graphMode):
                    self.audioGraphList.append(False)
                kihonkei = ',' + yomi
                pitches = self.getPitches(pitchAr, pitchNumAr, True)
                if self.kanaMode:
                    word = self.cleanWrongYomi(self.generateReadings(word).replace(' ', ''))
                    if baseReading:
                        word = re.sub(r'\[.+\]', '[' + baseReading + ']', word)
                if '[' not in word:
                    word += '[]'
                self.fStr += ' ' + word.replace(']', self.checkMode(self.dictMode, kihonkei) + self.checkMode(self.pitchMode, ';' + pitches) + ']') + ' '
            else:
                if  self.kanaMode:
                    word = self.generateReadings(word).replace(' ', '')
                else:
                    word += '[]'   
                self.fStr +=  ' ' + word + ' '
            return self.checkProceed()
        return False

    ## a compound has been found but it has split a word that mecab parsed as one word
    # this function deals with the remnant of that word and attempts to find a reading and accent information for it
    def processAlteredWord(self, altered):
        if  self.kanaMode:
            if self.results[self.idx - 1][0][-altered:] in self.dictionary.suffixDict:
                word = self.okuriganer(self.results[self.idx - 1][0][-altered:] + '[' + self.dictionary.suffixDict[self.results[self.idx - 1][0][-altered:]] + ']')
            else:
                word = self.results[self.idx - 1][0][-altered:]
                yomi, pitchAr, pitchNumAr, self.audioGraph = self.dictionary.initSearch(word, False,False,False,False,False, self.specifiedReading)
                if yomi:
                                
                    if (self.audioMode or self.graphMode) and self.audioGraph:
                        self.audioGraphList.append(self.audioGraph)
                    elif (self.audioMode or self.graphMode):
                        self.audioGraphList.append(False)
                    pitches = self.getPitches(pitchAr, pitchNumAr, True) 
                    if re.match(u'^[\u3040-\u309f]+$', word) or re.match(u'^[\u30a0-\u30ff]+$', word):
                        word = word + '[' + self.checkMode(self.pitchMode, ';' + pitches) + ']'
                    else:
                        word = self.okuriganer(word + '[' + yomi + self.checkMode(self.pitchMode, ';' + pitches) + ']')
                else:
                    word = self.okuriganer(self.generateReadings(word))
        else:
            word = self.results[self.idx - 1][0][-altered:]
        self.fStr += ' ' + word + ' '


    def processCompoundWord(self, compound, compAr):
        val = self.val
        if compAr[5]:
            self.audioGraph = compAr[5]
        kihonkei = ''
        if (val[1] == u"動詞" or val[1] == u'形容詞') and val[0] not in self.ignoreVerbs:
            kihonkei = ',' + self.kaner(val[8], True)
            pitches = self.getPitches(compAr[3], compAr[4], True)
            if val[0] in self.dictionary.potentialToKihonkei:
                compAr[2] = self.dictionary.potentialToKihonkei[val[0]][2]
        else:
            pitches = self.getPitches(compAr[3], compAr[4])
        if re.match(u'^[\u3040-\u309f]+$', compound) or re.match(u'^[\u30a0-\u30ff]+$', compound):
            self.fStr += ' ' + self.okuriganer(compound + '['+ self.checkMode(self.dictMode, kihonkei) + self.checkMode(self.pitchMode, ';' + pitches) + ']') + ' '
        else:
            if  self.kanaMode:
                word = self.okuriganer(compound + '[' + compAr[2] + self.checkMode(self.dictMode, kihonkei) + self.checkMode(self.pitchMode, ';' + pitches) + ']')
            else:
                word = self.okuriganer(compound + '[' + self.checkMode(self.dictMode, kihonkei) + self.checkMode(self.pitchMode, ';' + pitches) + ']')
            self.fStr += ' ' + word  + ' '
        altered = compAr[1]
        if self.idx == compAr[0] and not altered:
            self.idx += 1
        else:
            self.idx = compAr[0]
        if altered:
            self.processAlteredWord(altered)


    def processWord(self):
        val = self.val
        if val[1] == u'記号' or val[1] == u'助詞' or re.match(u'^[\u3040-\u309f]+$', val[0]) or re.match(u'^[\u30a0-\u30ff]+$', val[0]) :
            self.fStr += ' ' +  val[0] + ' '
        else:
            if self.kanaMode and len(val) > 8 and val[0] not in '０１２３４５６７８９':
                word = self.okuriganer(val[0] + '[' + self.kaner(val[8] ,True) + ']')
            else:
                word = val[0]
            self.fStr += ' ' + word + ' '
        self.idx += 1

    def attemptProcessCompoundWord(self):
        compound, compAr = self.checkCompound(self.idx, self.val, self.results, self.audioMode, self.graphMode, self.val[2], self.specifiedReading)
        if compound:
            self.processCompoundWord(compound, compAr)
        else:
            self.processWord()

    def processText(self, text):
        
        if self.audioMode or self.graphMode:
            self.audioGraphList = []
        while True:
            self.audioGraph = False
            self.checkSeparation()
            self.val = self.results[self.idx]
            self.prevW, self.nextW = self.getPrevWNextW()
            proceed = self.checkIgnoreValue()

            if proceed == 1:
                break
            elif proceed == 2:
                continue
            proceed = self.processVerbAdjectives()
            if proceed == 1:
                break
            elif proceed == 2:
                continue
            proceed = self.attemptProcessCompoundWord()
            if (self.audioMode or self.graphMode) and self.audioGraph:
                self.audioGraphList.append(self.audioGraph)
            elif (self.audioMode or self.graphMode):
                self.audioGraphList.append(False)
            if self.idx == len(self.results):
                break
        if not self.kanaMode and not self.dictMode and not self.pitchMode:
            return text, self.audioGraphList;
        else: 
            return self.ueMng.applyRulesToText(self.noBracketsNoSpaces(self.fStr.replace('[]', '').replace(',]', ']').replace('  ', ' '))), self.audioGraphList;

class AccentExporter:
    def  __init__(self, mw, aqt, UEManager, dictionary,  addon_path, adjustVerbs, separateWord, separateVerbPhrase, ignoreVerbs, dontCombineDict, skipList, parseWithMecab, verbToNoun):
        self.mw = mw
        self.aqt = aqt
        self.dictionary = dictionary
        self.addon_path = addon_path
        self.dictParser = AccentDictionaryParser(self, UEManager, adjustVerbs, separateWord, separateVerbPhrase, ignoreVerbs, dontCombineDict, skipList, parseWithMecab, verbToNoun)
        self.commonJS = self.getCommonJS()
        self.insertHTMLJS = self.getInsertHTMLJS()
        self.insertToFieldJS = self.getInsertToFieldJS()
        self.fetchIndividualJS = self.getFetchIndividualJS()
        self.fetchTextJS = self.getFetchTextJS()
        self.bracketsFromSelJS = self.getBracketFromSelJs()
        self.removeBracketsJS = self.getRemoveBrackedJS()

    def getCommonJS(self):
        common_utils_path = join(self.addon_path, "js", "common.js")
        with open(common_utils_path, "r") as common_utils_file:
            return common_utils_file.read()

    def getInsertToFieldJS(self):
        insertHTML = join(self.addon_path, "js", "insertHTMLToField.js")
        with open(insertHTML, "r", encoding="utf-8") as insertHTMLFile:
            return insertHTMLFile.read() 

    def getInsertHTMLJS(self):
        insertHTML = join(self.addon_path, "js", "insertHTML.js")
        with open(insertHTML, "r", encoding="utf-8") as insertHTMLFile:
            return insertHTMLFile.read() 

    def getFetchIndividualJS(self):
        fetchIndividual = join(self.addon_path, "js", "fetchIndividual.js")
        with open(fetchIndividual, "r", encoding="utf-8") as fetchIndividualFile:
            return fetchIndividualFile.read()    

    def getFetchTextJS(self):
        fetchText = join(self.addon_path, "js", "fetchText.js")
        with open(fetchText, "r") as fetchTextFile:
            return fetchTextFile.read()   

    def getBracketFromSelJs(self):
        bracketsFromSel = join(self.addon_path, "js", "bracketsFromSel.js")
        with open(bracketsFromSel, "r") as bracketsFromSelFile:
            return bracketsFromSelFile.read()

    def getRemoveBrackedJS(self):    
        removeBrackets = join(self.addon_path, "js", "removeBrackets.js")
        with open(removeBrackets, "r") as removeBracketsFile:
            return removeBracketsFile.read()

    def individualExport(self, editor):
        editor.web.eval(self.commonJS + self.fetchIndividualJS)

    def groupExport(self, editor):
        editor.web.eval(self.commonJS + self.fetchTextJS)

    def editorText(self, editor):    
        text = editor.web.selectedText()
        if not text:
            return False
        else:
            return text

    def cleanField(self, editor):
        if self.editorText(editor):
            editor.web.eval(self.commonJS + self.bracketsFromSelJS)
        else:
            editor.web.eval(self.commonJS + self.removeBracketsJS)

    def reloadEditor(self):
        browser = self.aqt.DialogManager._dialogs["Browser"][1]
        if browser:
            self.mw.progress.timer(100, browser.editor.loadNoteKeepingFocus, False)
        adder = self.aqt.DialogManager._dialogs["AddCards"][1]
        if adder:
            self.mw.progress.timer(100, adder.editor.loadNoteKeepingFocus, False)
        editCurrent = self.aqt.DialogManager._dialogs["EditCurrent"][1]
        if editCurrent:
            self.mw.progress.timer(100, editCurrent.editor.loadNoteKeepingFocus, False)


    def convertMalformedSpaces(self, text):
        return re.sub(r'& ?nbsp ?;', ' ', text)

    def finalizeGroupExport(self, editor, text, field, note):
        if note and field:
            # if type(editor.parentWindow) is not AddCards:
                # self.mw.checkpoint('Sentence Accent Generation')
            newText = text
            htmlFinds, text = self.htmlRemove(text)
            text, sounds = self.removeBrackets(text, True)
            text, invalids = self.replaceInvalidChars(text)
            text = self.mw.col.media.strip(text)
            results = self.dictParser.getParsed(text)
            results = self.wordData(results)
            text, audioGraphList = self.dictParser.dictBasedParsing(results, newText)   
            if htmlFinds:
                text = self.replaceHTML(text, htmlFinds)
            for match in sounds:
                text = text.replace(AUDIO_REPLACER, match, 1)
            if text:
                text = self.returnInvalids(text, invalids)
                newHTML = self.convertMalformedSpaces(text).strip()
                editor.web.eval(self.commonJS + self.insertHTMLJS % newHTML.replace('"', '\\"'))
            if audioGraphList:
                self.addVariants(audioGraphList, note, editor)      
                # note.flush() 
                # self.reloadEditor()

    def fetchParsedField(self, text, note):
            newText = text
            newHTML = text
            text = text.replace('</div> <div>', '</div><div>')
            htmlFinds, text = self.htmlRemove(text)
            text, sounds = self.removeBrackets(text, True)
            text = text.replace(',&', '-co-am-')
            text, invalids = self.replaceInvalidChars(text)
            text = self.mw.col.media.strip(text)
            results = self.dictParser.getParsed(text)        
            results = self.wordData(results)
            text, audioGraphList = self.dictParser.dictBasedParsing(results, newText)   
            if htmlFinds:
                text = self.replaceHTML(text, htmlFinds)
            for match in sounds:
                text = text.replace(AUDIO_REPLACER, match, 1)
            if text:
                text = self.returnInvalids(text, invalids)
                newHTML = text.replace('-co-am-', ',&').strip()
                
            if audioGraphList:
                self.addVariants(audioGraphList, note)
            return newHTML
            

    def returnEntities(self, text):
        return text.replace('◱', '&ensp;').replace('◲', '&lt;').replace('◳','&gt;').replace('◴', '&amp;')

    def cleanEntities(self, text):
        return text.replace('&ensp;', '◱').replace('&lt;','◲').replace('&gt;','◳').replace('&amp;','◴')

    def parseYomi(self, yomi):
        if ';' in yomi:
            yomi = yomi.split(';')[0]
        if ',' in yomi:
            yomi = yomi.split(',')[1]
        return yomi

    def finalizeIndividualExport(self, editor, text, field, note):
        if not note or not field or text == '':
            return
        text = self.cleanEntities(text)
        rawString = re.search(r'--IND--.+--IND--', text)
        if not rawString:
            config = self.getConfig()
            lookAhead = str(config['LookAhead'])
            rawString = re.search(r'--IND--.{1,' + lookAhead + r'}', text)
        if not rawString:
            return
        rawString = rawString.group().replace('--IND--', '')
        subString = re.search(u'[^　\s◱◲◳◴<>]+', rawString).group()
        yomi = re.search(r'\[a([^\]]+)\]', subString)
        if yomi:
            yomi = self.parseYomi(yomi.group(1))
        ogString = subString
        subString = re.sub(r'\[[^\]]+\]', '', subString)
        newText = subString
        newText = self.mw.col.media.strip(newText)
        results = self.dictParser.getParsed(newText)
        results = self.wordData(results)
        parsed, audioGraphList = self.dictParser.dictBasedParsing(results, subString, True, False, yomi)
        if audioGraphList:
            audioGraphList = [audioGraphList[0]]
        else:
            audioGraphList = False
        if parsed:
            parsed = parsed.split(' ')
            if len(parsed) > 1 and "[" in parsed[1]:
                parsed = parsed[1]
                if parsed != ogString:
                    if yomi:
                        if ';' in parsed:
                            parsed = re.search(r'\[[^\[\]]*(;[^\[\]]*\])', parsed).group(1)
                        newHTML = self.returnEntities(text.replace(rawString, rawString.replace(ogString, re.sub(r';[^\[\]]*\]' , parsed , ogString.replace('[a' , '['))))).replace('--IND--', '')
                    elif parsed in rawString:
                        newHTML = self.returnEntities(text.replace(rawString, rawString.replace(parsed, ' ' + parsed + ' '))).replace('--IND--', '')
                    else:
                        newHTML = self.returnEntities(text.replace(rawString, rawString.replace(re.sub(r'\[.*\]', '', parsed), ' ' + parsed + ' '))).replace('--IND--', '')
                    editor.web.eval(self.commonJS + self.insertHTMLJS % self.convertMalformedSpaces(newHTML).replace('"', '\\"'))
        if audioGraphList:
            self.addVariants(audioGraphList, note, editor)      
            # self.reloadEditor()

    def fetchIndividualExport(self, text, note):
        ogtext = text.replace('--IND--', '')
        if not note or text == '':
            return ''
        text = self.cleanEntities(text)
        rawString = re.search(r'--IND--.+--IND--', text)
        if not rawString:
            config = self.getConfig()
            lookAhead = str(config['LookAhead'])
            rawString = re.search(r'--IND--.{1,' + lookAhead + r'}', text)
        if not rawString:
            return ogtext
        rawString = rawString.group().replace('--IND--', '')
        subString = re.search(u'[^　\s◱◲◳◴<>]+', rawString).group()
        yomi = re.search(r'\[a([^\]]+)\]', subString)
        if yomi:
            yomi = self.parseYomi(yomi.group(1))
        ogString = subString
        subString = re.sub(r'\[[^\]]+\]', '', subString)
        newText = subString
        newText = self.mw.col.media.strip(newText)
        results = self.dictParser.getParsed(newText)
        results = self.wordData(results)
        parsed, audioGraphList = self.dictParser.dictBasedParsing(results, subString, True, False, yomi)
        if audioGraphList:
            audioGraphList = [audioGraphList[0]]
        else:
            audioGraphList = False
        if audioGraphList:
            self.addVariants(audioGraphList, note)
        textToReturn = ogtext
        if parsed:
            parsed = parsed.split(' ')
            if len(parsed) > 1 and "[" in parsed[1]:
                parsed = parsed[1]
                if parsed != ogString:
                    if yomi:
                        if ';' in parsed:
                            parsed = re.search(r'\[[^\[\]]*(;[^\[\]]*\])', parsed).group(1)
                        newHTML = self.returnEntities(text.replace(rawString, rawString.replace(ogString, re.sub(r';[^\[\]]*\]' , parsed , ogString.replace('[a' , '['))))).replace('--IND--', '')
                    elif parsed in rawString:
                        newHTML = self.returnEntities(text.replace(rawString, rawString.replace(parsed, ' ' + parsed + ' '))).replace('--IND--', '')
                    else:
                        newHTML = self.returnEntities(text.replace(rawString, rawString.replace(re.sub(r'\[.*\]', '', parsed), ' ' + parsed + ' '))).replace('--IND--', '')
                    
                    textToReturn = newHTML
        return textToReturn
              
    def wordData(self, results):
        wordResults = []
        for idx, val in enumerate(results):
            word, rest = val.split('\t', 1)
            wordList = []
            wordList.append(word)
            wordList+= rest.split(',')
            wordResults.append(wordList)
        return wordResults

    def replaceInvalidChars(self, text):
        invalids = []
        replaced = ''
        for char in text:
            if char.encode("utf-8", "ignore").decode('utf-8') == '':
                replaced += '□'
                invalids.append(char)
            else:
                replaced += char
        return replaced, invalids;

    def returnInvalids(self, text, invalids):
        if len(invalids) > 0:
            for i in invalids:
                text = text.replace('□', i, 1)
            return text
        else:
            return text

    def htmlRemove(self, text):
        pattern = r"(?:<[^<]+?>)"
        finds = re.findall(pattern, text)
        text = re.sub(r"<[^<]+?>", HTML_REPLACER, text)
        return finds,text;

    def replaceHTML(self, text, matches):
        if matches:
            for match in matches:
                text = text.replace(HTML_REPLACER, match, 1)
        return text

    def cleanSpaces(self, text):
        pattern  = r'[À-ÿA-Za-z:,.;()。0-9]+\s[À-ÿA-Za-z,.:;()。0-9]+\s*'
        finds = re.findall(pattern, text)
        if finds:
            for find in finds:
                text = text.replace(find, find.replace(' ', '&ensp;'), 1)
        return text.replace(' ', '')

    def removeBrackets(self, text, returnSounds = False, removeAudio = False):
        matches, text = self.htmlRemove(text)
        if '[' not in text and ']' not in text:
            text = self.replaceHTML(text.replace(' ', '&ensp;'), matches)
            if returnSounds:
                return text, [];
            return text
        elif ('[sound:' in text or re.search(r'\[\d', text)) and not re.search(r'\[[^s\d]', text):     
            text = self.replaceHTML(text.replace(' ', '&ensp;'), matches)
            if returnSounds:
                pattern = r"(?:\[sound:[^\]]+?\])|(?:\[\d*\])"
                finds = re.findall(pattern, text)
                text = re.sub(r"(?:\[sound:[^\]]+?\])|(?:\[\d*\])", AUDIO_REPLACER, text)
                return text, finds;
            return text
        if removeAudio:
            text = self.cleanSpaces(text)
            text = self.replaceHTML(text, matches)
            return re.sub(r'\[[^]]*?\]', '', text)
        else:
            pattern = r"(?:\[sound:[^\]]+?\])|(?:\[\d*\])"
            finds = re.findall(pattern, text)
            text = re.sub(r"(?:\[sound:[^\]]+?\])|(?:\[\d*\])", AUDIO_REPLACER, text)
            text  = re.sub(r'\[[^]]*?\]', '', text)
            text = self.cleanSpaces(text)
            text = self.replaceHTML(text, matches)
            if returnSounds:
                return text, finds;
            for match in finds:
                text = text.replace(AUDIO_REPLACER, match, 1)
            return text

    def getConfig(self):
        return self.mw.addonManager.getConfig(__name__)

    def addVariants(self, audioGraphs, note, editor = False): 
        config = self.getConfig()
        audioCon = config['AudioFields'].split(';')
        graphCon = config['PitchGraphFields'].split(';')
        fields = self.mw.col.models.fieldNames(note.model())
        aFields = audioCon[0].split(',')
        gFields = graphCon[0].split(',')
        aSep = '<br>'
        gSep = '<br>'
        if len(audioCon) == 3:
            aSep = audioCon[2]
        if len(graphCon) == 3:
            gSep = graphCon[2]
        for aField in aFields:
            if self.dictParser.graphMode and aField in gFields and (aField in fields or aField.lower() == 'clipboard'):
                text = self.writeAudioGraphsText(audioGraphs, note, aField, graphCon[1], gSep, 2, editor)
            else:
                if aField in fields or aField.lower() == 'clipboard':
                    text = self.writeAudioGraphsText(audioGraphs, note, aField, audioCon[1], aSep, 0, editor)
        for gField in gFields:
            if (gField in fields or gField.lower() == 'clipboard') and gField not in aFields:
                text = self.writeAudioGraphsText(audioGraphs, note, gField, graphCon[1], gSep, 1, editor)

    def getFieldOrdinal(self, note, field):
        fields = note._model["flds"]
        for f in fields:
            if field == f['name']:
                return f['ord']
        else:
            return False
        


    def writeAudioGraphsText(self, audioGraphs, note, field, overAdd, sep, which, editor):
        text = ''
        ordinal = False
        if editor:
            ordinal = self.getFieldOrdinal(note, field)
        if not audioGraphs or len(audioGraphs) == 0:
            return
        for idx, val in enumerate(audioGraphs):
            if not val:
                continue
            if which == 2:
                if val[1] or val[0]:                   
                    if val[1]:
                        text = self.addToText(text, idx, val[1], sep)
                    if val[0]:
                        for sound in val[0]:
                            text =  self.addToText(text, idx, sound[2], False, True)
            elif which == 1:
                if val[1]:
                    text = self.addToText(text, idx, val[1],sep)
            elif which == 0:
                if val[0]:
                    for sound in val[0]:
                        if sound[2] not in text:
                            text =  self.addToText(text, idx, sound[2], sep, True)
        if text == '':
            return
        if field.lower() == 'clipboard':
            Pyperclip.copy(sep.replace('<br>', '', 1) + text)
        elif overAdd == 'overwrite':
            self.addToNote(editor, note, field, ordinal, sep.replace('<br>', '', 1) + text)
        elif overAdd == 'add':
            if note[field] in ['', '<br>'] or editor:
                self.addToNote(editor, note, field, ordinal, note[field] + sep.replace('<br>', '', 1) + text)
            else:
                self.addToNote(editor, note, field, ordinal, note[field] + sep + text)
        elif overAdd == 'no':
            if note[field] == ['', '<br>']:
                self.addToNote(editor, note, field, ordinal, sep.replace('<br>', '', 1) + text)

    def addToNote(self, editor, note, field, ordinal, text):
        if text.startswith('<br>'):
            text = text[4:]
        if ordinal is not False and editor is not False:
            editor.web.eval(self.commonJS + self.insertToFieldJS % (text.replace('"', '\\"'), str(ordinal)))
        else:
            note[field] = text



    def addToText(self, text, idx, val, sep = False, audio = False):
        if val not in text:
            if text != '' and sep:
                text += sep
            if audio:
                text += '[sound:' + val + ']'
                self.moveAudioToMediaDir(val)
            else:
                text += val
        return text

    def moveAudioToMediaDir(self, filename):
        src = join(self.addon_path,"user_files", "accentAudio", filename)
        if exists(src): 
            path = join(self.mw.col.media.dir(), filename)
            if not exists(path): 
                copyfile(src, path)
            return True
        else:
            return False




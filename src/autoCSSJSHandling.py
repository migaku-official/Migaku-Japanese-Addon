# -*- coding: utf-8 -*-
# 
from os.path import join
from .miutils import miInfo, miAsk
import re

class AutoCSSJSHandler:
    def  __init__(self, mw, addon_path):
        self.mw = mw
        self.addon_path = addon_path
        self.wrapperDict = False
        self.jCssHeader = '/*###MIA JAPANESE SUPPORT CSS STARTS###\nDo Not Edit If Using Automatic CSS and JS Management*/'
        self.jCssFooter = '/*###MIA JAPANESE SUPPORT CSS ENDS###*/'
        self.jCssHeaderP = '\/\*###MIA JAPANESE SUPPORT CSS STARTS###\nDo Not Edit If Using Automatic CSS and JS Management\*\/'
        self.jCssFooterP = '\/\*###MIA JAPANESE SUPPORT CSS ENDS###\*\/'
        self.jHistHeader = '<!--###MIA JAPANESE SUPPORT CONVERTER JS START###\nDo Not Edit If Using Automatic CSS and JS Management-->'
        self.jHistFooter = '<!--###MIA JAPANESE SUPPORT CONVERTER JS ENDS###-->'
        self.jJSHeader = '<!--###MIA JAPANESE SUPPORT JS START###\nDo Not Edit If Using Automatic CSS and JS Management-->'
        self.jJSFooter = '<!--###MIA JAPANESE SUPPORT JS ENDS###-->' 
        self.jKHeader = '<!--###MIA JAPANESE SUPPORT KATAKANA CONVERTER JS START###\nDo Not Edit If Using Automatic CSS and JS Management-->'
        self.jKFooter = '<!--###MIA JAPANESE SUPPORT KATAKANA CONVERTER JS ENDS###-->'
        self.formatJapaneseJS = self.getFormatJapaneseJS()
        self.jFormattingFunctionsJS = self.getJFormattingFunctions()

    def getFormatJapaneseJS(self):
        formatJapanese = join(self.addon_path, "js", "formatJapanese.js")
        with open(formatJapanese, "r", encoding="utf-8") as formatJapaneseFile:
            return formatJapaneseFile.read() 

    def getJFormattingFunctions(self):
        jFormattingFunctions = join(self.addon_path, "js", "jFormattingFunctions.js")
        with open(jFormattingFunctions, "r", encoding="utf-8") as jFormattingFunctionsFile:
            return jFormattingFunctionsFile.read() 

    def getConfig(self):
        return self.mw.addonManager.getConfig(__name__)

    def checkProfile(self):
        config = self.getConfig()
        if self.mw.pm.name in config['Profiles'] or ('all' in config['Profiles'] or 'All' in config['Profiles'] or 'ALL' in config['Profiles']):
            return True
        return False     

    def injectWrapperElements(self):
        if not self.checkProfile():
            return
        config = self.getConfig()
        if config["AutoCssJsGeneration"].lower() != 'on':
            return
        variantCheck = self.checkVariantSyntax()
        self.wrapperDict, wrapperCheck = self.getWrapperDict();        
        models = self.mw.col.models.all()
        for model in models:
            if model['name'] in self.wrapperDict:
                model['css'] = self.editJapaneseCss(model['css'])
                for idx, t in enumerate(model['tmpls']):
                    modelDict = self.wrapperDict[model['name']]
                    t = self.injectJapaneseConverterToTemplate(t)
                    if self.templateInModelDict(t['name'], modelDict):
                        templateDict = self.templateFilteredDict(modelDict, t['name'])
                        t['qfmt'], t['afmt'] = self.cleanFieldWrappers(t['qfmt'], t['afmt'], model['flds'], templateDict)
                        for data in templateDict: 
                            if data[2] == 'both' or data[2] == 'front':                              
                                t['qfmt'] =  self.overwriteWrapperElement(t['qfmt'], data[1], data[3])
                                t['qfmt'] =  self.injectWrapperElement(t['qfmt'], data[1], data[3])
                                t['qfmt'] = self.editJapaneseJs(t['qfmt'])
                            if data[2] == 'both' or data[2] == 'back':          
                                t['afmt'] = self.overwriteWrapperElement(t['afmt'], data[1], data[3])
                                t['afmt'] = self.injectWrapperElement(t['afmt'], data[1], data[3])
                                t['afmt'] = self.editJapaneseJs(t['afmt'])
                    else:
                        t['qfmt'] = self.removeJapaneseJs(self.removeWrappers(t['qfmt']))
                        t['afmt'] = self.removeJapaneseJs(self.removeWrappers(t['afmt']))             
            else:
                model['css'] = self.removeJapaneseCss(model['css'])
                for t in model['tmpls']:
                    t = self.removeKanaOldJsFromTemplate(t)
                    t['qfmt'] = self.removeJapaneseJs(self.removeWrappers(t['qfmt']))
                    t['afmt'] = self.removeJapaneseJs(self.removeWrappers(t['afmt']))   
        self.mw.col.models.save()
        self.mw.col.models.flush()
        return variantCheck and wrapperCheck 


    def removeWrappers(self, text):
        pattern = r'<div display-type="[^>]+?" class="wrapped-japanese">({{[^}]+?}})</div>'
        text = re.sub(pattern, r'\1', text)
        return text


    def injectWrapperElement(self, text, field, dType):
        pattern = r'(?<!(?:class="wrapped-japanese">))({{'+ field + r'}})'
        replaceWith = '<div display-type="'+ dType +'" class="wrapped-japanese">{{'+ field + '}}</div>'
        text = re.sub(pattern, replaceWith,text)  
        return text

    def injectJapaneseConverterToTemplate(self, t):
        config = self.getConfig()
        converter = config['HistoricalConversion'].lower()
        kConfig = config['KatakanaConversion'].lower()
        katakana = 'false'
        if converter == "off" and kConfig == "off":
            t = self.removeKanaOldJsFromTemplate(t);       
        if kConfig not in ['on', 'off']:
            miInfo('"KatakanaConversion" has an invalid value in the config. Ensure that its value is either "on" or "off".', level="err")
            return t 
        elif kConfig  == 'on':
            katakana = 'true'        
        if converter not in ['both', 'kanji', 'kana', 'off']:
            miInfo('"HistoricalConversion" has an invalid value in the config. Ensure that its value is one of the following: "both/kanji/kana/off".', level="err")
            return t 
        elif converter in ['both', 'kanji', 'kana']:
            converterJS = self.getHistoricalConverterJs(converter, katakana)
            t['qfmt'] = self.newLineReduce(self.removeKataverterJs(self.removeConverterJs(t['qfmt'])) + '\n\n' + converterJS)
            t['afmt'] = self.newLineReduce(self.removeKataverterJs(self.removeConverterJs(t['afmt'])) + '\n\n' + converterJS)
            return t 
        if katakana == 'true':
            kataverterJS = self.getKataverterJS()
            t['qfmt'] = self.newLineReduce(self.removeKataverterJs(self.removeConverterJs(t['qfmt'])) + '\n\n' + kataverterJS)
            t['afmt'] = self.newLineReduce(self.removeKataverterJs(self.removeConverterJs(t['afmt'])) + '\n\n' + kataverterJS)
        return t 

    def removeKanaOldJsFromTemplate(self, t):
        t['qfmt'] = self.removeConverterJs(t['qfmt'])
        t['afmt'] = self.removeConverterJs(t['afmt'])  
        t['afmt'] = self.removeKataverterJs(t['afmt'])
        t['qfmt'] = self.removeKataverterJs(t['qfmt']) 
        return t              

    def injectJapaneseConverterJs(self):
        config = self.getConfig()
        converter = config['HistoricalConversion'].lower()
        kConfig = config['KatakanaConversion'].lower()
        katakana = 'false'
        if converter == "off" and kConfig == "off":
            self.removeKanaOldJs();       
        if kConfig not in ['on', 'off']:
            miInfo('"KatakanaConversion" has an invalid value in the config. Ensure that its value is either "on" or "off".', level="err")
            return False
        elif kConfig  == 'on':
            katakana = 'true'        
        if converter not in ['both', 'kanji', 'kana', 'off']:
            miInfo('"HistoricalConversion" has an invalid value in the config. Ensure that its value is one of the following: "both/kanji/kana/off".', level="err")
            return False
        elif converter in ['both', 'kanji', 'kana']:
            converterJS = self.getHistoricalConverterJs(converter, katakana)
            models = self.mw.col.models.all()
            for model in models:
                    for t in model['tmpls']:
                        t['qfmt'] = self.newLineReduce(self.removeKataverterJs(self.removeConverterJs(t['qfmt'])) + '\n\n' + converterJS)
                        t['afmt'] = self.newLineReduce(self.removeKataverterJs(self.removeConverterJs(t['afmt'])) + '\n\n' + converterJS)
            self.mw.col.models.save()
            self.mw.col.models.flush()
            return True
        if katakana == 'true':
            kataverterJS = self.getKataverterJS()
            models = self.mw.col.models.all()
            for model in models:
                for t in model['tmpls']:
                    t['qfmt'] = self.newLineReduce(self.removeKataverterJs(self.removeConverterJs(t['qfmt'])) + '\n\n' + kataverterJS)
                    t['afmt'] = self.newLineReduce(self.removeKataverterJs(self.removeConverterJs(t['afmt'])) + '\n\n' + kataverterJS)

    def newLineReduce(self, text):
        return re.sub(r'\n{3,}', '\n\n', text)

    def removeKanaOldJs(self):
        models = self.mw.col.models.all()
        for model in models:
            for t in model['tmpls']:
                t['qfmt'] = self.removeConverterJs(t['qfmt'])
                t['afmt'] = self.removeConverterJs(t['afmt'])  
                t['afmt'] = self.removeKataverterJs(t['afmt'])
                t['qfmt'] = self.removeKataverterJs(t['qfmt'])               
        return True

    def getKataverterJS(self):
        Kataverter = join(self.addon_path, "js", "Kataverter.js")
        with open(Kataverter, "r", encoding="utf-8") as KataverterFile:
            KataverterJS= KataverterFile.read()
        js = self.jKHeader + '<script>' + KataverterJS + '</script>' + self.jKFooter;
        return js


    def removeConverterJs(self, text):
        return re.sub(self.jHistHeader + r'.*?' + self.jHistFooter, '', text)

    def removeKataverterJs(self, text):
        return re.sub(self.jKHeader + r'.*?' + self.jKFooter, '', text)

    def getHistoricalConverterJs(self, conversionType, katakana):    
        converterFunctions = join(self.addon_path, "js", "converterFunctions.js")
        with open(converterFunctions, "r", encoding="utf-8") as converterFunctionsFile:
            converterFunctionsJS= converterFunctionsFile.read()
        kanjiKanaConverter = join(self.addon_path, "js", "kanjiKanaConverter.js")
        with open(kanjiKanaConverter, "r", encoding="utf-8") as kanjiKanaConverterFile:
            kanjiKanaConverterJS = kanjiKanaConverterFile.read()
        js = '<script>' + converterFunctionsJS + '(function(){const OLD_CONVERSION_TYPE ="' + conversionType + '";const ALSO_TO_KATA =' + katakana +';' + kanjiKanaConverterJS + '})();</script>'
        return self.jHistHeader + js + self.jHistFooter

    def checkVariantSyntax(self):
        config = self.getConfig()
        syntaxErrors = ''
        fieldErrors = []
        for variant in ['PitchGraphFields', 'AudioFields']:
            varAr = config[variant].split(';')
            if len(varAr) not in [2,3]:
                syntaxErrors += '\nThe "' + variant + '" configuration "'+ config[variant] +'" is incorrect. The syntax is invalid.'
            else:
                fields =  varAr[0].split(',')
                for field in fields:
                    if field.lower() not in ['clipboard' , 'none', ''] and not self.fieldExists(field):
                        syntaxErrors += '\nThe "' + variant + '" configuration "'+ config[variant] +'" is incorrect. The "' + field + '" field does not exist in your collection.'    
                        fieldErrors.append(field)
                if varAr[1].lower() not in ['overwrite', 'add', 'no']:
                    syntaxErrors += '\nThe "' + variant + '" configuration "'+ config[variant] +'" is incorrect. Please ensure that second value is either "overwrite", "add", or "no".'    
        if syntaxErrors != '':
            if len(fieldErrors) > 0:
                if miAsk('Please make sure the syntax is as follows "field,field;type(;separator)". The syntax is incorrect for the following entries:' + syntaxErrors + '\n\n Would you like to delete these fields from you configuration?'):
                    self.deletePitchAudioFields(fieldErrors, config)
            else:
                miInfo('Please make sure the syntax is as follows "field,field;type(;separator)". The syntax is incorrect for the following entries:' + syntaxErrors, level="err")
            return False
        return True

    def deletePitchAudioFields(self, fields, config):
        for variant in ['PitchGraphFields', 'AudioFields']:
            varAr = config[variant].split(';')
            currentFields = varAr[0].split(',')
            for field in fields:
                if field in currentFields:
                    currentFields.remove(field)
            if len(currentFields) < 1:
                currentFields.append('none')
            config[variant] = ','.join(currentFields) + ';' + varAr[1] 
            if len(varAr) > 2:
                config[variant] += ';' +  varAr[2]
        self.mw.addonManager.writeConfig(__name__, config)
                        

    def fieldExists(self, field):
        models = self.mw.col.models.all()
        for model in models:
            for fld in model['flds']:
                if field == fld['name'] or field.lower() == 'none':
                    return True
        return False

    def getWrapperDict(self):
        wrapperDict = {}   
        displayOptions = ['hover', 'coloredhover','kanji','coloredkanji','reading','coloredreading','kanjireading','coloredkanjireading']
        models = self.mw.col.models.all()
        config = self.getConfig()
        syntaxErrors = ''
        notFoundErrors = ''
        fieldConflictErrors = ''
        displayTypeError = ''
        alreadyIncluded = []
        for item in config['ActiveFields']:
            dataArray = item.split(";")
            displayOption = dataArray[0]
            if len(dataArray) != 6 or  '' in dataArray:
                syntaxErrors += '\n"' + item + '" in "' + displayOption + '"\n'
            elif displayOption.lower() not in displayOptions:
                displayTypeError += '\n"' + item + '" in "ActiveFields" has an incorrect display type of "'+ displayOption +'"\n'
            else:
                if self.mw.pm.name != dataArray[1] and 'all' != dataArray[1].lower():
                    continue
                if dataArray[2] != 'noteTypeName' and dataArray[3] != 'cardTypeName' and dataArray[4] != 'fieldName':
                    success, errorMsg = self.noteCardFieldExists(dataArray)
                    if success:
                        conflictFree,  conflicts = self.fieldConflictCheck(dataArray, alreadyIncluded, displayOption)
                        if conflictFree:
                            if dataArray[2] not in wrapperDict:
                                alreadyIncluded.append([dataArray, displayOption])
                                wrapperDict[dataArray[2]] = [[dataArray[3], dataArray[4], dataArray[5],displayOption]]
                            else:
                                if [dataArray[3], dataArray[4], dataArray[5],displayOption] not in wrapperDict[dataArray[2]]:
                                    alreadyIncluded.append([dataArray, displayOption])
                                    wrapperDict[dataArray[2]].append([dataArray[3], dataArray[4], dataArray[5],displayOption])
                        else:
                            fieldConflictErrors += 'A conflict was found in this field pair:\n\n' + '\n'.join(conflicts) + '\n\n'
                    else:
                            notFoundErrors += '"' + item + '" in "ActiveFields" has the following error(s):\n' + errorMsg + '\n\n'
        return self.checkWrapperDictErrors(syntaxErrors, displayTypeError, notFoundErrors, fieldConflictErrors, wrapperDict)

    def checkWrapperDictErrors(self, syntaxErrors, displayTypeError, notFoundErrors, fieldConflictErrors,  wrapperDict):
        if syntaxErrors != '':
            miInfo('The following entries have incorrect syntax:\nPlease make sure the format is as follows:\n"displayType;profileName;noteTypeName;cardTypeName;fieldName;side(;ReadingType)".\n' + syntaxErrors, level="err")
            return (wrapperDict, False);
        if displayTypeError != '':
            miInfo('The following entries have an incorrect display type. Valid display types are "Hover", "ColoredHover", "Kanji", "ColoredKanji", "KanjiReading", "ColoredKanjiReading", "Reading", and "ColoredReading".\n' + syntaxErrors, level="err")  
            return (wrapperDict, False);
        if notFoundErrors != '':
            miInfo('The following entries have incorrect values that are not found in your currently loaded Anki profile. Please note that this is not necessarily an error, if these fields or note types may exist within your other Anki profiles.\n\n' + notFoundErrors, level="wrn")
            return (wrapperDict, False);
        if fieldConflictErrors != '':
            miInfo('You have entries that point to the same field and the same side. Please make sure that a field and side combination does not conflict.\n\n' + fieldConflictErrors, level="err")
            return (wrapperDict, False);
        return (wrapperDict, True);


    def noteCardFieldExists(self, data):
        models = self.mw.col.models.all()
        error = ''
        note = False
        card = False
        field = False
        side = False
        if data[5] in ['both', 'front', 'back']:
            side = True
        for model in models:
            if model['name'] == data[2] and not note:
                note = True
                for t in model['tmpls']:
                    if t['name'] == data[3] and not card:
                        card = True
                for fld in model['flds']:
                    if fld['name'] == data[4] and not field:
                        field = True 
        if not note:
            return False, 'The "'+ data[2] +'" note type does not exist.';
        
        if not card:
            error += 'The "'+ data[3] +'" card type does not exist.\n'
        if not field:
            error += 'The "'+ data[4] +'" field does not exist.\n'
        if not side:
            error += 'The last value must be "front", "back", or "both", it cannot be "' + data[5] + '"'

        if error == '':
            return True, False;
        return False, error;

    def fieldConflictCheck(self, item, array, dType):
        conflicts = []
        for value in array:
            valAr = value[0]
            valDType = value[1]
            if valAr == item:
                conflicts.append('In "'+ valDType +'": ' + ';'.join(valAr))
                conflicts.append('In "'+ dType +'": ' + ';'.join(item))
                return False, conflicts;
            elif valAr[2] == item[2] and valAr[3] == item[3] and valAr[4] == item[4] and (valAr[5]  == 'both' or item[5] == 'both'):
                conflicts.append('In "'+ valDType +'": ' + ';'.join(valAr))
                conflicts.append('In "'+ dType +'": ' + ';'.join(item))
                return False, conflicts;
        return True, True; 

    def getJapaneseCss(self):
        config = self.getConfig()
        pitchColors = config['ColorsHANOK']
        css = '.j-mia-cont{display:inline-block;}.pitch-numbers{display:inline-block;position:relative;color:#000;font-size:10px;right:2px;padding:0 2px 8px 10px;bottom:7px;vertical-align:top;text-align:right}.thumb-hover:hover{cursor:pointer}.hovered-word{cursor:pointer}.unhovered-word .kanji-ruby{color:#000}.unhovered-word .kana-ruby{visibility:hidden}.unhovered-word.japanese-word{color:#000;background:0 0}.pitch-box{position:relative}.japanese-word{position:relative;display:inline-block}.kana-ruby{display:inline-block;text-align:justify!important}.pitch-accent-popup{box-shadow:2px 2px rgba(0,0,0,.6);position:absolute;display:none;z-index:10;background-color:#fff;border:1px solid #000;border-radius:5px;white-space:nowrap;padding:8px 0 0 4px;top:105%;left:-10%}.pitch-graph-container{position:relative;display:inline-block;top:25%}.pitch-box,.pitch-drop,.pitch-overbar{display:inline-block}.japanese-word .pitch-overbar{background-color:#000}.japanese-word .pitch-drop{background-color:#000}.pitch-overbar{background-color:red;height:2px;width:100%;position:absolute;top:-3px;left:0}.pitch-drop{background-color:red;height:6px;width:2px;position:absolute;top:-3px;right:-2px}.no-ruby{padding:2px 4px 2px 4px}.no-ruby-pitch{height:100%;width:100%;margin:auto;text-align:center;line-height:100%}.pitch-shape-box{padding:4px;display:inline-block;position:relative}.pitch-circle-box-right{display:inline-block;position:relative}.pitch-circle-box-left{padding-right:1.5px;display:inline-block;position:relative}.pitch-diamond{width:8px;height:8px;transform:rotate(45deg);display:inline-block;position:relative;bottom:2px}.left-pitch-circle,.right-pitch-circle{height:12px;width:6px;display:inline-block;position:relative}.right-pitch-circle{border-bottom-right-radius:12px;border-top-right-radius:12px}.left-pitch-circle{border-bottom-left-radius:12px;border-top-left-radius:12px}.pitch-shape-box .pitch-overbar{background-color:#000}.pitch-shape-box .pitch-drop{background-color:#000}.rubyMIA{display:inline-block;padding:0;margin:0;text-align:center}.rtMIA{padding:2px 0 0 0;margin:0;vertical-align:top;text-align:center;line-height:100%}.kana-ruby{position:relative;bottom:-1.5px;z-index:5}.kana-ruby1{font-size:10%}.kana-ruby2{font-size:20%}.kana-ruby3{font-size:30%}.kana-ruby4{font-size:40%}.kana-ruby5{font-size:50%}.kana-ruby6{font-size:60%}.kana-ruby7{font-size:70%}.kana-ruby8{font-size:80%}.kana-ruby9{font-size:90%}.kana-ruby10{font-size:100%}.rbMIA{display:inline-block;padding:0;margin:0}.wrapped-japanese{visibility:hidden}.ankidroid_dark_mode .pitch-box .pitch-drop,.ankidroid_dark_mode .pitch-box .pitch-overbar,.nightMode .pitch-box .pitch-drop,.nightMode .pitch-box .pitch-overbar,.night_mode .pitch-box .pitch-drop,.night_mode .pitch-box .pitch-overbar{background-color:#fff!important}.ankidroid_dark_mode .pitch-accent-popup,.nightMode .pitch-accent-popup,.night_mode .pitch-accent-popup{background-color:#000;border:1px solid #fff;box-shadow:2px 2px rgba(0,0,0,.2)}.ankidroid_dark_mode .unhovered-word .kana-ruby,.ankidroid_dark_mode .unhovered-word .kanji-ruby,.ankidroid_dark_mode .unhovered-word.japanese-word,.nightMode .unhovered-word .kana-ruby,.nightMode .unhovered-word .kanji-ruby,.nightMode .unhovered-word.japanese-word,.night_mode .unhovered-word .kana-ruby,.night_mode .unhovered-word .kanji-ruby,.night_mode .unhovered-word.japanese-word{color:#fff}.popup-comma{color:#000}.ankidroid_dark_mode .popup-comma,.nightMode .popup-comma,.night_mode .popup-comma{color:#fff}';
        hanok = ["heiban","atamadaka","nakadaka", "odaka", "kifuku"]
        count = 0
        for pitchColor in pitchColors:
            css += '.%s{color:%s;}'%(hanok[count], pitchColor)
            count += 1
        count = 0
        bgHanok = ["bgHeiban","bgAtamadaka","bgNakadaka", "bgOdaka", "bgKifuku"]    
        for pitchColor in pitchColors:
            css += '.%s{background-color:%s;}'%(bgHanok[count], pitchColor)
            count += 1
        return self.jCssHeader + '\n' + css + '\n' + self.jCssFooter

    def editJapaneseCss(self, css):
        pattern = self.jCssHeaderP + r'\n.*\n' + self.jCssFooterP
        japaneseCss = self.getJapaneseCss()
        if not css:
            return japaneseCss
        match = re.search(pattern, css)
        if match:
            if match.group() != japaneseCss:
       
                return css.replace(match.group(), japaneseCss)
            else:
                return css
        else:
            return css + '\n' + japaneseCss

    def templateInModelDict(self, template, modelDict):
        for entries in modelDict:
            if entries[0] == template:
                return True
        return False   

    def templateFilteredDict(self, modelDict, template):
        return list(filter(lambda data, tname = template: data[0] == tname, modelDict))

    def cleanFieldWrappers(self, front, back, fields, templateDict):
        for field in fields:
            sides = self.fieldInTemplateDict(field['name'], templateDict)   
            if len(sides) > 0:
                pattern = r'<div display-type="[^>]+?" class="wrapped-japanese">({{'+ field['name'] +'}})</div>'
                if 'both' not in sides or 'front' not in sides:
                    front = re.sub(pattern, '{{'+ field['name'] +'}}', front)
                    front = self.removeJapaneseJs(front)
                if 'both' not in sides or 'back' not in sides:
                    back = re.sub(pattern, '{{'+ field['name'] +'}}', back)
                    back = self.removeJapaneseJs(back)
            else:
                pattern = r'<div display-type="[^>]+?" class="wrapped-japanese">({{'+ field['name'] +'}})</div>'
                front = re.sub(pattern, '{{'+ field['name'] +'}}', front)
                back = re.sub(pattern, '{{'+ field['name'] +'}}', back)
                front = self.removeJapaneseJs(front)
                back = self.removeJapaneseJs(back)          
        return front, back;


    def getJapaneseJs(self):
        js = '<script>'+ self.jFormattingFunctionsJS +'(function(){const FG_FONT_SIZE=' + self.getFGSize() + ';const BUFFERED_OUTPUT=' + self.getBufferOutSetting() + ';const PITCH_GRAPHS=' + self.getGraphHoverSetting() + ';const PITCH_SHAPES=' + self.getShapeHoverSetting() + ';' + self.formatJapaneseJS + '})()</script>'
        return self.jJSHeader+ js + self.jJSFooter


    def editJapaneseJs(self, text):
        pattern = self.jJSHeader + r'.*?' + self.jJSFooter
        japaneseJS = self.getJapaneseJs()
        if not text:
            return japaneseJS
        match = re.search(pattern, text)
        if match:
            if match.group() != japaneseJS:
                return self.newLineReduce(re.sub(match.group, japaneseJS, text))
            else:
                return text
        else:
            return self.newLineReduce(text + '\n' + japaneseJS)
        return

    def removeJapaneseJs(self, text):
        return re.sub(self.jJSHeader + r'.*?' + self.jJSFooter, '', text)

    def fieldInTemplateDict(self, field, templateDict):
        sides = []
        for entries in templateDict:
            if entries[1] == field:
                sides.append(entries[2])
        return sides   

    def removeJapaneseCss(self, css):
        return re.sub(self.jCssHeaderP + r'\n.*\n' + self.jCssFooterP, '', css)

    def overwriteWrapperElement(self, text, field, dType):
        pattern = r'<div display-type="([^>]+?)" class="wrapped-japanese">{{'+ field + r'}}</div>'
        finds = re.findall(pattern, text)
        if len(finds) > 0:
            for find in finds:
                if dType.lower() != find[0].lower():
                    toReplace = '<div display-type="'+ find[0] + '" class="wrapped-japanese">{{'+ field + r'}}</div>'
                    replaceWith = '<div display-type="'+ dType +'" class="wrapped-japanese">{{'+ field + r'}}</div>'
                    text = text.replace(toReplace, replaceWith)
        return text

    def getFGSize(self):
        config = self.getConfig()
        size = config['FuriganaFontSize']
        if size in [1,2,3,4,5,6,7,8,9,10]:
            return str(size)
        return str(4)

    def getBufferOutSetting(self):
        config = self.getConfig()
        if config['BufferedOutput'].lower() == 'on':
            return 'true'
        return 'false'

    def getGraphHoverSetting(self):
        config = self.getConfig()
        if config['GraphOnHover'].lower() == 'on':
            return 'true'
        return 'false'

    def getShapeHoverSetting(self):
        config = self.getConfig()
        if config['DisplayShapes'].lower() == 'on':
            return 'true'
        return 'false'
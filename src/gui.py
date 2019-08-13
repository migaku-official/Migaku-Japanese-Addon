# -*- coding: utf-8 -*-
# 

import json
import sys
import math
from anki.hooks import addHook
from aqt.qt import *
from aqt.utils import openLink, tooltip, showInfo, askUser
from anki.utils import isMac, isWin, isLin
from anki.lang import _
from aqt.webview import AnkiWebView
import re
from . import Pyperclip 
import os
from os.path import dirname, join
from aqt import mw
from .jsgui import Ui_Dialog
from PyQt5 import QtWidgets
from operator import itemgetter
addon_path = dirname(__file__)
import platform

class JSGui(QScrollArea):
    def __init__(self, mw, colArray, MIAModel, reboot, CSSJSHandler, UEManager):
        super(JSGui, self).__init__()
        self.mw = mw 
        self.cA = self.updateCurrentProfileInfo(colArray)
        self.allFields = self.getAllFields()
        self.cont = QWidget()
        self.ui = Ui_Dialog()
        self.ui.setupUi(self.cont)
        self.reboot = reboot
        self.ueMng = UEManager
        self.CSSJSHandler = CSSJSHandler
        self.changingProfile = False
        self.config = self.getConfig()
        self.profileTT = "Profile: Select the profile."
        self.noteTT = "Note Type: Select the note type."
        self.cardTT = "Card Type: Select the card type."
        self.fieldTT = "Field: Select the field."
        self.sideTT =  "Side: Select the side of the card where the display type setting will apply."
        self.displayTypeTT =  "Display Type: Select the display type,\nhover over a display type for fuctionality details."
        self.sides = {'Front' : 'Front: Applies the display type to the front of the card.', 'Back' :'Back: Applies the display type to the back of the card.' , 'Both' : 'Both: Applies the display type to the front and back of the card.'}
        self.displayTypes = {'Kanji' : ['kanji', 'Kanji: Displays text without accent coloring or furigana.'],
'Colored Kanji' : ['coloredkanji', 'Colored Kanji: Displays text with accent coloring but no furigana.'],
'Hover' : ['hover', 'Hover: Displays text without accent coloring or furigana,\nbut displays an individual word\'s furigana when it is hovered.'], 
'Colored Hover' : ['coloredhover', 'Colored Hover: Displays text without accent coloring or furigana,\nbut displays an individual word\'s accent coloring and furigana when it is hovered.'],
'Kanji Reading' : ['kanjireading', 'Kanji Reading: Displays text without accent coloring but with furigana.'],
'Colored Kanji Reading' : ['coloredkanjireading', 'Colored Kanji Reading: Displays text with accent coloring and furigana.'],
'Reading' : ['reading', 'Reading: Displays text in kana without accent coloring.\nNote that if a word\'s kana reading is not available it will be displayed in kanji.'],
'Colored Reading' : ['coloredreading', 'Colored Reading: Displays text in kana with accent coloring.\nNote that if a word\'s kana reading is not available it will be displayed in kanji.']}
        self.displayTranslation = {'kanji' : 'Kanji', 'coloredkanji' : 'Colored Kanji',
            'hover' : 'Hover', 'coloredhover' : 'Colored Hover', 
            'kanjireading' : 'Kanji Reading', 'coloredkanjireading' : 'Colored Kanji Reading',
            'reading' : 'Reading', 'coloredreading' : 'Colored Reading'
            }
        self.MIAModel = MIAModel
        self.selectedProfiles = []
        self.selectedAudioFields = []
        self.selectedGraphFields = []
        self.buttonStatus = 0
        self.selectedRow = False
        self.initializing = False
        self.addMIANoteTypeOnApply = False
        self.sortedProfiles = False
        self.sortedNoteTypes = False
        self.importW = False
        self.arMenu = False
        self.setInitialValues()

    def setInitialValues(self):
        self.setWindowIcon(QIcon(join(addon_path, 'icons', 'mia.png')))
        self.setWindowTitle("Japanese Support Settings")
        self.cont.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)
        self.cont.setFixedSize(1167, 725)
        self.setWidget(self.cont)
        self.setWidgetResizable(True)
        self.resize(1200, 750)
        self.initActiveFieldsCB()
        self.setToolTips()
        self.loadCurrentAFs()
        self.loadCSSJSAddMIA()
        self.handleAutoCSSJS()
        self.loadProfileCB()
        self.loadProfilesList()
        self.loadAudioGraphFieldsCB()
        self.loadFieldsList(True)
        self.loadFieldsList(False)
        self.loadIndGroupExportOptions(True)
        self.loadIndGroupExportOptions(False)
        self.loadLookAhead()
        self.loadHANOK()
        self.loadBehaviorOptions()
        self.setupRulesTable()
        self.ueListCustomContextMenu()
        
        self.initHandlers()

    def setupRulesTable(self):
        rt = self.ui.rulesTable
        self.ueMng.setupModel(self)
        rt.setModel(self.ueMng.model)
        self.ueMng.model.ascendingOrder()
        self.updateRuleCounter()
        tableHeader2 = rt.horizontalHeader()
        tableHeader2.setSectionResizeMode(0, QHeaderView.Stretch)
        tableHeader2.setSectionResizeMode(1, QHeaderView.Stretch)
        # tableHeader2.setSectionResizeMode(2, QHeaderView.Fixed)
        # rt.setColumnWidth(2, 20)
    # def customContextMenu(self, event):
    #     menu = QMenu(self)
    #     quitAction = menu.addAction("Quit")

    #     action = menu.popup(self.mapToGlobal(event.pos()))
    #     if action == quitAction:
    #         showInfo('success')
    def customContextMenu(self, event):
        rows = self.ui.rulesTable.selectionModel().selectedRows()
        length = len(rows)
        if length > 0:
            menu = QMenu(self)
            delete = menu.addAction("Delete Selected Rows")
            pos = event.pos()
            x = pos.x() + 20
            y = pos.y() + 115
            action = menu.exec_(self.mapToGlobal(QPoint(x, y)))
            # position = menu.pos()
            # menu.move(position.x() + 20, position.y()+ 120)
            # menu.move(event.pos().x(), event.pos().y() - 100)
            if action == delete:
                self.removeMultipleRules(rows, str(length))

    def removeMultipleRules(self, rows, length):
        if askUser('Are you sure you would like to remove the ' + length + ' rules that are selected from the overwrite rule list?'):
            # for row in reversed(rows):
            #     self.deleteRuleAtRow(row.row())
            self.ui.rulesTable.setSortingEnabled(False)
            # original = self.ui.rulesTable.item(row, 0).text()
            # self.ueMng.deleteRule(original)
            self.ueMng.model.removeRows(rows[0].row(), len(rows))
            # self.ui.rulesTable.removeRow(row)
            # self.ueMng.saveUEList()
            self.updateRuleCounter()
            self.ui.rulesTable.setSortingEnabled(True)
            

    def ueListCustomContextMenu(self):
        self.ui.rulesTable.contextMenuEvent = self.customContextMenu
        

    def updateRuleCounter(self):
        self.ui.ruleCounter.setText('Rule Count: ' + str(self.ueMng.model.rowCount()))
    


    def addRule(self):
        original = self.ui.originalLE.text()
        overwrite = self.ui.overwriteLE.text()
        added, addId = self.ueMng.addRule(original, overwrite, self.ui.ncAddCB.isChecked(), self.ui.lcAddCB.isChecked(), self)
        if added:
            self.ui.originalLE.setText('')
            self.ui.overwriteLE.setText('')
            self.ui.searchRulesLE.setText('')

            # self.ui.rulesTable.setSortingEnabled(False)
            # self.addRuleToList(original, overwrite)
            # self.ui.rulesTable.setSortingEnabled(True)
            
            self.updateRuleCounter()
            
            if addId is not False:
                addIdx = self.ueMng.model.index(addId, 0)
                self.ui.rulesTable.scrollTo(addIdx)
                self.ui.rulesTable.selectRow(addId)
            else:
                self.ui.rulesTable.scrollToBottom()
                lastRow = self.ueMng.model.rowCount()  - 1
                self.ui.rulesTable.selectRow(lastRow)

    def closeEvent(self, event):
        if self.arMenu:
            self.arMenu.hide()
        if self.importW:
            self.importW.hide()
        event.accept() 

    def hideEvent(self, event):
        if self.arMenu:
            self.arMenu.hide()
        if self.importW:
            self.importW.hide()
        event.accept() 

    def openApplyRuleInquiry(self, rule):
        self.arMenu = QWidget(self, Qt.Window)
        self.arMenu.setWindowTitle('Apply Edited Rule?')
        self.arMenu.setWindowFlags(Qt.Dialog |Qt.MSWindowsFixedSizeDialogHint)
        self.arMenu.setFixedSize(270,80)
        self.arMenu.setWindowModality(Qt.ApplicationModal)
        label = QLabel('Apply to:', self.arMenu)
        hLayout = QHBoxLayout()
        ncCB = QCheckBox('new cards')
        lcCB = QCheckBox('learned cards')
        hLayout.addWidget(label)
        hLayout.addWidget(ncCB)
        hLayout.addWidget(lcCB)
        hLayout.addStretch()
        
        innerWidget = QWidget(self.arMenu)
        innerWidget.setGeometry(QRect(-3, 0, 275,40))
        innerWidget.setLayout(hLayout)

        # .addWidget(gb)
        applyButton = QPushButton('Yes', self.arMenu)
        cancelButton = QPushButton('No', self.arMenu)
        applyButton.setGeometry(QRect(135, 40, 80, 32))
        cancelButton.setGeometry(QRect(50, 40, 80, 32))
        cancelButton.clicked.connect(lambda: self.arMenu.hide())
        applyButton.clicked.connect(lambda: self.applyEditedRule( rule, ncCB.isChecked(), lcCB.isChecked()))
        self.arMenu.show()

    def applyAllRules(self):
        nc = self.ui.ncAllCB.isChecked() 
        lc = self.ui.lcAllCB.isChecked()
        if nc or lc:
            self.ueMng.applyRules(self.ueMng.model.sourceModel().ueList, nc, lc, self)

    def applyEditedRule(self, rule, nc, lc):
        if nc or lc:
            self.ueMng.applyRules(rule, nc, lc, self)
            self.arMenu.hide()

    def setRuleData(self, item, data):
        item.setData(Qt.UserRole, data)


    def resetRuleText(self, item, text):
        item.setText(text)


       
    def getDupeRule(self, rule):
        #testing
        return
        rl = self.ui.rulesTable
        rc = rl.rowCount()
        if rc > 0:
            for i in range(rc):
                if rl.item(i, 0).text() == rule:
                    return i;
        return False


    def restoreDefaultConfig(self):
        if askUser('Are you sure you would like to restore the default settings?'):
            conf = mw.addonManager.addonConfigDefaults(dirname(__file__))
            mw.addonManager.writeConfig(__name__, conf)
            self.close()
            self.reboot()


    def loadCSSJSAddMIA(self):
        if self.config['AutoCssJsGeneration'].lower() == 'on':
            self.ui.autoCSSJS.setChecked(True)
        if self.config['AddMIAJapaneseTemplate'].lower() == 'on':
            self.ui.addMIANoteType.setChecked(True)

    def initHandlers(self):
        self.ui.autoCSSJS.toggled.connect(self.handleAutoCSSJS)
        self.ui.addMIANoteType.toggled.connect(self.handleAddMIA)
        self.ui.activeProfileCB.currentIndexChanged.connect(self.profileChange )
        self.ui.activeNoteTypeCB.currentIndexChanged.connect(self.noteTypeChange)
        self.ui.activeCardTypeCB.currentIndexChanged.connect(self.selectionChange)
        self.ui.activeFieldCB.currentIndexChanged.connect(self.selectionChange)
        self.ui.activeSideCB.currentIndexChanged.connect(self.selectionChange)
        self.ui.activeDisplayTypeCB.currentIndexChanged.connect(self.selectionChange)
        self.ui.activeActionButton.clicked.connect(self.performButtonAction)
        self.ui.listWidget.cellClicked.connect(self.loadSelectedRow)
        self.ui.applyButton.clicked.connect(self.saveConfiguration)
        self.ui.cancelButton.clicked.connect(self.exit)
        self.ui.profilesPB.clicked.connect(lambda: self.addRemoveFromList(self.ui.profilesCB.currentText(), self.ui.profilesPB, self.ui.profilesList, self.selectedProfiles, True))
        self.ui.profilesCB.currentIndexChanged.connect(lambda: self.profAudioGraphChange(self.ui.profilesCB.currentText(), self.ui.profilesPB, self.selectedProfiles))
        self.ui.audioFieldsPB.clicked.connect(lambda: self.addRemoveFromList(self.ui.audioFieldsCB.currentText(), self.ui.audioFieldsPB, self.ui.audioFieldsList, self.selectedAudioFields, True))
        self.ui.audioFieldsCB.currentIndexChanged.connect(lambda: self.profAudioGraphChange(self.ui.audioFieldsCB.currentText(), self.ui.audioFieldsPB, self.selectedAudioFields))
        self.ui.pitchGraphsPB.clicked.connect(lambda: self.addRemoveFromList(self.ui.pitchGraphsCB.currentText(), self.ui.pitchGraphsPB, self.ui.pitchGraphsList, self.selectedGraphFields, True))
        self.ui.pitchGraphsCB.currentIndexChanged.connect(lambda: self.profAudioGraphChange(self.ui.pitchGraphsCB.currentText(), self.ui.pitchGraphsPB, self.selectedGraphFields))
        self.ui.audioAdd.clicked.connect(lambda: self.enableSep(self.ui.audioSep))
        self.ui.audioOverwrite.clicked.connect(lambda: self.disableSep(self.ui.audioSep))
        self.ui.audioIfEmpty.clicked.connect(lambda: self.disableSep(self.ui.audioSep))
        self.ui.graphAdd.clicked.connect(lambda: self.enableSep(self.ui.graphSep))
        self.ui.graphOverwrite.clicked.connect(lambda: self.disableSep(self.ui.graphSep))
        self.ui.graphIfEmpty.clicked.connect(lambda: self.disableSep(self.ui.graphSep))
        self.ui.heibanSelect.clicked.connect(lambda: self.openDialogColor(self.ui.heibanColor))
        self.ui.atamadakaSelect.clicked.connect(lambda: self.openDialogColor(self.ui.atamadakaColor))
        self.ui.nakadakaSelect.clicked.connect(lambda: self.openDialogColor(self.ui.nakadakaColor))
        self.ui.odakaSelect.clicked.connect(lambda: self.openDialogColor(self.ui.odakaColor))
        self.ui.kifukuSelect.clicked.connect(lambda: self.openDialogColor(self.ui.kifukuColor))
        self.ui.restoreDefaults.clicked.connect(self.restoreDefaultConfig)
        self.ui.addRuleButton.clicked.connect(self.addRule)
        self.ui.exportRules.clicked.connect(self.exportRules)
        self.ui.importRules.clicked.connect(self.importRules)
        self.ui.runRulesButton.clicked.connect(self.applyAllRules)
        self.ui.searchRulesLE.returnPressed.connect(self.initRuleSearch)
        self.ui.searchRulesButton.clicked.connect(self.initRuleSearch)
        self.ui.miaSiteIcon.clicked.connect(lambda: openLink('https://massimmersionapproach.com/'))
        self.ui.miaFBIcon.clicked.connect(lambda: openLink('https://www.facebook.com/MassImmersionApproach/'))
        self.ui.miaPatreonIcon.clicked.connect(lambda: openLink('https://www.patreon.com/massimmersionapproach'))
        self.ui.mattYT.clicked.connect(lambda: openLink('https://www.youtube.com/user/MATTvsJapan?sub_confirmation=1'))
        self.ui.mattTW.clicked.connect(lambda: openLink('https://twitter.com/mattvsjapan'))
        self.ui.yogaYT.clicked.connect(lambda: openLink('https://www.youtube.com/c/yogamia?sub_confirmation=1'))
        self.ui.yogaTW.clicked.connect(lambda: openLink('https://twitter.com/Yoga_MIA'))
        self.ui.gitHubIcon.clicked.connect(lambda: openLink('https://github.com/mass-immersion-approach'))

    def initRuleSearch(self):
        text = self.ui.searchRulesLE.text()
        if text == '':
            self.ueMng.model.ascendingOrder()
            self.ueMng.model.setFilterByColumn(text)
            self.updateRuleCounter()   
            self.ui.rulesTable.scrollToTop()
        else:
            self.ueMng.model.testData(text)
            self.ueMng.model.setFilterByColumn(text)
            self.updateRuleCounter()   
            self.ui.rulesTable.scrollToTop() 
        return

        
        text = self.ui.searchRulesLE.text()
        if text == '':
            self.loadUEList()
        else:
            rl = self.ui.rulesTable
            foundOriginal = []
            foundOverwrite = []
            text = text.lower()
            for original, overwrite in self.ueMng.ueList.items():
                LOriginal = original.lower()
                LOverwrite = overwrite.lower()
                if LOriginal == text:
                    foundOriginal.append([original, overwrite])
                elif text in LOriginal: 
                    foundOriginal.append([original, overwrite])
                elif LOverwrite == text:
                    foundOverwrite.append([original, overwrite])
                elif text in LOverwrite: 
                    foundOverwrite.append([original, overwrite])   
            sorted(foundOriginal, key=len)
            sorted(foundOverwrite, key=len)
            rl.setSortingEnabled(False)
            for ogOv in foundOriginal:
                self.addRuleToList(ogOv[0], ogOv[1])
            for ogOv in foundOverwrite:
                self.addRuleToList(ogOv[0], ogOv[1])
            self.updateRuleCounter()
            rl.setSortingEnabled(True)
        self.ui.rulesTable.scrollToTop()

    def exportRules(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        fileName, _ = QFileDialog.getSaveFileName(self,"Save Overwrite Rules List", 'overwriterules.json', 'JSON Files (*.json)', options=options)
        if fileName:
            self.ueMng.exportUEList(fileName)


    def importRules(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        fileName, _ = QFileDialog.getOpenFileName(self,"Select an Overwrite Rules List", "",'JSON Files (*.json)', options=options)
        if fileName:
            self.importW = QWidget(self, Qt.Window)
            self.importW.setWindowModality(Qt.ApplicationModal)
            self.importW.setWindowTitle('Import Overwrite Rules List')
            vLayout = QVBoxLayout()
            hLayout1 = QHBoxLayout()
            gb1 = QGroupBox('Import Behavior')
            overwriteRB = QRadioButton('Replace current list')
            combineRB = QRadioButton('Combine with current list')
            overwriteRB.setToolTip('Delete your current list, and import the new list in its place.')
            combineRB.setToolTip('Combine the imported list with your current overwrite rules list.')
            hLayout1.addWidget(combineRB)
            hLayout1.addWidget(overwriteRB)
            gb1.setLayout(hLayout1)
            hLayout2 = QHBoxLayout()
            gb2 = QGroupBox('Conflicting "Original" Field Behavior')
            ovCollideRB = QRadioButton('Honor imported list')
            laiCollideRB = QRadioButton('Honor current list')
            laiCollideRB.setToolTip('Any rules that are found to have the same original value as an existing rule in your \ncurrent list are ignored and not added to the combined list.')
            ovCollideRB.setToolTip('Overwrites any rules that have the same original value with the values in the imported list.')
            hLayout2.addWidget(ovCollideRB)
            hLayout2.addWidget(laiCollideRB)
            gb2.setLayout(hLayout2)
            vLayout.addWidget(QLabel('File to import: ' + fileName))
            vLayout.addWidget(gb1)
            vLayout.addWidget(gb2)
            importButton = QPushButton('Import')
            vLayout.addWidget(importButton)
            self.importW.setLayout(vLayout)
            overwriteRB.setChecked(True)
            ovCollideRB.setChecked(True)
            ovCollideRB.setEnabled(False)
            laiCollideRB.setEnabled(False)
            overwriteRB.clicked.connect(lambda: self.toggleImportOpts(combineRB.isChecked(), ovCollideRB, laiCollideRB))
            combineRB.clicked.connect(lambda: self.toggleImportOpts(combineRB.isChecked(), ovCollideRB, laiCollideRB))
            importButton.clicked.connect(lambda: self.ruleListImport(self.importW, fileName, combineRB.isChecked(), ovCollideRB.isChecked()))
            self.importW.show()

    def ruleListImport(self, window, fileName, combine, overwriteCollides):
        imported = self.ueMng.importUEList(fileName, combine, overwriteCollides) 
        if imported is not False:
            if not combine:
                showInfo(str(imported[0]) +' rules have been imported.', title="MIA Japanese Support Notice")
            else:
                if overwriteCollides:
                    showInfo(str(imported[0]) +' rules have been imported.<br>' + str(imported[1]) + ' rules have been overwritten.', title="MIA Japanese Support Notice")
                else:
                    showInfo(str(imported[0]) +' rules have been imported.<br>' + str(imported[1]) + ' rules have been ignored because they conflicted with existing rules.', title="MIA Japanese Support Notice")
            self.ueMng.setupModel(self)
            self.ui.rulesTable.setModel(self.ueMng.model)
            self.ueMng.model.ascendingOrder()
            self.updateRuleCounter()
            window.hide()
            

        ####opens window that allows user to select options
        # combine lists and replace conflicting original, don't replace conflicting original, overwrite conflicting entries
    def toggleImportOpts(self, enable, b1, b2):
        if enable:
            b1.setEnabled(True)
            b2.setEnabled(True)
        else:
            b1.setEnabled(False)
            b2.setEnabled(False)

    def exit(self):
        self.hide()

    def openDialogColor(self, lineEd):
        color = QColorDialog.getColor(parent=self)
        if color.isValid():
            lineEd.setText(color.name())
            lineEd.setStyleSheet('color:' + color.name() + ';')

    def enableSep(self, sep):
        sep.setEnabled(True)

    def disableSep(self, sep):
        sep.setEnabled(False)    

    def handleAddMIA(self):
        if self.ui.addMIANoteType.isChecked():
            if not self.checkMIANoteExistence():
                self.addMIANoteTypeOnApply = True
                self.resetMIAActiveFields()

    def loadLookAhead(self):
        self.ui.lookAhead.setValue(self.config['LookAhead'])

    def loadHANOK(self):
        colors = self.config['ColorsHANOK']
        self.ui.heibanColor.setText(colors[0])
        self.ui.heibanColor.setStyleSheet('color:' + colors[0] + ';')
        self.ui.atamadakaColor.setText(colors[1])
        self.ui.atamadakaColor.setStyleSheet('color:' + colors[1] + ';')
        self.ui.nakadakaColor.setText(colors[2])
        self.ui.nakadakaColor.setStyleSheet('color:' + colors[2] + ';')
        self.ui.odakaColor.setText(colors[3])
        self.ui.odakaColor.setStyleSheet('color:' + colors[3] + ';')
        self.ui.kifukuColor.setText(colors[4])
        self.ui.kifukuColor.setStyleSheet('color:' + colors[4] + ';')

    def loadBehaviorOptions(self):
        self.ui.furiganaFontSize.setValue(self.config['FuriganaFontSize'])
        if self.config['DisplayShapes'].lower() == 'on':
            self.ui.displayShapes.setChecked(True)
        if self.config['GraphOnHover'].lower() == 'on':
            self.ui.graphOnHover.setChecked(True)
        if self.config['BufferedOutput'].lower() == 'on':
            self.ui.bufferedOutput.setChecked(True)
        if self.config['PlayAudioOnClick'].lower() == 'on':
            self.ui.audioOnClick.setChecked(True)
        if self.config['KatakanaConversion'].lower() == 'on':
            self.ui.katakanaConversion.setChecked(True)
        if self.config['HistoricalConversion'].lower() == 'kanji' or self.config['HistoricalConversion'].lower() == 'both':
            self.ui.historicalKanji.setChecked(True)
        if self.config['HistoricalConversion'].lower() == 'kana' or self.config['HistoricalConversion'].lower() == 'both':
            self.ui.historicalKana.setChecked(True)

    def loadIndGroupExportOptions(self, group):
        if group:
            options = self.config['Group:Kana;DictForm;Pitch;Audio;Graphs']
            kana = self.ui.sentenceKana
            dictF = self.ui.sentenceDictForm
            audio = self.ui.sentenceAudio
            graphs = self.ui.sentenceGraphs
            accents = self.ui.sentenceAccents
        else:
            options = self.config['Individual:Kana;DictForm;Pitch;Audio;Graphs']
            kana = self.ui.wordKana
            dictF = self.ui.wordDictForm
            audio = self.ui.wordAudio
            graphs = self.ui.wordGraphs
            accents = self.ui.wordAccents
        options = options.split(';')
        if options[0].lower() == 'on' :
            kana.setChecked(True)
        if options[1].lower() == 'on' :
            dictF.setChecked(True)
        if options[3].lower() == 'on' :
            audio.setChecked(True)
        if options[4].lower() == 'on' :
            graphs.setChecked(True)
        if options[2].lower() == 'on' :
            accents.setChecked(True)

    def resetMIAActiveFields(self):
        self.removeMIAFields()
        self.addMIAFields()
        
    def checkMIANoteExistence(self):
        models = self.mw.col.models.all()
        for model in models:
            if model['name'] == 'MIA Japanese':
                return True
        return False

    def removeMIAFields(self):
        afList = self.ui.listWidget
        for i in reversed(range(afList.rowCount())):
            if afList.item(i, 1).text() == 'MIA Japanese':
                self.ui.listWidget.removeRow(i)


    def addMIAFields(self):
        self.addToList('All', 'MIA Japanese', 'Sentence', 'Expression', 'Front', 'Colored Hover')
        self.addToList('All', 'MIA Japanese', 'Sentence', 'Expression', 'Back', 'Colored Kanji Reading')
        self.addToList('All', 'MIA Japanese', 'Sentence', 'Meaning', 'Back', 'Colored Hover')

    def handleAutoCSSJS(self):
        if self.ui.autoCSSJS.isChecked():
            self.ui.activeProfileCB.setEnabled(True)
            self.ui.activeNoteTypeCB.setEnabled(True)
            self.ui.activeCardTypeCB.setEnabled(True)
            self.ui.activeFieldCB.setEnabled(True)
            self.ui.activeSideCB.setEnabled(True)
            self.ui.activeDisplayTypeCB.setEnabled(True)
            self.ui.activeActionButton.setEnabled(True)
            self.ui.addMIANoteType.setEnabled(True)
            self.ui.listWidget.setEnabled(True)

        else:
            self.ui.activeProfileCB.setEnabled(False)
            self.ui.activeNoteTypeCB.setEnabled(False)
            self.ui.activeCardTypeCB.setEnabled(False)
            self.ui.activeFieldCB.setEnabled(False)
            self.ui.activeSideCB.setEnabled(False)
            self.ui.activeDisplayTypeCB.setEnabled(False)
            self.ui.activeActionButton.setEnabled(False)
            self.ui.addMIANoteType.setEnabled(False)
            self.ui.listWidget.setEnabled(False)

    def selectionChange(self):
        if self.buttonStatus == 1:
            self.buttonStatus = 2
            self.ui.activeActionButton.setText('Save Changes')
        
    def editEntry(self, profile, nt, ct, field, side, dt):
        afList = self.ui.listWidget
        rc = self.selectedRow
        found = self.dupeRow(afList, profile, nt, ct, field, side, dt, rc)
        if found:
            showInfo('This row cannot be edited in this manner because row #' + str(found) + 
                ' in the Active Fields List already targets this given field and side combination. Please review that entry and try again.', title="MIA Japanese Support Error")
        else:
            afList.setSortingEnabled(False)
            
            rc[0].setText(profile)
            rc[1].setText(nt)
            rc[2].setText(ct)
            rc[3].setText(field)
            rc[4].setText(side)
            rc[5].setText(dt)
            afList.setSortingEnabled(True) 
        self.resetButton()   

    def getConfig(self):
        return self.mw.addonManager.getConfig(__name__)

    def loadCurrentAFs(self):
        afs = self.config['ActiveFields']
        for af in afs:
            afl = af.split(';')
            dt = afl[0].lower()
            if dt in self.displayTranslation:
                prof = afl[1]
                if prof == 'all':
                    prof = 'All'
                self.addToList(prof, afl[2], afl[3], afl[4], afl[5][0].upper() + afl[5][1:].lower() , self.displayTranslation[dt])

    def saveCSSJSAddMIA(self):
        mia = 'off'
        css = 'off'
        if self.ui.autoCSSJS.isChecked():
            css = 'on'
        if self.ui.addMIANoteType.isChecked():
            mia = 'on'
        return css, mia;   

    def saveConfiguration(self):
        sc, wc = self.saveSentenceWordConfig()
        ffs, la = self.saveNumberConfigOptions()
        ac, gc = self.saveAudioGraphsConfig()
        colors = self.saveHANOK()
        addmia, bo, autocss, ds, goh, kc, poc = self.saveBinaryOptions()
        newConf = {"ActiveFields" : self.saveActiveFields(), "Individual:Kana;DictForm;Pitch;Audio;Graphs" : wc, "Group:Kana;DictForm;Pitch;Audio;Graphs": sc,
         "FuriganaFontSize" : ffs, "LookAhead" : la, "Profiles" : self.saveProfilesConfig(),
         "AudioFields" : ac, "PitchGraphFields" :  gc, "ColorsHANOK" : colors, "AddMIAJapaneseTemplate": addmia, "BufferedOutput" :  bo,
         "AutoCssJsGeneration" : autocss, "DisplayShapes" : ds, "GraphOnHover" : goh, "KatakanaConversion" : kc, "PlayAudioOnClick" : poc,
         "HistoricalConversion" : self.saveHistoricalConversion()

         }
        if self.addMIANoteTypeOnApply:
            self.MIAModel.addModels() 
        mw.addonManager.writeConfig(__name__, newConf)
        self.CSSJSHandler.injectWrapperElements()
        self.hide()

    def saveHistoricalConversion(self):
        if self.ui.historicalKana.isChecked() and self.ui.historicalKanji.isChecked():
            return 'both'
        elif self.ui.historicalKanji.isChecked():
            return 'kanji'
        elif self.ui.historicalKana.isChecked():
            return 'kana'
        else:
            return 'off'

    def saveBinaryOptions(self):
        addmia = 'off'
        bo = 'off'
        autocss = 'off'
        ds = 'off'
        goh = 'off'
        kc = 'off'
        poc = 'off'
        if self.ui.addMIANoteType.isChecked():
            addmia = 'on'
        if self.ui.bufferedOutput.isChecked():
            bo = 'on'
        if self.ui.autoCSSJS.isChecked():
            autocss = 'on'
        if self.ui.displayShapes.isChecked():
            ds = 'on'
        if self.ui.graphOnHover.isChecked():
            goh = 'on'
        if self.ui.katakanaConversion.isChecked():
            kc = 'on'
        if self.ui.audioOnClick.isChecked():
            poc = 'on'
        return addmia, bo, autocss, ds, goh, kc, poc;

    def saveHANOK(self):
        return [self.ui.heibanColor.text(), self.ui.atamadakaColor.text(), self.ui.nakadakaColor.text(), self.ui.odakaColor.text(), self.ui.kifukuColor.text()]

    def saveAudioGraphsConfig(self):
        audioConfig = [ ','.join(self.selectedAudioFields)]
        graphConfig = [ ','.join(self.selectedGraphFields)]
        if self.ui.audioAdd.isChecked():
            audioConfig.append('add')
            audioConfig.append(self.ui.audioSep.text())
        elif self.ui.audioOverwrite.isChecked():
            audioConfig.append('overwrite')
        elif self.ui.audioIfEmpty.isChecked():
            audioConfig.append('no')
        if self.ui.graphAdd.isChecked():
            graphConfig.append('add')
            graphConfig.append(self.ui.graphSep.text())
        elif self.ui.graphOverwrite.isChecked():
            graphConfig.append('overwrite')
        elif self.ui.graphIfEmpty.isChecked():
            graphConfig.append('no')
        return ';'.join(audioConfig), ';'.join(graphConfig);
    
    def saveProfilesConfig(self):
        return self.selectedProfiles

    def saveNumberConfigOptions(self):
        return self.ui.furiganaFontSize.value(), self.ui.lookAhead.value();

    def saveSentenceWordConfig(self):
        sentenceConfig = ['off', 'off', 'off','off' , 'off']
        wordConfig = ['off', 'off', 'off','off' , 'off']
        if self.ui.sentenceKana.isChecked():
            sentenceConfig[0] = 'on'
        if self.ui.sentenceDictForm.isChecked():
            sentenceConfig[1] = 'on'
        if self.ui.sentenceAudio.isChecked():
            sentenceConfig[3] = 'on'
        if self.ui.sentenceGraphs.isChecked():
            sentenceConfig[4] = 'on'
        if self.ui.sentenceAccents.isChecked():
            sentenceConfig[2] = 'on'
        if self.ui.wordKana.isChecked():
            wordConfig[0] = 'on'
        if self.ui.wordDictForm.isChecked():
            wordConfig[1] = 'on'
        if self.ui.wordAudio.isChecked():
            wordConfig[3] = 'on'
        if self.ui.wordGraphs.isChecked():
            wordConfig[4] = 'on'
        if self.ui.wordAccents.isChecked():
            wordConfig[2] = 'on'
        return ';'.join(sentenceConfig),';'.join(wordConfig);

    def saveActiveFields(self):
        afList = self.ui.listWidget
        afs = []
        for i in range(afList.rowCount()):
            prof = afList.item(i, 0).text()
            if prof == 'All':
                prof = 'all'
            nt = afList.item(i, 1).text()
            ct = afList.item(i, 2).text()
            field = afList.item(i, 3).text()
            side = afList.item(i, 4).text().lower()
            target = afList.item(i,  5).text()
            for key, value in self.displayTranslation.items():
                if value == target:
                    dt = key
                    break
            afs.append(';'.join([dt,prof,nt,ct,field,side]))
        return afs
 
    def resetButton(self):
        self.initializing = True
        self.buttonStatus = 0
        self.ui.activeActionButton.setText('Add')
        self.selectedRow = False
        self.clearAllAF()
        self.initActiveFieldsCB()
        self.initializing = False

    def initEditMode(self):
        self.buttonStatus = 1
        self.ui.activeActionButton.setText('Cancel')

    def loadSelectedRow(self, row, col):
        afList = self.ui.listWidget
        prof = afList.item(row, 0).text()
        nt = afList.item(row, 1).text()
        ct = afList.item(row, 2).text()
        field = afList.item(row, 3).text()
        side = afList.item(row, 4).text()
        dt = afList.item(row, 5).text()
        if prof.lower() == 'all':
            loaded = self.unspecifiedProfileLoad( nt, ct, field, side, dt)
        else:
            loaded = self.specifiedProfileLoad(prof, nt, ct, field, side, dt)
        if loaded:
            self.initEditMode()
            self.selectedRow = [afList.item(row, 0), afList.item(row, 1), afList.item(row, 2), afList.item(row, 3), afList.item(row, 4), afList.item(row, 5)]
            
    def unspecifiedProfileLoad(self, nt, ct, field, side, dt):
        self.ui.activeProfileCB.setCurrentIndex(0)
        if self.findFirstNoteCardFieldMatch(nt, ct, field):
            index = self.ui.activeSideCB.findText(side, Qt.MatchFixedString)
            if index >= 0:
                self.ui.activeSideCB.setCurrentIndex(index)
            index = self.ui.activeDisplayTypeCB.findText(dt, Qt.MatchFixedString)
            if index >= 0:
                self.ui.activeDisplayTypeCB.setCurrentIndex(index)
            return True
        else: 
            return False

    def findFirstNoteCardFieldMatch(self, nt, ct, field):
        for i in range(self.ui.activeNoteTypeCB.count()):
            if self.ui.activeNoteTypeCB.itemText(i).startswith(nt):
                self.ui.activeNoteTypeCB.setCurrentIndex(i)
                ci = self.ui.activeCardTypeCB.findText(ct, Qt.MatchFixedString)
                if ci >= 0:
                    fi = self.ui.activeFieldCB.findText(field, Qt.MatchFixedString)
                    if fi >= 0:
                        self.ui.activeNoteTypeCB.setCurrentIndex(i)
                        self.ui.activeCardTypeCB.setCurrentIndex(ci)
                        self.ui.activeFieldCB.setCurrentIndex(fi)
                        return True
        return False

    def specifiedProfileLoad(self, prof, nt, ct, field, side, dt):
        index = self.ui.activeProfileCB.findText(prof, Qt.MatchFixedString)
        if index >= 0:
            self.ui.activeProfileCB.setCurrentIndex(index)
        index = self.ui.activeNoteTypeCB.findText(nt, Qt.MatchFixedString)
        if index >= 0:
            self.ui.activeNoteTypeCB.setCurrentIndex(index)
        index = self.ui.activeCardTypeCB.findText(ct, Qt.MatchFixedString)
        if index >= 0:
            self.ui.activeCardTypeCB.setCurrentIndex(index)
        index = self.ui.activeFieldCB.findText(field, Qt.MatchFixedString)
        if index >= 0:
            self.ui.activeFieldCB.setCurrentIndex(index)
        index = self.ui.activeSideCB.findText(side, Qt.MatchFixedString)
        if index >= 0:
            self.ui.activeSideCB.setCurrentIndex(index)
        index = self.ui.activeDisplayTypeCB.findText(dt, Qt.MatchFixedString)
        if index >= 0:
            self.ui.activeDisplayTypeCB.setCurrentIndex(index)
        return True

    def performButtonAction(self):
        if self.buttonStatus == 1:
            self.resetButton()
        else:
            profile = self.ui.activeProfileCB.currentText()
            nt = self.ui.activeNoteTypeCB.itemData(self.ui.activeNoteTypeCB.currentIndex()).split(':pN:')[1]
            ct = self.ui.activeCardTypeCB.currentText()
            field = self.ui.activeFieldCB.currentText()
            side = self.ui.activeSideCB.currentText()
            dt = self.ui.activeDisplayTypeCB.currentText()
            if profile != '' and nt != '' and ct != '' and field != '' and side != '' and dt != '':
                if self.buttonStatus == 0:
                    self.addToList(profile, nt, ct, field, side, dt)
                elif self.buttonStatus == 2:
                    self.editEntry(profile, nt, ct, field, side, dt)

    def dupeRow(self, afList, profile, nt, ct, field, side, dt, selRow = False):
        for i in range(afList.rowCount()):
            if selRow:
                if i == selRow[0].row():
                    continue
            if (afList.item(i, 0).text() == profile or afList.item(i, 0).text() == 'All' or profile == "All") and afList.item(i, 1).text() == nt and afList.item(i, 2).text() == ct and afList.item(i, 3).text() == field and (afList.item(i, 4).text() == side or afList.item(i, 4).text() == 'Both' or side == "Both"):
                return i + 1;
        return False

    def addToList(self, profile, nt, ct, field, side, dt):
        afList = self.ui.listWidget
        found = self.dupeRow(afList, profile, nt, ct, field, side, dt)
        if found:
            showInfo('This row cannot be added because row #' + str(found) + 
                ' in the Active Fields List already targets this given field and side combination. Please review that entry and try again.', title="MIA Japanese Support Error")
        else:
            afList.setSortingEnabled(False)
            rc = afList.rowCount()
            afList.setRowCount(rc + 1)
            afList.setItem(rc, 0, QTableWidgetItem(profile))
            afList.setItem(rc, 1, QTableWidgetItem(nt))
            afList.setItem(rc, 2, QTableWidgetItem(ct))
            afList.setItem(rc, 3, QTableWidgetItem(field))
            afList.setItem(rc, 4, QTableWidgetItem(side))
            afList.setItem(rc, 5, QTableWidgetItem(dt))
            deleteButton =  QPushButton("X");
            deleteButton.setFixedWidth(40)
            deleteButton.clicked.connect(self.removeRow)
            afList.setCellWidget(rc, 6, deleteButton);
            afList.setSortingEnabled(True)

    def removeRow(self):
        if askUser('Are you sure you would like to remove this entry from the active field list?'):
            self.ui.listWidget.removeRow(self.ui.listWidget.selectionModel().currentIndex().row())
            self.resetButton()

    def profileChange(self):
        if self.initializing:
            return
        self.changingProfile = True
        self.ui.activeNoteTypeCB.clear()
        self.ui.activeCardTypeCB.clear()
        self.ui.activeFieldCB.clear()
        if self.ui.activeProfileCB.currentIndex() == 0:
            self.loadAllNotes()
        else:
            prof = self.ui.activeProfileCB.currentText()
            for noteType in self.ciSort(self.cA[prof]):
                    self.ui.activeNoteTypeCB.addItem(noteType)
                    self.ui.activeNoteTypeCB.setItemData(self.ui.activeNoteTypeCB.count() - 1, noteType + ' (Prof:' + prof + ')',Qt.ToolTipRole)
                    self.ui.activeNoteTypeCB.setItemData(self.ui.activeNoteTypeCB.count() - 1, prof + ':pN:' + noteType)
        self.loadCardTypesFields()
        self.changingProfile = False
        self.selectionChange()

    def noteTypeChange(self):
        if self.initializing:
            return
        if not self.changingProfile:
            self.ui.activeCardTypeCB.clear()
            self.ui.activeFieldCB.clear()
            self.loadCardTypesFields()
        self.selectionChange()

    def loadCardTypesFields(self):
        curProf, curNote = self.ui.activeNoteTypeCB.itemData(self.ui.activeNoteTypeCB.currentIndex()).split(':pN:')     
        for cardType in self.cA[curProf][curNote]['cardTypes']:
            self.ui.activeCardTypeCB.addItem(cardType)
            self.ui.activeCardTypeCB.setItemData(self.ui.activeCardTypeCB.count() - 1, cardType,Qt.ToolTipRole)
        for field in self.cA[curProf][curNote]['fields']:
            self.ui.activeFieldCB.addItem(field)
            self.ui.activeFieldCB.setItemData(self.ui.activeFieldCB.count() - 1, field,Qt.ToolTipRole)
        return

    def updateCurrentProfileInfo(self, colA):
        pn = self.mw.pm.name
        noteTypes = self.mw.col.models.all()
        noteTypeDict = {}
        for note in noteTypes:
            noteTypeDict[note['name']] = {"cardTypes" : [], "fields" : []}
            for ct in note['tmpls']:
                noteTypeDict[note['name']]["cardTypes"].append(ct['name'])
            for f in note['flds']:
                noteTypeDict[note['name']]["fields"].append(f['name'])
            colA[pn] = noteTypeDict
        return colA
    
    def getAllFields(self):
        fieldList = []
        for prof in self.cA:
            for name, note in self.cA[prof].items():
                for f in note['fields']:
                    if f not in fieldList:
                        fieldList.append(f)
              
        return self.ciSort(fieldList)

    def ciSort(self, l):
        return sorted(l, key=lambda s: s.lower())

    def setToolTips(self):
        self.ui.activeProfileCB.setToolTip(self.profileTT)
        self.ui.activeNoteTypeCB.setToolTip(self.noteTT)
        self.ui.activeCardTypeCB.setToolTip(self.cardTT)
        self.ui.activeFieldCB.setToolTip(self.fieldTT)
        self.ui.activeSideCB.setToolTip(self.sideTT)
        self.ui.activeDisplayTypeCB.setToolTip(self.displayTypeTT)
        self.ui.autoCSSJS.setToolTip('If checked, the addon will manage the CSS and JS of all note and card types designated in the active fields list below.\nIf this is disabled the user is responsible for ensuring that their CSS and JS functions as they wish.')
        self.ui.addMIANoteType.setToolTip('If checked, the addon will attempt to add the MIA Japanese Note Type if it does not already exist.\nIt will also regenerate the active fields for the MIA Japanese Note Type.')
        self.ui.profilesCB.setToolTip('These are the profiles that the add-on will be active on.\nWhen set to "All", the add-on will be active on all profiles.')
        self.ui.sentenceKana.setToolTip('When checked, the addon will generate the kana reading of all\nrecognized words within the target field.')
        self.ui.sentenceDictForm.setToolTip('When checked, the addon will generate the dictionary form of all\nrecognized verbs and adjectives within the target field.')
        self.ui.sentenceAudio.setToolTip('When checked, the addon will export the audio when available, for all\nrecognized words within the target field, into the selected "Audio Field(s)".')
        self.ui.sentenceGraphs.setToolTip('When checked, the addon will export the pitch graph(s) when available, for all\nrecognized words within the target field, into the selected "Pitch Graph Field(s)".')
        self.ui.sentenceAccents.setToolTip('When checked, the addon will export the pitch accent(s) when available, for all\nrecognized words within the target field.')
        self.ui.wordKana.setToolTip('When checked, the addon will generate the kana reading for the next\nrecognized word within the highlighted text, or after the cursor\'s current position\nwithin a field if no text is currently highlighted.')
        self.ui.wordDictForm.setToolTip('When checked, the addon will generate the dictionary form for the next\nrecognized adjective or verb within the highlighted text, or after the cursor\'scurrent position\nwithin a field if no text is currently highlighted.')
        self.ui.wordAudio.setToolTip('When checked, the addon will generate the audio for the next\nrecognized word within the highlighted text, or after the cursor\'s current position\nwithin a field if no text is currently highlighted. The audio will be exported into the selected "Audio Field(s)".')
        self.ui.wordGraphs.setToolTip('When checked, the addon will generate the pitch graph(s) for the next\nrecognized word within the highlighted text, or after the cursor\'s current position\nwithin a field if no text is currently highlighted. The audio will be exported into the selected "Pitch Graph Field(s)".')
        self.ui.wordAccents.setToolTip('When checked, the addon will generate the pitch accent(s)for the next\nrecognized adjective or verb within the highlighted text, or after the cursor\'s current position\nwithin a field if no text is currently highlighted.')
        self.ui.audioFieldsCB.setToolTip('When audio generation is enabled the audio will be pasted within the selected audio field(s).\nNote that if a selected audio field has also been designated as a pitch graph field\nthat the pitch graph(s) will preceed the audio, and the pitch graph\'s separator will be used.')
        self.ui.audioAdd.setToolTip('Audio will be added on to the selected audio field(s) following the separator.\nThe default separator is an html line break "<br>".')
        self.ui.audioOverwrite.setToolTip('Audio will be generated into the selected audio field(s),\noverwriting their current contents.')
        self.ui.audioIfEmpty.setToolTip('Audio will be only be added to the selected audio field(s) if they are empty.')
        self.ui.audioSep.setToolTip('This is the separator to be used when adding audio to the selected audio field(s)\' current contents.\nThe default separator is an html line break "<br>".')
        self.ui.pitchGraphsCB.setToolTip('When pitch graph generation is enabled the pitch graph(s) will be pasted within the selected pitch graph field(s).\nNote that if a selected audio field has also been designated as a pitch graph field\nthat the pitch graph(s) will preceed the audio, and the pitch graph\'s separator will be used.')
        self.ui.graphAdd.setToolTip('Pitch graoph(s) will be added on to the selected pitch graph field(s) following the separator.\nThe default separator is an html line break "<br>".')
        self.ui.graphOverwrite.setToolTip('Pitch graph(s) will be generated into the selected pitch graph field(s),\noverwriting their current contents.')
        self.ui.graphIfEmpty.setToolTip('Pitch graph(s) will be only be added to the selected pitch graph field(s) if they are empty.')
        self.ui.graphSep.setToolTip('This is the separator to be used when adding pitch graph(s) to the selected pitch graph field(s)\' current contents.\nThe default separator is an html line break "<br>".')
        self.ui.lookAhead.setToolTip('This is the number of characters within which the addon will attempt to search for a recognizable word when using the "語" button, a larger number will be slightly slower.')
        self.ui.heibanColor.setToolTip('This is the color setting for words with a heiban (平板) pitch accent.')
        self.ui.atamadakaColor.setToolTip('This is the color setting for words with an atamadaka (頭高) pitch accent.')
        self.ui.nakadakaColor.setToolTip('This is the color setting for words with a nakadaka (中高) pitch accent.')
        self.ui.odakaColor.setToolTip('This is the color setting for words with an odaka (尾高) pitch accent.')
        self.ui.kifukuColor.setToolTip('This is the color setting for words with a kifuku (起伏) pitch accent.')
        self.ui.furiganaFontSize.setToolTip('This is the size setting of all displayed furigana.\nThe size is in relation to the percentage of the base word\'s, for\nexample 1 is 10\% of the baseword\' size, 2 is 20\%, and so on.')
        self.ui.bufferedOutput.setToolTip('The addon will load a card\'s text in chunks. This option is for very slow machines or \nuseful if a user has lots of cards with a huge amount of text. This option is\nexperimental and it is recommended that the user keeps text on their cards to a moderate length.')
        self.ui.displayShapes.setToolTip('If checked, pitch shapes signifying a word\'s alternate pitch accents will be displayed after\na word on the "coloredkanji", "coloredreading", and "coloredkanjireading" display type options.')
        self.ui.graphOnHover.setToolTip('If checked, the addon will display pitch accent graphs when hovering over a word.')
        self.ui.audioOnClick.setToolTip('If checked, audio will be played when clicking a word if it is available.\nNote that the audio will only be played for the first occurrence of the word within the pitch accent dictionary.')
        self.ui.katakanaConversion.setToolTip('If checked, all hiragana will be converted to katakana.')
        self.ui.historicalKanji.setToolTip('If checked, all kanji will be converted to their historical variants.')
        self.ui.historicalKana.setToolTip('If checked, all kana will be replaced with their historical spellings.')
        self.ui.originalLE.setToolTip('This is the text to be replaced.')
        self.ui.overwriteLE.setToolTip('This is the text that will replace the original text.')
        self.ui.ncAddCB.setToolTip('If selected, the rule to be added will be applied to the active fields \nin all new cards in your collection.')
        self.ui.lcAddCB.setToolTip('If selected, the rule to be added will be applied to the active fields \nin all cards you are currently studying in your collection.')
        self.ui.ncAllCB.setToolTip('If selected, all current overwrite rules will be applied to the active fields \nin all new cards in your collection.')
        self.ui.lcAllCB.setToolTip('If selected, all current overwrite rules will be applied to the active fields \nin all cards you are currently studying in your collection.')
        self.ui.addRuleButton.setToolTip('Adds a new overwrite rule and applies it to the collection if a checkbox is checked. \nRules are only applied to fields that have been designated an "active field" in the active fields tab.')
        self.ui.runRulesButton.setToolTip('Applies all overwrite rules to your collection. Rules are only applied to fields \nthat have been designated an "active field" in the active fields tab.')
        self.ui.importRules.setToolTip('Import an overwrite rules list. Options to overwrite or ignore duplicates, and to \noverwrite the current rules list with the newly imported list.')
        self.ui.exportRules.setToolTip('Export your current overwrite rules list.')
        

    def loadAllProfiles(self):
        if not self.sortedProfiles and not self.sortedNoteTypes:
            profL = []
            noteL = []
            for prof in self.cA:
                profL.append(prof)
                for noteType in self.cA[prof]:
                    noteL.append([noteType + ' (Prof:' + prof + ')', prof + ':pN:' + noteType])
            self.sortedProfiles = self.ciSort(profL)
            self.sortedNoteTypes = sorted(noteL, key=itemgetter(0))
        aP = self.ui.activeProfileCB
        for prof in self.sortedProfiles:
            aP.addItem(prof)
            aP.setItemData(aP.count() -1, prof, Qt.ToolTipRole)
        self.loadAllNotes()

    def loadAllNotes(self):
        for noteType in self.sortedNoteTypes:
            self.ui.activeNoteTypeCB.addItem(noteType[0])
            self.ui.activeNoteTypeCB.setItemData(self.ui.activeNoteTypeCB.count() - 1, noteType[0],Qt.ToolTipRole)
            self.ui.activeNoteTypeCB.setItemData(self.ui.activeNoteTypeCB.count() - 1, noteType[1])

    def clearAllAF(self):
        self.ui.activeProfileCB.clear()
        self.ui.activeNoteTypeCB.clear()
        self.ui.activeCardTypeCB.clear()
        self.ui.activeFieldCB.clear()
        self.ui.activeSideCB.clear()
        self.ui.activeDisplayTypeCB.clear()

    def initActiveFieldsCB(self):
        aP = self.ui.activeProfileCB
        aP.addItem('All')
        aP.addItem('──────────────────')
        aP.model().item(aP.count() - 1).setEnabled(False)
        aP.model().item(aP.count() - 1).setTextAlignment(Qt.AlignCenter)
        self.loadAllProfiles()  
        self.loadCardTypesFields()
        for key, value in self.sides.items():
            self.ui.activeSideCB.addItem(key)
            self.ui.activeSideCB.setItemData(self.ui.activeSideCB.count() - 1, value ,Qt.ToolTipRole)
        for key, value in self.displayTypes.items():
            self.ui.activeDisplayTypeCB.addItem(key)
            self.ui.activeDisplayTypeCB.setItemData(self.ui.activeDisplayTypeCB.count() - 1, value[1] ,Qt.ToolTipRole)
            self.ui.activeDisplayTypeCB.setItemData(self.ui.activeDisplayTypeCB.count() - 1, value[0])

    def loadProfileCB(self):
        pcb = self.ui.profilesCB
        pcb.addItem('All')
        pcb.addItem('──────')
        pcb.model().item(pcb.count() - 1).setEnabled(False)
        pcb.model().item(pcb.count() - 1).setTextAlignment(Qt.AlignCenter)
        for prof in self.cA:
            pcb.addItem(prof)
            pcb.setItemData(pcb.count() -1, prof, Qt.ToolTipRole)

    def loadProfilesList(self):
        pl = self.ui.profilesList
        profs = self.config['Profiles']
        if len(profs) == 0:
            pl.setText('<i>None currently selected.</i>')
        else:
            profl = []
            currentSelection = self.ui.profilesCB.currentText()
            for prof in  profs:
                if prof.lower() == 'all':
                    profl.append('All')
                    self.selectedProfiles = ['All']
                    if currentSelection == 'All':
                        self.ui.profilesPB.setText('Remove')
                        self.selectedProfiles = profl            
                        pl.setText('<i>All</i>')
                        return
                profl.append(prof)
                if currentSelection == prof:
                    self.ui.profilesPB.setText('Remove')
            self.selectedProfiles = profl            
            pl.setText('<i>' + ', '.join(profl) + '</i>')

    def loadAudioGraphFieldsCB(self):
        self.ui.audioFieldsCB.addItem('Clipboard')
        self.ui.audioFieldsCB.addItem('──────────────────')
        self.ui.audioFieldsCB.model().item(self.ui.audioFieldsCB.count() - 1).setEnabled(False)
        self.ui.audioFieldsCB.model().item(self.ui.audioFieldsCB.count() - 1).setTextAlignment(Qt.AlignCenter)
        self.ui.audioFieldsCB.addItems(self.allFields)
        self.ui.pitchGraphsCB.addItem('Clipboard')
        self.ui.pitchGraphsCB.addItem('──────────────────')
        self.ui.pitchGraphsCB.model().item(self.ui.pitchGraphsCB.count() - 1).setEnabled(False)
        self.ui.pitchGraphsCB.model().item(self.ui.pitchGraphsCB.count() - 1).setTextAlignment(Qt.AlignCenter)
        self.ui.pitchGraphsCB.addItems(self.allFields)

    def loadFieldsList(self, audio):
        if audio:
            fl = self.ui.audioFieldsList
            currentSelection = self.ui.audioFieldsCB.currentText()
            fs = self.config['AudioFields']
        else:
            fl = self.ui.pitchGraphsList
            currentSelection = self.ui.pitchGraphsCB.currentText()
            fs = self.config['PitchGraphFields']

        fieldList = fs.split(';')
        separator = False
        if len(fieldList) > 2:
            fields, addMode, separator = fieldList
        else:    
            fields, addMode = fieldList
        fields = fields.split(',')
        for idx, field in enumerate(fields):
            if field == 'clipboard':
                fields[idx] = 'Clipboard'
        if len(fields) == 1 and fields[0].lower() == 'none':
            fl.setText('<i>None currently selected.</i>')
        else:
            fl.setText('<i>' + ', '.join(fields) +'</i>')
        if audio:
            self.selectedAudioFields = fields
            if currentSelection in self.selectedAudioFields:
                self.ui.audioFieldsPB.setText('Remove')
        else:
            self.selectedGraphFields = fields 
            if currentSelection in self.selectedGraphFields:
                self.ui.pitchGraphsPB.setText('Remove')
        self.loadAddModes(addMode.lower(), separator, audio)
                
    def loadAddModes(self, addMode, separator, audio):
        if audio:
            add = self.ui.audioAdd
            overwrite = self.ui.audioOverwrite
            ifEmpty = self.ui.audioIfEmpty
            sepB = self.ui.audioSep
        else:
            add = self.ui.graphAdd
            overwrite = self.ui.graphOverwrite
            ifEmpty = self.ui.graphIfEmpty
            sepB = self.ui.graphSep
        if addMode == 'overwrite':
            overwrite.setChecked(True)
        elif addMode == 'add':
            add.setChecked(True)
        elif addMode == 'no':
            ifEmpty.setChecked(True)
        if separator:
            sepB.setText(separator)
        else:
            sepB.setText('<br>')
        if not add.isChecked():
            sepB.setEnabled(False)

    def addRemoveFromList(self, value, button, lWidget, vList, profiles = False):
        if button.text() == 'Remove':
            if value in vList:
                vList.remove(value)
                lWidget.setText(', '.join(vList))
                button.setText('Add')
                if len(vList) == 0:
                    lWidget.setText('<i>None currently selected.</i>')
        else:
            if profiles and value == 'All':
                vList.clear()
                vList.append('All')
                lWidget.setText('<i>All</i>')
                button.setText('Remove')
            else:
                if profiles:
                    if 'All' in vList:
                        vList.remove('All')
                vList.append(value)
                lWidget.setText('<i>'+ ', '.join(vList) + '</i>')
                button.setText('Remove')
                
    def profAudioGraphChange(self, value, button, vList):
        if value in vList:
            button.setText('Remove')
        else:
            button.setText('Add')


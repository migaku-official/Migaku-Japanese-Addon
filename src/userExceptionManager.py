# -*- coding: utf-8 -*-
# 
import re
import json
from . import Pyperclip 
from os.path import join, exists
from shutil import copyfile
from aqt.addcards import AddCards
from aqt.utils import  showInfo, askUser
from .addgui import Ui_Form
from aqt.qt import *
from aqt.editor import Editor
import anki.find
import codecs

class OgOvFilter(QSortFilterProxyModel):
    def __init__(self, model, parent = None):
        super(OgOvFilter, self).__init__(parent)
        self.setSourceModel(model)
        self.insertRows = model.insertRows
        self.strToCompare = ''

    def setFilterByColumn(self, strToCompare):
        self.strToCompare  = strToCompare
        self.invalidateFilter()

    # def lessThan(Left, right):
    #     leftRow = left.row()
    #     rightRow = right.row()
    #     leftIdx = sourceModel().index(leftRow, 0, QModelIndex())
    #     rightIdx = sourceModel().index(rightRow, 0, QModelIndex())
    #     leftOg = len(sourceModel().data(leftIdx).toString())
    #     rightOg = len(sourceModel().data(rightIdx).toString())
    #     leftIdx = sourceModel().index(leftRow, 1, QModelIndex())
    #     rightIdx = sourceModel().index(rightRow, 1, QModelIndex())
    #     leftOv = len(sourceModel().data(leftIdx).toString())
    #     rightOv = len(sourceModel().data(rightIdx).toString())

    #     # if left

    #     # if len(left)
    #     return False

    # def sort(self, col, order=QtCore.Qt.AscendingOrder):

    #     # Storing persistent indexes
    #     self.layoutAboutToBeChanged.emit()
    #     oldIndexList = self.persistentIndexList()
    #     oldIds = self._dfDisplay.index.copy()

    #     # Sorting data
    #     column = self._dfDisplay.columns[col]
    #     ascending = (order == QtCore.Qt.AscendingOrder)
    #     if column in self._sortBy:
    #         i = self._sortBy.index(column)
    #         self._sortBy.pop(i)
    #         self._sortDirection.pop(i)
    #     self._sortBy.insert(0, column)
    #     self._sortDirection.insert(0, ascending)
    #     self.updateDisplay()



    #     rl = self.ui.rulesTable
    #     foundOriginal = []
    #     foundOverwrite = []
    #     text = text.lower()
    #     for original, overwrite in self.ueMng.ueList.items():
    #         LOriginal = original.lower()
    #         LOverwrite = overwrite.lower()
    #         if LOriginal == text:
    #             foundOriginal.append([original, overwrite])
    #         elif text in LOriginal: 
    #             foundOriginal.append([original, overwrite])
    #         elif LOverwrite == text:
    #             foundOverwrite.append([original, overwrite])
    #         elif text in LOverwrite: 
    #             foundOverwrite.append([original, overwrite])   
    #     sorted(foundOriginal, key=len)
    #     sorted(foundOverwrite, key=len)

    #     for ogOv in foundOriginal:
    #         self.addRuleToList(ogOv[0], ogOv[1])
    #     for ogOv in foundOverwrite:
    #         self.addRuleToList(ogOv[0], ogOv[1])
    #     self.updateRuleCounter()







    #     # Updating persistent indexes
    #     newIds = self._dfDisplay.index
    #     newIndexList = []
    #     for index in oldIndexList:
    #         id = oldIds[index.row()]
    #         newRow = newIds.get_loc(id)
    #         newIndexList.append(self.index(newRow, index.column(), index.parent()))
    #     self.changePersistentIndexList(oldIndexList, newIndexList)
    #     self.layoutChanged.emit()
    #     self.dataChanged.emit(QtCore.QModelIndex(), QtCore.QModelIndex())


    # def sort(self, column, sortRole, text= False):
    #     # Storing persistent indexes
    #     self.layoutAboutToBeChanged.emit()
    #     oldIndexList = self.persistentIndexList()
    #     oldIds = self._dfDisplay.index.copy()


    #     # Updating persistent indexes
    #     newIds = self._dfDisplay.index
    #     newIndexList = []
    #     for index in oldIndexList:
    #         id = oldIds[index.row()]
    #         newRow = newIds.get_loc(id)
    #         newIndexList.append(self.index(newRow, index.column(), index.parent()))
    #     self.changePersistentIndexList(oldIndexList, newIndexList)
    #     self.layoutChanged.emit()
    #     self.dataChanged.emit(QtCore.QModelIndex(), QtCore.QModelIndex())
    #     
    def ascendingOrder(self):
        self.sourceModel().ueList = sorted(self.sourceModel().ueList)


    def testData(self, text):
        listBeforeReorder = self.sourceModel().ueList
        # showInfo(str(self.sourceModel().ueList))

        foundOriginal = []
        foundOverwrite = []
        notFound = []
        text = text.lower()
        for ogOv  in listBeforeReorder:
            original = ogOv[0]
            overwrite = ogOv[1]
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
            else:
                notFound.append([original, overwrite])   
        
        


        self.sourceModel().ueList = sorted(foundOriginal, key= lambda x: len(x[0])) + sorted(foundOverwrite,  key= lambda x: len(x[1])) + notFound
        # for ogOv in foundOriginal:
        #     self.addRuleToList(ogOv[0], ogOv[1])
        # for ogOv in foundOverwrite:
        #     self.addRuleToList(ogOv[0], ogOv[1])
        # self.updateRuleCounter()

    def saveList(self, path):
        ueList = self.sourceModel().ueList
        self.sourceModel().mng.ueList = ueList
        with codecs.open(path, "w","utf-8") as outfile:
            json.dump(ueList, outfile, ensure_ascii=False) 

    def filterAcceptsRow(self, sourceRow, sourceParent ):
        if self.strToCompare != '':
            ogIndex = self.sourceModel().index(sourceRow, 0, sourceParent)
           
            ovIndex = self.sourceModel().index(sourceRow, 1, sourceParent)
             
            if ogIndex.isValid() and ovIndex.isValid():
                og = self.sourceModel().data(ogIndex)
                ov = self.sourceModel().data(ovIndex)
                if self.strToCompare not in og and self.strToCompare not in ov:
                    return False
        return True

    def headerData(self, section, orientation, role):
        # if display role of vertical headers
        if orientation == Qt.Vertical and role == Qt.DisplayRole:
            # return the actual row number
            return section + 1
        # for other cases, rely on the base implementation
        return super(OgOvFilter, self).headerData(section, orientation, role)


class RulesModel(QAbstractTableModel):

    def __init__(self, ueList, manager, gui, parent=None):
        super(RulesModel, self).__init__(parent)
        self.ueList = ueList
        self.mng = manager
        self.gui = gui
        

    def rowCount(self, index=QModelIndex()):
        return len(self.ueList)

    def columnCount(self, index=QModelIndex()):
        return 2

    def data(self, index, role=Qt.DisplayRole):
        """ Depending on the index and role given, return data. If not 
            returning data, return None (PySide equivalent of QT's 
            "invalid QVariant").
        """

        if not index.isValid():
            return None

        if not 0 <= index.row() < len(self.ueList):
            return None
        # if role == Qt.BackgroundRole and index.column() == 2:
                # return self.create_gradient_brush()
        if role == Qt.DisplayRole or role == Qt.EditRole:
            original = self.ueList[index.row()][0]
            overwrite = self.ueList[index.row()][1]
            
            if index.column() == 0:
                return original
            elif index.column() == 1:
                return overwrite
            # elif index.column() == 2:
                # self.table.item(index.row(), 2).setStyleSheet('QTableView.item { background-color: blue;}')
                # return 'X'
            #     deleteRuleButton = QPushButton("X")
            #     deleteRuleButton.setFixedWidth(40)
                # deleteRuleButton.clicked.connect(self.removeRule)
                # self.table.setInsdexWidget(index, deleteRuleButton)
        
        return None

    # def showFullList(self):


    # def searchList(self):

    def headerData(self, section, orientation, role=Qt.DisplayRole):
        """ Set the headers to be displayed. """
        if role != Qt.DisplayRole:
            return None

        if orientation == Qt.Horizontal:
            if section == 0:
                return "Original"
            elif section == 1:
                return "Overwrite"
            # elif section == 2:
                # return ""
        if orientation == Qt.Vertical:
            return section + 1;
        return None

    def insertRows(self, position= False, rows=1, index=QModelIndex(), original= False, overwrite=False):
        """ Insert a row into the model. """
        if not position:
            position = self.rowCount()
        self.beginInsertRows(QModelIndex(), position, position)
        for row in range(rows):
            
            if original and overwrite:
                self.ueList.insert(position + row, [original, overwrite])
                # self.ueList.append([original, overwrite])
        self.endInsertRows()
        self.mng.saveUEList()
        return True

    def removeRows(self, position, rows=1, index=QModelIndex()):
        """ Remove a row from the model. """
        self.beginRemoveRows(QModelIndex(), position, position + rows - 1)

        del self.ueList[position:position+rows]
        self.endRemoveRows()
        self.mng.saveUEList()
        return True

    def setData(self, index, value, role=Qt.EditRole, overwriteRule = False, ruleDict = None):
        """ Adjust the data (set it to <value>) depending on the given 
            index and role. 
        """
        if role != Qt.EditRole:
            return False

        if overwriteRule and ruleDict['row'] < len(self.ueList):
            rule = self.ueList[ruleDict['row']]
            rule[0] = ruleDict['og']
            rule[1] = ruleDict['ov']
            self.mng.saveUEList()
            # self.dataChanged.emit(index, index)
            return True
        elif (index.isValid() and 0 <= index.row() < len(self.ueList)):
            rule = self.ueList[index.row()]
            if index.column() == 0 and self.checkRuleValidity(value, rule[1]) and value != rule[0] and self.mng.ruleExists(value, True) is False :
                rule[0] = value
            elif index.column() == 1 and self.checkRuleValidity(value, rule[0]) and value != rule[1]:
                rule[1] = value
            else:
                return False
            self.mng.saveUEList()
            self.dataChanged.emit(index, index)
            self.gui.openApplyRuleInquiry([[rule[0], rule[1]]])
            return True
        return False

    def checkRuleValidity(self, a, b):
        if a == b:
            showInfo('The original text and overwrite text cannot be the same.')
            return False
        elif a == '':
            showInfo('A rule must be at least one character long.')
            return False
        return True
                 

    def flags(self, index):
        """ Set the item flags at the given index. Seems like we're 
            implementing this function just to see how it's done, as we 
            manually adjust each tableView to have NoEditTriggers.
        """
        if not index.isValid():
            return Qt.ItemIsEnabled
        return Qt.ItemFlags(QAbstractTableModel.flags(self, index) |
                            Qt.ItemIsEditable)

class UserExceptionManager:


    def  __init__(self,mw, addon_path):
        self.mw = mw
        self.addon_path = addon_path
        self.listPath = False 
        self.activeFields = False
        self.model = False

    # def loadMainMenu(self):# loads menu into main JS menu as a new tab, uses UI, probably its own class that is accessed as a property

    def getListPath(self):
        # bigList = []
        # for i in range(100000):
        #     bigList.append(['b' + str(i), 'c' + str(i)])
        # with open(join(self.mw.col.media.dir(), 'biglistao.json'), 'w') as outfile:
        #     json.dump(bigList, outfile, ensure_ascii=False)
        return join(self.mw.col.media.dir(), '_userExceptionList.json')

    def updateCount(self, counter):
        counter.setText('Rule Count: ' + str(len(self.ueList)))

    def openAddMenu(self, editor = False, text = False):
        if editor:
            if isinstance(editor, Editor):
                self.addMenu = QWidget(editor.web)
            else:
                self.addMenu = QWidget(editor)
        else:
            self.addMenu = QWidget(self.mw)
        self.addMenu.setWindowIcon(QIcon(join(self.addon_path, 'icons', 'mia.png')))
        self.addMenu.setWindowFlags(Qt.Dialog |Qt.MSWindowsFixedSizeDialogHint)
        self.addMenu.ui = Ui_Form()
        self.addMenu.ui.setupUi(self.addMenu)
        self.updateCount(self.addMenu.ui.listCount)
        if not text and editor:
            text = editor.web.selectedText()
        if text:
            self.addMenu.ui.originalLE.setText(text)
            self.addMenu.ui.overwriteLE.setFocus()
        self.addMenu.show()
        self.addMenu.ui.addRuleButton.clicked.connect(self.addRuleAndClearText)
        

    # def addToUEList(self): # add new exception

    def addRuleAndClearText(self):
        if self.addRule(self.addMenu.ui.originalLE.text(), self.addMenu.ui.overwriteLE.text(), self.addMenu.ui.ncAddCB.isChecked(), self.addMenu.ui.lcAddCB.isChecked(), self.addMenu, True):
            self.addMenu.ui.originalLE.setText('')
            self.addMenu.ui.overwriteLE.setText('')

    def loadUEListFromJSON(self):
        with codecs.open(self.listPath, "r", "utf-8") as listFile:
            return json.load(listFile)

    def getUEList(self):  # loads UE List into a var from file, or returns an empty list
        self.listPath = self.getListPath()
        self.activeFields = False
        if exists(self.listPath): 
            self.ueList = self.loadUEListFromJSON()
        else:
            self.ueList = []
    

    def setupModel(self, gui):
        self.proxyFilter = OgOvFilter(RulesModel(self.ueList, self, gui))
        self.model = self.proxyFilter
        # self.proxyFilter.setSourceModel(RulesModel(self.ueList, self, gui))
        # self.model = RulesModel(self.ueList, self, gui)
        self.proxyFilter.setFilterKeyColumn(0)

    def addRule(self, original, overwrite, newCards, learnedCards, parentWidget, addMenu = False):
        if original == '' or overwrite == '':
            showInfo('The original and overwrite fields should not be empty.', title="MIA Japanese Support Notice")
            return False, False;
        if original == overwrite:
            showInfo('The original and overwrite fields should not contain the same text.', title="MIA Japanese Support Notice")
            return False, False;
        foundId = self.ruleExists(original)
        edit = False
        if foundId is not False:
            if not askUser('The rule "' + original + '" => "' + self.ueList[foundId][1] +'" already overwrites the given text. Would you like to overwrite it with your new rule?', title="MIA Japanese Support Add-on"):
                return False, False
            else:
                edit = True
        if edit: #setData(self, index, value, role=Qt.EditRole, overwriteRule = False, rule = None):
            self.model.setData(None, None, Qt.EditRole, True, {'row': foundId, 'og': original, 'ov': overwrite})
        else:
            self.writeRule(original, overwrite)
        if addMenu:
            self.updateCount(self.addMenu.ui.listCount)

        if newCards or learnedCards:
            self.applyRules([[original, overwrite]],  newCards, learnedCards, parentWidget) 

        return True, foundId;

    def ruleExists(self, original, message = False):

        for idx, ogOv in enumerate(self.ueList):
            if original == ogOv[0]:
                if message:
                    showInfo('A rule with this original value already exists ("' + original +'" => "' + self.ueList[idx][1] + '""), please ensure that you are defining a unique value.', title="MIA Japanese Support Error")
                return idx
        return False

    def writeRule(self, original, overwrite):
        if self.model:
            self.model.insertRows(original= original, overwrite= overwrite)
        else:
            self.ueList.append([original, overwrite])
        self.saveUEList()
        
    def getActiveFields(self):
        activeFieldsConfig = self.getConfig()['ActiveFields']
        activeFields = {}
        for af in activeFieldsConfig:
            splitAf = af.split(';')
            noteType = splitAf[2]
            field = splitAf[4]
            if noteType not in activeFields:
                activeFields[noteType] = [field]
            else:
                activeFields[noteType].append(field)
        return activeFields

    def getAllNotes(self):
        return anki.find.Finder(self.mw.col).findNotes('')


# "coloredhover;all;MIA Japanese;Sentence;Expression;front",
                        # "coloredkanjireading;all;MIA Japanese;Sentence;Expression;back",
                        # "coloredhover;all;MIA Japanese;Sentence;Meaning;back"
#
    def cardMeetsCriteria(self, cards, newCards, learnedCards):
        for card in cards:
            if (card.type == 0 and newCards) or ((card.type == 1 or card.type == 2) and learnedCards):
                return True
        return False
    
    def getProgressWidget(self, parentWidget, title):
        progressWidget = QWidget(parentWidget, Qt.Window)
        progressWidget.setWindowTitle(title)
        layout = QVBoxLayout()
        progressWidget.setFixedSize(400, 70)
        progressWidget.setWindowModality(Qt.ApplicationModal)
        bar = QProgressBar(progressWidget)
        if isMac:
            bar.setFixedSize(380, 50)
        else:
            bar.setFixedSize(390, 50)
        bar.move(10,10)
        per = QLabel(bar)
        per.setAlignment(Qt.AlignCenter)
        progressWidget.show()
        return progressWidget, bar; 

    def applyRules(self, ruleList, newCards, learnedCards, parentWidget, notes = False, message = False):
        if not self.activeFields:
            self.activeFields = self.getActiveFields()
        if not notes:
            notes = self.getAllNotes()
        altered = 0
        appliedRules = 0
        checkpointed = False
        progWid, bar = self.getProgressWidget(parentWidget, 'Applying Overwrite Rule(s)...')   
        bar.setMinimum(0)
        bar.setMaximum(len(notes))
        it = 0
        for nid in notes:
            note = self.mw.col.getNote(nid)
            alreadyAltered = False
            if not self.cardMeetsCriteria(note.cards(), newCards, learnedCards):
                continue
            noteType = note.model()
            if noteType['name'] in self.activeFields:
                fields = self.mw.col.models.fieldNames(note.model())
                for field in fields:
                    if field in self.activeFields[noteType['name']]:
                        for ogOv in ruleList:
                            original = ogOv[0] 
                            overwrite = ogOv[1]
                            # showInfo(original + ' ' + overwrite)
                            if original in note[field]:
                                # showInfo('found')
                                if not alreadyAltered:
                                    altered += 1
                                if not checkpointed:
                                    self.mw.checkpoint('Overwrite Rule Application')
                                    checkpointed = True
                                alreadyAltered = True
                                appliedRules += 1
                                note[field] = note[field].replace(original, overwrite)
                        note.flush()
            it += 1
            bar.setValue(it)
            self.mw.app.processEvents()            
        self.mw.reset()
        progWid.hide()
        showInfo('Rule(s) have been applied ' + str(appliedRules) + ' times.<br>' + str(altered) + ' notes have been altered.' , parent = parentWidget, title="MIA Japanese Support Notice")
                
    def applyRulesToText(self, text):
        for ogOv in self.ueList:
            original = ogOv[0] 
            overwrite = ogOv[1]
            if original in text:
                text = text.replace(original, overwrite)
        return text

    def saveUEList(self):  #saves UE List to file    
        self.model.saveList(self.listPath)
        # with codecs.open(self.listPath, "w","utf-8") as outfile:
            # json.dump(self.model.ueList, outfile, ensure_ascii=False)
        
    # def deleteRule(self, original):
    #     foundId = self.ruleExists(original)
    #     if foundId is not False:
    #         del self.ueList[foundId]

    def importUEList(self, fileName, combine, overwriteCollides):  #imports new list overwrite if desired
        # try:
            with open(fileName, "r", encoding="utf-8") as importedList:
                newList = json.load(importedList)

            if combine:
                tempUEList = self.model.sourceModel().ueList.copy()
                dictUEList = dict(tempUEList)
                totalImported = 0
                ignoredOrOverwritten = 0
                for ogOv in newList:
                    if len(ogOv) != 2:
                        showInfo('The overwrite rules list could not be imported. Please make sure the target file is a valid overwrite rules list and try again.', title="MIA Japanese Support Error")
                        return False
                    original = ogOv[0]  
                    overwrite = ogOv[1]
                    if not isinstance(original, str) or not isinstance(overwrite, str):
                        showInfo('The overwrite rules list could not be imported. Please make sure the target file is a valid overwrite rules list and try again.', title="MIA Japanese Support Error")
                        return False
                    if overwriteCollides:
                        if original in dictUEList:
                            ignoredOrOverwritten += 1
                            tempUEList.remove([original, dictUEList[original]])
                        tempUEList.append([original, overwrite])
                        totalImported += 1
                    else:
                        if original not in dictUEList:
                            tempUEList.append([original, overwrite])
                            totalImported += 1
                        else:
                            ignoredOrOverwritten += 1
                self.model.sourceModel().ueList = tempUEList
                self.saveUEList()
                
                return [totalImported, ignoredOrOverwritten]       
            else:


            # if combine:
            #     tempUEList = {}
            #     ogCount = len(self.ueList)
            #     original = next(iter(newList))
            #     if not isinstance(original, str) or not isinstance(newList[original], str):
            #         showInfo('The overwrite rules list could not be imported. Please make sure the target file is a valid overwrite rules list and try again.', title="MIA Japanese Support Error")
            #         return False
            #     if overwriteCollides:
            #         tempUEList.update(self.ueList)
            #         tempUEList.update(newList)
            #     else:
            #         tempUEList.update(newList)
            #         tempUEList.update(self.ueList)
            #     self.ueList = tempUEList
            #     self.saveUEList()

            #     return True       
            # else:
                self.model.sourceModel().ueList = newList
                self.saveUEList()
         
                return [len(self.ueList), 0]
        # except:
        #     showInfo('The overwrite rules list could not be imported. Please make sure the target file is a valid overwrite rules list and try again.', title="MIA Japanese Support Error")
        #     return False
    
    def getConfig(self):
        return self.mw.addonManager.getConfig(__name__)

    def exportUEList(self, fileName): #allow user to save a copy of their list where they want
        with open(fileName, 'w') as outfile:
            json.dump(self.ueList, outfile)
        showInfo('The overwrite rules list has been exported to "' + fileName +'"', title="MIA Japanese Support Notice")


    # def (self):

    # def (self):

    # def (self):

    # def (self):

    # def (self):

    # def (self):

    # def (self):

    # def (self):

    # def (self):

    # def (self):

    # def (self):
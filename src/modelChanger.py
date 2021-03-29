from aqt import mw
from aqt.browser import ChangeModel
from anki.hooks import wrap
from aqt.qt import *
from aqt.utils import askUser



def addLanguageModels():
    if not hasattr(mw, "migakuLanguageModels"):
        mw.migakuLanguageModels = {}
    mw.migakuLanguageModels["Migaku Japanese Sentence"] = { "valid-targets" : [
    "Migaku Japanese Sentence", 
    "Migaku Japanese Vocabulary", 
    "Migaku Japanese Audio Sentence", 
    "Migaku Japanese Audio Vocabulary"
    ],
    "fields" : ['Target Word', 'Sentence', 'Translation', 'Definitions', 'Image', 'Sentence Audio', 'Word Audio']
    }
    mw.migakuLanguageModels["Migaku Japanese Vocabulary"] = { "valid-targets" : [
    "Migaku Japanese Sentence", 
    "Migaku Japanese Vocabulary", 
    "Migaku Japanese Audio Sentence", 
    "Migaku Japanese Audio Vocabulary"
    ],
    "fields" : ['Target Word', 'Sentence', 'Translation', 'Definitions', 'Image', 'Sentence Audio', 'Word Audio']
    }
    mw.migakuLanguageModels["Migaku Japanese Audio Sentence"] = { "valid-targets" : [
    "Migaku Japanese Sentence", 
    "Migaku Japanese Vocabulary", 
    "Migaku Japanese Audio Sentence", 
    "Migaku Japanese Audio Vocabulary"
    ],
    "fields" : ['Target Word', 'Sentence', 'Translation', 'Definitions', 'Image', 'Sentence Audio', 'Word Audio']
    }
    mw.migakuLanguageModels["Migaku Japanese Audio Vocabulary"] = { "valid-targets" :  [
    "Migaku Japanese Sentence", 
    "Migaku Japanese Vocabulary", 
    "Migaku Japanese Audio Sentence", 
    "Migaku Japanese Audio Vocabulary"
    ],
    "fields" : ['Target Word', 'Sentence', 'Translation', 'Definitions', 'Image', 'Sentence Audio', 'Word Audio']
    }


addLanguageModels()

def migakuRebuildTemplateMap(self, key=None, attr=None):
    if not key:
        key = "t"
        attr = "tmpls"
    map = getattr(self, key + "widg")
    lay = getattr(self, key + "layout")
    src = self.oldModel[attr]
    dst = self.targetModel[attr]
    if map:
        try:
            lay.removeWidget(map)
            map.deleteLater()
            setattr(self, key + "MapWidget", None)
        except:
            pass
    map = QWidget()
    l = QGridLayout()
    combos = []
    targets = [x["name"] for x in dst] + [_("Nothing")]
    indices = {}
    for i, x in enumerate(src):
        l.addWidget(QLabel(_("Change %s to:") % x["name"]), i, 0)
        cb = QComboBox()
        cb.addItems(targets)
        idx = min(i, len(targets) - 1)
        cb.setCurrentIndex(idx)
        indices[cb] = idx
        qconnect(
            cb.currentIndexChanged,
            lambda i, cb=cb, key=key: self.onComboChanged(i, cb, key),
        )
        combos.append(cb)
        l.addWidget(cb, i, 1)
    map.setLayout(l)
    lay.addWidget(map)
    setattr(self, key + "widg", map)
    setattr(self, key + "layout", lay)
    setattr(self, key + "combos", combos)
    setattr(self, key + "indices", indices)


def migakuModelChanged(self, model):
    self.changeBetweenMigakuNoteTypes = False
    self.targetModel = model
    predeterminedTemplateAndFieldMap = changeIsBetweenValidMigakuNoteTypes(self.oldModel, self.targetModel)
    if predeterminedTemplateAndFieldMap:
        self.changeBetweenMigakuNoteTypes = predeterminedTemplateAndFieldMap
        if not hasattr(self, "migakuLabels") or not self.migakuLabels:
            replaceTemplateMap(self)
    else:
        maybeRemoveMigakuLabel(self)
        self.rebuildTemplateMap()
        self.rebuildFieldMap()

def getFieldNameList(fieldData):
    return [field['name'] for field in fieldData]

def fieldsAreTheSameAsTheDefault(testedNoteType, migakuNoteType):
    testedFields = getFieldNameList(testedNoteType["flds"])
    migakuFields = migakuNoteType["fields"]
    fieldsThatDontOccurInBoth = list(set(migakuFields)^set(testedFields))
    if len(fieldsThatDontOccurInBoth) == 0:
        return True
    return False

def changeIsBetweenValidMigakuNoteTypes(originalNoteType, targetNoteType):
    if originalNoteType["name"] in mw.migakuLanguageModels.keys():
        originMigakuNoteType = mw.migakuLanguageModels[originalNoteType["name"]]
        if onlyOneCardTypeInNoteType(originalNoteType) and fieldsAreTheSameAsTheDefault(originalNoteType, originMigakuNoteType):
            if targetNoteType["name"] in originMigakuNoteType["valid-targets"]:
                destinationMigakuNoteType = mw.migakuLanguageModels[targetNoteType["name"]]
                if onlyOneCardTypeInNoteType(targetNoteType) and fieldsAreTheSameAsTheDefault(targetNoteType, destinationMigakuNoteType):
                    fieldMap = generateFieldOrdinateMap(originalNoteType, targetNoteType)
                    templateMap = {0 : 0}
                    return [templateMap, fieldMap]
    return False

def onlyOneCardTypeInNoteType(noteType):
    if len(noteType["tmpls"]) == 1:
        return True
    return False

def generateFieldOrdinateMap(originalNoteType, targetNoteType):
    ogFields = originalNoteType["flds"]
    tFields = targetNoteType["flds"]
    fieldMap = {}
    for ogf in ogFields:
        ordinal = ogf["ord"]
        name = ogf["name"]
        targetOrdinal = getOrdinalForName(name, tFields)
        fieldMap[ordinal] = targetOrdinal
    return fieldMap 

def getOrdinalForName(name, fields):
    for field in fields:
        if field["name"] == name:
            return field["ord"]

{'name': 'Sentence', 'ord': 0, 'sticky': False, 'rtl': False, 'font': 'Arial', 'size': 20}

def maybeRemoveMigakuLabel(self):
    if hasattr(self, "migakuLabels") and self.migakuLabels:
        keys = ["t", "f"]
        for key in keys:
            lay = getattr(self, key + "layout")
            lay.removeWidget(self.migakuLabels[key])
            self.migakuLabels[key].deleteLater()
    self.migakuLabels = False   



def replaceTemplateMap(self):
    self.migakuLabels = {}
    keys = ["t", "f"]
    for key in keys:
        map = getattr(self, key + "widg")
        lay = getattr(self, key + "layout")
        self.migakuLabels[key] = QLabel('Migaku will automatically convert between these Note Types\nfor you. Simply press the "OK" button to proceed.')
        lay.addWidget(self.migakuLabels[key])
        if map:
            lay.removeWidget(map)
            map.deleteLater()
            setattr(self, key + "MapWidget", None)

def migakuAccept(self):
        # check maps
        if hasattr(self, "changeBetweenMigakuNoteTypes") and self.changeBetweenMigakuNoteTypes is not False:
            cmap, fmap = self.changeBetweenMigakuNoteTypes
        else:
            fmap = self.getFieldMap()
            cmap = self.getTemplateMap()
        if any(True for c in list(cmap.values()) if c is None):
            if not askUser(
                _(
                    """\
Any cards mapped to nothing will be deleted. \
If a note has no remaining cards, it will be lost. \
Are you sure you want to continue?"""
                )
            ):
                return
        self.browser.mw.checkpoint(_("Change Note Type"))
        b = self.browser
        b.mw.col.modSchema(check=True)
        b.mw.progress.start()
        b.model.beginReset()
        mm = b.mw.col.models
        mm.change(self.oldModel, self.nids, self.targetModel, fmap, cmap)
        b.search()
        b.model.endReset()
        b.mw.progress.finish()
        b.mw.reset()
        self.cleanup()
        QDialog.accept(self)

if not hasattr(ChangeModel, "migakuOveriddenMethods"):
    print("ADDED THROUGH JP")
    ChangeModel.migakuOveriddenMethods = True
    ChangeModel.accept = migakuAccept
    ChangeModel.modelChanged = migakuModelChanged
    ChangeModel.rebuildTemplateMap = migakuRebuildTemplateMap


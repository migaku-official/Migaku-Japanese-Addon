# -*- coding: utf-8 -*-
# 
from aqt.qt import *
import re
from aqt.utils import askUser
from os.path import join

class MassExporter:
    def  __init__(self, mw, exporter, addon_path):
        self.mw = mw
        self.exporter = exporter
        self.dictParser = self.exporter.dictParser
        self.addon_path = addon_path


    def onRegenerate(self, browser):
        import anki.find
        notes = browser.selectedNotes()
        if notes:
            fields = anki.find.fieldNamesForNotes(self.mw.col, notes)
            generateWidget = QDialog(None, Qt.Window)
            layout = QHBoxLayout()
            cbLabel = QLabel()
            cbLabel.setText('Origin:')
            cb = QComboBox()
            cb.addItems(fields)
            b1 = QCheckBox("Furigana")
            b1.setChecked(True)
            b2 = QCheckBox("Dict Form")
            b2.setChecked(True)
            b3 = QCheckBox("Accents")
            b3.setChecked(True)
            b4 = QCheckBox("Audio")
            b4.setChecked(True)
            b5 = QCheckBox("Graphs")
            b5.setChecked(True)
            destLabel =QLabel()
            destLabel.setText('Destination:')
            dest = QComboBox()
            dest.addItems(fields)
            addLabel =QLabel()
            addLabel.setText('Overwrite?:')
            addType = QComboBox()
            addType.addItems(['Add','Overwrite', 'If Empty'])
            b6 =  QPushButton('Execute')
            b6.clicked.connect(lambda: self.massGenerate(b1, b2, b3, b4, b5, str(cb.currentText()), notes, generateWidget, str(dest.currentText()), addType.currentText()))
            b7 =  QPushButton('Remove Readings')
            b7.clicked.connect(lambda: self.massRemove(str(cb.currentText()), notes, generateWidget))
            b8 =  QPushButton('Remove HTML')
            b8.clicked.connect(lambda: self.massRemoveHTML(str(cb.currentText()), notes, generateWidget))
            layout.addWidget(cbLabel)
            layout.addWidget(cb)
            layout.addWidget(b1)
            layout.addWidget(b2)
            layout.addWidget(b3)
            layout.addWidget(b4)
            layout.addWidget(b5)
            layout.addWidget(destLabel)
            layout.addWidget(dest)
            layout.addWidget(addLabel)
            layout.addWidget(addType)
            layout.addWidget(b6)
            layout.addWidget(b7)
            layout.addWidget(b8)
            generateWidget.setWindowTitle("Generate Accents And Furigana")
            generateWidget.setLayout(layout)
            generateWidget.exec_()
        else:
            showInfo('Please select some cards before attempting to mass generate.', title="MIA Japanese Support Error")



    def imgRemove(self, text):
        pattern = r"(?:<img[^<]+?>)"
        finds = re.findall(pattern, text)
        text = re.sub(r"<img[^<]+?>", "--=HTML=--", text)
        return finds,text;

    def replaceImg(self, text, matches):
        if matches:
            for match in matches:
                text = text.replace("--=HTML=--", match, 1)
        return text

    def removeHTML(self, text):
          text = text.replace('<br>', '---newline---')
          text = re.sub(r'<span class="[^<]*?">◆<\/span>', "", text)
          matches, text = self.imgRemove(text)
          text = re.sub(r'<[^<]*?>', "", text)
          text = self.replaceImg(text, matches)
          text = text.replace('---newline---', '<br>');
          return text

    def massRemoveHTML(self, field,  notes, generateWidget):
        if not askUser('Are you sure you want to mass remove HTML from the "'+ field +'" field? This will not remove images, or "<br>" defined line breaks, but will remove pitch shapes from the previous beta version of the MIA Japanese Support Addon.'):
            return
        self.mw.checkpoint('Mass HTML Removal')    
        generateWidget.close() 
        progWid, bar = self.getProgressWidget()   
        bar.setMinimum(0)
        bar.setMaximum(len(notes))
        val = 0;  
        for nid in notes:
            note = self.mw.col.getNote(nid)
            fields = self.mw.col.models.fieldNames(note.model())
            if field in fields:
                text = note[field] 
                text =  self.removeHTML(text)
                note[field] = text
                note.flush()
            val+=1;
            bar.setValue(val)
            self.mw.app.processEvents()
        self.mw.progress.finish()
        self.mw.reset()

    def getProgressWidget(self):
        progressWidget = QWidget(None)
        layout = QVBoxLayout()
        progressWidget.setFixedSize(400, 70)
        progressWidget.setWindowModality(Qt.ApplicationModal)
        progressWidget.setWindowTitle('Generating...')
        progressWidget.setWindowIcon(QIcon(join(self.addon_path, 'icons', 'mia.png')))
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

    def massRemove(self, field,  notes, generateWidget):
        if not askUser('Are you sure you want to mass remove readings from the "'+ field +'" field? .'):
            return
        self.mw.checkpoint('Mass Accent Removal')
        generateWidget.close() 
        progWid, bar = self.getProgressWidget()   
        bar.setMinimum(0)
        bar.setMaximum(len(notes))
        val = 0;  
        for nid in notes:
            note = self.mw.col.getNote(nid)
            fields = self.mw.col.models.fieldNames(note.model())
            if field in fields:
                text = note[field] 
                text =  self.exporter.removeBrackets(text)
                note[field] = text
                note.flush()
            val+=1;
            bar.setValue(val)
            self.mw.app.processEvents()
        self.mw.progress.finish()
        self.mw.reset()

    def massGenerate(self, furigana, dictform, accents, audio, charts, field,  notes, generateWidget, dest, addType):
        if not askUser('Are you sure you want to generate from the "' + field + '" field into the "'+ dest +'" field? This action can not be undone.'):
            return
        self.mw.checkpoint('Mass Accent Generation')
        generateWidget.close() 
        progWid, bar = self.getProgressWidget()   
        bar.setMinimum(0)
        bar.setMaximum(len(notes))
        val = 0;  
        for nid in notes:
            note = self.mw.col.getNote(nid)
            fields = self.mw.col.models.fieldNames(note.model())
            if field in fields and dest in fields:
                text = note[field] 
                newText = text
                text = text.replace('</div> <div>', '</div><div>')
                htmlFinds, text = self.exporter.htmlRemove(text)
                text, sounds = self.exporter.removeBrackets(text, True)
                text = text.replace(',&', '-co-am-')
                text, invalids = self.exporter.replaceInvalidChars(text);
                text = self.mw.col.media.strip(text).encode("utf-8", "ignore")
                results = self.dictParser.getParsed(text)
                results = self.exporter.wordData(results)
                text, audioGraphList = self.dictParser.dictBasedParsing(results, newText, False, [furigana.isChecked(), dictform.isChecked(), accents.isChecked(), audio.isChecked(), charts.isChecked()])
                if htmlFinds:
                    text = self.exporter.replaceHTML(text, htmlFinds)
                for match in sounds:
                    text = text.replace("-_-AUDIO-_-", match, 1)
                if text:
                    text = self.exporter.returnInvalids(text, invalids)
                    text = text.replace('-co-am-', ',&').strip()
                    if addType == 'If Empty':
                        if note[dest] == '':
                            note[dest] = text
                    elif addType == 'Add':
                        if note[dest] == '':
                            note[dest] = text
                        else:
                            note[dest] += '<br>' + text
                    else:
                        note[dest] = text    
                if audioGraphList:
                    self.exporter.addVariants(audioGraphList, note)
                if text or audioGraphList:       
                    note.flush()
            val+=1;
            bar.setValue(val)
            self.mw.app.processEvents()
        self.mw.progress.finish()
        self.mw.reset()
# -*- coding: utf-8 -*-
# 

import aqt
from aqt.qt import *
from os.path import dirname, join
from aqt.webview import AnkiWebView
import os
from aqt import mw
from os.path import dirname, join, basename, exists, join
from anki.hooks import addHook

addon_path = dirname(__file__)

def miMessage(text, parent=False):
    title = "Migaku"
    if parent is False:
        parent = aqt.mw.app.activeWindow() or aqt.mw
    icon = QIcon(join(addon_path, 'icons', 'migaku.png'))
    mb = QMessageBox(parent)
    mb.setWindowIcon(icon)
    mb.setWindowTitle(title)
    cb = QCheckBox("Don't show me this again.")
    wv = AnkiWebView()
    wv.setFixedSize(700, 700)
    wv.page().setHtml(text)
    wide = QWidget()
    wide.setFixedSize(18,18)
    mb.layout().addWidget(wv, 0, 1)
    mb.layout().addWidget(wide, 0, 2)
    mb.layout().setColumnStretch(0, 3)
    mb.layout().addWidget(cb, 1, 1)
    b = mb.addButton(QMessageBox.Ok)
    b.setFixedSize(100, 30)
    b.setDefault(True)
    mb.exec_()
    wv.deleteLater()
    if cb.isChecked():
        return True
    else:
        return False


migakuMessage = '''
<style>
    h3 {
        margin-top:15px;
        margin-left:15px;
        font-weight: 600;
        font-family: NeueHaas, input mono, sans-serif;
        color: #1e1e1e;
    }
    div {
        margin-left:15px;
        line-height: 1.5;
        font-family: Helmet,Freesans,Helvetica,Arial,sans-serif;
        color: #404040;
    }

    span{
        margin-left:15px;
        color:gray;
        font-size:13;
        font-family: Helmet,Freesans,Helvetica,Arial,sans-serif;
    }
    iframe{
        margin-left:15px;
    }
</style>
<h3>The MIA Add-On Series Is Now the Migaku Add-On Series!</h3>
<span>A message from Lucas (Yoga)<br><br></span>
<div style="">
    If you would like to know more about why this change in branding is happening.<br />
    Please watch the video!<br />
    Watch the video in your browser by clicking this link:<br />
    <a href="https://youtu.be/ztk54w8Bems">https://youtu.be/ztk54w8Bems</a>
</div>
<br>
<h3>The Truth About Matt vs. Japan and Why I’m Leaving MIA</h3>
<iframe width="640" height="360" src="https://www.youtube.com/embed/ztk54w8Bems" frameborder="0" allow="accelerometer; autoplay; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe>
</div>
<script>
    window.addEventListener("load", function () {
        var outsidelinks = document.getElementsByClassName("outsideLink");
        for (var i = 0; i < outsidelinks.length; i++) {
            outsidelinks[i].addEventListener("click", function (e) {
                pycmd("openLink:" + this.href);
            });
        }
    });
</script>
'''

def migakuMessageNeverShown():
    filePath = join(addon_path, "migakuMessageShown.txt")
    if not os.path.exists(filePath):
        return True
    return False

def createMigakuAlreadyShownFile():
    filePath = join(addon_path, "migakuMessageShown.txt")
    with open(filePath, "w") as file:
        file.write("Message Already Shown") 

def attemptShowMigakuBrandUpdateMessage():
    
    filePath = join(addon_path, "migakuMessageShown.txt")
    if not hasattr(mw, 'MigakuBrandUpdateMessage'):
        if migakuMessageNeverShown():
            mw.MigakuBrandUpdateMessage = True
            if miMessage(migakuMessage):
                createMigakuAlreadyShownFile()
    else:
        if migakuMessageNeverShown():
            createMigakuAlreadyShownFile()
            


addHook("profileLoaded", attemptShowMigakuBrandUpdateMessage)
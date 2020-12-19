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
import requests as req
import re
from aqt.utils import openLink


def attemptOpenLink(cmd):
    if cmd.startswith('openLink:'):
        openLink(cmd[9:])



addon_path = dirname(__file__)


def getConfig():
        return mw.addonManager.getConfig(__name__)

def saveConfiguration(newConf):
    mw.addonManager.writeConfig(__name__, newConf)

def getLatestVideos(config):
    try:
        resp = req.get("https://www.youtube.com/c/ImmerseWithYoga/videos")
        pattern = "\{\"videoId\"\:\"(.*?)\""
        matches = re.findall(pattern ,resp.text)
        videoIds = list(dict.fromkeys(matches))
        lastId = config["lastId"]
        if videoIds[0] == lastId:
            print("FAILED")
            return False, False
        
        videoEmbeds = []
        count = 0
        for vid in videoIds:
            if count > 6:
                break
            count+=1
            if (count == 1):
                videoEmbeds.append("<h2>A New Video Has Been Released!</h2>")
                videoEmbeds.append('<div class="iframe-wrapper"><div class="clickable-video-link" data-vid="'+ vid + '"></div><iframe width="640" height="360" src="https://www.youtube.com/embed/'+ vid + '" frameborder="0" allow="accelerometer; autoplay; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe></div>')
            else:
                if (count == 2):
                    videoEmbeds.append("<h2>Previous Videos:</h2>")
                videoEmbeds.append('<div class="iframe-wrapper" style="display:inline-block"><div class="clickable-video-link" data-vid="'+ vid + '"></div><iframe width="320" height="180" src="https://www.youtube.com/embed/'+ vid + '" frameborder="0" allow="accelerometer; autoplay; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe></div>')
        return "".join(videoEmbeds), videoIds[0]
    except:
        return False, False
    
    



def miMessage(text, parent=False):
    title = "Migaku"
    if parent is False:
        parent = aqt.mw.app.activeWindow() or aqt.mw
    icon = QIcon(join(addon_path, 'icons', 'migaku.png'))
    mb = QMessageBox(parent)
    mb.setWindowIcon(icon)
    mb.setWindowTitle(title)
    cb = QCheckBox("Don't show me the notice about this video again.")
    wv = AnkiWebView()
    wv._page._bridge.onCmd = attemptOpenLink
    wv.setFixedSize(680, 450)
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
    body{
    margin:0px;
    padding:0px;
    background-color: white !important;
    }
    h3 {
        margin-top:5px;
        margin-left:15px;
        font-weight: 600;
        font-family: NeueHaas, input mono, sans-serif;
        color: #404040;
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

    .iframe-wrapper{
        position:relative;
        margin-left:0px;
        line-height: 1;
    }

    .clickable-video-link{
        position:absolute;
        v-index:10;
        width:100%%;
        top:0px;
        left;0px;
        height:20%%;
        margin-left:0px;
        line-height: 1;
        cursor:pointer;

    }
</style>
<body>
<h3><b>Thanks so much for using the Migaku Add-on series!</b></h3>
<div class="center-div">
    If you would like to ensure you don't miss any Migaku updates, or new releases.<br>
    Please consider following us on <a href="https://www.youtube.com/c/ImmerseWithYoga">YouTube</a> and <a href="https://twitter.com/Migaku_Yoga">Twitter</a>!
    <br>And please consider supporting Migaku on <a href="https://www.patreon.com/Migaku">Patreon</a> if you have found value in our work!
</div>
<div>
%s
</div>
<script>

        const vids = document.getElementsByClassName("clickable-video-link");
        for (var i = 0; i < vids.length; i++) {
            vids[i].addEventListener("click", function (e) {
                const vidId = e.target.dataset.vid;
                pycmd("openLink:https://www.youtube.com/watch?v=" + vidId);
            });
        }

</script>
</body>
'''

def attemptShowMigakuBrandUpdateMessage():
    config = getConfig()
    shouldShow = config["displayAgain"]
    filePath = join(addon_path, "migakuMessageShown.txt")
    if not hasattr(mw, "MigakuMessageContent"):
        mw.MigakuMessageContent = getLatestVideos(config)
    videoIds,videoId = mw.MigakuMessageContent
    if not hasattr(mw, "MigakuShouldNotShowMessage"):
        if videoIds:
            config["displayAgain"] = True
            saveConfiguration(config)
            if miMessage(migakuMessage%videoIds):
                config["lastId"] = videoId
                config["displayAgain"] = False
                saveConfiguration(config)
        elif shouldShow:
            if miMessage(migakuMessage%""):
                    config["displayAgain"] = False
                    saveConfiguration(config)
        mw.MigakuShouldNotShowMessage = True
    else:
        if videoId:
            config["lastId"] = videoId
        config["displayAgain"] = False
        saveConfiguration(config)
        

     
addHook("profileLoaded", attemptShowMigakuBrandUpdateMessage)




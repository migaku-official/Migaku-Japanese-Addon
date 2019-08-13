# -*- coding: utf-8 -*-
# 

import aqt
from aqt.qt import *
from os.path import dirname, join

addon_path = dirname(__file__)

def miInfo(text, parent=False, level = 'msg'):
    if level == 'wrn':
        title = "Japanese Support Warning"
    elif level == 'not':
        title = "Japanese Support Notice"
    elif level == 'err':
        title = "Japanese Support Error"
    else:
        title = "Japanese Support Add-on"
    if parent is False:
        parent = aqt.mw.app.activeWindow() or aqt.mw
    icon = QIcon(join(addon_path, 'icons', 'mia.png'))
    mb = QMessageBox(parent)
    mb.setText(text)
    mb.setWindowIcon(icon)
    mb.setWindowTitle(title)
    b = mb.addButton(QMessageBox.Ok)
    b.setDefault(True)

    return mb.exec_()

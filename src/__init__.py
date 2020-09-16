# -*- coding: utf-8 -*-
#Thanks to Damien Elmes, the Migaku Japanese Add-on borrows lightly from his project.
#https://ankiweb.net/shared/info/3918629684
#
#Thanks to Asweigart, I use Pyperclip in this project
#https://github.com/asweigart/pyperclip
#
#And thanks to 奈幾乃 for the historical converter code
#http://mto.herokuapp.com/
#
# This is a beta prototype release, when officially released a fully commented version of this project will be added and linked on GitHub
# The final release will also be organized into individual .py files by functionality.
# Lucas - Migaku Founder

from . import models
from anki.hooks import addHook
addHook("profileLoaded", models.addModels)

from . import main, migakuMessage
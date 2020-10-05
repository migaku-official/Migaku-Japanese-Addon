# -*- coding: utf-8 -*-

# This file is based on the Japanese Support add-on's reading.py, which can be
# found at <https://github.com/ankitects/anki-addons>.
#
# Copyright: Ankitects Pty Ltd and contributors
# License: GNU GPL, version 3 or later; http://www.gnu.org/copyleft/gpl.html
#
# Automatic reading generation with kakasi and mecab.
#

import sys, os, platform, re, subprocess, aqt.utils
from anki.utils import stripHTML, isWin, isMac
from anki.hooks import addHook
from . import Pyperclip
from aqt import mw
from aqt.qt import *
from aqt.utils import showInfo
from .constants import *

BUFFER_SIZE = '819200'
config = mw.addonManager.getConfig(__name__)

kakasiArgs = ["-isjis", "-osjis", "-u", "-JH", "-KH"]
mecabArgs = ['--node-format=%m[%f[7]] ', '--eos-format=\n',
            '--unk-format=%m[] ']

supportDir = os.path.join(os.path.dirname(__file__), "support")

def htmlReplace(text):
    pattern = r"(?:<[^<]+?>)"
    finds = re.findall(pattern, text)
    text = re.sub(r"<[^<]+?>", HTML_REPLACER, text)
    return finds,text;

def escapeText(text):
    text = text.replace("\n", " ")
    text = text.replace(u'\uff5e', "~")
    text = re.sub("<br( /)?>", NEWLINE_REPLACER, text)
    matches, text = htmlReplace(text)

    text = text.replace(NEWLINE_REPLACER, "<br>")
    return matches, text;

if sys.platform == "win32":
    si = subprocess.STARTUPINFO()
    try:
        si.dwFlags |= subprocess.STARTF_USESHOWWINDOW
    except:
        si.dwFlags |= subprocess._subprocess.STARTF_USESHOWWINDOW
else:
    si = None

# Mecab
##########################################################################

def mungeForPlatform(popen):
    if isWin:
        popen = [os.path.normpath(x) for x in popen]
        popen[0] += ".exe"
    elif not isMac:
        popen[0] += ".lin"
    return popen

class MecabController(object):

    def __init__(self):
        self.mecab = None 

    def setup(self):
        self.mecabCmd = mungeForPlatform(
            [os.path.join(supportDir, "mecab")] + mecabArgs + [
                '-d', supportDir, '-r', os.path.join(supportDir,"mecabrc"), '-b', BUFFER_SIZE ])
        self.mecabCmdAlt = mungeForPlatform([
            os.path.join(supportDir, "mecab"),
            "-r", os.path.join(supportDir, "mecabrc"),
            "-d", supportDir, '-b', BUFFER_SIZE
            ])
        os.environ['DYLD_LIBRARY_PATH'] = supportDir
        os.environ['LD_LIBRARY_PATH'] = supportDir
        if not isWin:
            os.chmod(self.mecabCmd[0], 0o755)

    def ensureOpen(self, details = False):
        if not self.mecab:
            self.setup()
            if details:
                cmd = self.mecabCmdAlt
            else:
                cmd = self.mecabCmd
            try:
                self.mecab = subprocess.Popen(
                    cmd, bufsize=-1, stdin=subprocess.PIPE,
                    stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                    startupinfo=si)
            except OSError:
                raise Exception("Please ensure your Linux system has 64 bit binary support.")

    # def accents(self, text):
    #     self.ensureOpen(True)
    #     self.mecab.stdin.write(text + b"\n")
    #     self.mecab.stdin.flush()
    #     results, err = self.mecab.communicate()
    #     results = results.decode('utf-8', "ignore").split("\n")
    #     self.mecab = None

    #     return results

    def accents(self, text):
        text = text.replace('\n','').encode("utf-8", "ignore")
        self.ensureOpen(True)
        self.mecab.stdin.write(text + b"\n")
        self.mecab.stdin.flush()
        final = []
        while True:
            results = self.mecab.stdout.readline()
            results = results.decode('utf-8', "ignore")
            if results == 'EOS\r\n' or results == 'EOS\n':
                break
            final.append(results.replace('\r', '').replace('\n', ''))
        return final

    def reading(self, expr):

        self.ensureOpen()
        matches, expr = escapeText(expr)
        self.mecab.stdin.write(expr.encode('utf-8', "ignore") + b'\n')
        self.mecab.stdin.flush()
        expr = self.mecab.stdout.readline().rstrip(b'\r\n').decode('utf-8', "ignore")
        out = []
        for node in expr.split(" "):
            if not node:
                break
            (kanji, reading) = re.match("(.+)\[(.*)\]", node).groups()
            if kanji == reading or not reading:
                out.append(kanji)
                continue
            if kanji == kakasi.reading(reading):
                out.append(kanji)
                continue
            reading = kakasi.reading(reading)
            if reading == kanji:
                out.append(kanji)
                continue
            if kanji in u"一二三四五六七八九十０１２３４５６７８９":
                out.append(kanji)
                continue
            placeL = 0
            placeR = 0
            for i in range(1,len(kanji)):
                if kanji[-i] != reading[-i]:
                    break
                placeR = i
            for i in range(0,len(kanji)-1):
                if kanji[i] != reading[i]:
                    break
                placeL = i+1
            if placeL == 0:
                if placeR == 0:
                    out.append(" %s[%s]" % (kanji, reading))
                else:
                    out.append(" %s[%s]%s" % (
                        kanji[:-placeR], reading[:-placeR], reading[-placeR:]))
            else:
                if placeR == 0:
                    out.append("%s %s[%s]" % (
                        reading[:placeL], kanji[placeL:], reading[placeL:]))
                else:
                    out.append("%s %s[%s]%s" % (
                        reading[:placeL], kanji[placeL:-placeR],
                        reading[placeL:-placeR], reading[-placeR:]))
        fin = u""
        for c, s in enumerate(out):
            s += " "
            # if c < len(out) - 1 and re.match("^[A-Za-z0-9]+$", out[c+1]):
            #     s += " "
            fin += s
        for match in matches:
            fin = fin.replace(HTML_REPLACER, match, 1)

        return re.sub(r'& ?nbsp ?;', ' ', re.sub(r"< ?br ?>", "<br>", fin.strip()))

class KakasiController(object):

    def __init__(self):
        self.kakasi = None

    def setup(self):
        self.kakasiCmd = mungeForPlatform(
            [os.path.join(supportDir, "kakasi")] + kakasiArgs)
        os.environ['ITAIJIDICT'] = os.path.join(supportDir, "itaijidict")
        os.environ['KANWADICT'] = os.path.join(supportDir, "kanwadict")
        if not isWin:
            os.chmod(self.kakasiCmd[0], 0o755)

    def ensureOpen(self):
        if not self.kakasi:
            self.setup()
            try:
                self.kakasi = subprocess.Popen(
                    self.kakasiCmd, bufsize=-1, stdin=subprocess.PIPE,
                    stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                    startupinfo=si)
            except OSError:
                raise Exception("Please install kakasi")

    def reading(self, expr):
        self.ensureOpen()
        placeholder, expr = escapeText(expr)
        self.kakasi.stdin.write(expr.encode("sjis", "ignore") + b'\n')
        self.kakasi.stdin.flush()
        res = self.kakasi.stdout.readline().rstrip(b'\r\n').decode("sjis")
        return res

kakasi = KakasiController()


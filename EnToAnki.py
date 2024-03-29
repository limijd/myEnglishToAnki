#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import os
import sys
import re
import json
import argparse
import html2text

SCRIPT_PATH=os.path.dirname(os.path.realpath(__file__))
from EnChDict import EnChDict
stardict_db = "%s/stardict.sqlite.db" % SCRIPT_PATH
ANKI_ENGLISH_NOTE_FIELDS = ["word", "phonetic", "definition", "translation", "exchange", "detail", "bnc", "frq", "tts"]

class EnglishToAnki:
    def __init__(self, args=None):
        if not os.path.exists(stardict_db):
            print("%s doesn't exist, please decompress/copy the dictionary."%stardict_db)
            sys.exit(1)
        self.en_ch_dict = EnChDict(stardict_db)
        if args and args.enable_google_tts:
            self.en_ch_dict.EnableGoogleTTS()
        self.all_words = {}
        self.import_words = {}
        self.args = args
        return

    def processWordList(self, words):
        assert isinstance(words, list)
        for word in words:
            word = word.strip()
            self.all_words[word] = None
            for p in word.split(","):
                p = p.strip()
                self.all_words[p] = None
                for w in  re.findall(r'[a-zA-Z]+', p):
                    if len(w) > 1:
                        self.all_words[w] = None
        return

    def processTextList(self, textList):
        for text in textList:
            lines = text.split("\n")
            for line in lines:
                line=line.strip()
                #print("process line: %s"%line)
                if line[0] == '"' and line[-1] == '"' and len(line)>2:
                    w = line[1:-1]
                    w = w.lower()
                    self.all_words[w] = None
                    continue
                for w in re.findall(r'[a-zA-Z]+', line):
                    if len(w) > 1:
                        w = w.lower()
                        self.all_words[w] = None
        return

    def lookup_startdict(self):
        words = list(self.all_words.keys())
        #print("Looking up: %s"% ",".join(words))
        result, failed_list = self.en_ch_dict.lookup_stardict_sql(words)

        for k in result:
            self.all_words[k] = result[k]
            self.import_words[k] = result[k]

    def genAnkiCards(self, tts_dir=None):
        if not tts_dir:
            tts_dir = self.getAnkiTTSDir()
        anki_cards = self.en_ch_dict.result_to_anki(self.import_words, ANKI_ENGLISH_NOTE_FIELDS, tts_dir)
        return anki_cards

    def writeAnkiImportFile(self):
        if not self.args:
            assert 0 and "Output file is not specified" 
            return
        fp = open(self.args.out, "w")
        anki_cards = self.en_ch_dict.result_to_anki(self.import_words, ANKI_ENGLISH_NOTE_FIELDS, self.getAnkiTTSDir())
        for ac in anki_cards:
            fp.write(ac.encode("utf-8"))
            fp.write("\n")
        fp.close()

    def getAnkiDB(self):
        fp = open(os.path.expanduser("~/.configs.secure/evernote_to_anki.config.json"), "r")
        js = json.load(fp)
        self.anki_db = js["anki_db"]
        fp.close()
        return self.anki_db

    def getAnkiTTSDir(self):
        fp = open(os.path.expanduser("~/.configs.secure/evernote_to_anki.config.json"), "r")
        js = json.load(fp)
        anki_db = js["anki_db"]
        fp.close()

        dirs = anki_db.split("/")
        dirs[-1] = "collection.media"
        self.anki_tts_dir  = "/".join(dirs)
        return self.anki_tts_dir


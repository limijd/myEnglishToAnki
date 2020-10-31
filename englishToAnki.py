#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import os
import sys
import re
import json
import argparse
import logging
import html2text

SCRIPT_PATH=os.path.dirname(os.path.realpath(__file__))
sys.path.insert(0, "%s/evernote/lib"%SCRIPT_PATH)

from EnChDict import EnChDict
from EvernoteReader import EvernoteReader

ecdict_db = "%s/myDictDB/ecdict.sqlite.db" % SCRIPT_PATH
stardict_db = "%s/myDictDB/stardict.sqlite.db" % SCRIPT_PATH
ANKI_ENGLISH_NOTE_FIELDS = ["word", "phonetic", "definition", "translation", "exchange", "detail", "bnc", "frq", "tts"]


class EnglishToAnki:
    def __init__(self, args):
        self.en_ch_dict = EnChDict(stardict_db)
        if args.enable_google_tts:
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
            for w in re.findall(r'[a-zA-Z]+', text):
                if len(w) > 1:
                    self.all_words[w] = None
        return

    def lookup_startdict(self):
        words = self.all_words.keys()
        result, failed_list = self.en_ch_dict.lookup_stardict_sql(words)

        for k in result:
            self.all_words[k] = result[k]
            self.import_words[k] = result[k]


    def writeAnkiImportFile(self):
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


def main():
    """ entry of program """
    parser = argparse.ArgumentParser(prog=os.path.basename(__file__)
            , description="englishToAnki: add English to my ANKI database")
    parser.add_argument('-d', '--debug', action='store_true', help="debug mode")
    parser.add_argument('-nb', '--notebook', default='AnkiQuickNotes', help="Evernote notebook to be read")
    parser.add_argument('-o', '--out', default='anki.english.import.txt', help="output file for importing to ANKI")
    parser.add_argument('-egt', '--enable_google_tts', default=True, help="enable google tts")

    args = parser.parse_args()

    if args.debug:
        logging.basicConfig(format='[eta: %(asctime)s %(levelname)s] %(message)s',
                            datefmt='%Y-%m-%d %H:%M:%S', level=logging.DEBUG)
    else:
        logging.basicConfig(format='[eta: %(asctime)s %(levelname)s] %(message)s',
                            datefmt='%Y-%m-%d %H:%M:%S', level=logging.INFO)

    eta = EnglishToAnki(args)
    nr = EvernoteReader(args.notebook, only_tag="English")
    eta.processWordList(nr.getTitleList())
    eta.processTextList(nr.getContentList())

    eta.lookup_startdict()
    eta.writeAnkiImportFile()

    logging.info("Evernote to ANKI completed successfully.")

if __name__ == "__main__":
    main()

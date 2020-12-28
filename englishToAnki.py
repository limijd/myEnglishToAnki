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

from EvernoteReader import EvernoteReader
from EnToAnki import EnglishToAnki

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

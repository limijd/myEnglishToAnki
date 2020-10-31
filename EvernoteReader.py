#!/usr/bin/env python2
# -*- coding: utf-8 -*-

#API reference: https://dev.evernote.com/doc/reference/NoteStore.html


import os
import sys
import json
import logging
import re
import hashlib
import binascii
import html2text
import evernote.edam.userstore.constants as UserStoreConstants
import evernote.edam.type.ttypes as Types
import evernote.edam.notestore.ttypes as ns_ttypes
from evernote.api.client import EvernoteClient
#from bs4 import BeautifulSoup

ANKI_CONTENT_LIMIT = 131072

class EvernoteReader:
    def __init__(self, notebook_name, only_tag=None):
        self.notebook_name = notebook_name
        self.only_tag = only_tag
        self.token = self.readToken()
        assert self.token

        self.ev_client = None
        self.ev_note_store = None
        self.ev_notebook = None
        self.ev_notes_metadata = []
        self.ev_notes = {}

        self.ev_tags = {} #guid:tag map
        self.ev_tags_reverse = {} #guid:tag map

        self.clientConnect()
        self.fetchAllTags()

        self.fetchNotesMetadata()
        #do not fetch Notes by default
        self.fetchNotes()
        return


    def fetchAllTags(self):
        all_tags = self.ev_note_store.listTags()
        for tag in all_tags:
            self.ev_tags[tag.guid] = tag.name
            self.ev_tags_reverse[tag.name] = tag.guid

        return


    def readToken(self):
        token_file = os.path.expanduser("~/.configs.secure/evernote_to_anki.config.json")
        with open(token_file, "r") as fp:
            js = json.load(fp)
            assert "token" in js
            token = js["token"]
            return token
        return None


    def clientConnect(self):
        logging.info("Connect to Evernote...")
        self.ev_client = EvernoteClient(token=self.token, sandbox=False, china=False)
        self.ev_note_store = self.ev_client.get_note_store()
        notebooks = self.ev_note_store.listNotebooks()
        logging.info("Read all notebooks")
        for nb in notebooks:
            if nb.name == self.notebook_name:
                self.ev_notebook = nb

    def fetchNotesMetadata(self):
        logging.info("Getting metadata from notebook: %s", self.notebook_name)
        flt = ns_ttypes.NoteFilter()
        flt.notebookGuid = self.ev_notebook.guid
        rs = ns_ttypes.NotesMetadataResultSpec()
        rs.includeTitle = True
        rs.includeTagGuids = True
        nml = self.ev_note_store.findNotesMetadata(self.token, flt, 0, 10000, rs)

        for n in nml.notes:
            match_only_tag = False
            #n is "NoteMetadata" type
            if n.tagGuids:
                for t in n.tagGuids:
                    if self.ev_tags[t].lower() == self.only_tag.lower():
                        match_only_tag = True
            else:
                logging.info("No Tag found for: %s ", n.title)
            if match_only_tag:
                self.ev_notes_metadata.append([n.guid, n.title, n.tagGuids])
        return

    def getTitleList(self):
        title_list = []
        for n in self.ev_notes_metadata:
            title_list.append(n[1].lower())
        return title_list

    def getContentList(self):
        content_list = []
        for en in self.ev_notes.values():
            content_list.append(en[4])
        return content_list

    def fetchNotes(self):
        logging.info("Getting notes content from notebook: %s", self.notebook_name)
        for guid, title, tag_guids in self.ev_notes_metadata:
            tag_matched = False
            if self.only_tag:
                for tag_guid in tag_guids:
                    tag_name = self.ev_tags[tag_guid]
                    if tag_name.lower() == self.only_tag.lower():
                        tag_matched = True
                        break

            if not tag_matched:
                continue

            rs = ns_ttypes.NoteResultSpec()
            logging.debug("fetching note: %s",title)
            rs.includeContent = True #ENML contents
            note = self.ev_note_store.getNoteWithResultSpec(self.token, guid, rs)

            assert title==note.title
            #self.beautifyContent(note.content)
            content = self.processNoteContent(note.content)
            h = html2text.HTML2Text()
            plain_text_content = h.handle(content)
            self.ev_notes[note.contentHash] = [title, note.tagGuids, note.contentHash, content, plain_text_content]

    def processNoteContent(self, content):
        content = re.sub(r'\t', '  ', content, flags=re.UNICODE)
        content = re.sub(r'\n', '<br>', content, flags=re.UNICODE)
        search = re.search(r'<en-note>.*</en-note>', content, flags=re.UNICODE)
        if not search:
            return content
        else:
            return search.group(0)

    def writeAnkiImportTextFile(self, fn):
        logging.info("Export %d notes from %s to ANKI import file: %s", len(self.ev_notes), self.notebook_name, fn)
        fp = open(fn, "w")

        for note in self.ev_notes.values():
            is_english = False
            tags = []
            if note[1]:
                for guid in note[1]:
                    tag_name = self.ev_tags[guid]
                    tags.append(tag_name)
                    if tag_name.lower() == "english":
                        is_english = True
            tag = " ".join(tags)  #ANKI uses space to separate tags

            if is_english:
                #English will be imported to different ANKI deck.
                continue

            global ANKI_CONTENT_LIMIT
            if len(note[3]) > int(ANKI_CONTENT_LIMIT*0.8):
                logging.info("Skip note because content too long for ANKI: %s", note[0])
                continue

            fp.write("%s\t"%note[0].encode("utf-8"))
            fp.write("%s\t"%note[3].encode("utf-8"))
            fp.write("%s\n"%tag)
        fp.close()


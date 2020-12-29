#!/usr/bin/env python2
#from bottle import route, run, template, request, hook
from bottle import *
import urllib

import os
import sys
import re
import json
import argparse
import logging
import datetime
import tarfile

SCRIPT_PATH=os.path.dirname(os.path.realpath(__file__))

from EnChDict import EnChDict
from EnToAnki import EnglishToAnki

test_eta = EnglishToAnki()

@hook('before_request')
def setup_request():
    approot = url("/")
    if approot[-1] == "/":
        approot = approot[:-1]
    request.APPROOT = approot

    global err
    err = None

def PostBack():
    try:
        request.postFromPath
    except:
        assert 0;
    redirect(request.postFromPath)

@route('/web_download/<filename:path>')
def send_static(filename):
        return static_file(filename, root='%s/web_download/'%SCRIPT_PATH)

@route('/hello/<name>')
def index(name):
    return template('<b>Hello {{name}}</b>!', name=name)

@route('/')
def main():
    return template('<b>main</b>!')


@route('/english_to_anki_post', method='POST')
def english_to_anki_post():
    eta = EnglishToAnki()
    eta.en_ch_dict.EnableGoogleTTS()
    request.inpEnglishContent = request.POST.get("inpEnglishContent")
    eta.processTextList([request.inpEnglishContent])
    eta.lookup_startdict()
    tts_dir = "%s/web_tts/"%SCRIPT_PATH
    eta.anki_cards = eta.genAnkiCards(tts_dir)
    if len(eta.anki_cards) > 0:
        dateTimeObj = datetime.datetime.now()
        timestamp = dateTimeObj.strftime("%Y%m%d_%H%M%S%f")
        name = "anki_import.%s.txt"%timestamp
        tarname = "anki_import.%s.tar.gz"%timestamp
        fn = "%s/web_download/%s"%(SCRIPT_PATH,name)

        with open(fn, "w") as fp:
            for k in eta.anki_cards:
                fp.write(k.encode("utf-8"))
                fp.write("\n")

        eta.generated_mp3 = 0
        tarfn = "%s/web_download/%s"%(SCRIPT_PATH,tarname)
        cwd = os.getcwd()
        tarhandle = tarfile.open(tarfn, "w:gz")
        for word in eta.all_words.keys():
            mp3 = "web_tts/%s.mp3"%word
            if os.path.exists(mp3):
                eta.generated_mp3 = eta.generated_mp3 + 1
                tarhandle.add(mp3)
        os.chdir("%s/web_download"%SCRIPT_PATH)
        tarhandle.add(name)
        tarhandle.close()
        os.chdir(cwd)

        eta.tarball_size = os.path.getsize(tarfn)
        request.anki_import_filepath = tarfn
        request.anki_import_filename = tarname
    else:
        request.anki_import_filepath = None
        request.anki_import_filename = None
    return template('english_to_anki_result.tpl', request=request, eta=eta)

@route('/english_to_anki', method='GET')
def english_to_anki():
    eta = EnglishToAnki()
    return template('english_to_anki.tpl', request=request, eta=eta)

#please comment below run() if app is runing under wsgi
run(host='0.0.0.0', port=8080)


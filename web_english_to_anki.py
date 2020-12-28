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

SCRIPT_PATH=os.path.dirname(os.path.realpath(__file__))

from EnChDict import EnChDict
from EnToAnki import EnglishToAnki

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

@route('/hello/<name>')
def index(name):
    return template('<b>Hello {{name}}</b>!', name=name)

@route('/')
def main():
    return template('<b>main</b>!')


@route('/english_to_anki_post', method='POST')
def english_to_anki_post():
    eta = EnglishToAnki()
    request.inpEnglishContent = request.POST.get("inpEnglishContent")
    eta.processTextList([request.inpEnglishContent])
    eta.lookup_startdict()
    eta.anki_cards = eta.genAnkiCards()
    return template('english_to_anki_result.tpl', request=request, eta=eta)

@route('/english_to_anki', method='GET')
def english_to_anki():
    eta = EnglishToAnki()
    return template('english_to_anki.tpl', request=request, eta=eta)

run(host='localhost', port=8080)

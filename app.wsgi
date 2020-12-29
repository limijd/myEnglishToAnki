#!/home/wli/install/Python-2.7.18/bin/python
import sys
import os

sys.path.insert(0, "/var/www/myEnglishToAnki")

import bottle
import web_english_to_anki
application = bottle.default_app()

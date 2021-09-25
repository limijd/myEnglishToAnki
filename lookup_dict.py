#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import sys
import os
import sqlite3
import logging
import string

from EnChDict import *

d = EnChDict("stardict.sqlite.db")
result = d.lookup_stardict_sql(["hello", "because of"])

print(result)

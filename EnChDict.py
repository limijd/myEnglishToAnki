#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import sys
import os
import sqlite3
import logging
import string
from contextlib import closing

class EnChDict:
    def __init__(self, stardict_db):
        self.stardict_db = stardict_db


    def lookup_stardict_sql(self, words):
        num_words = len(words)
        words_arr = []
        lookup_result = {}
        NUM_PER_CHUNK=1024
        cur = 0
        while True:
            if cur+NUM_PER_CHUNK<num_words:
                arr = words[cur:cur+NUM_PER_CHUNK]
                cur = cur + NUM_PER_CHUNK
                words_arr.append(arr)
                continue
            else:
                arr = words[cur:num_words]
                words_arr.append(arr)
                break
            
        try:
            conn = sqlite3.connect(self.stardict_db)
        except Exception as e:
            logging.error(e)
            sys.exit(-1)

        for arr in words_arr:
            str_words = ", ".join(map(lambda x:"\'%s\'"%x, arr))
            sql = "SELECT * FROM stardict  WHERE word in ( %s )"%str_words
            results = None
            with closing(conn.cursor()) as cur:
                cur.execute(sql)
                columns = cur.description
                for value in cur.fetchall():
                    tmp = {}
                    for (index,column) in enumerate(value):
                        tmp[columns[index][0]] = column
                    lookup_result[tmp["word"]] = tmp

        conn.close()

        failed_list=[]
        for word in words:
            if not word in lookup_result:
                failed_list.append(word)
        return lookup_result, failed_list


    def parse_ecdict_exchange(self, exchange):
        if not exchange:
            return '';
        exchange = exchange.strip()
        parts = exchange.split("/")
        result = []
        for part in parts:
            k,v = part.split(":")
            if k=="p":
                k = "过去式"
            if k=="d":
                k = "过去分词"
            if k=="i":
                k = "现在分词"
            if k=="3":
                k = "第三人称单数"
            if k=="r":
                k = "形容词比较级"
            if k=="t":
                k = "形容词最高级"
            if k=="s":
                k = "名词复数"
            if k=="0":
                k = "lemma"
            if k=="1":
                k = "lemma的变换形式"
            result.append("%s: %s"%(k.decode("utf-8"),v))

        return "<br>".join(result)


    def result_to_anki(self, results, keys):
        cards = []
        for word, result in results.items():
            values = []
            for k in keys:
                v = result[k]
                v = v.replace("\t", "    ")
                v = v.replace("\n", "<br>")
                v = v.replace("\\n", "<br>")
                if k=="exchange":
                    values.append(self.parse_ecdict_exchange(v))
                else:
                    values.append(v)
            card = "%s"%("\t".join(values))
            cards.append(card)

        return cards


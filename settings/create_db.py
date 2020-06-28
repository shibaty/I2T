# -*- coding: utf-8 -*-
import os
import sqlite3
from contextlib import closing
import config

path = os.path.dirname(os.path.abspath(__file__))
dbfile = os.path.join(path, config.DBNAME)

with closing(sqlite3.connect(dbfile)) as conn:
  cur = conn.cursor()

  cur.execute('drop table if exists config')
  cur.execute('''
    create table config(key text primary key, value text)
  ''')

  sql = 'insert into config (key, value) values (?, ?)'
  datas = []
  for key, value in config.CONFIG.items():
    datas.append((key, value))
  cur.executemany(sql, datas)

  conn.commit()

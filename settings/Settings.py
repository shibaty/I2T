# -*- coding: utf-8 -*-
""" Settings """

import os.path
import threading
from contextlib import closing
import sqlite3
from . import config


class Settings(object):
  """ Settings """

  _instance = None
  _lock = threading.Lock()
  _dbfile = None

  def __new__(cls):
    """This Class is Singleton.
    """
    raise NotImplementedError()

  def __init__():
    pass

  @classmethod
  def get_instance(cls):
    """get instance

    Returns:
        instance
    """
    with cls._lock:
      if not cls._instance:
        cls._instance = super().__new__(cls)
        cls.__init()

    return cls._instance

  @classmethod
  def __init(cls):
    path = os.path.dirname(os.path.abspath(__file__))
    cls._dbfile = os.path.join(path, config.DBNAME)

  def get_config_all(self):
    with closing(sqlite3.connect(self._dbfile)) as conn:
      conn.row_factory = sqlite3.Row
      cur = conn.cursor()
      cur.execute('select * from config')
      rows = cur.fetchall()
      config = {}
      for row in rows:
        config[row['key']] = row['value']
      return config

  def get_config(self, key):
    with closing(sqlite3.connect(self._dbfile)) as conn:
      cur = conn.cursor()
      cur.execute('select value from config where key = ?', (key,))
      value = cur.fetchone()[0]

      return value

  def set_config(self, key, value):
    with closing(sqlite3.connect(self._dbfile)) as conn:
      cur = conn.cursor()
      cur.execute('update config set value = ? where key = ?', (value, key))
      conn.commit()

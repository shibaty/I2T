# -*- coding: utf-8 -*-
import threading
import logging
import logging.handlers


class Logger(object):

  _instance = None
  _lock = threading.Lock()
  _logger = None

  def __new__(cls):
    """This Class is Singleton.
    """
    raise NotImplementedError()

  def __init__():
    pass

  @classmethod
  def get_logger(cls):
    """get logger instance

    Returns:
        logger instance
    """
    with cls._lock:
      if not cls._instance:
        cls._instance = super().__new__(cls)
        cls.__init()

    return cls._logger

  @classmethod
  def __init(cls):
    cls._logger = logging.getLogger('I2T')
    handler = logging.handlers.RotatingFileHandler(
        filename='./logs/I2T.log',
        maxBytes=16 * 1024,
        backupCount=3)
    formatter = logging.Formatter(
        '%(asctime)s[%(levelname)s] %(filename)s#%(funcName)s:%(message)s')
    handler.setFormatter(formatter)
    cls._logger.addHandler(handler)
    cls._logger.setLevel(logging.DEBUG)

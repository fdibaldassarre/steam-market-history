#!/usr/bin/env python3

import os
import logging
from logging.handlers import RotatingFileHandler


class MainLogger():
    _config = None

    formatter = logging.Formatter(
        fmt="%(asctime)-22s %(levelname)-7s %(name)-14s :: %(funcName)s == %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    logpath = None
    file_handler = None
    stream_handler = None
    loggers = []

    def __init__(self, config):
        self._config = config
        self._createStreamHandler()

    def hasFileWriter(self):
        return self.file_handler is not None

    def _createFileHandler(self):
        self.file_handler = RotatingFileHandler(self.logpath,
                                                maxBytes=1048576,
                                                backupCount=10)
        self.file_handler.setFormatter(self.formatter)

    def _createStreamHandler(self):
        self.stream_handler = logging.StreamHandler()
        self.stream_handler.setFormatter(self.formatter)

    def setLogPath(self, path):
        self.logpath = path
        self._createFileHandler()
        self.addFileHandlerToAll()

    def getFileHandler(self):
        return self.file_handler

    def getStreamHandler(self):
        return self.stream_handler

    def addLogger(self, logger):
        self.loggers.append(logger)
        self.addFileHandler(logger)
        if self._config.debug:
            self.addStreamHandler(logger)
            logger.setLevel(logging.DEBUG)

    def addFileHandler(self, logger):
        if self.file_handler is not None:
            logger.addHandler(self.file_handler)

    def addStreamHandler(self, logger):
        logger.addHandler(self.stream_handler)

    def addFileHandlerToAll(self):
        for logger in self.loggers:
            self.addFileHandler(logger)


class LogFactory:
    _config = None

    def __init__(self, config):
        self._config = config
        self.main_logger = MainLogger(config)

    def _initialize_writer(self):
        log_folder = self._config.get_log_folder()
        if not os.path.exists(log_folder):
            os.mkdir(log_folder)
        path = os.path.join(log_folder, "main.log")
        self.main_logger.setLogPath(path)

    def _setup_logger(self, logger):
        logger.setLevel(logging.INFO)
        if not self.main_logger.hasFileWriter():
            self._initialize_writer()
        self.main_logger.addLogger(logger)

    def create_logger(self, name):
        logger = logging.getLogger(name)
        self._setup_logger(logger)
        return logger

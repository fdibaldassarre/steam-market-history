#!/usr/bin/env python3

import os

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from .MarketHistoryDao import MarketHistoryDAO


class DaoFactory:
    _config = None
    _logger = None

    _session_maker = None

    _market_history_dao = None

    def __init__(self, log_factory, config):
        self._logger = log_factory.create_logger("DaoFactory")
        self._config = config
        self.init()

    def init(self):
        db_path = self._config.get_database()
        db_folder = os.path.dirname(db_path)
        if not os.path.exists(db_folder):
            os.makedirs(db_folder)
        engine = create_engine('sqlite:///' + db_path, echo=self._config.debug_sql)
        if not os.path.exists(db_path):
            self._logger.info("Create database: %s" % db_path)
            from ..entities.Persistent import Base
            Base.metadata.create_all(engine)
        self._session_maker = sessionmaker(bind=engine, expire_on_commit=False)

    def get_market_history_dao(self):
        if self._market_history_dao is None:
            self._market_history_dao = MarketHistoryDAO(self._session_maker)
        return self._market_history_dao

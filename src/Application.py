#!/usr/bin/env python3

from .common.Configuration import ConfigManager
from .common.Logger import LogFactory
from .dao.DaoFactory import DaoFactory
from .manager.HistoryUpdater import HistoryUpdater
from .manager.CsvExporter import HistoryExporter
from .steam.SteamMarket import SteamMarket


class ServiceLocator:

    def __init__(self, config_path, debug=False):
        self.config = ConfigManager(config_path, debug)
        self.log_factory = LogFactory(self.config)
        self.dao_factory = DaoFactory(self.log_factory, self.config)

    def get_steam_market(self):
        return SteamMarket(self.log_factory, self.config)

    def get_history_dao(self):
        return self.dao_factory.get_market_history_dao()

    def get_history_updater(self):
        return HistoryUpdater(self.log_factory, self.get_history_dao(), self.get_steam_market())

    def get_history_exporter(self):
        return HistoryExporter(self.get_history_dao())


class MarketHistoryUpdater:

    def __init__(self, config_path, debug=False):
        self.locator = ServiceLocator(config_path, debug)
        self.updater = self.locator.get_history_updater()

    def update(self):
        self.updater.update()


class MarketHistoryExporter:

    def __init__(self, config_path, debug=False):
        self.locator = ServiceLocator(config_path, debug)
        self.exporter = self.locator.get_history_exporter()

    def export(self, *args, **kwargs):
        self.exporter.export(*args, **kwargs)

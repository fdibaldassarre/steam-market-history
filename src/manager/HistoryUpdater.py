#!/usr/bin/env python3

from math import ceil
from random import randint
from time import sleep

from queue import Queue
from threading import Thread

from ..steam.SteamMarket import PAGE_SIZE


THREAD_NUMBER = 4
DATABASE_QUEUE_SIZE = 50  # Must be greater then PAGE_SIZE

COMMIT_SIZE = 100


class MultiThreadUpdater():

    def __init__(self, steam_market, history_dao):
        self.market = steam_market
        self.history_dao = history_dao

    def _download_page(self):
        keep = True
        while keep:
            sleep(randint(1, 3))
            try:
                page = self._pages_queue.get(block=False)
            except Exception:
                keep = False
                break
            _, items = self.market.get_history(page)
            if items is None:
                sleep(5)
                continue
            for item in items:
                self._database_queue.put(item)

    def _persist_on_database(self):
        try:
            self.history_dao.openSession()
            inserted = 0
            while self._updating:
                while not self._database_queue.empty():
                    item = self._database_queue.get()
                    self.history_dao.insert(**item)
                    inserted += 1
                if inserted >= COMMIT_SIZE:
                    self.history_dao.commit()
                    inserted = 0
                sleep(1)
            self.history_dao.commit()
        finally:
            self.history_dao.closeSession()

    def _initialize(self):
        total_count, items = self.market.get_history(0)
        total_pages = ceil(total_count / PAGE_SIZE)
        self._pages_queue = Queue(maxsize=total_pages)
        for page in range(1, total_pages):
            self._pages_queue.put(page)
        self._database_queue = Queue(maxsize=DATABASE_QUEUE_SIZE)
        for item in items:
            self._database_queue.put(item)

    def start(self):
        self._initialize()
        # Start the update threads
        self._update_threads = []
        for i in range(THREAD_NUMBER):
            thread = Thread(target=self._download_page)
            thread.start()
            self._update_threads.append(thread)
        # Start the database thread
        self._updating = True
        self._database_thread = Thread(target=self._persist_on_database)
        self._database_thread.start()

    def join(self):
        for thread in self._update_threads:
            thread.join()
        self._updating = False
        self._database_thread.join()


class HistoryUpdater():

    def __init__(self, log_factory, history_dao, steam_market):
        self.logger = log_factory.create_logger("HistoryUpdater")
        self.history_dao = history_dao
        self.market = steam_market

    def update(self):
        login = self.market.login()
        if not login:
            self.logger.error("Login failure")
            return None
        last_item = self.history_dao.get_last_item()
        if last_item is None:
            self._downloadAllHistory()
        else:
            self._updateHistory(last_item)

    def _updateHistory(self, last_item):
        try:
            self.history_dao.openSession()
            page = 0
            keep = True
            while keep:
                total_count, items = self.market.get_history(page)
                for item in items:
                    if item['id'] > last_item.id:
                        self.history_dao.insert(**item)
                    else:
                        keep = False
                        break
            self.history_dao.commit()
        finally:
            self.history_dao.closeSession()

    def _downloadAllHistory(self):
        updater = MultiThreadUpdater(self.market, self.history_dao)
        updater.start()
        updater.join()

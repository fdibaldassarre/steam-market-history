#!/usr/bin/env python3

import csv

from ..entities.Persistent import ACTION_SELL
from ..entities.Persistent import ACTION_BUY
from ..entities.Persistent import ACTION_LISTING_CREATED
from ..entities.Persistent import ACTION_LISTING_CANCELED

HEADER = ["Date", "Action", "Item", "Game name", "Price"]


def get_action_display_name(action):
    if action == ACTION_SELL:
        return "Sell"
    elif action == ACTION_BUY:
        return "Buy"
    elif action == ACTION_LISTING_CREATED:
        return "Listing created"
    elif action == ACTION_LISTING_CANCELED:
        return "Listing removed"
    else:
        return "Unknown action"


class HistoryExporter:

    def __init__(self, history_dao):
        self.history_dao = history_dao

    def export(self, path, include_all=False):
        with open(path, "w") as hand:
            writer = csv.writer(hand, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
            self._write_file(writer, include_all)

    def _write_file(self, writer, include_all):
        writer.writerow(HEADER)
        for item in self.history_dao.get_all_buy_or_sell():
            line = []
            if item.acted_on is not None:
                line.append(item.acted_on)
            else:
                line.append(item.listed_on)
            line.append(get_action_display_name(item.action))
            line.append(item.name)
            line.append(item.game_name)
            if item.price is not None:
                line.append(str(item.price))
            else:
                line.append('')
            writer.writerow(line)

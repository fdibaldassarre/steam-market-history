#!/usr/bin/env python3

from ..entities.Domain import IMarketHistoryItem
from ..entities.Persistent import MarketHistoryItem

from .Common import EntityDAO
from .Common import withSession
from .Common import returnNonPersistent


class MarketHistoryDAO(EntityDAO):

    _entity = IMarketHistoryItem
    _entity_lazy = IMarketHistoryItem
    _persistent_entity = MarketHistoryItem

    @withSession
    @returnNonPersistent
    def get_last_item(self):
        items = self._getBy(order=MarketHistoryItem.id.desc(), limit=1)
        if len(items) == 0:
            return None
        else:
            return items[0]

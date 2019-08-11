#!/usr/bin/env python3


class Identifiable():
    def __init__(self, persistable):
        self.id = persistable.id


class Nameable(Identifiable):
    def __init__(self, persistable):
        super().__init__(persistable)
        self.name = persistable.name


class IMarketHistoryItem(Nameable):
    def __init__(self, persistable):
        super().__init__(persistable)
        self.game_name = persistable.game_name
        self.code = persistable.code
        self.listed_on = persistable.listed_on
        self.acted_on = persistable.acted_on
        self.acted_with = persistable.acted_with
        self.price = persistable.price
        self.action = persistable.action

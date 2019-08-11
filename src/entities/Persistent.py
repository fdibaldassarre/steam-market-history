#!/usr/bin/env python3

from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import String

from sqlalchemy.ext.declarative import declarative_base
Base = declarative_base()

ACTION_UNKNOW = 0
ACTION_SELL = 1
ACTION_BUY = 2
ACTION_LISTING_CREATED = 3
ACTION_LISTING_CANCELED = 4


class MarketHistoryItem(Base):
    __tablename__ = "MarketHistory"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False, index=True)
    game_name = Column(String, index=True)
    code = Column(String, nullable=False, index=True)
    listed_on = Column(String, index=True)
    acted_on = Column(String)
    acted_with = Column(String)
    price = Column(Integer)
    action = Column(Integer, index=True)

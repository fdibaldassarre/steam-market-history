#!/usr/bin/env python3

import json
from lxml import html

from .SteamCommunity import SteamCommunity

from ..entities.Persistent import ACTION_SELL
from ..entities.Persistent import ACTION_BUY
from ..entities.Persistent import ACTION_LISTING_CREATED
from ..entities.Persistent import ACTION_LISTING_CANCELED

API_HISTORY = 'https://steamcommunity.com/market/myhistory/render/?query=&start=%d&count=%d'

PAGE_SIZE = 10

XPATH_ELEMENTS = "//div[contains(@id, 'history_row')]"
XPATH_ACTION = "div[contains(@class, 'market_listing_left_cell')]"
XPATH_NAME = "div[@class='market_listing_item_name_block']/span[@class='market_listing_item_name']"
XPATH_GAME_NAME = "div[@class='market_listing_item_name_block']/span[@class='market_listing_game_name']"
XPATH_PRICE = "div[contains(@class, 'market_listing_their_price')]/span/span"
XPATH_ACTED_WITH = "div[contains(@class, 'market_listing_whoactedwith')]"
XPATH_LISTED_ON = "div[contains(@class, 'market_listing_listed_date')]"

SYMBOL_ACTION_SELL = '-'
SYMBOL_ACTION_BUY = '+'


def _get_xpath_value(div, xpath):
    results = div.xpath(xpath)
    if len(results) == 0:
        return None
    result = results[0]
    return result.text_content().strip()


def _get_action(action_raw, price_raw):
    if action_raw == SYMBOL_ACTION_SELL:
        action = ACTION_SELL
    elif action_raw == SYMBOL_ACTION_BUY:
        action = ACTION_BUY
    elif price_raw is None or price_raw == '':
        action = ACTION_LISTING_CANCELED
    else:
        action = ACTION_LISTING_CREATED
    return action


def _parse_price(price_raw):
    if price_raw is None or price_raw == '':
        return None
    price_no_currency = price_raw[:-1]
    price_raw = price_no_currency.replace(",", ".").replace("--", "00")
    try:
        price = int(float(price_raw) * 100)
    except Exception:
        price = None
    return price


class SteamMarket(SteamCommunity):

    def __init__(self, log_factory, config):
        super().__init__(log_factory, config)
        self.logger = log_factory.create_logger("SteamMarket")

    def _request_items_at_page(self, page):
        url = API_HISTORY % (page * PAGE_SIZE, PAGE_SIZE)
        page = self.download_url(url)
        if page is None:
            return None
        response = json.loads(page)
        return response

    def _market_item_from_html(self, div):
        item = {}
        item['code'] = int(div.attrib['id'].split('_')[2])
        item['name'] = _get_xpath_value(div, XPATH_NAME)
        item['game_name'] = _get_xpath_value(div, XPATH_GAME_NAME)
        # item['acted_with'] = _get_xpath_value(div, XPATH_ACTED_WITH)
        # Set listed/acted dates
        listed_divs = div.xpath(XPATH_LISTED_ON)
        item['acted_on'] = listed_divs[0].text_content().strip()
        if len(listed_divs) == 2:
            item['listed_on'] = listed_divs[1].text_content().strip()
        # Set price
        price_raw = _get_xpath_value(div, XPATH_PRICE)
        item['price'] = _parse_price(price_raw)
        # Set action
        action_raw = _get_xpath_value(div, XPATH_ACTION)
        item['action'] = _get_action(action_raw, price_raw)
        return item

    def _load_items_from_response(self, response):
        results_html = response["results_html"]
        page = html.document_fromstring(results_html)
        items = page.xpath(XPATH_ELEMENTS)
        market_items = []
        for item in items:
            market_item = self._market_item_from_html(item)
            market_items.append(market_item)
        return market_items

    def get_history(self, page):
        response = self._request_items_at_page(page)
        if response is None:
            self.logger.error("Cannot download history at page %d" % page)
            return -1, None
        total_count = response["total_count"]
        if total_count is None:
            self.logger.error("No history to download")
            return 0, None
        items = self._load_items_from_response(response)
        # Set ids
        for position_in_page, item in enumerate(items):
            position_global = total_count - position_in_page - page * PAGE_SIZE
            item['id'] = position_global
        return total_count, items

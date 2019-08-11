#!/usr/bin/env python3

import requests

from ..common.Utils import parse_json_file

URL_STEAMCOMMUNITY = "https://steamcommunity.com"


class SteamCommunity():

    def __init__(self, log_factory, config):
        self.logger = log_factory.create_logger("SteamCommunity")
        self.auth_file = config.get_steam_auth_file()
        self._logged_in = False
        self._load_cookies()

    def _load_cookies(self):
        auth_data = parse_json_file(self.auth_file)
        # Load cookies jar
        self.cookies_jar = requests.cookies.RequestsCookieJar()
        for key, value in auth_data['cookies'].items():
            self.cookies_jar.set(key, value, domain='steamcommunity.com', path='/')
        # Load headers
        user_agent = auth_data['user-agent']
        self.headers = {'User-Agent': user_agent}

    def login(self):
        if self._logged_in:
            return
        request = requests.get(URL_STEAMCOMMUNITY,
                               cookies=self.cookies_jar,
                               headers=self.headers)
        if request.status_code != 200:
            self.logger.error("Login response error. Staus code: %d" % request.status_code)
            return False
        if 'sessionid' not in request.cookies:
            self.logger.error("Session ID not set in cookies")
            return False
        self.logger.info("Login success")
        self.cookies_jar.update(request.cookies)
        self._logged_in = True
        return True

    def download_url(self, url):
        page_request = requests.get(url,
                                    cookies=self.cookies_jar,
                                    headers=self.headers)
        if page_request.status_code != 200:
            text = None
        else:
            text = page_request.text
        return text

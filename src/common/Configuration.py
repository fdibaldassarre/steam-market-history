#!/usr/bin/env python3

import os


class ConfigManager:

    debug = True
    debug_sql = True

    def __init__(self, config_folder, debug=False):
        self.config_folder = config_folder
        self.debug = debug
        self.debug_sql = debug

    def get_steam_auth_file(self):
        return os.path.join(self.config_folder, 'auth.json')

    def get_database(self):
        return os.path.join(self.config_folder, 'db/data.db')

    def get_log_folder(self):
        return os.path.join(self.config_folder, 'logs/')

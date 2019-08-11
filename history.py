#!/usr/bin/env python3

import argparse

from src.Application import MarketHistoryUpdater
from src.common.Places import MAIN_FOLDER


parser = argparse.ArgumentParser(description="Market History Updater")
parser.add_argument('--config', default=None,
                    help='configuration folder')
parser.add_argument('--debug', action='store_true',
                    help='show log in terminal')
args = parser.parse_args()

config_folder = args.config
debug = args.debug

if config_folder is None:
    config_folder = MAIN_FOLDER

updater = MarketHistoryUpdater(config_folder, debug=debug)
updater.update()

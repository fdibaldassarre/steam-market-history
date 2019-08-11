#!/usr/bin/env python3

import argparse

from src.Application import MarketHistoryExporter
from src.common.Places import MAIN_FOLDER


parser = argparse.ArgumentParser(description="Market History Exporter")
parser.add_argument('export_file', default=None,
                    help='target file')
parser.add_argument('--config', default=None,
                    help='configuration folder')
parser.add_argument('--debug', action='store_true',
                    help='show log in terminal')
args = parser.parse_args()

output_path = args.export_file
config_folder = args.config
debug = args.debug

if config_folder is None:
    config_folder = MAIN_FOLDER

exporter = MarketHistoryExporter(config_folder, debug=debug)
exporter.export(output_path)

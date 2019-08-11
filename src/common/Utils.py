#!/usr/bin/env python3

import json


def parse_json_file(path):
    with open(path, 'r') as hand:
        data = hand.read()
        config = json.loads(data)
    return config

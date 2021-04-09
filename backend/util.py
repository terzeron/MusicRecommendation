#!/usr/bin/env python


import json
from typing import Dict, Any


class Util:
    @staticmethod
    def read_config(conf_file: str) -> Dict[str, Any]:
        with open(conf_file, 'r') as infile:
            conf = json.load(infile)
            return conf
        return {}

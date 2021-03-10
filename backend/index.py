#!/usr/bin/env python
# -*- encoding: utf-8 -*-


import sys
import os
import re
import time
import json
import random
from datetime import datetime
from typing import List, Dict, Any, Optional
import logging
import logging.config
import requests
from flask import Flask, jsonify, request
from flask_cors import CORS


app = Flask(__name__)
app.config.from_object(__name__)
app.config['JSON_AS_ASCII'] = False
CORS(app, resources={r"/*": {"origins": "*"}})


logging.config.fileConfig(os.path.dirname(os.path.abspath(sys.argv[0])) + "/logging.conf")
LOGGER = logging.getLogger()


@app.route("/check", methods=["GET"])
def check():
    LOGGER.debug(request)
    return jsonify("ok")


@app.route("/recommend", methods=["GET", "POST"])
def recommend():
    LOGGER.debug(request)
    return jsonify("ok")



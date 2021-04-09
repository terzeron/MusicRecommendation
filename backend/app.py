#!/usr/bin/env python


import logging.config
from flask import Flask
from flask_cors import CORS


app = Flask(__name__)
app.config.from_object(__name__)
app.config['JSON_AS_ASCII'] = False
CORS(app, resources={r"/*": {"origins": "*"}})

logging.basicConfig(filename='../run.log', level=logging.DEBUG)

import views

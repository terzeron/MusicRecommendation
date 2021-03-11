#!/usr/bin/env python

import logging
import sys

logging.basicConfig(stream=sys.stderr)

sys.path.insert(0, '/home1/irteam/terzeron/music/backend')
sys.path.insert(1, '/home1/irteam/.pyenv/versions/3.9.2/lib/python3.9/site-packages')

from app import app as application

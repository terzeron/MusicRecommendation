#!/usr/bin/env python
# -*- encoding: utf-8 -*-


import re
from typing import Optional
from flask import Flask, jsonify, request
from flask.logging import create_logger
from flask_cors import CORS
from video_manager import VideoManager


app = Flask(__name__)
app.config.from_object(__name__)
app.config['JSON_AS_ASCII'] = False
CORS(app, resources={r"/*": {"origins": "*"}})
LOGGER = create_logger(app)


@app.route("/check", methods=["GET"])
def check() -> str:
    return jsonify("ok")


@app.route("/recommend", methods=["GET"])
@app.route("/recommend/<year_str>", methods=["GET"])
def recommend(year_str: str=None) -> str:
    LOGGER.debug(request)
    video_manager = VideoManager()
    year: Optional[int] = None
    try:
        if year_str:
            year = int(year_str)
    except TypeError:
        pass
    video_url = video_manager.choose_random_video_url(year=year)
    return jsonify({"video_url": video_url})


@app.route("/subscribe/{time_list_str}", methods=["POST"])
def subscribe(time_list_str: str) -> str:
    LOGGER.debug(request)
    time_list = time_list_str.split(",")
    for a_time in time_list:
        if re.search(r'\d\d?:\d\d', a_time):
            #register_schedule(a_time)
            None
    return jsonify({})


@app.route("/unsubscribe", methods=["DELETE"])
def unsubscribe() -> str:
    LOGGER.debug(request)
    return jsonify("ok")


if __name__ == "__main__":
    app.run()


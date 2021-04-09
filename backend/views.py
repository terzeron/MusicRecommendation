#!/usr/bin/env python
# -*- encoding: utf-8 -*-


import re
from typing import Optional
from flask import jsonify, request
from video_manager import VideoManager
from app import app


@app.route("/check", methods=["GET"])
def check() -> str:
    return jsonify(jsonify({"success": True}))


@app.route("/recommend", methods=["GET"])
@app.route("/recommend/<year_str>", methods=["GET"])
def recommend(year_str: str=None) -> str:
    app.logger.debug(request)
    video_manager = VideoManager(app.logger)
    year: Optional[int] = None
    try:
        if year_str:
            year = int(year_str)
    except TypeError:
        app.logger.error("type error in year string")
        return jsonify({"success": False, "video_url": None, "error_message": "type error in year string"})
    video_url = video_manager.choose_random_video_url(year=year)
    return jsonify({"success": True, "video_url": video_url})


@app.route("/subscribe/{time_list_str}", methods=["POST"])
def subscribe(time_list_str: str) -> str:
    app.logger.debug(request)
    time_list = time_list_str.split(",")
    for a_time in time_list:
        if re.search(r'\d\d?:\d\d', a_time):
            #register_schedule(a_time)
            return jsonify({"success": False, "error_message": "not implemented"})
    return jsonify({"success": False, "error_message": "not implemented"})


@app.route("/unsubscribe", methods=["DELETE"])
def unsubscribe() -> str:
    app.logger.debug(request)
    return jsonify({"success": False, "error_message": "not implemented"})


if __name__ == "__main__":
    app.run()

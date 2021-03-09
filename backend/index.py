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


def get_chart_list(term: str, year: int, week: int) -> List[str]:
    print(term, year, week)
    if term == "year":
        week_str = ""
    else:
        week_str = "&targetTime=%d" % week
    # m년 n주차
    chart_url = "http://gaonchart.co.kr/main/section/chart/online.gaon?nationGbn=T&serviceGbn=S1040%s&hitYear=%d&termGbn=%s" % (week_str, year, term)

    result_list: List[str] = []
    response = requests.get(chart_url)
    if response and response.status_code == 200:
        state = 0
        title = ""
        singer = ""
        for line in response.text.split('\n'):
            if state == 0:
                m = re.search(r'<td class="subject">', line)
                if m:
                    state = 1
            elif state == 1:
                m = re.search(r'<p title="[^"]+">(?P<title>[^<]+)<', line)
                if m:
                    title = m.group("title")
                    state = 2
            elif state == 2:
                m = re.search(r'<p class="singer" title="[^"]+">(?P<singer>[^<]+)<', line)
                if m:
                    singer = m.group("singer")
                    result_list.append(title + " " + singer)
                    state = 0
    else:
        LOGGER.error(response)
    return result_list


def get_youtube_link(conf: Dict[str, Any], song: str) -> Optional[str]:
    encoded_song = requests.utils.quote(song)
    url = "https://www.googleapis.com/youtube/v3/search?part=id,snippet&key=%s&q=%s" % (conf["google_api_key"], encoded_song)
    response = requests.get(url)
    if response and response.status_code == 200:
        data = json.loads(response.text)
        if "items" in data:
            if len(data["items"]) > 0:
                for item in data["items"]:
                    if "snippet" in item and item["snippet"] and "title" in item["snippet"] and re.search(r'([Cc]over|노래방|직캠|모음)', item["snippet"]["title"]):
                        break
                    return item["id"]["videoId"]
    else:
        LOGGER.error("error in getting data of '%s' from youtube", song)
        LOGGER.error(response.status_code)
        LOGGER.debug(response.text)
    return None


def collect_some_charts(conf: Dict[str, Any]):
    year = 2020
    week = datetime.now().isocalendar()[1]
    old_days = random.randrange(2011, year - 1)
    total_song_list: List[str] = []
    # 주간(최신)
    recent_week_song_list = get_chart_list("week", year, week)
    # 올해
    this_year_song_list = get_chart_list("year", year, 0)
    # 작년
    last_year_song_list = get_chart_list("year", year - 1, 0)
    # 작년 이전
    old_days_song_list = get_chart_list("year", old_days, 0)
    total_song_list.extend(recent_week_song_list)
    total_song_list.extend(this_year_song_list)
    total_song_list.extend(last_year_song_list)
    total_song_list.extend(old_days_song_list)

    with open('vid.json', 'r') as infile:
        song_vid_map = json.load(infile)

    failure_count = 0
    for song in set(total_song_list):
        vid = None
        if song in song_vid_map:
            vid = song_vid_map[song]
        if not vid or song not in song_vid_map:
            vid = get_youtube_link(conf, song)
            if not vid:
                failure_count = failure_count + 1
                if failure_count >= 5:
                    break
            song_vid_map[song] = vid
            time.sleep(1)

    with open('vid.json', 'w') as outfile:
        json.dump(song_vid_map, outfile, ensure_ascii=False)

    return total_song_list, recent_week_song_list, this_year_song_list, last_year_song_list, old_days_song_list, song_vid_map


def choose_one_song_from_list(song_list: List[str], song_vid_map: Dict[str, Any]):
    while True:
        random_song = random.choice(song_list)
        if random_song and random_song in song_vid_map:
            if not song_vid_map[random_song]:
                continue
            print(random_song)
            return "https://youtube.com/watch?v=%s" % song_vid_map[random_song]
    return "https://youtube.com/watch?v=IKlQMqPSwek"


def call_webhook(conf: Dict[str, Any], youtube_video_url: str) -> None:
    if "MUSIC_RECOMMENDATION_PROFILE" in os.environ and os.environ["MUSIC_RECOMMENDATION_PROFILE"] == "production":
        # 모니터링플랫폼개발팀 채널
        webhook_url = "https://hook.dooray.com/services/%s" % conf["dooray_webhook_url_postfix_for_team"]
    else:
        # 개인 채널
        webhook_url = "https://hook.dooray.com/services/%s" % conf["dooray_webhook_url_postfix_for_test"]
    data = {'botName': conf["dooray_bot_name"], 'botIconImage': conf["dooray_bot_icon_image_url"], 'text': youtube_video_url}
    headers = {'Content-Type': 'application/json'}
    response = requests.post(webhook_url, data=json.dumps(data), headers=headers)
    if response:
        print("success")
    else:
        print("failure")
        LOGGER.error(response)


def read_config(conf_file: str) -> Dict[str, Any]:
    with open(conf_file, 'r') as infile:
        conf = json.load(infile)
        return conf
    return {}


def main() -> int:
    conf = read_config("conf.json")
    if not conf or "google_api_key" not in conf:
        return -1
    total_song_list, recent_week_song_list, this_year_song_list, last_year_song_list, old_days_song_list, song_vid_map = collect_some_charts(conf)
    if len(total_song_list) <= 0:
        return -1
    print(len(total_song_list), len(recent_week_song_list), len(this_year_song_list), len(last_year_song_list), len(old_days_song_list), len(song_vid_map))
    video_url = choose_one_song_from_list(total_song_list, song_vid_map)
    if not video_url:
        return -1
    print(video_url)
    call_webhook(conf, video_url)
    return 0


if __name__ == "__main__":
    sys.exit(main())

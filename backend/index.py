#!/usr/bin/env python
# -*- encoding: utf-8 -*-

from flask import Flask, jsonify, request
from flask_cors import CORS
import requests 
import re
import json
import random
from datetime import datetime


app = Flask(__name__)
app.config.from_object(__name__)
app.config['JSON_AS_ASCII'] = False

CORS(app, resources={r"/*": {"origins": "*"}})


@app.route("/check", methods=["GET"])
def check():
    return jsonify("ok")


@app.route("/recommend", methods=["GET", "POST"])
def recommend():
    return jsonify("ok")


def get_chart_list(term, year, week):
    if term == "year":
        week_str = ""
    else:
        week_str = "&targetTime=%d" % week
    # m년 n주차
    chart_url = "http://gaonchart.co.kr/main/section/chart/online.gaon?nationGbn=T&serviceGbn=S1040%s&hitYear=%d&termGbn=%s" % (week_str, year, term)
    
    result_list = []
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
    return result_list


def get_youtube_link(song):
    song = requests.utils.quote(song)
    url = "https://www.googleapis.com/youtube/v3/search?part=id,snippet&key=AIzaSyCSwUm6Jj-8ntXhbt3fYGyYgoGCTyZ9C10&q=%s" % song
    response = requests.get(url)
    if response and response.status_code == 200:
        data = json.loads(response.text)
        if "items" in data:
            if len(data["items"]) > 0:
                return data["items"][0]["id"]["videoId"]
    return None
    

def collect_some_charts():
    year = 2020
    week = datetime.now().isocalendar()[1]
    old_days = random.randrange(2011, year - 1)
    song_list = []
    # 주간(최신)
    song_list.extend(get_chart_list("week", year, week))
    # 올해
    song_list.extend(get_chart_list("year", year, 0))
    # 작년
    song_list.extend(get_chart_list("year", year - 1, 0))
    # 작년 이전
    song_list.extend(get_chart_list("year", old_days, 0))

    with open('vid.json', 'r') as infile:
        song_vid_map = json.load(infile)

    failure_count = 0
    for song in set(song_list):
        if song in song_vid_map:
            vid = song_vid_map[song]
        if not vid or song not in song_vid_map:
            vid = get_youtube_link(song)
            if not vid:
                failure_count = failure_count + 1
                if failure_count > 5:
                    break
            song_vid_map[song] = vid

    with open('vid.json', 'w') as outfile:
        json.dump(song_vid_map, outfile, ensure_ascii=False)

    while True:
        random_song_vid = random.choice(list(song_vid_map.values()))
        if random_song_vid:
            return "https://youtube.com/watch?v=%s" % random_song_vid

    return "https://youtube.com/watch?v=IKlQMqPSwek"


def call_webhook(youtube_video_url):
    # 개인 채널
    #webhook_url = "https://hook.dooray.com/services/1387695619080878080/2957326539523470391/GvPIA6NATC67gi9492YTTQ"
    # 모니터링플랫폼개발팀 채널
    webhook_url = "https://hook.dooray.com/services/1387695619080878080/2957329687924651354/wUnX5Qv2QJKojDpR-xsuUA"
    data = {'botName': '음악 추천', 'botIconImage': 'https://www.flaticon.com/premium-icon/icons/svg/1895/1895657.png', 'text': youtube_video_url}
    headers = {'Content-Type': 'application/json'}
    if requests.post(webhook_url, data=json.dumps(data), headers=headers):
        print("success")
    else:
        print("failure")
        
                       
if __name__ == "__main__":
    video_url = collect_some_charts()
    call_webhook(video_url)

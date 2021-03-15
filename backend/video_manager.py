#!/usr/bin/env python


import re
import random
import json
import time
from datetime import datetime, date
from typing import List, Tuple, Optional
import requests
from util import Util
from db_manager import DBManager
from app import app


class VideoManager:
    video_url_prefix = "https://youtube.com/watch?v="
    default_video_url = "https://youtube.com/watch?v=IKlQMqPSwek"
    db_file_name = "song_video.db"
    table_name = "song_video"


    def __init__(self) -> None:
        self.conf = Util.read_config("conf.json")
        if not self.conf or "google_api_key" not in self.conf:
            raise Exception("Configuration error")
        self.db_manager = DBManager(VideoManager.db_file_name, VideoManager.table_name)


    def __del__(self) -> None:
        self.conf = {}
        del self.db_manager


    def get_youtube_link(self, song_name: str) -> Tuple[Optional[str], Optional[str]]:
        encoded_song_name = requests.utils.quote(song_name)
        url = "https://www.googleapis.com/youtube/v3/search?part=id,snippet&key=%s&q=%s" % (self.conf["google_api_key"], encoded_song_name)
        response = requests.get(url)
        if response and response.status_code == 200:
            data = json.loads(response.text)
            if "items" in data:
                if len(data["items"]) > 0:
                    for item in data["items"]:
                        if "snippet" in item and item["snippet"] and "title" in item["snippet"] and re.search(r'([Cc]over|노래방(?!에서)|직캠|모음|\[도서\])', item["snippet"]["title"]):
                            continue
                        return item["id"]["videoId"], item["snippet"]["title"]
        else:
            app.logger.debug("error in getting data of '%s' from youtube", song_name)
            app.logger.debug(response.status_code)
            app.logger.debug(response.text)

        return (None, None)


    @staticmethod
    def collect_song_name_list_from_chart(term: str, year: int, week: int) -> List[Tuple[str, int]]:
        app.logger.debug("# collect_song_name_list_from_chart(term=%s, year=%d, week=%d)", term, year, week)
        if term == "year":
            week_str = ""
        else:
            week_str = "&targetTime=%d" % week
        # m년 n주차
        chart_url = "http://gaonchart.co.kr/main/section/chart/online.gaon?nationGbn=T&serviceGbn=ALL%s&hitYear=%d&termGbn=%s" % (week_str, year, term)

        result_list: List[Tuple[str, int]] = []
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
                        result_list.append((title + " " + singer, year))
                        state = 0
        else:
            app.logger.debug(response)

        return result_list


    def collect(self) -> None:
        this_year = date.today().year
        last_year = this_year - 1
        week = datetime.now().isocalendar()[1]
        old_days = random.randrange(2011, last_year)

        # 주간(최신)
        recent_week_song_name_list = VideoManager.collect_song_name_list_from_chart("week", this_year, week)
        # 작년
        last_year_song_name_list = VideoManager.collect_song_name_list_from_chart("year", last_year, 0)
        # 작년 이전
        old_days_song_name_list = VideoManager.collect_song_name_list_from_chart("year", old_days, 0)

        failure_count = 0
        for song_name, year in set(recent_week_song_name_list + last_year_song_name_list + old_days_song_name_list):
            # cached data
            video_id: Optional[str] = self.db_manager.get_video_id_by_song_name(song_name)
            if not video_id:
                video_id, video_name = self.get_youtube_link(song_name)
                app.logger.debug("song: %s -> vide: %s", song_name, video_name)
                # fast fallback
                if not video_id:
                    failure_count = failure_count + 1
                    if failure_count >= 5:
                        break

                # update cache
                self.db_manager.put(song_name, year, video_id, video_name)
                time.sleep(1)


    def choose_random_video_url(self, year: int=None) -> str:
        random.seed(datetime.now())
        failure_count = 0
        while True:
            if failure_count >= 5:
                break

            if year:
                video_id = self.db_manager.get_random_video_id_by_year(year)
            else:
                video_id = self.db_manager.get_random_video_id()

            if video_id:
                video_url = VideoManager.video_url_prefix + video_id
                app.logger.debug("video_url=%s", video_url)
                return video_url

            failure_count = failure_count + 1

        return VideoManager.default_video_url

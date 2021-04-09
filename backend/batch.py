#!/usr/bin/env python
# -*- encoding: utf-8 -*-


import sys
import os
import json
from typing import Dict, Any
import logging.config
import requests
from video_manager import VideoManager
from util import Util


logging.basicConfig(filename='../run.log', level=logging.DEBUG)
LOGGER = logging.getLogger()


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


def main() -> int:
    video_manager = VideoManager(LOGGER)
    video_manager.collect()
    video_url = video_manager.choose_random_video_url()
    if not video_url:
        return -1
    print(video_url)

    conf = Util.read_config("conf.json")
    if not conf or "google_api_key" not in conf:
        return -1
    call_webhook(conf, video_url)
    return 0


if __name__ == "__main__":
    sys.exit(main())

import json

import requests
from botpy import logging

_log = logging.get_logger()
def search_meme(url,keyword,tags):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36 Edg/139.0.0.0",
        "Content-Type": "application/json"
    }
    try:
        response = requests.post(url, headers=headers, json={
            "barrage":keyword,
            "submitTime":[],
            "tags":""
        })
        if response.ok:
            data = response.json().get("data")
            return data
        else:
            raise Exception(response.text)
    except Exception as e:
        _log.error(e)
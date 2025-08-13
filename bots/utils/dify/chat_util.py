import requests
from botpy import logging

from bots import global_config

_log = logging.get_logger()
def get_reply(conversation_id,user_id,text,url,api_key):
    try:
        response = requests.post(url=url, headers={
        "Authorization": f"Bearer {api_key}"},
                  json={
                      "response_mode": "blocking",
                      "user": user_id,
                      "inputs": {
                      },
                      "query": text,
                      "conversation_id": conversation_id
                  }
                )
        _log.info(response)
        if response.ok:
            return response.json()
        else:
            raise Exception()
    except Exception as e:
        raise e
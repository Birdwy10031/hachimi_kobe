import requests
from botpy import logging

_log = logging.get_logger()

def get_reply(conversation_id, user_id, text, file_list, url, api_key):
    try:
        response = requests.post(url=url, headers={
        "Authorization": f"Bearer {api_key}"},
                  json={
                      "response_mode": "blocking",
                      "user": user_id,
                      "inputs": {
                          "img":[
                              {
                                  "dify_model_identity": "__dify__file__",
                                  "id": None,
                                  "tenant_id": "963fc7bf-c699-4f9e-8554-2dea35627665",
                                  "type": "image",
                                  "transfer_method": "remote_url",
                                  "remote_url": "https://assets-docs.dify.ai/dify-enterprise-mintlify/zh_CN/guides/workflow/812d1b2f167065e17df8392b2cb3cc8a.png",
                                  "related_id": None,
                                  "filename": "812d1b2f167065e17df8392b2cb3cc8a.png",
                                  "extension": ".jpg",
                                  "mime_type": "image/jpg",
                                  "size": 253358,
                                  "url": "https://assets-docs.dify.ai/dify-enterprise-mintlify/zh_CN/guides/workflow/812d1b2f167065e17df8392b2cb3cc8a.png"
                              }
                          ]
                      },
                      "query": text,
                      "conversation_id": conversation_id,
                      "files":[]
                  }
                )
        _log.info(response.text)
        if response.ok:
            return response.json()
        else:
            raise Exception(response.text)
    except Exception as e:
        raise e
def upload(user_id,file_path,url,api_key):
    try:
        response = requests.post(url=url, headers={
            "Authorization": f"Bearer {api_key}"},
                                 data={
                                    "file": open(file_path, "rb"),
                                    "user": user_id,
                                 }
                                 )
        _log.info(response.text)
        if response.ok:
            return response.json()
        else:
            raise Exception(response.text)
    except Exception as e:
        raise e

if __name__ == '__main__':
    data = get_reply(None,"test","你看看",["https://ts2.tc.mm.bing.net/th/id/OIP-C.PHgMwKINH3zNyGGEIZO20gHaKh?rs=1&pid=ImgDetMain&o=7&rm=3"],"http://119.29.219.247/v1/chat-messages","app-eji81DemxMjijUSEsiDLfjC3")
    print(data)
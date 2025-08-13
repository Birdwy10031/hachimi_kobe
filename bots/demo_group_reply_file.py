# -*- coding: utf-8 -*-
import asyncio
import os

import botpy
from botpy import logging
from botpy.ext.cog_yaml import read
from botpy.message import GroupMessage, Message

test_config = read(os.path.join(os.path.dirname(__file__), "config.yaml"))

_log = logging.get_logger()


class MyClient(botpy.Client):
    async def on_ready(self):
        _log.info(f"robot 「{self.robot.name}」 on_ready!")

    async def on_group_at_message_create(self, message: GroupMessage):
        file_url = "https://brdw-1367983852.cos.ap-chengdu.myqcloud.com/output.silk?q-sign-algorithm=sha1&q-ak=AKIDNr48oaBd-lOoqUa8nd772wB_aJHPw-sqKA3JgjRTGojqSR_ZxJkKBS121c6Mv06e&q-sign-time=1754929621;1754933221&q-key-time=1754929621;1754933221&q-header-list=host&q-url-param-list=&q-signature=4388a436b8bd59122b076bcc46d9616acf92d172&x-cos-security-token=AEwLSScBV6ROKB6u9DjjVFj7G8EAQzia385d72bed889dabe0cab0896f4e7600bWM3oOkIyq1sx-g6ccRt4-qeHOH33tQnc0iLyvbK97fd_Fl8d0E8kdMfVtRN2TlpuPilsr1dpJMPbNWZHxhLiyVuRgkjqJZAs_wG5qykuLWgK5yNhVI2QegVPu3Bpnzu0heMoIqbO1TdyYyAGrvze-7dw_-GHXA2bFFs4YwHE6D75Ime7buaQA3f4sTKYuFJdsj70GeJY9o0hBj4xdrBBLyoYns11XauLtIzI4FnOUBbGQDeshlb88sZuvyqvmPadCQ8gU0fmYBAt9n9wQS9Eaw"  # 这里需要填写上传的资源Url
        uploadMedia = await message._api.post_group_file(
            group_openid=message.group_openid, 
            file_type=3, # 文件类型要对应上，具体支持的类型见方法说明
            url=file_url # 文件Url

        )

        # 资源上传后，会得到Media，用于发送消息
        await message._api.post_group_message(
            group_openid=message.group_openid,
            msg_type=7,  # 7表示富媒体类型
            msg_id=message.id, 
            media=uploadMedia
        )

if __name__ == "__main__":
    # 通过预设置的类型，设置需要监听的事件通道
    # intents = botpy.Intents.none()
    # intents.public_messages=True

    # 通过kwargs，设置需要监听的事件通道
    intents = botpy.Intents(public_messages=True)
    client = MyClient(intents=intents)
    client.run(appid=test_config["appid"], secret=test_config["secret"])
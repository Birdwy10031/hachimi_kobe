# -*- coding: utf-8 -*-
import os

import botpy
from botpy import logging
from botpy.ext.cog_yaml import read
from botpy.message import GroupMessage
from bots.utils.dify import chat_util
from bots.utils.redis.redis_client import RedisClient

test_config = read(os.path.join(os.path.dirname(__file__), "config.yaml"))
_log = logging.get_logger()
# 连接redis
redis = RedisClient(host = test_config["redis_host"],password = test_config["redis_password"])
chat_url = test_config["kobe_chat_url"]
chat_api_key = test_config["kobe_chat_api_key"]

class MyClient(botpy.Client):
    async def on_ready(self):
        _log.info(f"robot 「{self.robot.name}」 on_ready!")

    async def on_group_at_message_create(self, message: GroupMessage):
        _log.info(message)
        text = message.content
        user_id = message.author.member_openid
        group_id = message.group_openid
        bot_name = self.robot.name
        _log.info(text)
        #判断cmd消息
        if text.startswith(' /'):
            cmd, *args = text[2:].split()
            _log.info(f"收到命令：{cmd}，参数：{args}")
            if cmd == "man":
                messageResult = await message._api.post_group_message(
                    group_openid=group_id,
                    msg_type=0,
                    msg_id=message.id,
                    content="What can i say?"
                )
                _log.info(messageResult)
                return
            elif cmd == "哈基米":
                #上传后发送富媒体
                file_url = "https://hachimi-kobe-bots.oss-cn-chengdu.aliyuncs.com/audio/hachimi/firstKey.silk?Expires=1755099805&OSSAccessKeyId=TMP.3KrTQxasZ5xUC1fGBQ1fxuxp9drDBL1dmDV65PzNzW8vtjGhfrqxv3MSRDcCBanV5QGBtHE9tZSuPVbwNWzdNV5hNr1Hc4&Signature=fw8lOU71J3sNOlTglec6etRsw%2Fo%3D"  # 这里需要填写上传的资源Url
                uploadMedia = await message._api.post_group_file(
                    group_openid=message.group_openid,
                    file_type=3,  # 文件类型要对应上，具体支持的类型见方法说明
                    url=file_url  # 文件Url

                )

                # 资源上传后，会得到Media，用于发送消息
                await message._api.post_group_message(
                    group_openid=message.group_openid,
                    msg_type=7,  # 7表示富媒体类型
                    msg_id=message.id,
                    media=uploadMedia
                )
                return

        try:
            key = bot_name+":"+user_id
            conversation_id = None
            if redis.exists(key):
                conversation_id = redis.get(key)
                _log.info(f"继续对话{conversation_id}")
            data = chat_util.get_reply(conversation_id,user_id,text,chat_url,chat_api_key)
            messageResult = await message._api.post_group_message(
                    group_openid=group_id,
                    msg_type=0,
                    msg_id=message.id,
                    content=data.get('answer'),
                    )
            _log.info(messageResult)
            #关联 user->conversation_id
            #保留20min
            redis.set(key,data.get("conversation_id"),ex=1200)
        except Exception as e:
            _log.info(f"Unexpected error: {e}")



if __name__ == "__main__":
    # 通过预设置的类型，设置需要监听的事件通道
    # intents = botpy.Intents.none()
    # intents.public_messages=True

    # 通过kwargs，设置需要监听的事件通道
    intents = botpy.Intents(public_messages=True)


    kobe = MyClient(intents=intents)
    kobe.run(appid=test_config["kobe_appid"], secret=test_config["kobe_secret"])

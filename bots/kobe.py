# -*- coding: utf-8 -*-
import json
import os
import random
from http.client import responses

import botpy
from botpy import logging
from botpy.ext.cog_yaml import read
from botpy.message import GroupMessage
from bots.utils.dify import chat_util
from bots.utils.redis.redis_client import RedisClient
from bots.utils.sb_6657 import sb_6657_util
from bots.utils.scrap.hltv import HltvScraper


config = read(os.path.join(os.path.dirname(__file__), "config.yaml"))
_log = logging.get_logger()
# 连接redis
redis = RedisClient(host = config["redis_host"], password = config["redis_password"])
chat_url = config["chat_url"]
chat_api_key = config["kobe_chat_api_key"]
translator_api_key = config["translator_api_key"]
hltv_user_id = "Counter-Strike Fun"
scraper = HltvScraper()
def format_news_list(news_list):

    res = "\n"
    ch_news_list = []
    conversation_id = redis.get(hltv_user_id)
    try:
        #必须先转成dict，然后jsonstr
        data = chat_util.get_reply(conversation_id, hltv_user_id, json.dumps(news_list), chat_url, translator_api_key)
        # 固定一个user 一个conversation
        redis.set(hltv_user_id, data["conversation_id"])
        ch_news_list = json.loads(data.get('answer'))
        _log.info(ch_news_list.__str__)
    except Exception as e:
        _log.error(e)

    for index, news in enumerate(news_list):
        ch_news = ch_news_list[index]
        res+=f"\n{index}:"
        res+=f"\n  {news['title']} {news['recent']}"
        res+=f"\n  {ch_news['title']}"

    return res

class MyClient(botpy.Client):
    async def on_ready(self):
        # news = await scraper.scrap_news_list()
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
            cmd, arg = text[2:].split()
            _log.info(f"收到命令：{cmd}，参数：{arg}")
            if cmd == "来点烂梗":
                search_url_6657 = config["search_url_6657"]
                meme_list = sb_6657_util.search_meme(url=search_url_6657,keyword=arg,tags="")
                reply = ""
                if meme_list:
                    sz = len(meme_list)
                    if sz > 20:
                        for _ in range(sz):
                            cur = random.randint(0,sz-1)
                            meme = meme_list[cur]
                            reply+=f'\n {meme["barrage"]}'
                    else:
                        for meme in meme_list:
                            reply+=f'\n {meme["barrage"]}'
                else:
                    reply="太有小众宝藏关键词了，啥都没找到！"
                messageResult = await message._api.post_group_message(
                    group_openid=group_id,
                    msg_type=0,
                    msg_id=message.id,
                    content=reply
                )
                _log.info(messageResult)
                return
            elif cmd == "hltvNews":
                #爬取最新新闻
                # 启动chrome
                await scraper.start()
                living_name,news_list =await scraper.scrap_news_list()
                reply = ""
                if living_name:
                    reply += f"现在有小众宝藏比赛哦，6657见收到扣1：{living_name}\n"
                reply += "本日新闻："+format_news_list(news_list)
                # #上传后发送富媒体
                # file_url = "https://hachimi-kobe-bots.oss-cn-chengdu.aliyuncs.com/audio/hachimi/firstKey.silk?Expires=1755099805&OSSAccessKeyId=TMP.3KrTQxasZ5xUC1fGBQ1fxuxp9drDBL1dmDV65PzNzW8vtjGhfrqxv3MSRDcCBanV5QGBtHE9tZSuPVbwNWzdNV5hNr1Hc4&Signature=fw8lOU71J3sNOlTglec6etRsw%2Fo%3D"  # 这里需要填写上传的资源Url
                # uploadMedia = await message._api.post_group_file(
                #     group_openid=message.group_openid,
                #     file_type=3,  # 文件类型要对应上，具体支持的类型见方法说明
                #     url=file_url  # 文件Url
                #
                # )
                #
                # # 资源上传后，会得到Media，用于发送消息
                # await message._api.post_group_message(
                #     group_openid=message.group_openid,
                #     msg_type=7,  # 7表示富媒体类型
                #     msg_id=message.id,
                #     media=uploadMedia
                # )
                messageResult = await message._api.post_group_message(
                    group_openid=group_id,
                    msg_type=0,
                    msg_id=message.id,
                    content=reply
                )
                _log.info(messageResult)
                return
            elif cmd == "hltvMatches":
                # 爬取赛事
                # 启动chrome
                await scraper.start()
                reply = ""
                match_list = await scraper.scrap_match_list()
                _log.info(match_list)
                for match in match_list:
                    team1 = match["team1"]
                    team2 = match["team2"]
                    if not team1["time"]:
                        #已经开打
                        reply+=f"\n {team1['name']} vs {team2['name']} {team1['score']}({team1['mapsWon']}):{team2['mapsWon']}({team2['mapsWon']})"
                    else:
                        reply+=f"\n {team1['name']} vs {team2['name']} {team1['time']}"
                messageResult = await message._api.post_group_message(
                        group_openid=group_id,
                        msg_type=0,
                        msg_id=message.id,
                        content=reply
                )
                _log.info(messageResult)
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

    #通过kwargs，设置需要监听的事件通道
    intents = botpy.Intents(public_messages=True)
    kobe = MyClient(intents=intents)
    kobe.run(appid=config["kobe_appid"], secret=config["kobe_secret"])

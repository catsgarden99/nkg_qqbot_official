# -*- coding: utf-8 -*-
import asyncio
import json
import os

import botpy
from botpy import logging
from botpy.ext.cog_yaml import read
from botpy.message import GroupMessage, Message
import requests

test_config = read(os.path.join(os.path.dirname(__file__), "config.yaml"))
with open('groupmember_city.json', 'r') as mem_city_file:
    member_city = dict(json.load(mem_city_file))
# print(member_city)
gaodekey = test_config["gaodekey"]

_log = logging.get_logger()


class MyClient(botpy.Client):
    async def on_ready(self):
        _log.info(f"robot 「{self.robot.name}」 on_ready!")

    async def on_group_at_message_create(self, message: GroupMessage):
        # 天气
        print(message.author.member_openid)
        user_openid = message.author.member_openid

        reply_str = ""
        
        if message.content.startswith(" /天气 "):

            address = message.content.replace(" ", "")[3:]

            if address == "":
                if user_openid not in member_city:
                    reply_str = "请设置默认城市"
                else:
                    address = member_city[user_openid]

            addressCode_json = requests.get("https://restapi.amap.com/v3/config/district",{"keywords":address,"subdistrict":0,"key":gaodekey}).json()["districts"]
            if len(addressCode_json) == 0:
                reply_str = "不认识这个城市捏"
            else:
                addressCode = addressCode_json[0]["adcode"]
                weather = requests.get("https://restapi.amap.com/v3/weather/weatherInfo",{"city":addressCode,"key":gaodekey,"extensions":"base"}).json()
                temperature = weather["lives"][0]["temperature"]
                reply_str = address + "目前温度为：" + temperature + "度"

            # 回复
            messageResult = await message._api.post_group_message(
                group_openid=message.group_openid,
                msg_type=0, 
                msg_id=message.id,
                content=reply_str
                )
            _log.info(messageResult)

        if message.content.startswith(" /天气默认城市 "):
            # 截取地址
            member_city[user_openid] = message.content.replace(" ", "")[7:]
            print(member_city)
            # 写入本地
            with open('groupmember_city.json', 'w') as mem_city_file:
                json.dump(member_city,mem_city_file)
            reply_str = "已添加天气默认城市"
            # 回复
            messageResult = await message._api.post_group_message(
                group_openid=message.group_openid,
                msg_type=0, 
                msg_id=message.id,
                content=reply_str
                )
            _log.info(messageResult)
            
        if message.content.startswith(" /摸鱼日历 "):
            file_url = "https://api.j4u.ink/v1/store/redirect/moyu/calendar/today.png"  # 这里需要填写上传的资源Url

            try:
                uploadMedia = await message._api.post_group_file(
                    group_openid=message.group_openid, 
                    file_type=1, # 文件类型要对应上，具体支持的类型见方法说明
                    url=file_url # 文件Url
                )

                await message._api.post_group_message(
                    group_openid=message.group_openid,
                    msg_type=7,  # 7表示富媒体类型
                    msg_id=message.id, 
                    media=uploadMedia
                )
            except Exception as e:
                # print(f"图片下载失败！ Caught an exception: {e}")
                messageResult = await message._api.post_group_message(
                    group_openid=message.group_openid,
                    msg_type=0, 
                    msg_id=message.id,
                    content="api又坏了拿不到图片啦"
                    )
                _log.info(messageResult)


if __name__ == "__main__":
    # 通过预设置的类型，设置需要监听的事件通道
    # intents = botpy.Intents.none()
    # intents.public_messages=True

    # 通过kwargs，设置需要监听的事件通道
    intents = botpy.Intents(public_messages=True)
    client = MyClient(intents=intents)
    client.run(appid=test_config["appid"], secret=test_config["secret"])
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
    member_city = json.load(mem_city_file)
print(member_city)
gaodekey = test_config["gaodekey"]

_log = logging.get_logger()


class MyClient(botpy.Client):
    async def on_ready(self):
        _log.info(f"robot 「{self.robot.name}」 on_ready!")

    async def on_group_at_message_create(self, message: GroupMessage):
        # print(message.content)
        # 天气
        print(message.author.member_openid)
        user_openid = message.author.member_openid

        reply_str = ""
        
        if message.content.startswith(" /天气 "):
            address = message.content.replace(" ", "")[3:]
            # if member_city
            addressCode = requests.get("https://restapi.amap.com/v3/config/district",{"keywords":address,"subdistrict":0,"key":gaodekey}).json()["districts"][0]["adcode"]
            weather = requests.get("https://restapi.amap.com/v3/weather/weatherInfo",{"city":addressCode,"key":gaodekey,"extensions":"base"}).json()
            temperature = weather["lives"][0]["temperature"]

            reply_str = address + "目前温度为：" + temperature + "度"

        if message.content.startswith(" /天气默认城市 "):
            # 截取地址
            member_city[user_openid] = message.content.replace(" ", "")[7:]
            print(member_city)
            # 写入本地
            with open('groupmember_city.json', 'w') as mem_city_file:
                json.dump(member_city,mem_city_file)
            reply_str = "已添加天气默认城市"
            

        messageResult = await message._api.post_group_message(
            group_openid=message.group_openid,
              msg_type=0, 
              msg_id=message.id,
            #   content=f"收到了消息：{message.content}" + weather_str
              content=reply_str
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
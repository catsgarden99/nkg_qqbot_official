# -*- coding: utf-8 -*-
import asyncio
import os

import botpy
from botpy import logging
from botpy.ext.cog_yaml import read
from botpy.message import GroupMessage, Message
import requests

test_config = read(os.path.join(os.path.dirname(__file__), "config.yaml"))
gaodekey = test_config["gaodekey"]

_log = logging.get_logger()


class MyClient(botpy.Client):
    async def on_ready(self):
        _log.info(f"robot 「{self.robot.name}」 on_ready!")

    async def on_group_at_message_create(self, message: GroupMessage):
        print(message.content)
        if message.content.startswith(" /天气"):
            address = message.content.replace(" ", "")[3:]
            addressCode = requests.get("https://restapi.amap.com/v3/config/district",{"keywords":address,"subdistrict":0,"key":gaodekey}).json()["districts"][0]["adcode"]
            weather = requests.get("https://restapi.amap.com/v3/weather/weatherInfo",{"city":addressCode,"key":gaodekey,"extensions":"base"}).json()
            temperature = weather["lives"][0]["temperature"]

            # print(weather.json())
            weather_str = address + "目前温度为：" + temperature + "度"
            

        messageResult = await message._api.post_group_message(
            group_openid=message.group_openid,
              msg_type=0, 
              msg_id=message.id,
            #   content=f"收到了消息：{message.content}" + weather_str
              content=weather_str
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
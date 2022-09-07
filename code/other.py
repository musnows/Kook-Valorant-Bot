import json
import time

import aiohttp
from khl import Bot, Client, Event, EventTypes, Message
from khl.card import Card, CardMessage, Element, Module, Struct, Types


# 历史上的今天，来自https://www.free-api.com/doc/317
async def history(msg: Message):
    url = "https://api.asilu.com/today"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            json_dict = json.loads(await response.text())
    cm = CardMessage()
    now_date = time.strftime("%m月%d日", time.localtime())
    c1 = Card(Module.Header(f'历史上的{now_date}'), Module.Context('以古为镜,可以知兴替...'))
    c1.append(Module.Divider())
    for its in json_dict['data']:
        c1.append(
            Module.Section(f"{its['year']}年，{its['title']}", Element.Button('查看', f"{its['link']}", Types.Click.LINK)))
        c1.append(Module.Divider())

    c1.append(Module.Context('注：免费api，部分结果可能有出入'))
    cm.append(c1)
    await msg.reply(cm)


# 天气 来自http://api.asilu.com/#today
async def weather(msg: Message, city: str):
    url = f'https://query.asilu.com/weather/baidu?city={city}'
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            json_dict = json.loads(await response.text())
    cm = CardMessage()
    now_date = time.strftime("%Y-%m-%d", time.localtime())
    c1 = Card(Module.Header(f"已为您查询 {json_dict['city']} 的天气，更新于{json_dict['update_time']}"),
              Module.Context('力尽不知热，但惜夏日长...'))
    c1.append(Module.Divider())
    i = 3
    for its in json_dict['weather']:
        if i > 0:
            c1.append(Module.Section(f"{its['date']}  天气: {its['weather']}  温度: {its['temp']}  风向: {its['wind']}", ))
            c1.append(Module.Divider())
            i -= 1
        else:
            break

    c1.append(Module.Context('来自百度，部分结果可能有出入'))
    cm.append(c1)
    await msg.reply(cm)

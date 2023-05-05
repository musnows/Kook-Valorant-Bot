import json
import time
import aiohttp
import random
import traceback
from datetime import datetime,timedelta

from khl import Bot,Message,PrivateMessage,Channel
from khl.card import Card, CardMessage, Element, Module, Types, Struct
from ..utils.log import BotLog


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



#####################################################################################################

def init(bot:Bot,debug_ch:Channel):
    """debug_ch: channel for sending debug msg
    """
    # 倒计时函数，单位为秒，默认60秒
    @bot.command(name="countdown")
    async def countdown(msg: Message, time: int = 60, *args):
        BotLog.log_msg(msg)
        if args != ():
            await msg.reply(f"参数错误，countdown命令只支持1个参数\n正确用法: `/countdown 120` 生成一个120s的倒计时")
            return
        elif time <= 0 or time >= 90000000:
            await msg.reply(f"倒计时时间超出范围！")
            return
        try:
            cm = CardMessage()
            c1 = Card(Module.Header('本狸帮你按下秒表喽~'), color=(198, 65, 55))  # color=(90,59,215) is another available form
            c1.append(Module.Divider())
            c1.append(Module.Countdown(datetime.now() + timedelta(seconds=time), mode=Types.CountdownMode.SECOND))
            cm.append(c1)
            await msg.reply(cm)
        except Exception as result:
            await BotLog.base_exception_handler("countdown", traceback.format_exc(), msg, debug_send=debug_ch)


    # 掷骰子 saying `!roll 1 100` in channel,or `/roll 1 100 5` to dice 5 times once
    @bot.command(name="roll")
    async def roll(msg: Message, t_min: int = 1, t_max: int = 100, n: int = 1, *args):
        BotLog.log_msg(msg)
        if args != ():
            return await msg.reply(
                f"参数错误，roll命令只支持3个参数\n正确用法:\n```\n/roll 1 100 生成一个1到100之间的随机数\n/roll 1 100 3 生成三个1到100之间的随机数\n```")
        elif t_min >= t_max:  #范围小边界不能大于大边界
            return await msg.reply(f'范围错误，必须提供两个参数，由小到大！\nmin:`{t_min}` max:`{t_max}`')
        elif t_max >= 10000000:  #不允许用户使用太大的数字
            return await msg.reply(f"掷骰子的数据超出范围！")
        elif n > 32:
            return await msg.reply(f"当前仅支持同时投掷32个骰子")
        try:
            result = [random.randint(t_min, t_max) for i in range(n)]
            await msg.reply(f'掷出来啦: {result}')
        except Exception as result:
            await BotLog.base_exception_handler("roll", traceback.format_exc(), msg, debug_send=debug_ch)

    # 返回天气
    @bot.command(name='we')
    async def Weather(msg: Message, city: str = "err"):
        BotLog.log_msg(msg)
        if city == "err":
            await msg.reply(f"函数参数错误，城市: `{city}`\n")
            return

        try:
            await weather(msg, city)
        except Exception as result:
            await BotLog.base_exception_handler("Weather", traceback.format_exc(), msg, debug_send=debug_ch)
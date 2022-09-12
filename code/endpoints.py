import json
import time
import aiohttp
from khl import  Message
from khl.card import Card, CardMessage, Element, Module, Types

with open('./config/config.json', 'r', encoding='utf-8') as f:
    config = json.load(f)

Botoken = config['token']
kook = "https://www.kookapp.cn"
headers = {f'Authorization': f"Bot {Botoken}"}

###########################翻译############################################

import urllib.request
import urllib.parse

# youdao code is from https://github.com/Chinese-boy/Many-Translaters
def youdao_translate(txt: str):
    #print(txt)
    url = 'http://fanyi.youdao.com/translate?smartresult=dict&smartresult=rule&sessionFrom=https://www.baidu.com/link'
    data = {
        'from': 'AUTO',
        'to': 'AUTO',
        'smartresult': 'dict',
        'client': 'fanyideskweb',
        'salt': '1500092479607',
        'sign': 'c98235a85b213d482b8e65f6b1065e26',
        'doctype': 'json',
        'version': '2.1',
        'keyfrom': 'fanyi.web',
        'action': 'FY_BY_CL1CKBUTTON',
        'typoResult': 'true',
        'i': txt
    }

    data = urllib.parse.urlencode(data).encode('utf-8')
    wy = urllib.request.urlopen(url, data)
    html = wy.read().decode('utf-8')
    ta = json.loads(html)
    #print(ta['translateResult'][0][0]['tgt'])
    return ta['translateResult'][0][0]['tgt']


# 读取彩云的key
with open('./config/caiyun.json', 'r', encoding='utf-8') as f:
    config = json.load(f)

CyKey = config['token']

# caiyun translte
async def caiyun_translate(source, direction):
    url = "http://api.interpreter.caiyunai.com/v1/translator"
    # WARNING, this token is a test token for new developers,
    # and it should be replaced by your token
    token = CyKey
    payload = {
        "source": source,
        "trans_type": direction,
        "request_id": "demo",
        "detect": True,
    }
    headers = {
        "content-type": "application/json",
        "x-authorization": "token " + token,
    }

    #用aiohttp效率更高
    async with aiohttp.ClientSession() as session:
        async with session.post(url, data=json.dumps(payload), headers=headers) as response:
            return json.loads(await response.text())["target"]


# 由于彩云不支持输入中文自动翻译成英文（目前只支持其他语种自动转中文）
# 所以需要判断来源是否是中文，如果是中文自动翻译成English
def is_CN(word):
    for ch in word:
        if '\u4e00' <= ch <= '\u9fff':
            return True
    return False


# # for translate test
# txt = input()
# if is_Chinese(txt):
#     target = tranlate(txt, "auto2en")
# else:
#     target = tranlate(txt, "auto2zh")
# print(target)

#################################机器人在玩状态####################################

# 让机器人开始打游戏
async def status_active_game(game: int):
    url = kook + "/api/v3/game/activity"
    params = {"id": game, "data_type": 1}
    async with aiohttp.ClientSession() as session:
        async with session.post(url, data=params, headers=headers) as response:
            return json.loads(await response.text())


# 让机器人开始听歌
async def status_active_music(name: str, singer: str):
    url = kook + "/api/v3/game/activity"
    params = {"data_type": 2, "software": "qqmusic", "singer": singer, "music_name": name}
    async with aiohttp.ClientSession() as session:
        async with session.post(url, data=params, headers=headers) as response:
            return json.loads(await response.text())


# 删除机器人的当前动态
async def status_delete(d: int):
    url = kook + "/api/v3/game/delete-activity"
    params = {"data_type": d}
    async with aiohttp.ClientSession() as session:
        async with session.post(url, data=params, headers=headers) as response:
            return json.loads(await response.text())
            #print(ret)


# 获取服务器用户数量用于更新（现在已经移植到了另外一个bot上）
async def server_status(Gulid_ID: str = "3566823018281801"):
    url = kook + "/api/v3/guild/user-list"
    params = {"guild_id": Gulid_ID}
    async with aiohttp.ClientSession() as session:
        async with session.get(url, params=params, headers=headers) as response:
            ret1 = json.loads(await response.text())
            #print(ret1)
            return ret1

########################################other#######################################

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

from upd_msg import icon_cm
from datetime import datetime,timedelta


#抽奖相关代码（开始抽奖）
def roll_vip_start(vip_num:int,vip_day:int,roll_day:int):
    """
    Args:
        vip_num (int): num of vip uuid
        vip_day (int): day of vip
        roll_day (int): day of roll end

    Returns:
        CardMessage for roll 
    """
    roll_second = roll_day*86400
    cm = CardMessage()
    c = Card()
    c.append(Module.Section(Element.Text(f"添加表情回应，参加抽奖！"), Element.Image(src=icon_cm.ahri_kda3, size='sm')))
    c.append(Module.Context(Element.Text(f"奖励：{vip_day}天的阿狸vip激活码 | 奖品：{vip_num}个", Types.Text.KMD)))
    c.append(
        Module.Countdown(datetime.now() + timedelta(seconds=roll_second), mode=Types.CountdownMode.DAY))
    cm.append(c)
    return cm



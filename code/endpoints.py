import json
import time
import aiohttp
from khl import  Bot,Message,ChannelPrivacyTypes
from khl.card import Card, CardMessage, Element, Module, Types

with open('./config/config.json', 'r', encoding='utf-8') as f:
    config = json.load(f)
#初始化一个bot，下方更新卡片消息需要
bot = Bot(token=config['token'])

kook_base_url = "https://www.kookapp.cn"
kook_headers = {f'Authorization': f"Bot {config['token']}"}

#################################机器人在玩状态####################################

# 让机器人开始打游戏
async def status_active_game(game: int):
    url = kook_base_url + "/api/v3/game/activity"
    params = {"id": game, "data_type": 1}
    async with aiohttp.ClientSession() as session:
        async with session.post(url, data=params, headers=kook_headers) as response:
            return json.loads(await response.text())


# 让机器人开始听歌
async def status_active_music(name: str, singer: str):
    url = kook_base_url + "/api/v3/game/activity"
    params = {"data_type": 2, "software": "qqmusic", "singer": singer, "music_name": name}
    async with aiohttp.ClientSession() as session:
        async with session.post(url, data=params, headers=kook_headers) as response:
            return json.loads(await response.text())


# 删除机器人的当前动态
async def status_delete(d: int):
    url = kook_base_url + "/api/v3/game/delete-activity"
    params = {"data_type": d}
    async with aiohttp.ClientSession() as session:
        async with session.post(url, data=params, headers=kook_headers) as response:
            return json.loads(await response.text())
            #print(ret)


# 获取服务器用户数量用于更新（现在已经移植到了另外一个bot上）
async def guild_userlist(Guild_ID: str = "3566823018281801"):
    url = kook_base_url + "/api/v3/guild/user-list"
    params = {"guild_id": Guild_ID}
    async with aiohttp.ClientSession() as session:
        async with session.get(url, params=params, headers=kook_headers) as response:
            ret1 = json.loads(await response.text())
            #print(ret1)
            return ret1

# 获取阿狸加入的服务器数量
async def guild_list():
    url = kook_base_url + "/api/v3/guild/list"
    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=kook_headers) as response:
            ret1 = json.loads(await response.text())
            #print(ret1)
            return ret1
        
# 获取服务器详情
async def guild_view(Guild_ID:str):
    url = kook_base_url + "/api/v3/guild/view"
    params = {"guild_id": Guild_ID}
    async with aiohttp.ClientSession() as session:
        async with session.get(url, params=params, headers=kook_headers) as response:
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



##########################################icon##############################################

from typing import Union

# 图标
class icon_cm:
    val_logo = "https://img.kookapp.cn/assets/2022-09/gVBtXI0ZSg03n03n.png"
    val_logo_gif = "https://img.kookapp.cn/assets/2022-09/5skrwZcjGJ0dc07i.gif"
    whats_that = "https://img.kookapp.cn/assets/2022-09/uhm2AewC1i0e80e8.png"
    dont_do_that = "https://img.kookapp.cn/assets/2022-09/wUNDAfzBlr0e80e8.png"
    lagging = "https://img.kookapp.cn/assets/2022-09/D1nqrTszjQ0e80e8.png"
    correct = "https://img.kookapp.cn/assets/2022-09/DknXSpwrlQ0e80e8.gif"
    duck = "https://img.kookapp.cn/assets/2022-09/qARsaxW6lp0e80e8.gif"
    that_it = "https://img.kookapp.cn/assets/2022-09/LqD0pQY2P70e80e8.png"
    to_much_money = "https://img.kookapp.cn/assets/2022-09/y17ZhjjaVf0e80e8.png"
    shaka = "https://img.kookapp.cn/assets/2022-09/kMWT5AoEic0e80e8.png"
    say_hello_to_camera = "https://img.kookapp.cn/assets/2022-09/sHh8VJrMp20e80e8.png"
    crying_crab = "https://img.kookapp.cn/assets/2022-09/DfveorD0lS0e80e8.png"
    im_good_phoniex = "https://img.kookapp.cn/assets/2022-09/RdiFsx16Aw0e80e8.png"
    rgx_card = "https://img.kookapp.cn/assets/2022-09/p1VwoNZZWD0e80e8.gif"
    rgx_broken = "https://img.kookapp.cn/assets/2022-09/A8wPGOtJmz0e80e8.gif"
    shot_on_fire = "https://img.kookapp.cn/assets/2022-09/L5EeqS3GDC0e80e8.png"
    powder = "https://img.kookapp.cn/assets/2022-09/nwXm6aNzj20e80e8.png"
    ahri1 = "https://img.kookapp.cn/assets/2022-09/TU9bVQdHiz08c08c.jpg"
    ahri2 = "https://img.kookapp.cn/assets/2022-09/bK1v7R6D7j08c08c.jpg"
    ahri3 = "https://img.kookapp.cn/assets/2022-09/zS5B2wkBvG08c08c.jpg"
    ahri_kda1 = "https://img.kookapp.cn/assets/2022-09/kOwzlg7x6M0rs0rs.jpg"
    ahri_kda2 = "https://img.kookapp.cn/assets/2022-09/OMcQuhcrXo0sc0sc.jpg"
    ahri_kda3 = "https://img.kookapp.cn/assets/2022-09/JHUxBavOeC0xg0xg.jpg"
    ahri_star = "https://img.kookapp.cn/assets/2022-09/NY1m6182Ae0v80v8.jpg"
    ahri_dark = "https://img.kookapp.cn/assets/2022-09/HJJJPrYxUo14w14w.jpg"
    ahri_sour = "https://img.kookapp.cn/assets/2022-09/bnPK4GhBfc0x40x4.jpg"
    ahri_forest = "https://img.kookapp.cn/assets/2022-09/9ObV0banuE1ew1ew.jpg"
    ahri_game = "https://img.kookapp.cn/assets/2022-09/Rp6bnjsLnZ0cg0cg.jpg"


#更新卡片消息
async def upd_card(msg_id: str,
                   content,
                   target_id='',
                   channel_type: Union[ChannelPrivacyTypes, str] = 'public',
                   bot=bot):
    content = json.dumps(content)
    data = {'msg_id': msg_id, 'content': content}
    if target_id != '':
        data['temp_target_id'] = target_id
    if channel_type == 'public' or channel_type == ChannelPrivacyTypes.GROUP:
        result = await bot.client.gate.request('POST', 'message/update', data=data)
    else:
        result = await bot.client.gate.request('POST', 'direct-message/update', data=data)
    return result

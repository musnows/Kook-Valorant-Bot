import json
import aiohttp
import time

from khl import Bot

with open('./config/config.json', 'r', encoding='utf-8') as f:
    config = json.load(f)
bot = Bot(token=config['token'])

Botoken = config['token']
kook = "https://www.kookapp.cn"
headers = {f'Authorization': f"Bot {Botoken}"}


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


# 获取服务器用户数量用于更新
async def server_status(Gulid_ID: str = "3566823018281801"):
    url = kook + "/api/v3/guild/user-list"
    params = {"guild_id": Gulid_ID}
    async with aiohttp.ClientSession() as session:
        async with session.get(url, params=params, headers=headers) as response:
            ret1 = json.loads(await response.text())
            #print(ret1)
            return ret1

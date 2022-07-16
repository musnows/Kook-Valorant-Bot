import json
import aiohttp
#import asyncio

from khl import Bot

with open('./config/config.json', 'r', encoding='utf-8') as f:
    config = json.load(f)
# 用读取来的 config 初始化 bot，字段对应即可
bot = Bot(token=config['token'])
Botoken=config['token']

# 让阿狸开始打瓦洛兰特
async def status_active():
    url="https://www.kookapp.cn/api/v3/game/activity"
    headers={f'Authorization': f"Bot {Botoken}"}
    params = {"id":453027,"data_type":1}
    async with aiohttp.ClientSession() as session:
        async with session.post(url, data=params,headers=headers) as response:
                return json.loads(await response.text())


# 删除机器人的当前动态
async def status_delete():
    url="https://www.kookapp.cn/api/v3/game/delete-activity"
    headers={f'Authorization': f"Bot {Botoken}"}
    params = {"data_type":1}
    async with aiohttp.ClientSession() as session:
        async with session.post(url, data=params,headers=headers) as response:
                return json.loads(await response.text())
                #print(ret)
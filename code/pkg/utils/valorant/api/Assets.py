# valorant-api.com
import aiohttp
import json


async def fetch_item_iters(iters_id="") -> dict:
    """获取全部的皮肤等级（史诗/传说）,提供uuid则获取特定的结果"""
    url = "https://valorant-api.com/v1/contenttiers/" + iters_id
    headers = {'Connection': 'close'}
    params = {"language": "zh-TW"}
    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers, params=params) as response:
            res_iters = json.loads(await response.text())

    return res_iters


async def fetch_skins(skin_uuid="") -> dict:
    """获取所有皮肤
    - skin_uuid 皮肤的主uuid，和商店返回值中的uuid不是一样的
    - 商店返回值中的uuid是 skin[level][0] 的uuid
    """
    url = "https://valorant-api.com/v1/weapons/skins/" + skin_uuid
    headers = {'Connection': 'close'}
    params = {"language": "zh-TW"}
    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers, params=params) as response:
            res_skin = json.loads(await response.text())

    return res_skin


async def fetch_bundles(bundles_uuid="") -> dict:
    """获取所有皮肤捆绑包,提供uuid则获取特定捆绑包"""
    url = "https://valorant-api.com/v1/bundles/" + bundles_uuid
    headers = {'Connection': 'close'}
    params = {"language": "zh-TW"}
    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers, params=params) as response:
            res_bundle = json.loads(await response.text())

    return res_bundle


async def fetch_contract(contract_uuid="") -> dict:
    """获取通行证情况，提供uuid获取特定通行证"""
    url = "https://valorant-api.com/v1/contracts/" + contract_uuid
    headers = {'Connection': 'close'}
    params = {"language": "zh-TW"}
    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers, params=params) as response:
            res_con = json.loads(await response.text())

    return res_con


async def fetch_playercard(card_uuid="") -> dict:
    """获取玩家卡面，提供uuid获取特定玩家卡片"""
    url = "https://valorant-api.com/v1/playercards/" + card_uuid
    headers = {'Connection': 'close'}
    params = {"language": "zh-TW"}
    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers, params=params) as response:
            res_card = json.loads(await response.text())

    return res_card


async def fetch_title(title_uuid="") -> dict:
    """获取玩家称号，提供uuid获取特定称号"""
    url = "https://valorant-api.com/v1/playertitles/" + title_uuid
    headers = {'Connection': 'close'}
    params = {"language": "zh-TW"}
    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers, params=params) as response:
            res_title = json.loads(await response.text())

    return res_title


async def fetch_spary(spary_uuid="") -> dict:
    """获取喷漆"""
    url = "https://valorant-api.com/v1/sprays/" + spary_uuid
    headers = {'Connection': 'close'}
    params = {"language": "zh-TW"}
    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers, params=params) as response:
            res_sp = json.loads(await response.text())

    return res_sp


async def fetch_buddies(buddies_uuid="") -> dict:
    """获取吊坠"""
    url = "https://valorant-api.com/v1/buddies/levels/" + buddies_uuid
    headers = {'Connection': 'close'}
    params = {"language": "zh-TW"}
    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers, params=params) as response:
            res_sp = json.loads(await response.text())

    return res_sp


async def fetch_skin_levels(skin_level_id="") -> dict:
    """获取皮肤，通过lv0的uuid(商店返回值)"""
    url = f"https://valorant-api.com/v1/weapons/skinlevels/" + skin_level_id
    headers = {'Connection': 'close'}
    params = {"language": "zh-TW"}
    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers, params=params) as response:
            res_skin = json.loads(await response.text())
    return res_skin


async def fetch_agents(agent_uuid="") -> dict:
    """获取英雄信息，提供uuid则获取特定英雄"""
    url = f"https://valorant-api.com/v1/agents/{agent_uuid}"
    headers = {'Connection': 'close'}
    params = {"language": "zh-TW"}
    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers, params=params) as response:
            res_skin = json.loads(await response.text())
    return res_skin


async def fetch_maps(maps_uuid="") -> dict:
    """获取所有地图，提供uuid则获取特定地图"""
    url = "https://valorant-api.com/v1/maps" + maps_uuid
    headers = {'Connection': 'close'}
    params = {"language": "zh-TW"}
    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers, params=params) as response:
            res_skin = json.loads(await response.text())
    return res_skin


async def fetch_maps_url(map_url: str) -> dict:
    """通过地图的url获取地图信息
    - map_url: `/Game/Maps/Triad/Triad`
    """
    maps = await fetch_maps()
    ret = {}
    for m in maps["data"]:
        if m["mapUrl"] == map_url:
            ret = m

    return ret
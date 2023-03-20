# encoding: utf-8:
import json
import aiohttp

from ..EzAuth import X_RIOT_CLIENTVERSION, X_RIOT_CLIENTVPLATFROM, RiotUserToken

# https://github.com/HeyM1ke/ValorantClientAPI

async def fetch_user_gameID(ru: RiotUserToken) -> dict:
    """获取用户游戏id和tag"""
    url = "https://pd.ap.a.pvp.net/name-service/v2/players"
    payload = json.dumps([ru.user_id])
    headers = {
        "Content-Type": "application/json",
        "X-Riot-Entitlements-JWT": ru.entitlements_token,
        "Authorization": "Bearer " + ru.access_token
    }
    async with aiohttp.ClientSession() as session:
        async with session.put(url, headers=headers, data=payload) as response:
            res = json.loads(await response.text())
    return res


async def fetch_daily_shop(ru: RiotUserToken) -> dict:
    """获取用户每日商店"""
    url = "https://pd.ap.a.pvp.net/store/v2/storefront/" + ru.user_id
    headers = {
        "Content-Type": "application/json",
        "X-Riot-Entitlements-JWT": ru.entitlements_token,
        "Authorization": "Bearer " + ru.access_token
    }
    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers) as response:
            res = json.loads(await response.text())
    return res


async def fetch_valorant_point(ru: RiotUserToken) -> dict:
    """获取玩家的vp和r点"""
    url = "https://pd.ap.a.pvp.net/store/v1/wallet/" + ru.user_id
    headers = {
        "Content-Type": "application/json",
        "X-Riot-Entitlements-JWT": ru.entitlements_token,
        "Authorization": "Bearer " + ru.access_token
    }
    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers) as response:
            res = json.loads(await response.text())
    return res


async def fetch_vp_rp_dict(ru: RiotUserToken) -> dict[str, int]:
    """获取vp和r点的dict，先调用原始api，再取出vp和rp
    - {'vp': vp, 'rp': rp}
    """
    resp = await fetch_valorant_point(ru)
    vp = resp["Balances"]["85ad13f7-3d1b-5128-9eb2-7cd8ee0b5741"]  #vp
    rp = resp["Balances"]["e59aa87c-4cbf-517a-5983-6e81511be9b7"]  #R点
    return {'vp': vp, 'rp': rp}


async def fetch_item_price_all(ru: RiotUserToken) -> dict:
    """获取商品价格（所有）"""
    url = "https://pd.ap.a.pvp.net/store/v1/offers/"
    headers = {
        "Content-Type": "application/json",
        "X-Riot-Entitlements-JWT": ru.entitlements_token,
        "Authorization": "Bearer " + ru.access_token
    }
    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers) as response:
            res = json.loads(await response.text())

    return res


async def fetch_item_price_uuid(ru: RiotUserToken, item_id: str) -> str:
    """获取商品价格（用uuid获取单个价格）
    - 返回值为 "0" 代表没有找到
    """
    res = await fetch_item_price_all(ru)  #获取所有价格

    for item in res['Offers']:  #遍历查找指定uuid
        if item_id == item['OfferID']:
            return item

    return "0"  #没有找到


async def fetch_player_loadout(ru: RiotUserToken) -> dict:
    """获取获取玩家当前装备的卡面和称号"""
    url = f"https://pd.ap.a.pvp.net/personalization/v2/players/{ru.user_id}/playerloadout"
    headers = {
        "Content-Type": "application/json",
        "X-Riot-Entitlements-JWT": ru.entitlements_token,
        "Authorization": "Bearer " + ru.access_token,
        'Connection': 'close'
    }
    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers) as response:
            res = json.loads(await response.text())

    return res


async def fetch_player_contract(ru: RiotUserToken) -> dict:
    """获取合约（任务,通信证）进度"""
    #url="https://pd.ap.a.pvp.net/contract-definitions/v2/definitions/story"
    url = f"https://pd.ap.a.pvp.net/contracts/v1/contracts/" + ru.user_id
    headers = {
        "Content-Type": "application/json",
        "X-Riot-Entitlements-JWT": ru.entitlements_token,
        "Authorization": "Bearer " + ru.access_token,
        "X-Riot-ClientPlatform": X_RIOT_CLIENTVPLATFROM,
        "X-Riot-ClientVersion": X_RIOT_CLIENTVERSION
    }
    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers) as response:
            res = json.loads(await response.text())

    return res


async def fetch_player_level(ru: RiotUserToken) -> dict:
    """获取玩家的等级信息
    """
    url = "https://pd.ap.a.pvp.net/account-xp/v1/players/" + ru.user_id
    headers = {
        "Content-Type": "application/json",
        "X-Riot-Entitlements-JWT": ru.entitlements_token,
        "Authorization": "Bearer " + ru.access_token,
    }
    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers) as response:
            res = json.loads(await response.text())

    return res


async def fetch_match_histroy(ru: RiotUserToken, startIndex=0, endIndex=20) -> dict:
    """获取玩家的战绩历史

    Docs: https://valapidocs.techchrism.me/endpoint/match-history
    
    Args:
    - startIndex (Optional)
        The index of the first match to return. Defaults to 0
    - endIndex (Optional)
        The index of the last match to return. Defaults to 20
    """
    url = f"https://pd.ap.a.pvp.net/match-history/v1/history/{ru.user_id}?startIndex={startIndex}&endIndex={endIndex}"
    headers = {
        "Content-Type": "application/json",
        "X-Riot-Entitlements-JWT": ru.entitlements_token,
        "Authorization": "Bearer " + ru.access_token,
    }
    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers) as response:
            res = json.loads(await response.text())

    return res


async def fetch_match_details(ru: RiotUserToken, match_id: str) -> dict:
    """获取某一场比赛的详细信息"""
    url = f"https://pd.ap.a.pvp.net/match-details/v1/matches/{match_id}"
    headers = {
        "Content-Type": "application/json",
        "X-Riot-Entitlements-JWT": ru.entitlements_token,
        "Authorization": "Bearer " + ru.access_token,
    }
    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers) as response:
            res = json.loads(await response.text())

    return res
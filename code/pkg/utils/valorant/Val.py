# encoding: utf-8:
import json
import aiohttp
from khl import Message
from khl.card import Card, Element, Module, Types

# 预加载文件
from .EzAuth import X_RIOT_CLIENTVERSION,X_RIOT_CLIENTVPLATFROM,RiotUserToken
from ..file.Files import GameIdDict, ValErrDict, ValItersList, ValPriceList, ValSkinList
SKIN_ICON_ERR = "https://img.kookapp.cn/assets/2023-02/ekwdy7PiQC0e803m.png"

####################################保存用户的游戏ID操作#######################################

#保存用户id
async def saveid_main(msg: Message, game_id: str) -> None:
    global GameIdDict
    flag = 0
    # 如果用户id已有，则进行修改
    if msg.author_id in GameIdDict.keys():
        GameIdDict[msg.author_id] = game_id
        await msg.reply(f'本狸已经修改好你的游戏id啦!')
        flag = 1  #修改完毕后，将flag置为1

    #没有该用户信息，进行追加操作
    if flag == 0:
        GameIdDict[msg.author_id] = game_id
        await msg.reply(f"本狸已经记下你的游戏id喽~")


# 显示已有id的个数
async def saveid_count(msg: Message) -> None:
    countD = len(GameIdDict)
    await msg.reply(f"目前狸狸已经记下了`{countD}`个小伙伴的id喽~")


# 实现读取用户游戏ID并返回
async def myid_main(msg: Message) -> None:
    if msg.author_id in GameIdDict.keys():
        flag = 1  #找到了对应用户的id
        await msg.reply(f'游戏id: ' + GameIdDict[msg.author_id])
    else:
        countD = len(GameIdDict)
        await msg.reply(f"狸狸不知道你的游戏id呢，用`/saveid`告诉我吧！\n```\n/saveid 你的游戏id```\n目前狸狸已经记下了`{countD}`个小伙伴的id喽！")


####################################  err code  ################################################


# 查询游戏错误码
async def val_errcode(msg: Message, num: str = "-1") -> None:
    if num == "-1":
        await msg.reply(
            '目前支持查询的错误信息有：\n```\n0-1,4-5,7-21,29,31,33,38,43-46,49-70,81,84,128,152,1067,9001,9002,9003\n```\n注：van和val错误码都可用本命令查询'
        )
    elif num in ValErrDict:
        await msg.reply(ValErrDict[num])
    else:
        await msg.reply('抱歉，本狸还不会这个呢~ 你能教教我吗？[当然!](https://f.wps.cn/w/awM5Ej4g/)')


#关于dx报错的解决方法
async def dx123(msg: Message) -> None:
    await msg.reply(
        '报错弹窗内容为`The following component(s) are required to run this program:DirectX Runtime`\n需要下载微软官方驱动安装，官网搜索[DirectX End-User Runtime Web Installer]\n你还可以下载本狸亲测可用的DX驱动 [链接](https://pan.baidu.com/s/1145Ll8vGtByMW6OKk6Zi2Q)，暗号是1067哦！\n狸狸记得之前玩其他游戏的时候，也有遇到过这个问题呢~'
    )


###################################### local files search ######################################################


#从list中获取价格
def fetch_item_price_bylist(item_id) -> dict:
    for item in ValPriceList['Offers']:  #遍历查找指定uuid
        if item_id == item['OfferID']:
            return item
    return {}

#从list中获取等级(这个需要手动更新)
def fetch_item_iters_bylist(iter_id) -> dict:
    res = {}
    for iter in ValItersList['data']:  #遍历查找指定uuid
        if iter_id == iter['uuid']:
            res = {'data': iter}  #所以要手动创建一个带data的dict作为返回值
    return res


#从list中获取皮肤
def fetch_skin_bylist(item_id) -> dict: 
    res = {}  #下面我们要操作的是获取通行证的皮肤，但是因为遍历的时候已经跳过data了，返回的时候就不好返回
    for item in ValSkinList['data']:  #遍历查找指定uuid
        if item_id == item['levels'][0]['uuid']:
            res['data'] = item  #所以要手动创建一个带data的dict作为返回值
            # 可能出现图标为空的情况（异星霸主 斗牛犬）
            while(res['data']['displayIcon']==None): 
                for level in item['levels']: # 在等级里面找皮肤图标
                    if level["displayIcon"] != None:
                        res['data']['displayIcon'] = level["displayIcon"]
                        break # 找到了，退出循环
                # 没找到，替换成err图片
                res['data']['displayIcon'] = SKIN_ICON_ERR
            
    return res


#从list中，通过皮肤名字获取皮肤列表
def fetch_skin_list_byname(name) ->list[dict]:
    wplist = list()  #包含该名字的皮肤list
    for skin in ValSkinList['data']:
        if name in skin['displayName']:
            data = {'displayName': skin['displayName'], 'lv_uuid': skin['levels'][0]['uuid']}
            wplist.append(data)
    return wplist


#从list中通过皮肤lv0uuid获取皮肤等级
def fetch_skin_iters_bylist(item_id) -> dict:
    res_iters = {}
    for it in ValSkinList['data']:
        if it['levels'][0]['uuid'] == item_id:
            res_iters = fetch_item_iters_bylist(it['contentTierUuid'])
    return res_iters


# 用名字查询捆绑包包含什么枪
async def fetch_bundle_weapen_byname(name)->list[dict]:
    # 捆绑包的所有皮肤
    WeapenList = list()
    for skin in ValSkinList['data']:
        if name in skin['displayName']:
            # 为了方便查询价格，在这里直接把skin的lv0-uuid也给插入进去
            data = {'displayName': skin['displayName'], 'lv_uuid': skin['levels'][0]['uuid']}
            WeapenList.append(data)

    return WeapenList


####################################################################################################
###################https://github.com/HeyM1ke/ValorantClientAPI#####################################
####################################################################################################


async def fetch_user_gameID(ru:RiotUserToken) -> dict:
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


async def fetch_daily_shop(ru:RiotUserToken) -> dict:
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


async def fetch_valorant_point(ru:RiotUserToken)-> dict:
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


async def fetch_vp_rp_dict(ru:RiotUserToken)-> dict[str,int]:
    """获取vp和r点的dict，先调用原始api，再取出vp和rp
    - {'vp': vp, 'rp': rp}
    """
    resp = await fetch_valorant_point(ru)
    vp = resp["Balances"]["85ad13f7-3d1b-5128-9eb2-7cd8ee0b5741"]  #vp
    rp = resp["Balances"]["e59aa87c-4cbf-517a-5983-6e81511be9b7"]  #R点
    return {'vp': vp, 'rp': rp}


async def fetch_item_price_all(ru:RiotUserToken)-> dict:
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


async def fetch_item_price_uuid(ru:RiotUserToken, item_id: str)-> str:
    """获取商品价格（用uuid获取单个价格）
    - 返回值为 "0" 代表没有找到
    """
    res = await fetch_item_price_all(ru)  #获取所有价格

    for item in res['Offers']:  #遍历查找指定uuid
        if item_id == item['OfferID']:
            return item

    return "0"  #没有找到


async def fetch_player_loadout(ru:RiotUserToken)->dict:
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


async def fetch_player_contract(ru:RiotUserToken)->dict:
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

async def fetch_player_level(ru:RiotUserToken) -> dict:
    """获取玩家的等级信息
    """
    url = "https://pd.ap.a.pvp.net/account-xp/v1/players/"
    headers = {
        "Content-Type": "application/json",
        "X-Riot-Entitlements-JWT": ru.entitlements_token,
        "Authorization": "Bearer " + ru.access_token,
    }
    async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers) as response:
                res = json.loads(await response.text())

    return res


async def fetch_match_histroy(ru:RiotUserToken,startIndex=0,endIndex=20) -> dict:
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

async def fetch_match_details(ru:RiotUserToken,match_id:str) -> dict:
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


###########################################valorant-api.com#############################################


async def fetch_item_iters(iters_id: str)-> dict:
    """获取全部的皮肤等级（史诗/传说）"""
    url = "https://valorant-api.com/v1/contenttiers/" + iters_id
    headers = {'Connection': 'close'}
    params = {"language": "zh-TW"}
    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers, params=params) as response:
            res_iters = json.loads(await response.text())

    return res_iters


async def fetch_skins_all()->dict:
    """获取所有皮肤"""
    url = "https://valorant-api.com/v1/weapons/skins"
    headers = {'Connection': 'close'}
    params = {"language": "zh-TW"}
    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers, params=params) as response:
            res_skin = json.loads(await response.text())

    return res_skin


async def fetch_bundles_all()->dict:
    """获取所有皮肤捆绑包"""
    url = "https://valorant-api.com/v1/bundles"
    headers = {'Connection': 'close'}
    params = {"language": "zh-TW"}
    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers, params=params) as response:
            res_bundle = json.loads(await response.text())

    return res_bundle


async def fetch_contract_uuid(id:str) -> dict:
    """获取通行证情况，uuid"""
    url = "https://valorant-api.com/v1/contracts/" + id
    headers = {'Connection': 'close'}
    params = {"language": "zh-TW"}
    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers, params=params) as response:
            res_con = json.loads(await response.text())

    return res_con


async def fetch_playercard_uuid(id:str)-> dict:
    """获取玩家卡面，uuid"""
    url = "https://valorant-api.com/v1/playercards/" + id
    headers = {'Connection': 'close'}
    params = {"language": "zh-TW"}
    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers, params=params) as response:
            res_card = json.loads(await response.text())

    return res_card


async def fetch_title_uuid(id:str)-> dict:
    """获取玩家称号，uuid"""
    url = "https://valorant-api.com/v1/playertitles/" + id
    headers = {'Connection': 'close'}
    params = {"language": "zh-TW"}
    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers, params=params) as response:
            res_title = json.loads(await response.text())

    return res_title


async def fetch_spary_uuid(id:str)-> dict:
    """获取喷漆，uuid"""
    url = "https://valorant-api.com/v1/sprays/" + id
    headers = {'Connection': 'close'}
    params = {"language": "zh-TW"}
    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers, params=params) as response:
            res_sp = json.loads(await response.text())

    return res_sp


async def fetch_buddies_uuid(id:str)->dict:
    """获取吊坠，uuid"""
    url = "https://valorant-api.com/v1/buddies/levels/" + id
    headers = {'Connection': 'close'}
    params = {"language": "zh-TW"}
    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers, params=params) as response:
            res_sp = json.loads(await response.text())

    return res_sp


async def fetch_skinlevel_uuid(id:str)->dict:
    """获取皮肤，通过lv0的uuid"""
    url = f"https://valorant-api.com/v1/weapons/skinlevels/" + id
    headers = {'Connection': 'close'}
    params = {"language": "zh-TW"}
    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers, params=params) as response:
            res_skin = json.loads(await response.text())
    return res_skin


async def fetch_agents_uuid(agent_uuid:str) -> dict:
    """获取英雄信息，通过uuid"""
    url = f"https://valorant-api.com/v1/agents/{agent_uuid}"
    headers = {'Connection': 'close'}
    params = {"language": "zh-TW"}
    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers, params=params) as response:
            res_skin = json.loads(await response.text())
    return res_skin


async def fetch_maps_all() -> dict:
    """获取所有地图"""
    url = "https://valorant-api.com/v1/maps"
    headers = {'Connection': 'close'}
    params = {"language": "zh-TW"}
    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers, params=params) as response:
            res_skin = json.loads(await response.text())
    return res_skin


async def fetch_maps_url(map_url:str) -> dict:
    """通过地图的url获取地图信息
    - map_url: `/Game/Maps/Triad/Triad`
    """
    maps = await fetch_maps_all()
    ret = {}
    for m in maps["data"]:
        if m["mapUrl"] == map_url:
            ret = m
    
    return ret


#######################################通行证#######################################################


# 获取不同奖励的信息
async def get_reward(reward):
    reward_type = reward['reward']['type']
    print("get_reward() ", reward_type)
    if reward_type == 'PlayerCard':  #玩家卡面
        return await fetch_playercard_uuid(reward['reward']['uuid'])
    elif reward_type == 'Currency':  #代币
        # 拳头通行证返回值里面没有数量，我谢谢宁
        return {
            'data': {
                "assetPath": "ShooterGame/Content/Currencies/Currency_UpgradeToken_DataAsset",
                "displayIcon":
                "https://media.valorant-api.com/currencies/e59aa87c-4cbf-517a-5983-6e81511be9b7/displayicon.png",
                "displayName": "輻能點數",
                "displayNameSingular": "輻能點數",
                "largeIcon":
                "https://media.valorant-api.com/currencies/e59aa87c-4cbf-517a-5983-6e81511be9b7/largeicon.png",
                "uuid": "e59aa87c-4cbf-517a-5983-6e81511be9b7"
            }
        }
    elif reward_type == 'EquippableSkinLevel':  #皮肤
        return fetch_skinlevel_uuid(reward['reward']['uuid'])
    elif reward_type == 'Spray':  #喷漆
        return await fetch_spary_uuid(reward['reward']['uuid'])
    elif reward_type == 'EquippableCharmLevel':  #吊坠
        return await fetch_buddies_uuid(reward['reward']['uuid'])
    elif reward_type == 'Title':  #玩家头衔
        return await fetch_title_uuid(reward['reward']['uuid'])

    return None
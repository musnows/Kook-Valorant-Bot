# encoding: utf-8:
import json
import aiohttp
from khl import Bot, Message
from khl.card import Card, CardMessage, Element, Module, Types

# 预加载文件
from endpoints.FileManage import GameIdDict, ValErrDict, ValBundleList, ValItersList, ValPriceList, ValSkinList


####################################保存用户的游戏ID操作#######################################

#保存用户id
async def saveid_main(msg: Message, game_id: str):
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
async def saveid_count(msg: Message):
    countD = len(GameIdDict)
    await msg.reply(f"目前狸狸已经记下了`{countD}`个小伙伴的id喽~")


# 实现读取用户游戏ID并返回
async def myid_main(msg: Message):
    if msg.author_id in GameIdDict.keys():
        flag = 1  #找到了对应用户的id
        await msg.reply(f'游戏id: ' + GameIdDict[msg.author_id])
    else:
        countD = len(GameIdDict)
        await msg.reply(f"狸狸不知道你的游戏id呢，用`/saveid`告诉我吧！\n```\n/saveid 你的游戏id```\n目前狸狸已经记下了`{countD}`个小伙伴的id喽！")


####################################  err code  ################################################


# 查询游戏错误码
async def val_errcode(msg: Message, num: str = "-1"):
    if num == "-1":
        await msg.reply(
            '目前支持查询的错误信息有：\n```\n0-1,4-5,7-21,29,31,33,38,43-46,49-70,81,84,128,152,1067,9001,9002,9003\n```\n注：van和val错误码都可用本命令查询'
        )
    elif num in ValErrDict:
        await msg.reply(ValErrDict[num])
    else:
        await msg.reply('抱歉，本狸还不会这个呢~ 你能教教我吗？[当然!](https://f.wps.cn/w/awM5Ej4g/)')


#关于dx报错的解决方法
async def dx123(msg: Message):
    await msg.reply(
        '报错弹窗内容为`The following component(s) are required to run this program:DirectX Runtime`\n需要下载微软官方驱动安装，官网搜索[DirectX End-User Runtime Web Installer]\n你还可以下载本狸亲测可用的DX驱动 [链接](https://pan.baidu.com/s/1145Ll8vGtByMW6OKk6Zi2Q)，暗号是1067哦！\n狸狸记得之前玩其他游戏的时候，也有遇到过这个问题呢~'
    )


###################################### local files search ######################################################


#从list中获取价格
def fetch_item_price_bylist(item_id):
    for item in ValPriceList['Offers']:  #遍历查找指定uuid
        if item_id == item['OfferID']:
            return item


#从list中获取等级(这个需要手动更新)
def fetch_item_iters_bylist(iter_id):
    for iter in ValItersList['data']:  #遍历查找指定uuid
        if iter_id == iter['uuid']:
            res = {'data': iter}  #所以要手动创建一个带data的dict作为返回值
            return res


#从list中获取皮肤
def fetch_skin_bylist(item_id):
    res = {}  #下面我们要操作的是获取通行证的皮肤，但是因为遍历的时候已经跳过data了，返回的时候就不好返回
    for item in ValSkinList['data']:  #遍历查找指定uuid
        if item_id == item['levels'][0]['uuid']:
            res['data'] = item  #所以要手动创建一个带data的dict作为返回值
            return res


#从list中，通过皮肤名字获取皮肤列表
def fetch_skin_byname_list(name):
    wplist = list()  #包含该名字的皮肤list
    for skin in ValSkinList['data']:
        if name in skin['displayName']:
            data = {'displayName': skin['displayName'], 'lv_uuid': skin['levels'][0]['uuid']}
            wplist.append(data)
    return wplist


#从list中通过皮肤lv0uuid获取皮肤等级
def fetch_skin_iters_bylist(item_id):
    for it in ValSkinList['data']:
        if it['levels'][0]['uuid'] == item_id:
            res_iters = fetch_item_iters_bylist(it['contentTierUuid'])
            return res_iters


# 用名字查询捆绑包包含什么枪
async def fetch_bundle_weapen_byname(name):
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


#获取用户游戏id(从使用对象修改成使用文件中的内容)
async def fetch_user_gameID(auth):
    url = "https://pd.ap.a.pvp.net/name-service/v2/players"
    payload = json.dumps([auth['auth_user_id']])
    headers = {
        "Content-Type": "application/json",
        "X-Riot-Entitlements-JWT": auth['entitlements_token'],
        "Authorization": "Bearer " + auth['access_token']
    }
    async with aiohttp.ClientSession() as session:
        async with session.put(url, headers=headers, data=payload) as response:
            res = json.loads(await response.text())
    return res


# 获取每日商店
async def fetch_daily_shop(u):
    url = "https://pd.ap.a.pvp.net/store/v2/storefront/" + u['auth_user_id']
    headers = {
        "Content-Type": "application/json",
        "X-Riot-Entitlements-JWT": u['entitlements_token'],
        "Authorization": "Bearer " + u['access_token']
    }
    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers) as response:
            res = json.loads(await response.text())
    return res


# Api获取玩家的vp和r点
async def fetch_valorant_point(u):
    url = "https://pd.ap.a.pvp.net/store/v1/wallet/" + u['auth_user_id']
    headers = {
        "Content-Type": "application/json",
        "X-Riot-Entitlements-JWT": u['entitlements_token'],
        "Authorization": "Bearer " + u['access_token']
    }
    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers) as response:
            res = json.loads(await response.text())
    return res


# 获取vp和r点的dict
async def fetch_vp_rp_dict(u):
    resp = await fetch_valorant_point(u)
    vp = resp["Balances"]["85ad13f7-3d1b-5128-9eb2-7cd8ee0b5741"]  #vp
    rp = resp["Balances"]["e59aa87c-4cbf-517a-5983-6e81511be9b7"]  #R点
    return {'vp': vp, 'rp': rp}


# 获取商品价格（所有）
async def fetch_item_price_all(u):
    url = "https://pd.ap.a.pvp.net/store/v1/offers/"
    headers = {
        "Content-Type": "application/json",
        "X-Riot-Entitlements-JWT": u['entitlements_token'],
        "Authorization": "Bearer " + u['access_token']
    }
    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers) as response:
            res = json.loads(await response.text())

    return res


# 获取商品价格（用uuid获取单个价格）
async def fetch_item_price_uuid(u, item_id: str):
    res = await fetch_item_price_all(u)  #获取所有价格

    for item in res['Offers']:  #遍历查找指定uuid
        if item_id == item['OfferID']:
            return item

    return "0"  #没有找到


# 获取皮肤等级（史诗/传说）
async def fetch_item_iters(iters_id: str):
    url = "https://valorant-api.com/v1/contenttiers/" + iters_id
    headers = {'Connection': 'close'}
    params = {"language": "zh-TW"}
    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers, params=params) as response:
            res_iters = json.loads(await response.text())

    return res_iters


# 获取所有皮肤
async def fetch_skins_all():
    url = "https://valorant-api.com/v1/weapons/skins"
    headers = {'Connection': 'close'}
    params = {"language": "zh-TW"}
    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers, params=params) as response:
            res_skin = json.loads(await response.text())

    return res_skin


# 获取所有皮肤捆绑包
async def fetch_bundles_all():
    url = "https://valorant-api.com/v1/bundles"
    headers = {'Connection': 'close'}
    params = {"language": "zh-TW"}
    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers, params=params) as response:
            res_bundle = json.loads(await response.text())

    return res_bundle


# 获取获取玩家当前装备的卡面和称号
async def fetch_player_loadout(u):
    url = f"https://pd.ap.a.pvp.net/personalization/v2/players/{u['auth_user_id']}/playerloadout"
    headers = {
        "Content-Type": "application/json",
        "X-Riot-Entitlements-JWT": u['entitlements_token'],
        "Authorization": "Bearer " + u['access_token'],
        'Connection': 'close'
    }
    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers) as response:
            res = json.loads(await response.text())

    return res


# 获取合约（任务）进度
# client version from https://valorant-api.com/v1/version
async def fetch_player_contract(u):
    #url="https://pd.ap.a.pvp.net/contract-definitions/v2/definitions/story"
    url = f"https://pd.ap.a.pvp.net/contracts/v1/contracts/" + u['auth_user_id']
    headers = {
        "Content-Type": "application/json",
        "X-Riot-Entitlements-JWT": u['entitlements_token'],
        "Authorization": "Bearer " + u['access_token'],
        "X-Riot-ClientPlatform":
        "ew0KCSJwbGF0Zm9ybVR5cGUiOiAiUEMiLA0KCSJwbGF0Zm9ybU9TIjogIldpbmRvd3MiLA0KCSJwbGF0Zm9ybU9TVmVyc2lvbiI6ICIxMC4wLjE5MDQyLjEuMjU2LjY0Yml0IiwNCgkicGxhdGZvcm1DaGlwc2V0IjogIlVua25vd24iDQp9",
        "X-Riot-ClientVersion": "release-05.03-shipping-8-745499"
    }
    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers) as response:
            res = json.loads(await response.text())

    return res


# 获取玩家当前通行证情况，uuid
async def fetch_contract_uuid(id):
    url = "https://valorant-api.com/v1/contracts/" + id
    headers = {'Connection': 'close'}
    params = {"language": "zh-TW"}
    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers, params=params) as response:
            res_con = json.loads(await response.text())

    return res_con


# 获取玩家卡面，uuid
async def fetch_playercard_uuid(id):
    url = "https://valorant-api.com/v1/playercards/" + id
    headers = {'Connection': 'close'}
    params = {"language": "zh-TW"}
    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers, params=params) as response:
            res_card = json.loads(await response.text())

    return res_card


# 获取玩家称号，uuid
async def fetch_title_uuid(id):
    url = "https://valorant-api.com/v1/playertitles/" + id
    headers = {'Connection': 'close'}
    params = {"language": "zh-TW"}
    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers, params=params) as response:
            res_title = json.loads(await response.text())

    return res_title


# 获取喷漆，uuid
async def fetch_spary_uuid(id):
    url = "https://valorant-api.com/v1/sprays/" + id
    headers = {'Connection': 'close'}
    params = {"language": "zh-TW"}
    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers, params=params) as response:
            res_sp = json.loads(await response.text())

    return res_sp


# 获取吊坠，uuid
async def fetch_buddies_uuid(id):
    url = "https://valorant-api.com/v1/buddies/levels/" + id
    headers = {'Connection': 'close'}
    params = {"language": "zh-TW"}
    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers, params=params) as response:
            res_sp = json.loads(await response.text())

    return res_sp


# 获取皮肤，通过lv0的uuid
async def fetch_skinlevel_uuid(id):
    url = f"https://valorant-api.com/v1/weapons/skinlevels/" + id
    headers = {'Connection': 'close'}
    params = {"language": "zh-TW"}
    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers, params=params) as response:
            res_skin = json.loads(await response.text())
    return res_skin


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


# 创建一个玩家任务和通信证的卡片消息
async def create_cm_contract(msg: Message):
    # 预加载用户token(其实已经没用了)
    with open("./log/UserAuthID.json", 'r', encoding='utf-8') as frau:
        UserTokenDict = json.load(frau)

    userdict = UserTokenDict[msg.author_id]
    # 获取玩家当前任务和通行证情况
    player_mision = await fetch_player_contract(userdict)
    print(player_mision)
    interval_con = len(player_mision['Contracts'])
    battle_pass = player_mision['Contracts'][interval_con - 1]
    print(battle_pass, '\n')
    contract = await fetch_contract_uuid(battle_pass["ContractDefinitionID"])
    print(contract, '\n')
    cur_chapter = battle_pass['ProgressionLevelReached'] // 5  #计算出当前的章节
    remain_lv = battle_pass['ProgressionLevelReached'] % 5  #计算出在当前章节的位置
    print(cur_chapter, ' - ', remain_lv)
    if remain_lv:  #说明还有余度
        cur_chapter += 1  #加1
    else:  #为0的情况，需要修正为5。比如30级是第六章节的最后一个
        remain_lv = 5

    reward_list = contract['data']['content']['chapters'][cur_chapter - 1]  #当前等级所属章节
    print(reward_list, '\n')
    reward = reward_list['levels'][remain_lv - 1]  #当前所处的等级和奖励
    print(reward)
    reward_next = ""  #下一个等级的奖励
    if remain_lv < 5:
        reward_next = reward_list['levels'][remain_lv]  #下一级
    elif remain_lv >= 5 and cur_chapter < 11:  #避免越界
        reward_next = contract['data']['content']['chapters'][cur_chapter]['levels'][0]  #下一章节的第一个
    print(reward_next, '\n')

    c1 = Card(Module.Header(f"通行证 - {contract['data']['displayName']}"), Module.Divider())
    reward_res = await get_reward(reward)
    reward_nx_res = await get_reward(reward_next)
    print(reward_res, '\n', reward_nx_res, '\n')

    cur = f"当前等级：{battle_pass['ProgressionLevelReached']}\n"
    cur += f"当前奖励：{reward_res['data']['displayName']}\n"
    cur += f"奖励类型：{reward['reward']['type']}\n"
    cur += f"经验XP：{reward['xp']-battle_pass['ProgressionTowardsNextLevel']}/{reward['xp']}\n"
    c1.append(Module.Section(cur))
    if 'displayIcon' in reward_res['data']:  #有图片才插入
        c1.append(Module.Container(Element.Image(src=reward_res['data']['displayIcon'])))  #将图片插入进去
    next = f"下一奖励：{reward_nx_res['data']['displayName']}  - 类型:{reward_next['reward']['type']}\n"
    c1.append(Module.Context(Element.Text(next, Types.Text.KMD)))
    return c1

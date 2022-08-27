# encoding: utf-8:
import json
import valorant
import aiohttp
import requests
import time

from khl import Bot, Message
from khl.card import CardMessage, Card, Module, Element, Types

# 用读取来的 config 初始化 bot，字段对应即可
with open('./config/config.json', 'r', encoding='utf-8') as f:
    config = json.load(f)

bot = Bot(token=config['token'])

##########################################################################################
##########################################################################################

# 没啥用的中二病指令
async def kda123(msg: Message):
    await msg.reply('本狸就是女王！\n[https://s1.ax1x.com/2022/07/03/jGFl0U.jpg](https://s1.ax1x.com/2022/07/03/jGFl0U.jpg)')

# 查询皮肤！只支持English皮肤名
async def skin123(msg: Message,name:str):
    try:
        # 读取valorant api的key
        with open('./config/valorant.json', 'r', encoding='utf-8') as f:
            config = json.load(f)
        client = valorant.Client(config['token'], locale=None)
        skins = client.get_skins()
        #name = input("Search a Valorant Skin Collection: ")
        results = skins.find_all(name=lambda x: name.lower() in x.lower())
        cm = CardMessage()
        c1 = Card(Module.Header('查询到你想看的皮肤了！'),Module.Context('还想查其他皮肤吗...'))
        c1.append(Module.Divider())
        for skin in results:
            c1.append(Module.Section(f"\t{skin.name.ljust(21)} ({skin.localizedNames['zh-TW']})"))
            #print(f"\t{skin.name.ljust(21)} ({skin.localizedNames['zh-CN']})")
        cm.append(c1)
        await msg.reply(cm)
    except Exception as result:
        await msg.reply("未知错误 %s" % result)

# 获取排行榜上的玩家，默认获取前15位胜场超过10的玩家
async def lead123(msg: Message,sz:int,num:int):
    try:
        with open('./config/valorant.json', 'r', encoding='utf-8') as f:
            config = json.load(f)
        client = valorant.Client(config['token'], locale=None,region='ap',route='asia')
        lb = client.get_leaderboard(size=sz)
        players = lb.players.get_all(numberOfWins=num)# 筛选出胜场超过num的
        cm = CardMessage()
        c1 = Card(Module.Header('查询到你想看的排行榜了！'),Module.Context('什么？你也上榜了嘛...'))
        c1.append(Module.Divider())
        for p in lb.players:
            c1.append(Module.Section(f"#{p.leaderboardRank} - {p.gameName} ({p.numberOfWins} wins)"))
            #print(f"#{p.leaderboardRank} - {p.gameName} ({p.numberOfWins} wins)")
        cm.append(c1)
        await msg.reply(cm)
    except Exception as result:
        await msg.reply("未知错误 %s" % result)


####################################保存用户的游戏ID操作#######################################

# 预加载文件
with open("./log/game_idsave.json", 'r',encoding='utf-8') as frgm:
    GameIdDict = json.load(frgm)

#保存用户id
async def saveid123(msg: Message,game_id:str):
    global GameIdDict
    flag=0
    # 如果用户id已有，则进行修改
    if msg.author_id in GameIdDict.keys():
        GameIdDict[msg.author_id]=game_id
        await msg.reply(f'本狸已经修改好你的游戏id啦!')
        flag=1#修改完毕后，将flag置为1

    #没有该用户信息，进行追加操作
    if flag==0:
        GameIdDict[msg.author_id]=game_id
        await msg.reply(f"本狸已经记下你的游戏id喽~")
    # 修改/新增都需要写入文件
    with open("./log/game_idsave.json",'w',encoding='utf-8') as fw2:
        json.dump(GameIdDict,fw2,indent=2,sort_keys=True, ensure_ascii=False)
      

# 让阿狸记住游戏id的help指令
async def saveid_1(msg: Message):
    await msg.reply("基本方式看图就行啦！如果你的id之中有空格，需要用**英文的单引号**括起来哦！就像这样: `/saveid '你的id'`\n[https://s1.ax1x.com/2022/06/27/jV2qqe.png](https://s1.ax1x.com/2022/06/27/jV2qqe.png)\n注：阿狸升级以后已经不需要用单引号括起来了")

# 显示已有id的个数
async def saveid_2(msg: Message):
    countD = len(GameIdDict)
    await msg.reply("目前狸狸已经记下了%d个小伙伴的id喽~"% (countD))

     
# 实现读取用户游戏ID并返回
async def myid123(msg: Message):
    flag=0
    if msg.author_id in GameIdDict.keys():
           flag=1#找到了对应用户的id
           await msg.reply(f'游戏id: '+GameIdDict[msg.author_id])

    if flag==0:
       countD= len(GameIdDict)
       await msg.reply("狸狸不知道你的游戏id呢，用`/saveid`告诉我吧！\n```\n/saveid 你的游戏id```\n目前狸狸已经记下了%d个小伙伴的id喽！"% (countD))


##########################################################################################

# 查询游戏错误码
async def val123(msg: Message, num: int):
    # msg 触发指令为 '/val 错误码'
    # msg.reply() 根据错误码回复对应解决方法
    if num ==0:
        await msg.reply('目前支持查询的错误信息有：\n「val 1,4-5,7-21,29,31,33,38,43-46,49-70,81,84,128,152,1067,9001,9002」')
    elif num == 1067:
        await msg.reply('1.请检查您的电脑是否有安装「完美对战平台」，可能有冲突；\n2.请在「控制面板-时钟和区域」中尝试修改时区为`美国`或者`香港`，这不会影响您电脑的时间显示；\n3.尝试重启游戏、重启加速器（更换节点）、重启电脑；\n4.可能和您的鼠标驱动有冲突，尝试关闭雷蛇/罗技的鼠标驱动软件;\n5.尝试进入bios开启tmp2.0\n6.卸载valorant，打开csgo/ow/r6。')
    elif num == 1:
        await msg.reply('网络连接问题，请重启游戏、更换加速器（节点）、重启电脑。')
    elif num == 4:
        await msg.reply('您的名称无效，请重新注册账户')
    elif num == 5:
        await msg.reply('1.账户在别处登录；\n2.网络连接问题，请重启游戏、更换加速器（节点）、重启电脑。')
    elif num == 7:
        await msg.reply('账户可能被冻结，请查看注册邮箱是否有相关邮件信息')
    elif num > 7 and num <=11:
        await msg.reply('网络连接问题，请重启游戏、更换加速器（节点）、重启电脑。')
    elif num == 12:
        await msg.reply('客户端启动超时，检查网络后重启客户端，或重新下载游戏客户端')
    elif num >= 13 and num <=21:
        await msg.reply('网络连接问题，请重启游戏、更换加速器（节点）、重启电脑。')
    elif num == 29:
        await msg.reply('1.防火墙问题，尝试关闭系统防火墙；\n2.网络连接问题，请重启游戏、更换加速器（节点）、重启电脑。')
    elif num == 31:
        await msg.reply('网络连接问题，请重启游戏、更换加速器（节点）、重启电脑。')
    elif num == 33:
        await msg.reply('客户端启动超时，检查网络后重启客户端，或重新下载游戏客户端')
    elif num == 38:
        await msg.reply('网络连接问题，请重启游戏、更换加速器（节点）、重启电脑。')
    elif num == 43:
        await msg.reply('客户端启动超时，检查网络后重启客户端，或重新下载游戏客户端')
    elif num >= 44 and num <= 45:
        await msg.reply('反作弊未初始化：重启拳头客户端,如果未恢复,先卸载Vanguard,重启电脑后再启动游戏')
    elif num == 46:
        await msg.reply('服务器维护中……')
    elif num >= 49 and num <= 60:
        await msg.reply('网络连接问题，请重启游戏、更换加速器（节点）、重启电脑。')
    elif num == 61:
        await msg.reply('哎呀你干了啥，怎么被系统ban了？狸狸可不喜欢你这样哦~')
    elif num >= 62 and num <= 67:
        await msg.reply('网络连接问题，请重启游戏、更换加速器（节点）、重启电脑。')
    elif num == 68:
        await msg.reply('1.请尝试关闭valorant，右键图标以管理员身份运行游戏\n2.网络连接问题，请重启游戏、更换加速器（节点）、重启电脑。')
    elif num >= 69 and num <= 70:
        await msg.reply('网络连接问题，请重启游戏、更换加速器（节点）、重启电脑。')
    elif num == 81:
        await msg.reply('网络连接问题，请重启游戏、更换加速器（节点）、重启电脑。')
    elif num == 84:
        await msg.reply('网络连接问题，请重启游戏、更换加速器（节点）、重启电脑。')
    elif num == 128:
        await msg.reply('1.重启电脑和游戏客户端，卸载Vanguard、卸载游戏进行重装；\n2.需要提醒您，修改系统配置是一项有风险的操作，请确认您需要这么做！\n请查看本图进行操作:[https://s1.ax1x.com/2022/06/24/jFGXBd.png](https://s1.ax1x.com/2022/06/24/jFGXBd.png) ')
        #这里要使用[URL](URL)的方式，让开黑啦识别出图片url并直接显示
    elif num == 152:
        await msg.reply('您的硬件被识别封锁，这可不是一个好兆头。')
    elif num == 9001:
        await msg.reply('`VAN9001_This build of Vanguard requires TPM version 2.0 and secure boot to be enabled in order to play.`\n需要您进电脑主板的bios打开tmp2.0哦！')
    elif num == 9002:
        await msg.reply('`VAN9002—This build of Vanguard requires Control Flow Guard (CFG)to be enabled in system exploit protection settings.`\n设置页面搜索Exploit Protection ，[开启控制流保护（CFG）](https://www.bilibili.com/read/cv11536577)。')
    elif num == 10086:
        await msg.reply('本狸才不给你的手机充话费呢！')
    elif num == 10000:
        await msg.reply('本狸提醒您：谨防电信诈骗哦~')
    else:
        await msg.reply('抱歉，本狸还不会这个呢~ 你能教教我吗？[当然!](https://f.wps.cn/w/awM5Ej4g/)')

#关于dx报错的解决方法
async def dx123(msg: Message):
    await msg.reply('报错弹窗内容为`The following component(s) are required to run this program:DirectX Runtime`\n需要下载微软官方驱动安装，官网搜索[DirectX End-User Runtime Web Installer]\n你还可以下载本狸亲测可用的DX驱动 [链接](https://pan.baidu.com/s/1145Ll8vGtByMW6OKk6Zi2Q)，暗号是1067哦！\n狸狸记得之前玩其他游戏的时候，也有遇到过这个问题呢~')


####################################################################################################
###################https://github.com/HeyM1ke/ValorantClientAPI#####################################
####################################################################################################

import riot_auth

# 获取拳头的token
# 此部分代码来自 https://github.com/floxay/python-riot-auth
async def authflow(user: str, passwd: str):
    CREDS = user, passwd
    auth = riot_auth.RiotAuth()
    await auth.authorize(*CREDS)
    # Reauth using cookies. Returns a bool indicating whether the reauth attempt was successful.
    # await auth.reauthorize()
    # print(f"Access Token Type: {auth.token_type}\n")
    # print(f"Access Token: {auth.access_token}\n")
    # print(f"Entitlements Token: {auth.entitlements_token}\n")
    # print(f"User ID: {auth.user_id}")
    return auth

#获取用户游戏id
async def fetch_user_gameID(auth):
    url = "https://pd.AP.a.pvp.net/name-service/v2/players"
    payload = json.dumps([auth.user_id])
    headers = {
        "Content-Type": "application/json",
        "X-Riot-Entitlements-JWT": auth.entitlements_token,
        "Authorization": "Bearer " + auth.access_token
    }
    async with aiohttp.ClientSession() as session:
        async with session.put(url, headers=headers,data=payload) as response:
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

# 获取vp和r点
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


# 获取商品价格（所有）
async def fetch_item_price_all(u):
    url="https://pd.ap.a.pvp.net/store/v1/offers/"
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
async def fetch_item_price_uuid(u,item_id:str):
    res=await fetch_item_price_all(u)#获取所有价格

    for item in res['Offers']:#遍历查找指定uuid
        if item_id == item['OfferID']:
            return item

    return "0"#没有找到


# 获取皮肤等级（史诗/传说）
async def fetch_item_iters(iters_id:str):
    url="https://valorant-api.com/v1/contenttiers/"+iters_id
    headers = {'Connection': 'close'}
    params = {"language": "zh-TW"}
    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers,params=params) as response:
            res_iters = json.loads(await response.text())

    return res_iters
    
# 获取所有皮肤
async def fetch_skins_all():
    url="https://valorant-api.com/v1/weapons/skins"
    headers = {'Connection': 'close'}
    params = {"language": "zh-TW"}
    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers,params=params) as response:
            res_skin = json.loads(await response.text())

    return res_skin
    
# 获取所有皮肤捆绑包
async def fetch_bundles_all():
    url="https://valorant-api.com/v1/bundles"
    headers = {'Connection': 'close'}
    params = {"language": "zh-TW"}
    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers,params=params) as response:
            res_bundle = json.loads(await response.text())

    return res_bundle

# 获取获取玩家当前装备的卡面和称号
async def fetch_player_loadout(u):
    url=f"https://pd.ap.a.pvp.net/personalization/v2/players/{u['auth_user_id']}/playerloadout"
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
    url=f"https://pd.ap.a.pvp.net/contracts/v1/contracts/"+u['auth_user_id']
    headers = {
        "Content-Type": "application/json",
        "X-Riot-Entitlements-JWT": u['entitlements_token'],
        "Authorization": "Bearer " + u['access_token'],
        "X-Riot-ClientPlatform" : "ew0KCSJwbGF0Zm9ybVR5cGUiOiAiUEMiLA0KCSJwbGF0Zm9ybU9TIjogIldpbmRvd3MiLA0KCSJwbGF0Zm9ybU9TVmVyc2lvbiI6ICIxMC4wLjE5MDQyLjEuMjU2LjY0Yml0IiwNCgkicGxhdGZvcm1DaGlwc2V0IjogIlVua25vd24iDQp9",
        "X-Riot-ClientVersion": "release-05.03-shipping-8-745499"
    }
    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers) as response:
            res = json.loads(await response.text())

    return res

# 获取玩家当前通行证情况，uuid
async def fetch_contract_uuid(id):
    url="https://valorant-api.com/v1/contracts/"+id
    headers = {'Connection': 'close'}
    params = {"language": "zh-TW"}
    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers,params=params) as response:
            res_con = json.loads(await response.text())

    return res_con

# 用名字查询捆绑包包含什么枪
async def fetch_bundle_byname(name):
    # 所有皮肤
    with open("./log/ValSkin.json", 'r', encoding='utf-8') as frsk:
        ValSkinList = json.load(frsk)

    WeapenList=list()
    for skin in ValSkinList['data']:
        if name in skin['displayName']:
            # 为了方便查询价格，在这里直接把skin的lv0-uuid也给插入进去
            data={'weapen':skin['displayName'],'lv_uuid':skin['levels'][0]['uuid']}
            WeapenList.append(data)
    
    return WeapenList


# 获取玩家卡面，uuid
async def fetch_playercard_uuid(id):
    url="https://valorant-api.com/v1/playercards/"+id
    headers = {'Connection': 'close'}
    params = {"language": "zh-TW"}
    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers,params=params) as response:
            res_card = json.loads(await response.text())

    return res_card

# 获取玩家称号，uuid
async def fetch_title_uuid(id):
    url="https://valorant-api.com/v1/playertitles/"+id
    headers = {'Connection': 'close'}
    params = {"language": "zh-TW"}
    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers,params=params) as response:
            res_title = json.loads(await response.text())

    return res_title

# 获取喷漆，uuid
async def fetch_spary_uuid(id):
    url="https://valorant-api.com/v1/sprays/"+id
    headers = {'Connection': 'close'}
    params = {"language": "zh-TW"}
    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers,params=params) as response:
            res_sp = json.loads(await response.text())

    return res_sp
    

# 获取吊坠，uuid
async def fetch_buddies_uuid(id):
    url="https://valorant-api.com/v1/buddies/levels/"+id
    headers = {'Connection': 'close'}
    params = {"language": "zh-TW"}
    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers,params=params) as response:
            res_sp = json.loads(await response.text())

    return res_sp

# 获取皮肤，通过lv0的uuid
async def fetch_skinlevel_uuid(id):
    url = f"https://valorant-api.com/v1/weapons/skinlevels/"+id
    headers = {'Connection': 'close'}
    params = {"language": "zh-TW"}
    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers,params=params) as response:
            res_skin = json.loads(await response.text())
    return res_skin